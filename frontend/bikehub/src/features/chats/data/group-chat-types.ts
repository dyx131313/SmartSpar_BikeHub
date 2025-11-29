// 群聊功能类型定义

export enum GroupType {
  PUBLIC = 'public',
  PRIVATE = 'private',
  SYSTEM = 'system'
}

export enum MessageType {
  TEXT = 'text',
  IMAGE = 'image',
  FILE = 'file',
  SYSTEM = 'system',
  VOICE = 'voice'
}

export enum MemberRole {
  OWNER = 'owner',
  ADMIN = 'admin',
  MEMBER = 'member'
}

// 基础用户信息
export interface UserInfo {
  id: number;
  username: string;
  full_name: string;
  email: string;
  role: string;
}

// 群聊信息
export interface ChatGroup {
  id: number;
  name: string;
  description?: string;
  avatar_url?: string;
  group_type: GroupType;
  max_members: number;
  created_by: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  member_count?: number;
  last_message_time?: string;
  user_role?: MemberRole;
  is_muted?: boolean;
  last_read_at?: string;
  unread_count?: number;
}

// 群聊成员
export interface ChatGroupMember {
  id: number;
  group_id: number;
  user_id: number;
  role: MemberRole;
  nickname?: string;
  is_muted: boolean;
  is_active: boolean;
  joined_at: string;
  last_read_at?: string;
  username: string;
  full_name: string;
  email: string;
  user_role: string;
}

// 消息信息
export interface ChatMessage {
  id: number;
  group_id?: number;
  sender_id: number;
  receiver_id?: number;
  message_type: MessageType;
  content: string;
  file_url?: string;
  file_name?: string;
  file_size?: number;
  reply_to_id?: number;
  is_deleted: boolean;
  is_edited: boolean;
  edited_at?: string;
  created_at: string;
  username: string;
  full_name: string;
  is_read_by_me?: boolean;
  sender?: UserInfo;
  reply_to?: ChatMessage;
  read_count?: number;
}

// API响应类型
export interface ChatGroupListResponse {
  groups: ChatGroup[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface ChatMessageListResponse {
  messages: ChatMessage[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface ChatGroupMemberListResponse {
  members: ChatGroupMember[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface ChatStatisticsResponse {
  total_groups: number;
  total_messages: number;
  unread_messages: number;
  active_groups: number;
}

// 创建群聊表单
export interface CreateGroupForm {
  name: string;
  description?: string;
  avatar_url?: string;
  group_type: GroupType;
  max_members: number;
}

// 发送消息表单
export interface SendMessageForm {
  content: string;
  message_type: MessageType;
  reply_to_id?: number;
  file?: File;
}

// 搜索请求
export interface ChatSearchRequest {
  query: string;
  search_type: 'all' | 'groups' | 'messages' | 'users';
  group_id?: number;
}

export interface ChatSearchResponse {
  groups: ChatGroup[];
  messages: ChatMessage[];
  users: UserInfo[];
  total_results: number;
}

// WebSocket消息类型
export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

export interface ChatNotificationMessage extends WebSocketMessage {
  type: 'chat_notification';
  data: {
    message_id: number;
    group_id?: number;
    sender_id: number;
    sender_name: string;
    message_type: string;
    content: string;
    group_name?: string;
    is_private: boolean;
  };
}

// 文件上传响应
export interface FileUploadResponse {
  url: string;
  filename: string;
  size: number;
  content_type: string;
}

// 用户聊天设置
export interface UserChatSetting {
  id: number;
  user_id: number;
  setting_key: string;
  setting_value: string;
  created_at: string;
  updated_at: string;
}

// UI状态类型
export interface ChatState {
  selectedGroup: ChatGroup | null;
  messages: ChatMessage[];
  groups: ChatGroup[];
  members: ChatGroupMember[];
  loading: boolean;
  sendingMessage: boolean;
  hasMoreMessages: boolean;
  currentPage: number;
  searchQuery: string;
  searchResults: ChatSearchResponse;
  statistics: ChatStatisticsResponse | null;
}

// 聊天操作动作
export interface ChatActions {
  setSelectedGroup: (group: ChatGroup | null) => void;
  setMessages: (messages: ChatMessage[]) => void;
  addMessage: (message: ChatMessage) => void;
  updateMessage: (messageId: number, updates: Partial<ChatMessage>) => void;
  deleteMessage: (messageId: number) => void;
  setGroups: (groups: ChatGroup[]) => void;
  addGroup: (group: ChatGroup) => void;
  updateGroup: (groupId: number, updates: Partial<ChatGroup>) => void;
  removeGroup: (groupId: number) => void;
  setMembers: (members: ChatGroupMember[]) => void;
  addMember: (member: ChatGroupMember) => void;
  updateMember: (memberId: number, updates: Partial<ChatGroupMember>) => void;
  removeMember: (memberId: number) => void;
  setLoading: (loading: boolean) => void;
  setSendingMessage: (sending: boolean) => void;
  setHasMoreMessages: (hasMore: boolean) => void;
  setCurrentPage: (page: number) => void;
  setSearchQuery: (query: string) => void;
  setSearchResults: (results: ChatSearchResponse) => void;
  setStatistics: (stats: ChatStatisticsResponse) => void;
  loadGroups: () => Promise<void>;
  loadMessages: (groupId: number, page?: number, beforeMessageId?: number) => Promise<void>;
  sendMessage: (groupId: number, form: SendMessageForm) => Promise<void>;
  createGroup: (form: CreateGroupForm) => Promise<void>;
  addMembersToGroup: (groupId: number, userIds: number[]) => Promise<void>;
  removeMemberFromGroup: (groupId: number, memberId: number) => Promise<void>;
  markMessageAsRead: (messageId: number) => Promise<void>;
  searchChat: (query: string, searchType?: string, groupId?: number) => Promise<void>;
  loadStatistics: () => Promise<void>;
}

// 通知类型
export interface ChatNotification {
  id: string;
  type: 'new_message' | 'new_group' | 'member_added' | 'member_removed' | 'group_updated';
  title: string;
  message: string;
  data: any;
  timestamp: string;
  read: boolean;
}

// 聊天配置
export interface ChatConfig {
  pageSize: number;
  maxFileSize: number;
  allowedFileTypes: string[];
  enableNotifications: boolean;
  enableSounds: boolean;
  autoScroll: boolean;
  showMessageTimestamps: boolean;
  showOnlineStatus: boolean;
}