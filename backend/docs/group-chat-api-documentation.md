# 群聊功能API文档

## API概述

群聊功能提供了完整的RESTful API和WebSocket接口，支持群聊管理、消息传输、用户管理等核心功能。

**基础URL**: `http://localhost:5000/api/chat`
**WebSocket URL**: `ws://localhost:8765`
**认证方式**: JWT Bearer Token

## 数据模型

### 群聊类型 (GroupType)
- `public`: 公开群聊
- `private`: 私密群聊
- `system`: 系统群聊

### 消息类型 (MessageType)
- `text`: 文本消息
- `image`: 图片消息
- `file`: 文件消息
- `system`: 系统消息
- `voice`: 语音消息

### 成员角色 (MemberRole)
- `owner`: 群主
- `admin`: 管理员
- `member`: 普通成员

## 群聊管理API

### 获取用户群聊列表

```http
GET /api/chat/groups?page=1&page_size=20
```

**Query参数:**
- `page` (可选): 页码，默认1
- `page_size` (可选): 每页数量，默认20，最大100

**响应示例:**
```json
{
  "groups": [
    {
      "id": 1,
      "name": "运维交流群",
      "description": "运维人员交流群",
      "avatar_url": null,
      "group_type": "private",
      "max_members": 100,
      "created_by": 1,
      "is_active": true,
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z",
      "member_count": 15,
      "last_message_time": "2025-01-15T15:20:00Z",
      "user_role": "owner",
      "is_muted": false,
      "last_read_at": "2025-01-15T15:00:00Z",
      "unread_count": 3
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 20,
  "has_more": false
}
```

### 创建群聊

```http
POST /api/chat/groups
Content-Type: application/json

{
  "name": "新群聊",
  "description": "群聊描述",
  "group_type": "public",
  "max_members": 100
}
```

**响应示例:**
```json
{
  "message": "群聊创建成功",
  "group": {
    "id": 6,
    "name": "新群聊",
    "description": "群聊描述",
    "group_type": "public",
    "max_members": 100,
    "created_by": 1,
    "is_active": true,
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z"
  }
}
```

### 获取群聊详情

```http
GET /api/chat/groups/{group_id}
```

**响应示例:**
```json
{
  "group": {
    "id": 1,
    "name": "运维交流群",
    "description": "运维人员交流群",
    "group_type": "private",
    "max_members": 100,
    "member_count": 15
  }
}
```

### 更新群聊信息

```http
PUT /api/chat/groups/{group_id}
Content-Type: application/json

{
  "name": "更新后的群名",
  "description": "更新后的描述",
  "max_members": 150
}
```

### 删除群聊

```http
DELETE /api/chat/groups/{group_id}
```

**响应:**
```json
{
  "message": "群聊删除成功"
}
```

## 群聊成员管理API

### 获取群聊成员列表

```http
GET /api/chat/groups/{group_id}/members?page=1&page_size=50
```

**响应示例:**
```json
{
  "members": [
    {
      "id": 1,
      "group_id": 1,
      "user_id": 1,
      "role": "owner",
      "nickname": "群主",
      "is_muted": false,
      "is_active": true,
      "joined_at": "2025-01-15T10:30:00Z",
      "last_read_at": "2025-01-15T15:00:00Z",
      "username": "admin",
      "full_name": "系统管理员",
      "email": "admin@bikehub.com",
      "user_role": "admin"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 50,
  "has_more": false
}
```

### 添加群聊成员

```http
POST /api/chat/groups/{group_id}/members
Content-Type: application/json

{
  "user_ids": [2, 3, 4]
}
```

**响应:**
```json
{
  "message": "成功添加3名成员",
  "added_user_ids": [2, 3, 4]
}
```

### 更新成员信息

```http
PUT /api/chat/groups/{group_id}/members/{member_id}
Content-Type: application/json

{
  "role": "admin",
  "nickname": "管理员",
  "is_muted": false
}
```

### 移除群聊成员

```http
DELETE /api/chat/groups/{group_id}/members/{member_id}
```

### 离开群聊

```http
POST /api/chat/groups/{group_id}/leave
```

## 消息管理API

### 获取群聊消息列表

```http
GET /api/chat/groups/{group_id}/messages?page=1&page_size=50&before_message_id=100
```

**Query参数:**
- `page` (可选): 页码
- `page_size` (可选): 每页数量
- `before_message_id` (可选): 获取指定消息ID之前的消息

**响应示例:**
```json
{
  "messages": [
    {
      "id": 1,
      "group_id": 1,
      "sender_id": 1,
      "message_type": "text",
      "content": "大家好！",
      "file_url": null,
      "file_name": null,
      "file_size": null,
      "reply_to_id": null,
      "is_deleted": false,
      "is_edited": false,
      "edited_at": null,
      "created_at": "2025-01-15T10:30:00Z",
      "username": "admin",
      "full_name": "系统管理员",
      "is_read_by_me": true
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 50,
  "has_more": true
}
```

### 发送群聊消息

```http
POST /api/chat/groups/{group_id}/messages
Content-Type: multipart/form-data

content=Hello World
message_type=text
file=@/path/to/file.jpg
reply_to_id=5
```

**响应示例:**
```json
{
  "message": "消息发送成功",
  "data": {
    "id": 101,
    "group_id": 1,
    "sender_id": 1,
    "message_type": "text",
    "content": "Hello World",
    "created_at": "2025-01-15T15:30:00Z",
    "username": "admin",
    "full_name": "系统管理员"
  }
}
```

### 编辑消息

```http
PUT /api/chat/messages/{message_id}
Content-Type: application/json

{
  "content": "编辑后的消息内容"
}
```

### 撤回消息

```http
DELETE /api/chat/messages/{message_id}
```

### 标记消息为已读

```http
POST /api/chat/messages/{message_id}/read
```

**响应:**
```json
{
  "message": "消息已标记为已读"
}
```

### 标记群聊所有消息为已读

```http
POST /api/chat/groups/{group_id}/read-all
```

## 搜索功能API

### 搜索聊天内容

```http
GET /api/chat/search?q=keyword&type=all&group_id=1
```

**Query参数:**
- `q` (必需): 搜索关键词
- `type` (可选): 搜索类型 (`all`, `groups`, `messages`, `users`)
- `group_id` (可选): 限制搜索的群聊ID

**响应示例:**
```json
{
  "groups": [
    {
      "id": 1,
      "name": "搜索匹配的群",
      "description": "包含关键词的描述"
    }
  ],
  "messages": [
    {
      "id": 10,
      "content": "包含关键词的消息内容",
      "sender_name": "发送者",
      "group_name": "群聊名称"
    }
  ],
  "users": [
    {
      "id": 2,
      "username": "匹配用户",
      "full_name": "用户姓名"
    }
  ],
  "total_results": 5
}
```

### 搜索用户

```http
GET /api/chat/users/search?q=username&limit=20
```

**响应示例:**
```json
[
  {
    "id": 2,
    "username": "testuser",
    "full_name": "测试用户",
    "email": "test@example.com",
    "role": "user"
  }
]
```

## 统计信息API

### 获取聊天统计

```http
GET /api/chat/statistics
```

**响应示例:**
```json
{
  "total_groups": 5,
  "total_messages": 1500,
  "unread_messages": 12,
  "active_groups": 4
}
```

### 获取未读消息数量

```http
GET /api/chat/unread-count
```

**响应示例:**
```json
{
  "unread_count": 12
}
```

## 文件上传API

### 上传文件

```http
POST /api/chat/upload
Content-Type: multipart/form-data

file=@/path/to/file.jpg
```

**响应示例:**
```json
{
  "url": "http://localhost:5000/uploads/chat/file_1234567890.jpg",
  "filename": "file.jpg",
  "size": 1024000,
  "content_type": "image/jpeg"
}
```

## 管理员专用API

### 管理员获取所有群聊

```http
GET /api/chat/admin/groups?page=1&page_size=20
Authorization: Bearer ADMIN_TOKEN
```

### 管理员删除群聊

```http
DELETE /api/chat/admin/groups/{group_id}
Authorization: Bearer ADMIN_TOKEN
```

### 管理员禁用/启用群聊

```http
POST /api/chat/admin/groups/{group_id}/disable
POST /api/chat/admin/groups/{group_id}/enable
Authorization: Bearer ADMIN_TOKEN
```

## WebSocket接口

### 连接建立

```javascript
const ws = new WebSocket('ws://localhost:8765?token=YOUR_JWT_TOKEN');
```

### 客户端发送消息类型

#### 1. 心跳检测
```json
{
  "type": "ping"
}
```

#### 2. 加入群聊
```json
{
  "type": "join_group",
  "group_id": 1
}
```

#### 3. 离开群聊
```json
{
  "type": "leave_group",
  "group_id": 1
}
```

#### 4. 标记消息已读
```json
{
  "type": "mark_as_read",
  "message_id": 100
}
```

#### 5. 正在输入状态
```json
{
  "type": "typing",
  "group_id": 1,
  "is_typing": true
}
```

### 服务端推送消息类型

#### 1. 连接成功
```json
{
  "type": "connection_success",
  "data": {
    "user_id": 1,
    "groups": [1, 2, 3],
    "online_count": 25
  }
}
```

#### 2. 新消息通知
```json
{
  "type": "new_message",
  "data": {
    "message_id": 101,
    "group_id": 1,
    "sender_id": 2,
    "sender_name": "张三",
    "message_type": "text",
    "content": "Hello World",
    "group_name": "运维群",
    "is_private": false
  }
}
```

#### 3. 消息编辑通知
```json
{
  "type": "message_edited",
  "data": {
    "message_id": 101,
    "content": "编辑后的内容",
    "edited_at": "2025-01-15T15:35:00Z"
  }
}
```

#### 4. 消息删除通知
```json
{
  "type": "message_deleted",
  "data": {
    "message_id": 101,
    "deleted_at": "2025-01-15T15:35:00Z"
  }
}
```

#### 5. 成员加入通知
```json
{
  "type": "member_joined",
  "data": {
    "group_id": 1,
    "member": {
      "user_id": 3,
      "username": "newuser",
      "full_name": "新用户",
      "role": "member"
    }
  }
}
```

#### 6. 成员离开通知
```json
{
  "type": "member_left",
  "data": {
    "group_id": 1,
    "user_id": 3
  }
}
```

#### 7. 用户状态变化
```json
{
  "type": "user_status_changed",
  "data": {
    "user_id": 2,
    "status": "online" // "online" | "offline"
  }
}
```

#### 8. 群聊信息更新
```json
{
  "type": "group_updated",
  "data": {
    "id": 1,
    "name": "更新后的群名",
    "description": "更新后的描述"
  }
}
```

#### 9. 正在输入通知
```json
{
  "type": "user_typing",
  "data": {
    "group_id": 1,
    "user_id": 2,
    "is_typing": true
  }
}
```

## 错误处理

### HTTP状态码

- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源不存在
- `413`: 文件过大
- `429`: 请求频率限制
- `500`: 服务器内部错误

### 错误响应格式

```json
{
  "error": "错误描述信息"
}
```

### WebSocket错误处理

```json
{
  "type": "error",
  "data": {
    "message": "错误描述信息"
  }
}
```

## 限制和约束

### 请求频率限制
- API请求: 100次/分钟
- 消息发送: 60次/分钟
- 文件上传: 10次/分钟

### 文件限制
- 单文件最大: 10MB
- 支持格式: jpg, jpeg, png, gif, pdf, doc, docx, txt, zip, rar

### 群聊限制
- 最大成员数: 500人
- 最大群聊数: 100个/用户
- 消息保存期: 90天

### WebSocket限制
- 连接数: 10个/用户
- 消息大小: 64KB
- 心跳间隔: 30秒

## 示例代码

### JavaScript客户端示例

```javascript
// API客户端类
class ChatAPI {
  constructor(baseURL, token) {
    this.baseURL = baseURL;
    this.token = token;
  }

  async request(method, endpoint, data = null, isFormData = false) {
    const url = `${this.baseURL}${endpoint}`;
    const options = {
      method,
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    };

    if (!isFormData && data) {
      options.headers['Content-Type'] = 'application/json';
      options.body = JSON.stringify(data);
    } else if (data) {
      options.body = data;
    }

    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  }

  async getGroups(page = 1, pageSize = 20) {
    return this.request('GET', `/groups?page=${page}&page_size=${pageSize}`);
  }

  async createGroup(groupData) {
    return this.request('POST', '/groups', groupData);
  }

  async sendMessage(groupId, messageData) {
    const formData = new FormData();
    Object.keys(messageData).forEach(key => {
      formData.append(key, messageData[key]);
    });
    return this.request('POST', `/groups/${groupId}/messages`, formData, true);
  }
}

// WebSocket客户端
class ChatWebSocket {
  constructor(token, callbacks = {}) {
    this.token = token;
    this.callbacks = callbacks;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect() {
    const wsUrl = `ws://localhost:8765?token=${this.token}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket连接成功');
      this.reconnectAttempts = 0;
      this.callbacks.onOpen?.();
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onclose = () => {
      console.log('WebSocket连接关闭');
      this.callbacks.onClose?.();
      this.reconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket错误:', error);
      this.callbacks.onError?.(error);
    };
  }

  handleMessage(message) {
    switch (message.type) {
      case 'new_message':
        this.callbacks.onNewMessage?.(message.data);
        break;
      case 'user_typing':
        this.callbacks.onUserTyping?.(message.data);
        break;
      default:
        console.log('收到消息:', message);
    }
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  joinGroup(groupId) {
    this.send({ type: 'join_group', group_id: groupId });
  }

  sendTyping(groupId, isTyping) {
    this.send({ type: 'typing', group_id: groupId, is_typing: isTyping });
  }

  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => this.connect(), 1000 * this.reconnectAttempts);
    }
  }
}

// 使用示例
const token = 'YOUR_JWT_TOKEN';
const chatAPI = new ChatAPI('http://localhost:5000/api/chat', token);

// 获取群聊列表
chatAPI.getGroups().then(data => {
  console.log('群聊列表:', data.groups);
});

// 发送消息
chatAPI.sendMessage(1, {
  content: 'Hello World',
  message_type: 'text'
});

// WebSocket连接
const chatWS = new ChatWebSocket(token, {
  onNewMessage: (message) => {
    console.log('收到新消息:', message);
  },
  onUserTyping: (data) => {
    console.log('用户正在输入:', data);
  }
});

chatWS.connect();
chatWS.joinGroup(1);
```

## 更新日志

### v1.0.0 (2025-01-15)
- 初始版本发布
- 实现基本群聊功能
- WebSocket实时通信
- 消息编辑和撤回
- 文件上传支持

### v1.1.0 (计划中)
- 语音消息支持
- 消息引用回复
- 群聊公告功能
- 表情包支持
- 移动端优化

如有问题或建议，请联系开发团队。