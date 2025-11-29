/**
 * 群聊功能API接口
 */
import { api } from '@/lib/api';
import type {
  ChatGroup,
  ChatMessage,
  ChatGroupMember,
  ChatGroupListResponse,
  ChatMessageListResponse,
  ChatGroupMemberListResponse,
  ChatStatisticsResponse,
  CreateGroupForm,
  SendMessageForm,
  ChatSearchResponse,
  FileUploadResponse,
  UserChatSetting,
  UserInfo
} from '@/features/chats/data/group-chat-types';

/**
 * 群聊API类
 */
export class GroupChatAPI {
  /**
   * 获取用户的群聊列表
   */
  static async getGroups(page = 1, pageSize = 20): Promise<ChatGroupListResponse> {
    const response = await api.get(`/api/chat/groups?page=${page}&page_size=${pageSize}`);
    return response.data;
  }

  /**
   * 创建群聊
   */
  static async createGroup(data: CreateGroupForm): Promise<{ message: string; group: ChatGroup }> {
    const response = await api.post('/api/chat/groups', data);
    return response.data;
  }

  /**
   * 获取群聊详情
   */
  static async getGroup(groupId: number): Promise<{ group: ChatGroup }> {
    const response = await api.get(`/api/chat/groups/${groupId}`);
    return response.data;
  }

  /**
   * 更新群聊信息
   */
  static async updateGroup(groupId: number, data: Partial<CreateGroupForm>): Promise<{ message: string; group: ChatGroup }> {
    const response = await api.put(`/api/chat/groups/${groupId}`, data);
    return response.data;
  }

  /**
   * 删除群聊
   */
  static async deleteGroup(groupId: number): Promise<{ message: string }> {
    const response = await api.delete(`/api/chat/groups/${groupId}`);
    return response.data;
  }

  /**
   * 获取群聊成员列表
   */
  static async getGroupMembers(groupId: number, page = 1, pageSize = 50): Promise<ChatGroupMemberListResponse> {
    const response = await api.get(`/api/chat/groups/${groupId}/members?page=${page}&page_size=${pageSize}`);
    return response.data;
  }

  /**
   * 添加群聊成员
   */
  static async addGroupMembers(groupId: number, userIds: number[]): Promise<{ message: string; added_user_ids: number[] }> {
    const response = await api.post(`/api/chat/groups/${groupId}/members`, { user_ids: userIds });
    return response.data;
  }

  /**
   * 移除群聊成员
   */
  static async removeGroupMember(groupId: number, memberId: number): Promise<{ message: string }> {
    const response = await api.delete(`/api/chat/groups/${groupId}/members/${memberId}`);
    return response.data;
  }

  /**
   * 更新群聊成员信息
   */
  static async updateGroupMember(groupId: number, memberId: number, data: { role?: string; nickname?: string; is_muted?: boolean }): Promise<{ message: string; member: ChatGroupMember }> {
    const response = await api.put(`/api/chat/groups/${groupId}/members/${memberId}`, data);
    return response.data;
  }

  /**
   * 离开群聊
   */
  static async leaveGroup(groupId: number): Promise<{ message: string }> {
    const response = await api.post(`/api/chat/groups/${groupId}/leave`);
    return response.data;
  }

  /**
   * 获取群聊消息列表
   */
  static async getGroupMessages(groupId: number, page = 1, pageSize = 50, beforeMessageId?: number): Promise<ChatMessageListResponse> {
    let url = `/api/chat/groups/${groupId}/messages?page=${page}&page_size=${pageSize}`;
    if (beforeMessageId) {
      url += `&before_message_id=${beforeMessageId}`;
    }
    const response = await api.get(url);
    return response.data;
  }

  /**
   * 发送群聊消息
   */
  static async sendGroupMessage(groupId: number, data: SendMessageForm): Promise<{ message: string; data: ChatMessage }> {
    const formData = new FormData();

    // 添加文本内容
    if (data.content) {
      formData.append('content', data.content);
    }
    formData.append('message_type', data.message_type);

    // 添加回复信息
    if (data.reply_to_id) {
      formData.append('reply_to_id', data.reply_to_id.toString());
    }

    // 添加文件
    if (data.file) {
      formData.append('file', data.file);
    }

    const response = await api.post(`/api/chat/groups/${groupId}/messages`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  /**
   * 撤回消息
   */
  static async recallMessage(messageId: number): Promise<{ message: string }> {
    const response = await api.delete(`/api/chat/messages/${messageId}`);
    return response.data;
  }

  /**
   * 编辑消息
   */
  static async editMessage(messageId: number, content: string): Promise<{ message: string; data: ChatMessage }> {
    const response = await api.put(`/api/chat/messages/${messageId}`, { content });
    return response.data;
  }

  /**
   * 标记消息为已读
   */
  static async markMessageAsRead(messageId: number): Promise<{ message: string }> {
    const response = await api.post(`/api/chat/messages/${messageId}/read`);
    return response.data;
  }

  /**
   * 获取私聊消息列表
   */
  static async getPrivateMessages(userId: number, page = 1, pageSize = 50, beforeMessageId?: number): Promise<ChatMessageListResponse> {
    let url = `/api/chat/private/${userId}/messages?page=${page}&page_size=${pageSize}`;
    if (beforeMessageId) {
      url += `&before_message_id=${beforeMessageId}`;
    }
    const response = await api.get(url);
    return response.data;
  }

  /**
   * 发送私聊消息
   */
  static async sendPrivateMessage(userId: number, data: SendMessageForm): Promise<{ message: string; data: ChatMessage }> {
    const formData = new FormData();

    if (data.content) {
      formData.append('content', data.content);
    }
    formData.append('message_type', data.message_type);

    if (data.reply_to_id) {
      formData.append('reply_to_id', data.reply_to_id.toString());
    }

    if (data.file) {
      formData.append('file', data.file);
    }

    const response = await api.post(`/api/chat/private/${userId}/messages`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  /**
   * 搜索聊天内容
   */
  static async searchChat(query: string, searchType = 'all', groupId?: number): Promise<ChatSearchResponse> {
    let url = `/api/chat/search?q=${encodeURIComponent(query)}&type=${searchType}`;
    if (groupId) {
      url += `&group_id=${groupId}`;
    }
    const response = await api.get(url);
    return response.data;
  }

  /**
   * 获取聊天统计信息
   */
  static async getStatistics(): Promise<ChatStatisticsResponse> {
    const response = await api.get('/api/chat/statistics');
    return response.data;
  }

  /**
   * 上传文件
   */
  static async uploadFile(file: File): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/api/chat/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  /**
   * 获取用户聊天设置
   */
  static async getUserChatSettings(): Promise<UserChatSetting[]> {
    const response = await api.get('/api/chat/settings');
    return response.data;
  }

  /**
   * 更新用户聊天设置
   */
  static async updateUserChatSetting(key: string, value: string): Promise<{ message: string; setting: UserChatSetting }> {
    const response = await api.put('/api/chat/settings', { setting_key: key, setting_value: value });
    return response.data;
  }

  /**
   * 搜索用户
   */
  static async searchUsers(query: string, limit = 20): Promise<UserInfo[]> {
    const response = await api.get(`/api/chat/users/search?q=${encodeURIComponent(query)}&limit=${limit}`);
    return response.data;
  }

  /**
   * 获取用户信息
   */
  static async getUserInfo(userId: number): Promise<UserInfo> {
    const response = await api.get(`/api/chat/users/${userId}`);
    return response.data;
  }

  /**
   * 获取未读消息数量
   */
  static async getUnreadCount(): Promise<{ unread_count: number }> {
    const response = await api.get('/api/chat/unread-count');
    return response.data;
  }

  /**
   * 标记群聊所有消息为已读
   */
  static async markGroupAsRead(groupId: number): Promise<{ message: string }> {
    const response = await api.post(`/api/chat/groups/${groupId}/read-all`);
    return response.data;
  }

  /**
   * 标记所有消息为已读
   */
  static async markAllAsRead(): Promise<{ message: string }> {
    const response = await api.post('/api/chat/read-all');
    return response.data;
  }

  // 管理员专用接口

  /**
   * 管理员获取所有群聊列表
   */
  static async adminGetAllGroups(page = 1, pageSize = 20): Promise<ChatGroupListResponse> {
    const response = await api.get(`/api/chat/admin/groups?page=${page}&page_size=${pageSize}`);
    return response.data;
  }

  /**
   * 管理员删除群聊
   */
  static async adminDeleteGroup(groupId: number): Promise<{ message: string }> {
    const response = await api.delete(`/api/chat/admin/groups/${groupId}`);
    return response.data;
  }

  /**
   * 管理员禁用群聊
   */
  static async adminDisableGroup(groupId: number): Promise<{ message: string }> {
    const response = await api.post(`/api/chat/admin/groups/${groupId}/disable`);
    return response.data;
  }

  /**
   * 管理员启用群聊
   */
  static async adminEnableGroup(groupId: number): Promise<{ message: string }> {
    const response = await api.post(`/api/chat/admin/groups/${groupId}/enable`);
    return response.data;
  }
}

// 导出API实例
export const groupChatAPI = GroupChatAPI;