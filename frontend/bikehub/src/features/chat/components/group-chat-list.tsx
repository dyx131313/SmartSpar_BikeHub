/**
 * 群聊列表组件
 */
import React, { useEffect, useState } from 'react';
import { Badge, Button, Input, ScrollArea, Avatar, AvatarFallback, AvatarImage, Tooltip, TooltipTrigger, TooltipContent, DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui';
import { Search, Plus, MoreVertical, Bell, BellOff, Settings, Users, MessageSquare, Crown, Shield, User, X } from 'lucide-react';
import { groupChatAPI } from '../api/group-chat-api';
import { ChatGroup, MemberRole, ChatGroupMember } from '../data/group-chat-types';

interface GroupChatListProps {
  selectedGroupId?: number | null;
  onGroupSelect: (group: ChatGroup) => void;
  onCreateGroup: () => void;
  onSearchUsers: () => void;
}

export const GroupChatList: React.FC<GroupChatListProps> = ({
  selectedGroupId,
  onGroupSelect,
  onCreateGroup,
  onSearchUsers,
}) => {
  const [groups, setGroups] = useState<ChatGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [hasMore, setHasMore] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [membersCache, setMembersCache] = useState<Map<number, ChatGroupMember[]>>(new Map());

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
    const currentUserUsername = localStorage.getItem('username');
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

  useEffect(() => {
    loadGroups(1);
  }, []);

  return (
    <div className="flex flex-col h-full">
      {/* 头部 */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">群聊</h2>
          <div className="flex gap-2">
            <Button variant="ghost" size="sm" onClick={onSearchUsers}>
              <Search className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={onCreateGroup}>
              <Plus className="h-4 w-4" />
            </Button>
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
                  className={`relative p-3 rounded-lg cursor-pointer transition-colors hover:bg-accent/50 ${
                    selectedGroupId === group.id ? 'bg-accent' : ''
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
                          className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100"
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
                        <DropdownMenuItem
                          onClick={(e) => {
                            e.stopPropagation();
                            handleLeaveGroup(group.id, group.name);
                          }}
                          className="text-destructive"
                        >
                          <X className="h-4 w-4 mr-2" />
                          退出群聊
                        </DropdownMenuItem>
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
    </div>
  );
};