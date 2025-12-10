/**
 * 群聊列表组件
 */
import React, { useEffect, useState } from 'react';
import { Badge, Button, Input, ScrollArea, Avatar, AvatarFallback, AvatarImage, Tooltip, TooltipTrigger, TooltipContent, DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui';
import { Search, Plus, MoreVertical, Bell, BellOff, Settings, Users, MessageSquare, Crown, Shield, User, X, Trash2, AlertTriangle } from 'lucide-react';
import { groupChatAPI } from '../api/group-chat-api';
import { ChatGroup, MemberRole, ChatGroupMember } from '../data/group-chat-types';
import { useAuthStore } from '@/stores/auth-store';

interface GroupChatListProps {
  selectedGroupId?: number | null;
  onGroupSelect: (group: ChatGroup) => void;
  onCreateGroup: () => void;
  onSearchUsers: () => void;
  /** 最新创建的群聊，提供后会立即插入列表顶部 */
  createdGroup?: ChatGroup | null;
}

export const GroupChatList: React.FC<GroupChatListProps> = ({
  selectedGroupId,
  onGroupSelect,
  onCreateGroup,
  onSearchUsers,
  createdGroup,
}) => {
  const [groups, setGroups] = useState<ChatGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [hasMore, setHasMore] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [membersCache, setMembersCache] = useState<Map<number, ChatGroupMember[]>>(new Map());
  const [userRole, setUserRole] = useState<string>('');
  const [deletingGroup, setDeletingGroup] = useState<number | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [groupToDelete, setGroupToDelete] = useState<ChatGroup | null>(null);

  // 加载群聊列表
  const loadGroups = async (page = 1, query = '') => {
    try {
      setLoading(true);
      const response = await groupChatAPI.getGroups(page, 20);

      if (page === 1) {
        setGroups(response.groups);
      } else {
        setGroups(prev => [...prev, ...response.groups]);
      }

      setHasMore(response.has_more);
    } catch (error) {
      console.error('加载群聊列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 处理搜索
  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    if (query.trim()) {
      try {
        const response = await groupChatAPI.searchChat(query, 'groups');
        setGroups(response.groups);
      } catch (error) {
        console.error('搜索群聊失败:', error);
      }
    } else {
      loadGroups(1);
    }
  };

  // 加载更多
  const handleLoadMore = () => {
    if (hasMore && !loading) {
      const nextPage = currentPage + 1;
      setCurrentPage(nextPage);
      loadGroups(nextPage, searchQuery);
    }
  };

  // 处理免打扰
  const handleMuteToggle = async (groupId: number, isMuted: boolean) => {
    try {
      // 获取群聊成员列表
      const members = await loadGroupMembers(groupId);
      const currentMemberId = getCurrentUserMemberId(groupId, members);

      if (!currentMemberId) {
        console.error('找不到当前用户的成员信息');
        return;
      }

      await groupChatAPI.updateGroupMember(groupId, currentMemberId, { is_muted: !isMuted });
      setGroups(prev => prev.map(group =>
        group.id === groupId ? { ...group, is_muted: !isMuted } : group
      ));
    } catch (error) {
      console.error('切换免打扰状态失败:', error);
    }
  };

  // 退出群聊
  const handleLeaveGroup = async (groupId: number, groupName: string) => {
    if (!confirm(`确定要退出群聊"${groupName}"吗？`)) return;

    try {
      await groupChatAPI.leaveGroup(groupId);
      setGroups(prev => prev.filter(group => group.id !== groupId));
      if (selectedGroupId === groupId) {
        onGroupSelect({} as ChatGroup);
      }
    } catch (error) {
      console.error('退出群聊失败:', error);
      alert('退出群聊失败，请重试');
    }
  };

  // 获取角色图标
  const getRoleIcon = (role?: MemberRole) => {
    switch (role) {
      case MemberRole.OWNER:
        return <Crown className="h-3 w-3 text-yellow-500" />;
      case MemberRole.ADMIN:
        return <Shield className="h-3 w-3 text-blue-500" />;
      default:
        return <User className="h-3 w-3 text-gray-400" />;
    }
  };

  // 获取群聊类型颜色
  const getGroupTypeColor = (type: string) => {
    switch (type) {
      case 'system':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'private':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-green-100 text-green-800 border-green-200';
    }
  };

  // 获取当前用户的成员ID
  const getCurrentUserMemberId = (groupId: number, members: ChatGroupMember[]): number | undefined => {
    // 假设当前用户的ID可以从localStorage或其他地方获取
    // 这里我们通过用户名来匹配（在实际应用中应该使用用户ID）
    const currentUserUsername = localStorage.getItem('username') || localStorage.getItem('user');
    console.log('获取用户名用于匹配:', currentUserUsername);
    if (currentUserUsername) {
      return members.find(member => member.username === currentUserUsername)?.id;
    }
    return undefined;
  };

  // 加载群聊成员
  const loadGroupMembers = async (groupId: number) => {
    if (membersCache.has(groupId)) {
      return membersCache.get(groupId)!;
    }

    try {
      const response = await groupChatAPI.getGroupMembers(groupId);
      membersCache.set(groupId, response.members);
      return response.members;
    } catch (error) {
      console.error('加载群聊成员失败:', error);
      return [];
    }
  };

  // 删除群聊
  const handleDeleteGroup = async () => {
    if (!groupToDelete) return;

    try {
      setDeletingGroup(groupToDelete.id);
      await groupChatAPI.deleteGroup(groupToDelete.id);

      // 从列表中移除群聊
      setGroups(prev => prev.filter(group => group.id !== groupToDelete.id));

      // 如果删除的是当前选中的群聊，清空选择
      if (selectedGroupId === groupToDelete.id) {
        onGroupSelect({} as ChatGroup);
      }

      // 重新加载群聊列表
      loadGroups(1);

      // 关闭对话框
      setDeleteDialogOpen(false);
      setGroupToDelete(null);

      alert(`群聊"${groupToDelete.name}"已被删除`);
    } catch (error) {
      console.error('删除群聊失败:', error);
      alert('删除群聊失败，请重试');
    } finally {
      setDeletingGroup(null);
    }
  };

  // 打开删除确认对话框
  const openDeleteDialog = (group: ChatGroup) => {
    setGroupToDelete(group);
    setDeleteDialogOpen(true);
  };

  // 检查用户是否有权限删除群聊（仅管理员）
  const canDeleteGroup = (group: ChatGroup) => {
    // 尝试从多个来源获取用户角色
    let userRole: string | null = localStorage.getItem('role') ||
                   localStorage.getItem('user_role') ||
                   localStorage.getItem('user-role');

    // 如果localStorage中没有，尝试从auth store获取
    if (!userRole) {
      const authState = useAuthStore.getState()?.auth?.user;
      const roleFromAuth = authState?.role;
      if (roleFromAuth) {
        // 处理可能是字符串数组的情况
        userRole = Array.isArray(roleFromAuth) ? roleFromAuth[0] : String(roleFromAuth);
      }
      console.log('从 auth store 获取的角色:', roleFromAuth);
    }

    // 只有管理员才能删除群聊
    return userRole === 'admin';
  };

  // 获取删除按钮的显示文本
  const getDeleteButtonText = (group: ChatGroup) => {
    if (!canDeleteGroup(group)) {
      return '无权限删除';
    }
    return '删除群聊';
  };

  useEffect(() => {
    // 获取用户角色 - 尝试多个可能的键名
    const role = localStorage.getItem('role') ||
                 localStorage.getItem('user_role') ||
                 localStorage.getItem('user-role') ||
                 '';

    console.log('=== GroupChatList useEffect ===');
    console.log('从 localStorage 获取的 role:', localStorage.getItem('role'));
    console.log('从 localStorage 获取的 user_role:', localStorage.getItem('user_role'));
    console.log('从 localStorage 获取的 user-role:', localStorage.getItem('user-role'));
    console.log('最终使用的角色:', role);
    console.log('role 类型:', typeof role);
    console.log('localStorage 中的所有键:', Object.keys(localStorage));
    console.log('localStorage 中的 access_token:', localStorage.getItem('access_token')?.substring(0, 50) + '...');
    setUserRole(role);

    loadGroups(1);
  }, []);

  // 当有新建的群聊传入时，立即插入到列表顶部（避免必须刷新）
  useEffect(() => {
    if (createdGroup?.id) {
      setGroups(prev => [createdGroup, ...prev.filter(g => g.id !== createdGroup.id)]);
    }
  }, [createdGroup]);

  // 添加一个定时器检查，以防localStorage在组件渲染后才被设置
  useEffect(() => {
    const checkRoleInterval = setInterval(() => {
      const role = localStorage.getItem('role');
      if (role && role !== userRole) {
        console.log('检测到角色变化:', role);
        setUserRole(role);
      }
    }, 1000);

    return () => clearInterval(checkRoleInterval);
  }, [userRole]);

  return (
    <div className="flex flex-col h-full">
      {/* 头部 */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">群聊</h2>
          <div className="flex items-center gap-4">
            <div className="flex gap-2">
              <Button variant="ghost" size="sm" onClick={onSearchUsers}>
                <Search className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={onCreateGroup}>
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* 搜索框 */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="搜索群聊..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* 群聊列表 */}
      <ScrollArea className="flex-1">
        <div className="p-2">
          {loading && groups.length === 0 ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : groups.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>暂无群聊</p>
              <Button variant="ghost" size="sm" className="mt-2" onClick={onCreateGroup}>
                创建第一个群聊
              </Button>
            </div>
          ) : (
            <div className="space-y-1">
              {groups.map((group) => (
                <div
                  key={group.id}
                  className={`relative p-3 rounded-lg cursor-pointer transition-colors hover:bg-[var(--sidebar-item-hover)] hover:text-[var(--sidebar-foreground)] ${
                    selectedGroupId === group.id
                      ? 'bg-[var(--group-item-active)] text-[var(--sidebar-item-active-text)]'
                      : ''
                  }`}
                  onClick={() => onGroupSelect(group)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 flex-1 min-w-0">
                      {/* 群头像 */}
                      <div className="relative">
                        <Avatar className="h-10 w-10">
                          <AvatarImage src={group.avatar_url} alt={group.name} />
                          <AvatarFallback className="bg-primary/10 text-primary">
                            <Users className="h-5 w-5" />
                          </AvatarFallback>
                        </Avatar>
                        {/* 角色标识 */}
                        <div className="absolute -bottom-1 -right-1 bg-background rounded-full p-0.5">
                          {getRoleIcon(group.user_role)}
                        </div>
                      </div>

                      {/* 群聊信息 */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-medium truncate">{group.name}</h3>
                          <span className={`text-xs px-1.5 py-0.5 rounded-full border ${getGroupTypeColor(group.group_type)}`}>
                            {group.group_type === 'system' ? '系统' : group.group_type === 'private' ? '私密' : '公开'}
                          </span>
                          {group.is_muted && (
                            <Tooltip>
                            <TooltipTrigger asChild>
                              <BellOff className="h-3 w-3 text-muted-foreground" />
                            </TooltipTrigger>
                            <TooltipContent>已开启免打扰</TooltipContent>
                          </Tooltip>
                          )}
                        </div>

                        {group.description && (
                          <p className="text-sm text-muted-foreground truncate mb-1">
                            {group.description}
                          </p>
                        )}

                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <span>{group.member_count || 0}人</span>
                            {group.last_message_time && (
                              <span>·</span>
                            )}
                            {group.last_message_time && (
                              <span>{new Date(group.last_message_time).toLocaleDateString()}</span>
                            )}
                          </div>

                          {/* 未读消息数量 */}
                          {(group.unread_count && group.unread_count > 0) && (
                            <Badge variant="destructive" className="text-xs">
                              {group.unread_count > 99 ? '99+' : group.unread_count}
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* 操作菜单 */}
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          onClick={(e) => {
                            e.stopPropagation();
                            handleMuteToggle(group.id, group.is_muted || false);
                          }}
                        >
                          {group.is_muted ? (
                            <>
                              <Bell className="h-4 w-4 mr-2" />
                              开启消息提醒
                            </>
                          ) : (
                            <>
                              <BellOff className="h-4 w-4 mr-2" />
                              免打扰
                            </>
                          )}
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={(e) => {
                            e.stopPropagation();
                            onGroupSelect(group);
                          }}
                        >
                          <MessageSquare className="h-4 w-4 mr-2" />
                          进入聊天
                        </DropdownMenuItem>
                        {canDeleteGroup(group) && (
                        <DropdownMenuItem
                          onClick={(e) => {
                            e.stopPropagation();
                            openDeleteDialog(group);
                          }}
                          className="text-destructive"
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          {getDeleteButtonText(group)}
                        </DropdownMenuItem>
                      )}
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
              ))}

              {/* 加载更多按钮 */}
              {hasMore && (
                <div className="p-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleLoadMore}
                    disabled={loading}
                    className="w-full"
                  >
                    {loading ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary mr-2"></div>
                    ) : (
                      '加载更多'
                    )}
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      </ScrollArea>

      {/* 删除群聊确认对话框 */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <Trash2 className="h-5 w-5 text-destructive" />
              删除群聊
            </AlertDialogTitle>
            <AlertDialogDescription className="text-base">
              确定要删除群聊"{groupToDelete?.name}"吗？此操作将永久删除该群聊及其所有消息，且无法恢复。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteGroup}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              disabled={deletingGroup === groupToDelete?.id}
            >
              {deletingGroup === groupToDelete?.id ? '删除中...' : '确认删除'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};