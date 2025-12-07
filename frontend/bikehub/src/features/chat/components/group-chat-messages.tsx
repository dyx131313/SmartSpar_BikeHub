/**
 * 群聊消息组件
 */
import React, { useState, useRef, useEffect } from 'react';
import { ScrollArea, Avatar, AvatarFallback, AvatarImage, Button, Input, Tooltip, TooltipTrigger, TooltipContent, DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui';
import { Send, Paperclip, Smile, Reply, MoreVertical, Edit, Trash2, Copy, Download, RotateCcw, Check } from 'lucide-react';
import { groupChatAPI } from '../api/group-chat-api';
import { ChatGroup, ChatMessage, MessageType, SendMessageForm } from '../data/group-chat-types';

interface GroupChatMessagesProps {
  group: ChatGroup | null;
  messages: ChatMessage[];
  loading: boolean;
  sending: boolean;
  hasMore: boolean;
  onLoadMore: () => void;
  onSendMessage: (content: string, messageType: MessageType, file?: File) => void;
  onReplyMessage: (messageId: number) => void;
  onEditMessage: (messageId: number, content: string) => void;
  onDeleteMessage: (messageId: number) => void;
  onMarkAsRead: (messageId: number) => void;
}

export const GroupChatMessages: React.FC<GroupChatMessagesProps> = ({
  group,
  messages,
  loading,
  sending,
  hasMore,
  onLoadMore,
  onSendMessage,
  onReplyMessage,
  onEditMessage,
  onDeleteMessage,
  onMarkAsRead,
}) => {
  const [messageContent, setMessageContent] = useState('');
  const [replyToMessage, setReplyToMessage] = useState<ChatMessage | null>(null);
  const [editingMessage, setEditingMessage] = useState<ChatMessage | null>(null);
  const [editContent, setEditContent] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // 处理发送消息
  const handleSendMessage = () => {
    if (!messageContent.trim() && !selectedFile) return;

    const messageType = selectedFile ?
      (selectedFile.type.startsWith('image/') ? MessageType.IMAGE : MessageType.FILE) :
      MessageType.TEXT;

    onSendMessage(messageContent, messageType, selectedFile || undefined);

    // 清空输入
    setMessageContent('');
    setSelectedFile(null);
    setReplyToMessage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // 处理文件选择
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // 检查文件大小 (10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert('文件大小不能超过10MB');
        return;
      }
      setSelectedFile(file);
    }
  };

  // 处理回复
  const handleReply = (message: ChatMessage) => {
    setReplyToMessage(message);
    if (scrollAreaRef.current) {
      scrollAreaRef.current.querySelector('input')?.focus();
    }
  };

  // 处理编辑
  const handleEdit = (message: ChatMessage) => {
    setEditingMessage(message);
    setEditContent(message.content);
  };

  // 处理编辑取消
  const handleEditCancel = () => {
    setEditingMessage(null);
    setEditContent('');
  };

  // 处理编辑保存
  const handleEditSave = () => {
    if (editingMessage && editContent.trim()) {
      onEditMessage(editingMessage.id, editContent);
      setEditingMessage(null);
      setEditContent('');
    }
  };

  // 复制消息内容
  const handleCopyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
    // 可以添加提示
  };

  // 格式化时间
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 24) {
      return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    } else {
      return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' });
    }
  };

  // 渲染消息内容
  const renderMessageContent = (message: ChatMessage) => {
    // 如果正在编辑这条消息
    if (editingMessage?.id === message.id) {
      return (
        <div className="flex items-center gap-2 p-2 bg-accent rounded-lg">
          <Input
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            className="flex-1"
            placeholder="编辑消息..."
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleEditSave();
              } else if (e.key === 'Escape') {
                handleEditCancel();
              }
            }}
            autoFocus
          />
          <Button size="sm" onClick={handleEditSave}>
            <Check className="h-4 w-4" />
          </Button>
          <Button size="sm" variant="outline" onClick={handleEditCancel}>
            <RotateCcw className="h-4 w-4" />
          </Button>
        </div>
      );
    }

    // 正常渲染
    switch (message.message_type) {
      case MessageType.TEXT:
        return (
          <div className="break-words">
            {message.content.split('\n').map((line, index) => (
              <p key={index} className={index > 0 ? 'mt-1' : ''}>
                {line}
              </p>
            ))}
          </div>
        );

      case MessageType.IMAGE:
        return (
          <div className="space-y-2">
            {message.content && <p>{message.content}</p>}
            {message.file_url && (
              <img
                src={message.file_url}
                alt="图片消息"
                className="max-w-xs max-h-64 rounded-lg cursor-pointer hover:opacity-90"
                onClick={() => window.open(message.file_url, '_blank')}
              />
            )}
          </div>
        );

      case MessageType.FILE:
        return (
          <div className="space-y-2">
            {message.content && <p>{message.content}</p>}
            {message.file_url && (
              <div className="flex items-center gap-2 p-2 bg-accent/50 rounded-lg">
                <div className="p-2 bg-primary/10 rounded">
                  <Download className="h-4 w-4 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{message.file_name}</p>
                  {message.file_size && (
                    <p className="text-xs text-muted-foreground">
                      {(message.file_size / 1024).toFixed(1)} KB
                    </p>
                  )}
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    const link = document.createElement('a');
                    link.href = message.file_url!;
                    link.download = message.file_name || 'file';
                    link.click();
                  }}
                >
                  下载
                </Button>
              </div>
            )}
          </div>
        );

      case MessageType.SYSTEM:
        return (
          <div className="text-center text-sm text-muted-foreground italic py-2">
            {message.content}
          </div>
        );

      default:
        return <p>{message.content}</p>;
    }
  };

  // 渲染回复消息
  const renderReplyTo = (message: ChatMessage) => {
    if (!message.reply_to_id) return null;

    const replyToMessage = messages.find(m => m.id === message.reply_to_id);
    if (!replyToMessage) return null;

    return (
      <div className="flex items-start gap-2 mb-2 p-2 bg-accent/30 rounded-l-lg border-l-2 border-primary/50">
        <Reply className="h-3 w-3 text-muted-foreground mt-0.5" />
        <div className="flex-1 min-w-0">
          <p className="text-xs text-muted-foreground">回复 {replyToMessage.full_name}</p>
          <p className="text-sm truncate">{replyToMessage.content}</p>
        </div>
      </div>
    );
  };

  // 渲染单条消息
  const renderMessage = (message: ChatMessage) => {
    const isOwnMessage = message.sender_id === group?.created_by; // 这里应该是当前用户ID
    const isSystem = message.message_type === MessageType.SYSTEM;

    if (isSystem) {
      return (
        <div key={message.id} className="flex justify-center">
          <div className="text-sm text-muted-foreground bg-accent/50 px-3 py-1 rounded-full">
            {renderMessageContent(message)}
          </div>
        </div>
      );
    }

    return (
      <div
        key={message.id}
        className={`flex items-end gap-2 mb-4 ${isOwnMessage ? 'flex-row-reverse' : ''}`}
      >
        {/* 头像 */}
        <Avatar className="h-8 w-8">
          <AvatarImage src="" alt={message.full_name} />
          <AvatarFallback>
            {message.full_name.charAt(0).toUpperCase()}
          </AvatarFallback>
        </Avatar>

        {/* 消息内容 */}
        <div className={`max-w-md lg:max-w-lg xl:max-w-2xl ${isOwnMessage ? 'items-end' : 'items-start'}`}>
          {/* 发送者名称 */}
          {!isOwnMessage && (
            <p className="text-xs text-muted-foreground mb-1 px-2">
              {message.full_name}
            </p>
          )}

          {/* 消息气泡 */}
          <div
            className={`relative rounded-2xl px-4 py-2 ${
              isOwnMessage
                ? 'bg-primary text-primary-foreground'
                : 'bg-accent'
            }`}
          >
            {/* 回复内容 */}
            {renderReplyTo(message)}

            {/* 消息内容 */}
            {renderMessageContent(message)}

            {/* 消息时间和状态 */}
            <div className={`flex items-center gap-1 mt-1 text-xs ${
              isOwnMessage ? 'text-primary-foreground/70' : 'text-muted-foreground'
            }`}>
              <span>{formatTime(message.created_at)}</span>
              {message.is_edited && <span>(已编辑)</span>}
              {isOwnMessage && (
                <span className="ml-1">
                  {message.is_read_by_me ? '已读' : '未读'}
                </span>
              )}
            </div>
          </div>

          {/* 操作按钮 */}
          {isOwnMessage && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100"
                >
                  <MoreVertical className="h-3 w-3" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align={isOwnMessage ? 'end' : 'start'}>
                <DropdownMenuItem onClick={() => handleReply(message)}>
                  <Reply className="h-4 w-4 mr-2" />
                  回复
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleEdit(message)}>
                  <Edit className="h-4 w-4 mr-2" />
                  编辑
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleCopyMessage(message.content)}>
                  <Copy className="h-4 w-4 mr-2" />
                  复制
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => onDeleteMessage(message.id)}
                  className="text-destructive"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  删除
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </div>
    );
  };

  // 滚动到底部
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (!group) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-accent rounded-full flex items-center justify-center mx-auto mb-4">
            <Reply className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-medium mb-2">选择一个群聊</h3>
          <p className="text-muted-foreground">开始与其他成员交流</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* 头部 */}
      <div className="p-4 border-b flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h3 className="font-semibold">{group.name}</h3>
          <span className="text-sm text-muted-foreground">
            {group.member_count || 0} 成员
          </span>
        </div>
      </div>

      {/* 消息列表 */}
      <ScrollArea ref={scrollAreaRef} className="flex-1">
        <div className="p-4 space-y-4">
          {/* 加载更多 */}
          {hasMore && (
            <div className="flex justify-center">
              <Button
                variant="outline"
                size="sm"
                onClick={onLoadMore}
                disabled={loading}
              >
                {loading ? '加载中...' : '加载更多消息'}
              </Button>
            </div>
          )}

          {/* 消息列表 */}
          {[...messages].reverse().map(renderMessage)}

          {/* 底部占位 */}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* 输入区域 */}
      <div className="border-t p-4">
        {/* 回复预览 */}
        {replyToMessage && (
          <div className="flex items-center justify-between p-2 bg-accent/50 rounded-lg mb-2">
            <div className="flex items-center gap-2 text-sm">
              <Reply className="h-3 w-3" />
              <span>回复 {replyToMessage.full_name}</span>
              <span className="text-muted-foreground truncate">
                {replyToMessage.content}
              </span>
            </div>
            <Button size="sm" variant="ghost" onClick={() => setReplyToMessage(null)}>
              ×
            </Button>
          </div>
        )}

        {/* 文件预览 */}
        {selectedFile && (
          <div className="flex items-center justify-between p-2 bg-accent/50 rounded-lg mb-2">
            <div className="flex items-center gap-2 text-sm">
              <Paperclip className="h-3 w-3" />
              <span>{selectedFile.name}</span>
              <span className="text-muted-foreground">
                ({(selectedFile.size / 1024).toFixed(1)} KB)
              </span>
            </div>
            <Button size="sm" variant="ghost" onClick={() => setSelectedFile(null)}>
              ×
            </Button>
          </div>
        )}

        {/* 输入框 */}
        <div className="flex items-end gap-2">
          <div className="flex-1">
            <Input
              value={messageContent}
              onChange={(e) => setMessageContent(e.target.value)}
              placeholder="输入消息..."
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              disabled={sending}
            />
          </div>

          {/* 文件上传 */}
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileSelect}
            className="hidden"
            accept="image/*,.pdf,.doc,.docx,.txt,.zip,.rar"
          />
          {/* 发送文件 */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="outline"
                size="icon"
                onClick={() => fileInputRef.current?.click()}
                disabled={sending}
              >
                <Paperclip className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>发送文件</TooltipContent>
          </Tooltip>

          {/* 表情按钮 */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="outline" size="icon" disabled={sending}>
                <Smile className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>表情</TooltipContent>
          </Tooltip>

          {/* 发送按钮 */}
          <Button
            onClick={handleSendMessage}
            disabled={sending || (!messageContent.trim() && !selectedFile)}
          >
            {sending ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};