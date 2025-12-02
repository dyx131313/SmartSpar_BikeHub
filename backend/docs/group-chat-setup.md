# 群聊功能部署和使用指南

## 功能概述

本群聊功能为BikeHub项目提供了完整的站内聊天系统，支持：

- ✅ **群聊创建和管理**：管理员可创建公开群、私密群和系统群
- ✅ **实时消息传输**：基于WebSocket的实时通信
- ✅ **成员管理**：添加/移除成员，权限管理（群主/管理员/成员）
- ✅ **消息类型**：支持文本、图片、文件等多种消息类型
- ✅ **消息状态**：已读/未读状态，消息编辑和撤回
- ✅ **搜索功能**：群聊搜索、消息搜索、用户搜索
- ✅ **通知系统**：新消息通知、群聊动态通知
- ✅ **管理后台**：完整的群聊管理界面

## 系统架构

### 后端组件
- **数据库模型** (`chat_models.py`): 定义了完整的数据模型
- **API路由** (`chat.py`): 提供RESTful API接口
- **WebSocket服务** (`websocket_service.py`): 实时消息推送
- **数据库表** (`chat_schema.sql`): 数据库表结构

### 前端组件
- **API客户端** (`group-chat-api.ts`): 封装API调用
- **UI组件**: 群聊列表、消息界面、管理后台等
- **WebSocket Hook** (`use-websocket.ts`): 实时通信处理
- **类型定义** (`group-chat-types.ts`): TypeScript类型定义

## 部署步骤

### 1. 数据库设置

首先，运行数据库脚本创建必要的表：

```sql
-- 在MySQL中执行
source backend/database/chat_schema.sql;
```

### 2. 后端设置

1. **安装依赖**：
```bash
cd backend
pip install flask-socketio websockets
```

2. **更新路由**：
确保在 `backend/app/routes/__init__.py` 中导入chat模块：

```python
from app.routes import chat
```

3. **配置WebSocket服务器**：

创建启动脚本 `run_websocket.py`：

```python
#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.routes.websocket import run_websocket_server

if __name__ == "__main__":
    run_websocket_server()
```

4. **启动服务**：
```bash
# 启动Flask API服务器
python run.py

# 启动WebSocket服务器（新终端）
python run_websocket.py
```

### 3. 前端设置

1. **更新路由配置**：

在 `frontend/bikehub/src/routes/_authenticated/chats/` 下创建新的路由：

```tsx
// group-chats.tsx
import { GroupChats } from '@/features/chats/group-chats'

export default function GroupChatsPage() {
  return <GroupChats />
}
```

2. **更新侧边栏导航**：

在侧边栏组件中添加群聊链接：

```tsx
// 侧边栏配置中添加
{
  title: "群聊",
  href: "/chats/group",
  icon: MessagesSquare,
  badge: unreadCount > 0 ? unreadCount.toString() : undefined,
}
```

### 4. 环境变量配置

在 `.env` 文件中添加：

```env
# WebSocket服务器地址
NEXT_PUBLIC_WS_URL=ws://localhost:8765

# 文件上传配置
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_PATH=uploads/chat
```

## 功能测试

### 基本功能测试

1. **创建群聊**：
   - 登录管理员账户
   - 进入群聊页面
   - 点击"创建群聊"按钮
   - 填写群聊信息并创建

2. **添加成员**：
   - 在群聊中点击"管理成员"
   - 搜索并添加用户
   - 验证成员权限

3. **发送消息**：
   - 在群聊中输入消息
   - 测试文本、图片、文件发送
   - 验证消息实时接收

4. **消息管理**：
   - 测试消息编辑功能
   - 测试消息撤回功能
   - 验证已读状态更新

### WebSocket连接测试

```javascript
// 在浏览器控制台测试WebSocket连接
const ws = new WebSocket('ws://localhost:8765?token=YOUR_JWT_TOKEN');

ws.onopen = () => {
  console.log('WebSocket连接成功');
  ws.send(JSON.stringify({ type: 'ping' }));
};

ws.onmessage = (event) => {
  console.log('收到消息:', JSON.parse(event.data));
};
```

### API测试

```bash
# 测试获取群聊列表
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:5000/api/chat/groups

# 测试创建群聊
curl -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{"name":"测试群聊","group_type":"public","max_members":50}' \
     http://localhost:5000/api/chat/groups

# 测试发送消息
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "content=测试消息" \
     -F "message_type=text" \
     http://localhost:5000/api/chat/groups/1/messages
```

## 配置选项

### 群聊类型

- **公开群聊** (`public`): 任何人都可以查看和加入
- **私密群聊** (`private`): 需要邀请才能加入
- **系统群聊** (`system`): 系统自动管理，用户自动加入

### 权限级别

- **群主** (`owner`): 完全管理权限，可以删除群聊
- **管理员** (`admin`): 管理成员，禁言等权限
- **成员** (`member`): 基本聊天权限

### 消息类型

- **文本消息** (`text`): 普通文本聊天
- **图片消息** (`image`): 图片分享
- **文件消息** (`file`): 文件分享
- **系统消息** (`system`): 系统通知
- **语音消息** (`voice`): 语音消息（预留）

## 性能优化

### 1. 数据库优化

```sql
-- 为常用查询添加索引
CREATE INDEX idx_chat_messages_group_created ON chat_messages(group_id, created_at);
CREATE INDEX idx_chat_group_members_user_group ON chat_group_members(user_id, group_id);
CREATE INDEX idx_chat_messages_sender_created ON chat_messages(sender_id, created_at);
```

### 2. 缓存策略

- **群聊信息缓存**: Redis缓存群聊基本信息
- **在线用户缓存**: 内存中维护在线用户列表
- **消息分页**: 实现虚拟滚动优化大量消息加载

### 3. 文件存储

建议使用对象存储服务（如AWS S3、阿里云OSS）：

```python
# 配置文件上传
UPLOAD_CONFIG = {
    'provider': 's3',  # 's3', 'aliyun_oss', 'local'
    'bucket': 'bikehub-chat-files',
    'region': 'us-east-1',
    'access_key': 'YOUR_ACCESS_KEY',
    'secret_key': 'YOUR_SECRET_KEY'
}
```

## 安全考虑

### 1. 权限控制
- 所有API都需要JWT认证
- 群聊操作需要成员权限验证
- 管理员操作需要管理员权限

### 2. 内容安全
- 实现内容过滤和敏感词检测
- 文件类型和大小限制
- 消息频率限制

### 3. WebSocket安全
- Token验证
- 连接频率限制
- 消息内容验证

## 故障排除

### 常见问题

1. **WebSocket连接失败**
   - 检查端口8765是否开放
   - 验证JWT Token是否有效
   - 检查防火墙设置

2. **消息发送失败**
   - 检查用户是否是群聊成员
   - 验证文件大小是否超限
   - 检查数据库连接

3. **前端页面加载慢**
   - 优化消息分页加载
   - 实现虚拟滚动
   - 添加缓存机制

### 日志监控

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# WebSocket连接日志
logger = logging.getLogger('websocket')
logger.setLevel(logging.INFO)
```

## 后续扩展

1. **语音/视频通话**: 集成WebRTC实现音视频通话
2. **机器人功能**: 添加聊天机器人自动回复
3. **消息加密**: 实现端到端加密
4. **群聊公告**: 添加群聊公告和置顶消息
5. **表情包**: 支持自定义表情包和贴纸
6. **消息撤回时间限制**: 设置消息撤回时间窗口
7. **群聊统计**: 添加活跃度统计和数据报表

## 联系支持

如果在部署过程中遇到问题，请：

1. 查看系统日志: `tail -f logs/app.log`
2. 检查数据库连接: `mysql -u root -p bikehub`
3. 验证API响应: `curl http://localhost:5000/api/chat/statistics`

更多技术支持请参考项目文档或联系开发团队。