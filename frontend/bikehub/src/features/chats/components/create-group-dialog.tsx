/**
 * 创建群聊对话框组件
 */
import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button, Input, Textarea, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Avatar, AvatarFallback, AvatarImage, Badge, ScrollArea, Checkbox } from '@/components/ui';
import { X, Users, Search } from 'lucide-react';
import { groupChatAPI } from '../api/group-chat-api';
import { CreateGroupForm, GroupType, UserInfo } from '../data/group-chat-types';

interface CreateGroupDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: (group: any) => void;
}

export const CreateGroupDialog: React.FC<CreateGroupDialogProps> = ({
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
  const [availableUsers, setAvailableUsers] = useState<UserInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searching, setSearching] = useState(false);

  // 加载可用用户
  const loadUsers = async () => {
    try {
      setSearching(true);
      const users = await groupChatAPI.searchUsers('', 50);
      setAvailableUsers(users);
    } catch (error) {
      console.error('加载用户列表失败:', error);
    } finally {
      setSearching(false);
    }
  };

  // 搜索用户
  const handleSearchUsers = async (query: string) => {
    setSearchQuery(query);
    if (query.trim()) {
      try {
        setSearching(true);
        const users = await groupChatAPI.searchUsers(query, 20);
        setAvailableUsers(users);
      } catch (error) {
        console.error('搜索用户失败:', error);
      } finally {
        setSearching(false);
      }
    } else {
      loadUsers();
    }
  };

  // 处理用户选择
  const handleUserToggle = (user: UserInfo) => {
    const isSelected = selectedUsers.some(u => u.id === user.id);
    if (isSelected) {
      setSelectedUsers(prev => prev.filter(u => u.id !== user.id));
    } else {
      if (selectedUsers.length >= formData.max_members - 1) {
        alert(`最多只能选择 ${formData.max_members - 1} 个成员`);
        return;
      }
      setSelectedUsers(prev => [...prev, user]);
    }
  };

  // 处理表单提交
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      alert('请输入群聊名称');
      return;
    }

    if (formData.max_members < 2) {
      alert('群聊最大成员数量不能少于2人');
      return;
    }

    if (selectedUsers.length === 0 && formData.group_type !== GroupType.SYSTEM) {
      alert('请至少选择一个成员');
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
      alert('创建群聊失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  // 关闭对话框
  const handleClose = () => {
    setFormData({
      name: '',
      description: '',
      group_type: GroupType.PUBLIC,
      max_members: 100,
    });
    setSelectedUsers([]);
    setSearchQuery('');
    onClose();
  };

  useEffect(() => {
    if (open) {
      loadUsers();
    }
  }, [open]);

  return (
    <Dialog open={open} onOpenChange={handleClose}>
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
                            onClick={() => handleUserToggle(user)}
                          >
                            <div className="flex items-center space-x-3">
                              <Checkbox checked={isSelected} />
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

              {/* 已选择的成员 */}
              {selectedUsers.length > 0 && (
                <div>
                  <label className="text-sm font-medium">已选择的成员</label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {selectedUsers.map((user) => (
                      <Badge key={user.id} variant="secondary" className="flex items-center gap-1">
                        <Avatar className="h-4 w-4">
                          <AvatarImage src="" alt={user.full_name} />
                          <AvatarFallback className="text-xs">
                            {user.full_name.charAt(0).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        {user.full_name}
                        <button
                          type="button"
                          onClick={() => handleUserToggle(user)}
                          className="ml-1 hover:bg-secondary-foreground/20 rounded"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
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
};