/**
 * 管理员群聊管理页面
 */
import React, { useState, useEffect } from 'react';
import { Button, Input, Badge, Table, TableBody, TableCell, TableHead, TableHeader, TableRow, Card, CardContent, CardDescription, CardHeader, CardTitle, Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, ScrollArea, Avatar, AvatarFallback, AvatarImage, Tooltip, DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui';
import { Search, Plus, Users, Settings, Eye, Edit, Trash2, Shield, Ban, Check, X, MoreVertical, Crown, Filter } from 'lucide-react';
import { groupChatAPI } from '../api/group-chat-api';
import { ChatGroup, GroupType, MemberRole, ChatGroupMember } from '../data/group-chat-types';
import { toast } from 'sonner';
import { useConfirm } from '@/components/confirm-provider'

// 过滤器接口
interface GroupFilters {
  type?: GroupType | 'all';
  status?: 'all' | 'active' | 'inactive';
  search?: string;
}

interface AdminGroupManagementProps {
  onGroupSelect?: (group: ChatGroup) => void;
}

export const AdminGroupManagement: React.FC<AdminGroupManagementProps> = ({ onGroupSelect }) => {
  const [groups, setGroups] = useState<ChatGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGroup, setSelectedGroup] = useState<ChatGroup | null>(null);
  const [groupMembers, setGroupMembers] = useState<ChatGroupMember[]>([]);
  const [loadingMembers, setLoadingMembers] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [memberDialogOpen, setMemberDialogOpen] = useState(false);
  const [filterType, setFilterType] = useState<GroupType | 'all'>('all');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'inactive'>('active');

  // 表单数据
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    avatar_url: '',
    group_type: GroupType.PUBLIC,
    max_members: 100,
  });

  // 处理群聊类型变更
  const handleGroupTypeChange = (value: GroupType) => {
    setFormData(prev => ({ ...prev, group_type: value }));
  };

  // 分页状态
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [totalPages, setTotalPages] = useState(0);

  const confirmFn = useConfirm()

  // 加载群聊列表
  const loadGroups = async (page = 1, filters: GroupFilters = {}) => {
    try {
      setLoading(true);
      const response = await groupChatAPI.adminGetAllGroups(page, pageSize);

      // 应用过滤
      let filteredGroups = response.groups;
      if (filters.type && filters.type !== 'all') {
        filteredGroups = filteredGroups.filter(g => g.group_type === filters.type);
      }
      if (filters.status && filters.status !== 'all') {
        filteredGroups = filteredGroups.filter(g => g.is_active === (filters.status === 'active'));
      }
      if (filters.search && typeof filters.search === 'string') {
        const searchLower = filters.search.toLowerCase();
        filteredGroups = filteredGroups.filter(g =>
          g.name.toLowerCase().includes(searchLower) ||
          g.description?.toLowerCase().includes(searchLower)
        );
      }

      setGroups(filteredGroups);
      setTotalPages(Math.ceil(response.total / pageSize));
    } catch (error) {
      console.error('加载群聊列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 加载群聊成员
  const loadGroupMembers = async (groupId: number) => {
    try {
      setLoadingMembers(true);
      const response = await groupChatAPI.getGroupMembers(groupId);
      setGroupMembers(response.members);
    } catch (error) {
      console.error('加载群聊成员失败:', error);
    } finally {
      setLoadingMembers(false);
    }
  };

  // 创建群聊
  const handleCreateGroup = async () => {
    if (!formData.name.trim()) {
      toast.error('请输入群聊名称');
      return;
    }

    // 验证数据格式
    const requestData = {
      name: formData.name.trim(),
      description: formData.description?.trim() || undefined,
      avatar_url: formData.avatar_url?.trim() || undefined,
      group_type: formData.group_type, // 这是枚举值，会序列化为字符串
      max_members: formData.max_members
    };

    console.log('Creating group with data:', requestData);
    console.log('Group type value:', requestData.group_type);
    console.log('Group type typeof:', typeof requestData.group_type);

    try {
      const response = await groupChatAPI.createGroup(requestData);
      console.log('Create group response:', response);
      setGroups(prev => [response.group, ...prev]);
      setCreateDialogOpen(false);
      resetForm();
    } catch (error: any) {
      console.error('创建群聊失败:', error);
      console.error('Error details:', {
        message: error.message,
        status: error.status,
        response: error.response,
        data: error.data
      });

      // 显示更详细的错误信息
      let errorMessage = '创建群聊失败，请重试';
      if (error.response?.data?.error) {
        errorMessage = `创建失败: ${error.response.data.error}`;
      } else if (error.data?.error) {
        errorMessage = `创建失败: ${error.data.error}`;
      } else if (error.message) {
        errorMessage = `创建失败: ${error.message}`;
      }

      toast.error(errorMessage);
    }
  };

  // 更新群聊
  const handleUpdateGroup = async () => {
    if (!selectedGroup || !formData.name.trim()) {
      toast.error('请输入群聊名称');
      return;
    }

    try {
      const response = await groupChatAPI.updateGroup(selectedGroup.id, formData);
      setGroups(prev => prev.map(g => g.id === selectedGroup.id ? response.group : g));
      setEditDialogOpen(false);
      resetForm();
    } catch (error) {
      console.error('更新群聊失败:', error);
      toast.error('更新群聊失败，请重试');
    }
  };

  // 删除群聊
  const handleDeleteGroup = async (group: ChatGroup) => {
    const confirmFn = useConfirm()
    const ok = await confirmFn({ title: '删除群聊', desc: `确定要删除群聊"${group.name}"吗？此操作不可恢复！`, confirmText: '删除', cancelBtnText: '取消', destructive: true })
    if (!ok) {
      return;
    }

    try {
      await groupChatAPI.adminDeleteGroup(group.id);
      setGroups(prev => prev.filter(g => g.id !== group.id));
      if (selectedGroup?.id === group.id) {
        setSelectedGroup(null);
        setGroupMembers([]);
      }
    } catch (error) {
      console.error('删除群聊失败:', error);
      toast.error('删除群聊失败，请重试');
    }
  };

  // 启用/禁用群聊
  const handleToggleGroupStatus = async (group: ChatGroup) => {
    const action = group.is_active ? 'disable' : 'enable';
    const confirmMessage = group.is_active
      ? `确定要禁用群聊"${group.name}"吗？`
      : `确定要启用群聊"${group.name}"吗？`;

    const ok2 = await confirmFn({ title: '确认操作', desc: confirmMessage, confirmText: action === 'disable' ? '禁用' : '启用', cancelBtnText: '取消', destructive: action === 'disable' })
    if (!ok2) return;

    try {
      if (action === 'disable') {
        await groupChatAPI.adminDisableGroup(group.id);
      } else {
        await groupChatAPI.adminEnableGroup(group.id);
      }

      setGroups(prev => prev.map(g =>
        g.id === group.id ? { ...g, is_active: !g.is_active } : g
      ));
    } catch (error) {
      console.error(`${action === 'disable' ? '禁用' : '启用'}群聊失败:`, error);
      toast.error(`${action === 'disable' ? '禁用' : '启用'}群聊失败，请重试`);
    }
  };

  // 更新成员角色
  const handleUpdateMemberRole = async (member: ChatGroupMember, newRole: MemberRole) => {
    if (!selectedGroup) return;

    try {
      await groupChatAPI.updateGroupMember(selectedGroup.id, member.id, { role: newRole });
      setGroupMembers(prev => prev.map(m =>
        m.id === member.id ? { ...m, role: newRole } : m
      ));
    } catch (error) {
      console.error('更新成员角色失败:', error);
      toast.error('更新成员角色失败，请重试');
    }
  };

  // 移除成员
  const handleRemoveMember = async (member: ChatGroupMember) => {
    if (!selectedGroup) return;
    const ok3 = await confirmFn({ title: '移除成员', desc: `确定要将 ${member.full_name} 移出群聊吗？`, confirmText: '移除', cancelBtnText: '取消', destructive: true })
    if (!ok3) return;

    try {
      await groupChatAPI.removeGroupMember(selectedGroup.id, member.id);
      setGroupMembers(prev => prev.filter(m => m.id !== member.id));
    } catch (error) {
      console.error('移除成员失败:', error);
      toast.error('移除成员失败，请重试');
    }
  };

  // 重置表单
  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      avatar_url: '',
      group_type: GroupType.PUBLIC,
      max_members: 100,
    });
  };

  // 打开编辑对话框
  const openEditDialog = (group: ChatGroup) => {
    setSelectedGroup(group);
    setFormData({
      name: group.name,
      description: group.description || '',
      avatar_url: group.avatar_url || '',
      group_type: group.group_type,
      max_members: group.max_members,
    });
    setEditDialogOpen(true);
  };

  // 获取角色图标
  const getRoleIcon = (role?: MemberRole) => {
    switch (role) {
      case MemberRole.OWNER:
        return <Crown className="h-3 w-3 text-yellow-500" />;
      case MemberRole.ADMIN:
        return <Shield className="h-3 w-3 text-blue-500" />;
      default:
        return <Users className="h-3 w-3 text-gray-400" />;
    }
  };

  // 获取群聊类型颜色
  const getGroupTypeColor = (type: GroupType) => {
    switch (type) {
      case GroupType.SYSTEM:
        return 'bg-red-100 text-red-800 border-red-200';
      case GroupType.PRIVATE:
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-green-100 text-green-800 border-green-200';
    }
  };

  useEffect(() => {
    loadGroups(currentPage, {
      search: searchQuery,
      type: filterType,
      status: filterStatus,
    });
    console.log("🧨 CreateGroupDialog mounted");
    return () => console.log("🧨 CreateGroupDialog unmounted");
  }, [currentPage, pageSize, searchQuery, filterType, filterStatus]);

  return (
    <div className="flex h-full gap-6">
      {/* 群聊列表 */}
      <div className="flex-1">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>群聊管理</CardTitle>
                <CardDescription>
                  管理所有群聊，包括创建、编辑、删除和成员管理
                </CardDescription>
              </div>
              <Button onClick={() => setCreateDialogOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                创建群聊
              </Button>
            </div>

            {/* 搜索和过滤 */}
            <div className="flex gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="搜索群聊名称或描述..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>

              <Select value={filterType} onValueChange={(value: GroupType | 'all') => setFilterType(value)}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="群聊类型" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部类型</SelectItem>
                  <SelectItem value={GroupType.PUBLIC}>公开群聊</SelectItem>
                  <SelectItem value={GroupType.PRIVATE}>私密群聊</SelectItem>
                  <SelectItem value={GroupType.SYSTEM}>系统群聊</SelectItem>
                </SelectContent>
              </Select>

              <Select value={filterStatus} onValueChange={(value: 'all' | 'active' | 'inactive') => setFilterStatus(value)}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="状态" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部状态</SelectItem>
                  <SelectItem value="active">启用</SelectItem>
                  <SelectItem value="inactive">禁用</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardHeader>

          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>群聊名称</TableHead>
                    <TableHead>类型</TableHead>
                    <TableHead>成员数量</TableHead>
                    <TableHead>创建者</TableHead>
                    <TableHead>状态</TableHead>
                    <TableHead>创建时间</TableHead>
                    <TableHead>操作</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {groups.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                        暂无群聊数据
                      </TableCell>
                    </TableRow>
                  ) : (
                    groups.map((group) => (
                      <TableRow
                        key={group.id}
                        className="cursor-pointer hover:bg-accent/50"
                        onClick={() => {
                          setSelectedGroup(group);
                          loadGroupMembers(group.id);
                        }}
                      >
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <Avatar className="h-8 w-8">
                              <AvatarImage src={group.avatar_url} alt={group.name} />
                              <AvatarFallback>
                                <Users className="h-4 w-4" />
                              </AvatarFallback>
                            </Avatar>
                            <div>
                              <p className="font-medium">{group.name}</p>
                              {group.description && (
                                <p className="text-sm text-muted-foreground truncate max-w-32">
                                  {group.description}
                                </p>
                              )}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <span className={`text-xs px-2 py-1 rounded-full border ${getGroupTypeColor(group.group_type)}`}>
                            {group.group_type === 'system' ? '系统' : group.group_type === 'private' ? '私密' : '公开'}
                          </span>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            <Users className="h-4 w-4" />
                            {group.member_count || 0}
                          </div>
                        </TableCell>
                        <TableCell>{group.creator_name || '管理员'}</TableCell>
                        <TableCell>
                          <Badge variant={group.is_active ? 'default' : 'secondary'}>
                            {group.is_active ? '启用' : '禁用'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {new Date(group.created_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={(e) => e.stopPropagation()}
                              >
                                <MoreVertical className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem
                                onClick={(e) => {
                                  e.stopPropagation();
                                  onGroupSelect?.(group);
                                }}
                              >
                                <Eye className="h-4 w-4 mr-2" />
                                查看详情
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                onClick={(e) => {
                                  e.stopPropagation();
                                  openEditDialog(group);
                                }}
                              >
                                <Edit className="h-4 w-4 mr-2" />
                                编辑
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setSelectedGroup(group);
                                  loadGroupMembers(group.id);
                                  setMemberDialogOpen(true);
                                }}
                              >
                                <Users className="h-4 w-4 mr-2" />
                                管理成员
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleToggleGroupStatus(group);
                                }}
                              >
                                {group.is_active ? (
                                  <>
                                    <Ban className="h-4 w-4 mr-2" />
                                    禁用
                                  </>
                                ) : (
                                  <>
                                    <Check className="h-4 w-4 mr-2" />
                                    启用
                                  </>
                                )}
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDeleteGroup(group);
                                }}
                                className="text-destructive"
                              >
                                <Trash2 className="h-4 w-4 mr-2" />
                                删除
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            )}

            {/* 分页 */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-4">
                <div className="text-sm text-muted-foreground">
                  第 {currentPage} 页，共 {totalPages} 页
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    disabled={currentPage === 1}
                  >
                    上一页
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                    disabled={currentPage === totalPages}
                  >
                    下一页
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* 成员管理面板 */}
      {selectedGroup && (
        <div className="w-96">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                {selectedGroup.name} - 成员管理
              </CardTitle>
              <CardDescription>
                管理群聊成员和权限
              </CardDescription>
            </CardHeader>

            <CardContent>
              {loadingMembers ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                </div>
              ) : (
                <ScrollArea className="h-96">
                  <div className="space-y-2">
                    {groupMembers.length === 0 ? (
                      <div className="text-center py-8 text-muted-foreground">
                        暂无成员
                      </div>
                    ) : (
                      groupMembers.map((member) => (
                        <div
                          key={member.id}
                          className="flex items-center justify-between p-2 rounded-lg border"
                        >
                          <div className="flex items-center gap-3">
                            <Avatar className="h-8 w-8">
                              <AvatarImage src="" alt={member.full_name} />
                              <AvatarFallback>
                                {member.full_name.charAt(0).toUpperCase()}
                              </AvatarFallback>
                            </Avatar>
                            <div>
                              <p className="font-medium">{member.full_name}</p>
                              <p className="text-sm text-muted-foreground">
                                @{member.username}
                              </p>
                            </div>
                            {getRoleIcon(member.role)}
                          </div>

                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="sm">
                                <MoreVertical className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem
                                onClick={() => {
                                  const newRole = member.role === MemberRole.ADMIN ?
                                    MemberRole.MEMBER : MemberRole.ADMIN;
                                  handleUpdateMemberRole(member, newRole);
                                }}
                                disabled={member.role === MemberRole.OWNER}
                              >
                                <Shield className="h-4 w-4 mr-2" />
                                {member.role === MemberRole.ADMIN ? '取消管理员' : '设为管理员'}
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                onClick={() => handleRemoveMember(member)}
                                disabled={member.role === MemberRole.OWNER}
                                className="text-destructive"
                              >
                                <X className="h-4 w-4 mr-2" />
                                移除成员
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </div>
                      ))
                    )}
                  </div>
                </ScrollArea>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* 创建群聊对话框 */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>创建群聊</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">群聊名称</label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="请输入群聊名称"
              />
            </div>
            <div>
              <label className="text-sm font-medium">群聊描述</label>
              <Input
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="请输入群聊描述（可选）"
              />
            </div>
            <div>
              <label className="text-sm font-medium">群聊类型</label>
              <Select
                value={formData.group_type}
                onValueChange={(value: GroupType) => setFormData(prev => ({ ...prev, group_type: value }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={GroupType.PUBLIC}>公开群聊</SelectItem>
                  <SelectItem value={GroupType.PRIVATE}>私密群聊</SelectItem>
                  <SelectItem value={GroupType.SYSTEM}>系统群聊</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium">最大成员数量</label>
              <Input
                type="number"
                value={formData.max_members}
                onChange={(e) => setFormData(prev => ({ ...prev, max_members: parseInt(e.target.value) || 100 }))}
                min={2}
                max={500}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleCreateGroup}>
              创建
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 编辑群聊对话框 */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>编辑群聊</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">群聊名称</label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="请输入群聊名称"
              />
            </div>
            <div>
              <label className="text-sm font-medium">群聊描述</label>
              <Input
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="请输入群聊描述（可选）"
              />
            </div>
            <div>
              <label className="text-sm font-medium">最大成员数量</label>
              <Input
                type="number"
                value={formData.max_members}
                onChange={(e) => setFormData(prev => ({ ...prev, max_members: parseInt(e.target.value) || 100 }))}
                min={2}
                max={500}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleUpdateGroup}>
              保存
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};