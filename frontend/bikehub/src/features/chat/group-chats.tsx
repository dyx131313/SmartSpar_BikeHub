/**
 * 群聊主页面
 */
import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Header } from '@/components/layout/header';
import { Main } from '@/components/layout/main';
import { RequireAuth } from '@/components/require-auth';
import { ConfigDrawer } from '@/components/config-drawer';
import { Search } from '@/components/search';
import { ThemeSwitch } from '@/components/theme-switch';

// 导入群聊相关组件
import { GroupChatList } from './components/group-chat-list';
import { GroupChatMessages } from './components/group-chat-messages';
import CreateGroupDialog from './components/create-group-dialog';
import { groupChatAPI } from './api/group-chat-api';
import { ChatGroup, ChatMessage, MessageType, UserInfo } from './data/group-chat-types';

export function GroupChats() {
  console.log('🔄 GroupChats 组件渲染');

  const [groups, setGroups] = useState<ChatGroup[]>([]);
  const [selectedGroup, setSelectedGroup] = useState<ChatGroup | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  console.log('📊 GroupChats 状态 - groups.length:', groups.length);
  console.log('📊 GroupChats 状态 - createDialogOpen:', createDialogOpen);

  // 加载群聊列表
  const loadGroups = async () => {
    console.log('📥 loadGroups 函数被调用');
    try {
      setLoading(true);
      console.log('📥 正在加载群聊列表...');
      const response = await groupChatAPI.getGroups();
      console.log('📥 群聊加载完成，数量:', response.groups?.length);
      setGroups(response.groups);
      setHasMore(response.has_more);
      setCurrentPage(response.page);
    } catch (error) {
      console.error('加载群聊列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 加载群聊消息
  const loadMessages = async (groupId: number, page = 1) => {
    try {
      setLoading(true);
      const response = await groupChatAPI.getGroupMessages(groupId, page);

      if (page === 1) {
        setMessages(response.messages);
      } else {
        setMessages(prev => [...response.messages, ...prev]);
      }

      setHasMore(response.has_more);
      setCurrentPage(response.page);
    } catch (error) {
      console.error('加载消息失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 加载更多消息
  const handleLoadMore = () => {
    if (selectedGroup && hasMore && !loading) {
      loadMessages(selectedGroup.id, currentPage + 1);
    }
  };

  // 发送消息
  const handleSendMessage = async (content: string, messageType: MessageType, file?: File) => {
    if (!selectedGroup) return;

    try {
      setSending(true);
      const response = await groupChatAPI.sendGroupMessage(selectedGroup.id, {
        content,
        message_type: messageType,
        file,
      });

      // 添加新消息到列表顶部
      setMessages(prev => [response.data, ...prev]);

      // 更新群聊的最后消息时间
      setGroups(prev => prev.map(group =>
        group.id === selectedGroup.id
          ? { ...group, last_message_time: response.data.created_at }
          : group
      ));
    } catch (error) {
      console.error('发送消息失败:', error);
      alert('发送消息失败，请重试');
    } finally {
      setSending(false);
    }
  };

  // 回复消息
  const handleReplyMessage = (messageId: number) => {
    // 实现回复逻辑
    console.log('回复消息:', messageId);
  };

  // 编辑消息
  const handleEditMessage = async (messageId: number, content: string) => {
    try {
      const response = await groupChatAPI.editMessage(messageId, content);
      setMessages(prev => prev.map(msg =>
        msg.id === messageId ? response.data : msg
      ));
    } catch (error) {
      console.error('编辑消息失败:', error);
      alert('编辑消息失败，请重试');
    }
  };

  // 删除消息
  const handleDeleteMessage = async (messageId: number) => {
    if (!confirm('确定要删除这条消息吗？')) return;

    try {
      await groupChatAPI.recallMessage(messageId);
      setMessages(prev => prev.filter(msg => msg.id !== messageId));
    } catch (error) {
      console.error('删除消息失败:', error);
      alert('删除消息失败，请重试');
    }
  };

  // 标记消息为已读
  const handleMarkAsRead = async (messageId: number) => {
    try {
      await groupChatAPI.markMessageAsRead(messageId);
      // 可以更新本地状态
    } catch (error) {
      console.error('标记消息已读失败:', error);
    }
  };

  // 处理群聊选择
  const handleGroupSelect = (group: ChatGroup) => {
    setSelectedGroup(group);
    setMessages([]);
    setCurrentPage(1);
    setHasMore(false);
    loadMessages(group.id);
  };

  // 处理创建群聊成功
  const handleCreateGroupSuccess = (group: ChatGroup) => {
    console.log('✅ 群聊创建成功:', group.name, 'ID:', group.id);
    setGroups(prev => [group, ...prev]);
    setSelectedGroup(group);
    loadMessages(group.id);
  };

  // 处理搜索用户
  const handleSearchUsers = () => {
    // 实现搜索用户逻辑
    console.log('搜索用户');
  };

  useEffect(() => {
    loadGroups();
  }, []);

  return (
    <>
      <RequireAuth>
        <Header>
          <Search />
          <div className="ms-auto flex items-center space-x-4">
            <ThemeSwitch />
            <ConfigDrawer />
          </div>
        </Header>

        <Main fixed>
          <section className="flex h-full gap-6">
            {/* 左侧群聊列表 */}
            <div className="hidden w-80 flex-col gap-2 border-r border-border/80 pr-4 md:flex lg:w-96">
              <GroupChatList
                selectedGroupId={selectedGroup?.id}
                onGroupSelect={handleGroupSelect}
                onCreateGroup={() => setCreateDialogOpen(true)}
                onSearchUsers={handleSearchUsers}
              />
            </div>

            {/* 右侧聊天区域 */}
            <div className="flex-1 pl-2">
              <GroupChatMessages
                group={selectedGroup}
                messages={messages}
                loading={loading}
                sending={sending}
                hasMore={hasMore}
                onLoadMore={handleLoadMore}
                onSendMessage={handleSendMessage}
                onReplyMessage={handleReplyMessage}
                onEditMessage={handleEditMessage}
                onDeleteMessage={handleDeleteMessage}
                onMarkAsRead={handleMarkAsRead}
              />
            </div>
          </section>

          {/* 创建群聊对话框 */}
          <CreateGroupDialog
            open={createDialogOpen}
            onClose={() => setCreateDialogOpen(false)}
            onSuccess={handleCreateGroupSuccess}
          />
        </Main>
      </RequireAuth>
    </>
  );
}