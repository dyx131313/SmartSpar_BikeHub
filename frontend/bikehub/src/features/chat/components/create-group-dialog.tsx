/**
 * 创建群聊对话框组件
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui';
import { Button, Input, Textarea, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Avatar, AvatarFallback, AvatarImage, Badge, ScrollArea } from '@/components/ui';
import { Users, Search } from 'lucide-react';
import { groupChatAPI } from '../api/group-chat-api';
import { CreateGroupForm, GroupType, UserInfo } from '../data/group-chat-types';
import { api } from '@/lib/api';
import { toast } from 'sonner';

interface CreateGroupDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: (group: any) => void;
}

const CreateGroupDialog: React.FC<CreateGroupDialogProps> = React.memo(({
  open,
  onClose,
  onSuccess,
}) => {
  const [formData, setFormData] = useState<CreateGroupForm>({
    name: '',
    description: '',
    group_type: GroupType.PUBLIC,
    max_members: 100,
  });
  const [selectedUsers, setSelectedUsers] = useState<UserInfo[]>([]);

  // 监控 selectedUsers 的变化
  useEffect(() => {
    console.log('🔄 selectedUsers 状态更新，当前数量:', selectedUsers.length, '时间戳:', Date.now());
    console.log('🔄 selectedUsers 内容:', selectedUsers.map(u => u.full_name));
  }, [selectedUsers]);
  const [availableUsers, setAvailableUsers] = useState<UserInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searching, setSearching] = useState(false);

  // 加载可用用户
  const loadUsers = useCallback(async () => {
    console.log('🔍 loadUsers 函数被调用');
    try {
      setSearching(true);
      console.log('🔍 正在加载用户列表...');
      // 直接使用 API 获取用户，不使用 getAllAvailableUsers
      const response = await api.get(`/api/chat/users/search?q=&limit=50`);
      console.log('🔍 用户加载完成，数量:', response.users?.length);
      setAvailableUsers(response.users);
    } catch (error) {
      console.error('加载用户列表失败:', error);
    } finally {
      setSearching(false);
    }
  }, [setAvailableUsers, setSearching]);

  // 搜索用户
  const handleSearchUsers = useCallback(async (query: string) => {
    console.log('🔍 handleSearchUsers 被调用 - query:', query);
    setSearchQuery(query);
    if (query.trim()) {
      try {
        setSearching(true);
        console.log('🔍 正在搜索用户:', query);
        const users = await groupChatAPI.searchUsers(query, 20);
        console.log('🔍 搜索完成，结果数量:', users?.length);
        setAvailableUsers(users);
      } catch (error) {
        console.error('搜索用户失败:', error);
      } finally {
        setSearching(false);
      }
    } else {
      console.log('🔍 搜索框为空，重置为所有用户');
      // 当搜索框为空时，重置为所有用户
      loadUsers();
    }
  }, [loadUsers, setSearchQuery]);

  // 处理用户选择
  const handleUserToggle = useCallback((user: UserInfo) => {
    console.log('👤 handleUserToggle 被调用 - user:', user.full_name, 'ID:', user.id, '时间戳:', Date.now());
    setSelectedUsers(prev => {
      console.log('👤 setSelectedUsers 开始执行 - prev.length:', prev.length, '时间戳:', Date.now());
      const isSelected = prev.some(u => u.id === user.id);
      console.log('👤 用户选择状态:', isSelected, '当前已选数量:', prev.length);
      if (isSelected) {
        console.log('👤 取消选择用户:', user.full_name);
        const newSelected = prev.filter(u => u.id !== user.id);
        console.log('👤 返回新的选中列表，长度:', newSelected.length, '时间戳:', Date.now());
        return newSelected;
      } else {
        // 使用函数式获取最新的 formData
        const currentMaxMembers = 100; // 默认值，确保不会出错
        if (prev.length >= currentMaxMembers - 1) {
          console.log('👤 已达到最大选择数量限制');
          toast.error(`最多只能选择 ${currentMaxMembers - 1} 个成员`);
          return prev;
        }
        console.log('👤 添加用户到选择列表:', user.full_name);
        const newSelected = [...prev, { ...user }];
        console.log('👤 返回新的选中列表，长度:', newSelected.length, '时间戳:', Date.now());
        return newSelected;
      }
    });
  }, []);

  // 处理表单提交
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      toast.error('请输入群聊名称');
      return;
    }

    if (formData.max_members < 2) {
      toast.error('群聊最大成员数量不能少于2人');
      return;
    }

    if (selectedUsers.length === 0 && formData.group_type !== GroupType.SYSTEM) {
      toast.error('请至少选择一个成员');
      return;
    }

    try {
      setLoading(true);

      // 创建群聊
      const response = await groupChatAPI.createGroup(formData);

      // 添加成员
      if (selectedUsers.length > 0) {
        await groupChatAPI.addGroupMembers(response.group.id, selectedUsers.map(u => u.id));
      }

      onSuccess(response.group);
      handleClose();
    } catch (error) {
      console.error('创建群聊失败:', error);
      toast.error('创建群聊失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  // 关闭对话框 - 保留状态，只调用 onClose
  const handleClose = useCallback(() => {
    console.log('🚪 handleClose 函数被调用');
    console.log('🚪 延迟调用 onClose');
    onClose();
  }, [onClose]);

  useEffect(() => {
    console.log('⚡ useEffect 运行 - open:', open, 'loadUsers:', !!loadUsers);
    if (open) {
      console.log('⚡ open 为 true，调用 loadUsers');
      loadUsers();
    } else {
      console.log('⚡ open 为 false，不加载用户');
    }
  }, [open]); // 只依赖 open，避免 loadUsers 变化导致重新执行

  return (
    <Dialog open={open} onOpenChange={(newOpen) => {
      console.log('🎭 Dialog onOpenChange 被调用 - old open:', open, 'new open:', newOpen);
      if (!newOpen) {
        console.log('🎭 Dialog 关闭，调用 handleClose');
        handleClose();
      }
    }}>
      <DialogContent className="max-w-2xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>创建群聊</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="flex-1 flex flex-col space-y-4">
          {/* 基本信息 */}
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">群聊名称 *</label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="请输入群聊名称"
                maxLength={100}
                required
              />
            </div>

            <div>
              <label className="text-sm font-medium">群聊描述</label>
              <Textarea
                value={formData.description || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="请输入群聊描述（可选）"
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
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
                  onChange={(e) => setFormData(prev => ({ ...prev, max_members: parseInt(e.target.value) || 2 }))}
                  min={2}
                  max={500}
                />
              </div>
            </div>
          </div>

          {/* 成员选择 */}
          {formData.group_type !== GroupType.SYSTEM && (
            <div className="flex-1 flex flex-col space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium">选择成员</label>
                  <Badge variant="secondary">
                    {selectedUsers.length} / {formData.max_members - 1}
                  </Badge>
                </div>

                {/* 搜索框 */}
                <div className="relative mb-2">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="搜索用户..."
                    value={searchQuery}
                    onChange={(e) => handleSearchUsers(e.target.value)}
                    className="pl-10"
                  />
                </div>

                {/* 用户列表 */}
                <ScrollArea className="h-64 border rounded-lg p-2">
                  {searching ? (
                    <div className="flex items-center justify-center py-8">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                    </div>
                  ) : availableUsers.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <Users className="h-8 w-8 mx-auto mb-2 opacity-50" />
                      <p>暂无可用用户</p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {availableUsers.map((user) => {
                        const isSelected = selectedUsers.some(u => u.id === user.id);
                        return (
                          <div
                            key={user.id}
                            className={`flex items-center justify-between p-2 rounded-lg cursor-pointer transition-colors ${
                              isSelected ? 'bg-primary/10 border border-primary/20' : 'hover:bg-accent'
                            }`}
                            onClick={(e) => {
                              e.preventDefault();
                              e.stopPropagation();
                              handleUserToggle(user);
                            }}
                          >
                            <div className="flex items-center space-x-3">
                           
                              <Avatar className="h-8 w-8">
                                <AvatarImage src="" alt={user.full_name} />
                                <AvatarFallback>
                                  {user.full_name.charAt(0).toUpperCase()}
                                </AvatarFallback>
                              </Avatar>
                              <div>
                                <p className="font-medium">{user.full_name}</p>
                                <p className="text-sm text-muted-foreground">
                                  @{user.username} · {user.role}
                                </p>
                              </div>
                            </div>
                            {isSelected && (
                              <div className="w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                                <span className="text-primary-foreground text-xs">✓</span>
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </ScrollArea>
              </div>

            </div>
          )}

          <DialogFooter>
            <Button type="button" variant="outline" onClick={handleClose}>
              取消
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  创建中...
                </>
              ) : (
                '创建群聊'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
});

export default CreateGroupDialog;