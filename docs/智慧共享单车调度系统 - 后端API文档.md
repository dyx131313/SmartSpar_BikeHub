# 智慧共享单车调度系统 - 后端API文档

## 项目信息
- **项目名称**: 智慧共享单车调度系统 (SmartSpar BikeHub)
- **API版本**: v1.0
- **基础URL**: `http://localhost:5000/api`
- **WebSocket URL**: `ws://localhost:8765`（群聊功能）
- **技术栈**: Python Flask + MySQL + JWT认证
- **最后更新**: 2025年12月

## 目录
1. [通用信息](#通用信息)
2. [用户认证与管理](#用户认证与管理)
3. [站点信息管理](#站点信息管理)
4. [需求数据管理](#需求数据管理)
5. [AI预测模块](#ai预测模块)
6. [A*算法路径规划模块](#a算法路径规划模块)
7. [调度任务管理](#调度任务管理)
8. [单车历史数据管理](#单车历史数据管理)
9. [群聊功能](#群聊功能)
10. [权限管理系统](#权限管理系统)
11. [错误码说明](#错误码说明)

## 通用信息

### 请求格式
- **Content-Type**: `application/json`
- **认证方式**: Bearer Token (JWT)
- **字符编码**: UTF-8

### 响应格式
所有接口统一返回JSON格式：

#### 成功响应格式
```json
{
  "message": "操作成功",
  "data": {
    // 具体数据
  },
  "total": 100,        // 仅分页接口
  "pages": 5,          // 仅分页接口
  "current_page": 1,   // 仅分页接口
  "per_page": 20       // 仅分页接口
}
```

#### 错误响应格式
```json
{
  "error": "错误描述信息"
}
```

### 认证说明
除登录接口外，所有接口都需要在请求头中携带JWT Token：
```
Authorization: Bearer <your_jwt_token>
```

## 用户认证与管理

### 1. 用户登录
**接口地址**: `POST /api/auth/login`

**请求参数**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应数据**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@bikehub.com",
    "role": "admin",
    "full_name": "系统管理员",
    "phone": null,
    "is_active": true,
    "last_login": "2025-11-12T10:30:00",
    "created_at": "2025-11-01T00:00:00",
    "updated_at": "2025-11-12T10:30:00"
  }
}
```

### 2. 用户登出
**接口地址**: `POST /api/auth/logout`

**权限要求**: 需要登录

**响应数据**:
```json
{
  "message": "登出成功",
  "logout_time": "2025-11-12T15:30:00"
}
```

### 3. 刷新访问令牌
**接口地址**: `POST /api/auth/refresh`

**权限要求**: 需要刷新令牌

**响应数据**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@bikehub.com",
    "role": "admin",
    "full_name": "系统管理员"
  }
}
```

### 4. 获取当前登录用户信息
**接口地址**: `GET /api/auth/me`

**权限要求**: 需要登录

### 5. 获取用户列表
**接口地址**: `GET /api/users`

**权限要求**: 管理员

**查询参数**:
- `page` (可选): 页码，默认1
- `per_page` (可选): 每页数量，默认20，最大100
- `role` (可选): 用户角色过滤

### 6. 创建用户
**接口地址**: `POST /api/users`

**权限要求**: 管理员

**请求参数**:
```json
{
  "username": "dispatcher01",
  "email": "dispatcher01@bikehub.com",
  "password": "password123",
  "role": "dispatcher",
  "full_name": "调度员01",
  "phone": "13800138001"
}
```

### 7. 获取用户个人资料
**接口地址**: `GET /api/users/profile`

### 8. 更新用户信息
**接口地址**: `PUT /api/users/{id}`

### 9. 用户头像上传
**接口地址**: `POST /api/users/avatar`

**认证**: 需要 JWT 认证
**请求**: multipart/form-data，包含 `avatar` 字段（文件）

**响应**:
```json
{
  "message": "头像上传成功",
  "data": {
    "avatar_url": "/uploads/avatars/用户ID_随机字符串.扩展名"
  }
}
```

### 10. 删除头像
**接口地址**: `DELETE /api/users/avatar`

**认证**: 需要 JWT 认证

## 站点信息管理

### 1. 获取站点列表
**接口地址**: `GET /api/stations`

**权限要求**: 所有认证用户

**查询参数**:
- `page` (可选): 页码，默认1
- `per_page` (可选): 每页数量，默认20，最大100
- `station_type` (可选): 站点类型过滤

### 2. 创建站点
**接口地址**: `POST /api/stations`

**权限要求**: 仅管理员

**请求参数**:
```json
{
  "name": "教学楼B栋",
  "station_type": "teaching_building",
  "latitude": 31.2334,
  "longitude": 121.4767,
  "capacity": 25,
  "description": "教学楼B栋门口停车点"
}
```

### 3. 获取单个站点
**接口地址**: `GET /api/stations/{id}`

**权限要求**: 所有认证用户

### 4. 更新站点
**接口地址**: `PUT /api/stations/{id}`

**权限要求**: 仅管理员

### 5. 删除站点
**接口地址**: `DELETE /api/stations/{id}`

**权限要求**: 仅管理员

## 需求数据管理

### 1. 获取需求数据
**接口地址**: `GET /api/demand-data`

**权限要求**: 管理员、调度员

**查询参数**:
- `page` (可选): 页码，默认1
- `per_page` (可选): 每页数量，默认20，最大100
- `station_type` (可选): 站点类型过滤
- `start_date` (可选): 开始日期，格式：2025-11-01T00:00:00
- `end_date` (可选): 结束日期，格式：2025-11-12T23:59:59
- `weather` (可选): 天气过滤
- `weekday` (可选): 星期几(1-7)

### 2. 创建需求数据
**接口地址**: `POST /api/demand-data`

**权限要求**: 所有角色都可创建

**请求参数 (单个)**:
```json
{
  "timestamp": "2025-11-12T12:00:00",
  "station_id": 1,
  "station_type": "canteen",
  "weekday": 3,
  "is_holiday": 0,
  "weather": "sunny",
  "temp": 25.5,
  "demand": 22
}
```

### 3. 导入需求数据
**接口地址**: `POST /api/demand-data/import`

**权限要求**: 管理员、调度员

**请求参数**: `file`: JSON文件 (multipart/form-data)

### 4. 获取需求数据统计
**接口地址**: `GET /api/demand-data/statistics`

**权限要求**: 管理员、调度员

## AI预测模块

### 1. 获取预测结果
**接口地址**: `GET /api/predictions`

**权限要求**: 调度员、管理员

**查询参数**:
- `page` (可选): 页码，默认1
- `per_page` (可选): 每页数量，默认20，最大100
- `station_id` (可选): 站点ID过滤
- `start_time` (可选): 开始时间
- `end_time` (可选): 结束时间

### 2. 创建预测结果
**接口地址**: `POST /api/predictions`

**权限要求**: 调度员、管理员

### 3. 批量生成预测
**接口地址**: `POST /api/predictions/batch`

**权限要求**: 调度员、管理员

### 4. 获取特定站点预测
**接口地址**: `GET /api/predictions/station/{station_id}`

**权限要求**: 调度员、管理员

### 5. 预测看板数据
**接口地址**: `GET /api/predictions/dashboard`

**权限要求**: 调度员、管理员

## A*算法路径规划模块

### 1. 创建路径规划
**接口地址**: `POST /api/route-planning/plan`

**请求参数**:
```json
{
  "plan_name": "食堂到图书馆单车调度",
  "start_station_id": 1,
  "end_station_id": 2,
  "waypoints": [3],
  "task_id": 10,
  "bike_capacity": 20,
  "optimization_goal": "shortest",
  "priority": 3
}
```

### 2. 仅计算路径（不保存）
**接口地址**: `POST /api/route-planning/calculate`

### 3. 多点路径规划
**接口地址**: `POST /api/route-planning/multi-point`

### 4. 获取站点间路径
**接口地址**: `GET /api/route-planning/stations/{from_station_id}/to/{to_station_id}`

### 5. 获取路径规划列表
**接口地址**: `GET /api/route-planning`

## 调度任务管理

### 1. 创建调度任务
**接口地址**: `POST /api/dispatch-tasks`

**权限要求**: 调度员(dispatcher)或管理员(admin)

**请求参数**:
```json
{
  "task_name": "教学楼到宿舍区单车调度",
  "from_station_id": 3,
  "to_station_id": 4,
  "bike_count": 15,
  "priority": 2,
  "assigned_to": 3
}
```

### 2. 获取调度任务列表
**接口地址**: `GET /api/dispatch-tasks`

**权限要求**: 所有认证用户（根据角色返回不同数据）

**查询参数**:
- `page`: 页码，默认1
- `per_page`: 每页数量，默认20，最大100
- `status`: 任务状态过滤 (`pending`, `in_progress`, `completed`, `cancelled`)
- `priority`: 优先级过滤 (1-5)
- `assigned_to`: 分配给的用户ID过滤

### 3. 获取单个调度任务
**接口地址**: `GET /api/dispatch-tasks/<id>`

**权限要求**: 根据角色权限控制

### 4. 更新调度任务
**接口地址**: `PUT /api/dispatch-tasks/<id>`

**权限要求**: 根据角色限制更新字段

**权限说明**:
- **运维员(operator)**: 只能更新任务状态为 `in_progress` 或 `completed`
- **调度员(dispatcher)**: 可以更新所有字段
- **管理员(admin)**: 可以更新所有字段

### 5. 删除调度任务
**接口地址**: `DELETE /api/dispatch-tasks/<id>`

**权限要求**: 管理员或任务创建者(调度员)

### 6. 分配调度任务
**接口地址**: `POST /api/dispatch-tasks/<id>/assign`

**权限要求**: 调度员或管理员

## 单车历史数据管理

### 1. 获取单车历史数据
**接口地址**: `GET /api/bike-history`

**权限要求**: 调度员、运维员或管理员

**查询参数**:
- `station_id` (可选): 站点ID过滤
- `start_date` (可选): 开始日期，格式：2025-11-01T00:00:00
- `end_date` (可选): 结束日期，格式：2025-11-12T23:59:59
- `page` (可选): 页码，默认1
- `per_page` (可选): 每页数量，默认50

### 2. 创建单车历史记录
**接口地址**: `POST /api/bike-history`

**权限要求**: 调度员、运维员或管理员

### 3. 批量创建单车历史记录
**接口地址**: `POST /api/bike-history/batch`

**权限要求**: 调度员、运维员或管理员

### 4. 获取单车历史统计信息
**接口地址**: `GET /api/bike-history/statistics`

**权限要求**: 调度员、运维员或管理员

## 群聊功能

### 基础信息
- **基础URL**: `http://localhost:5000/api/chat`
- **WebSocket URL**: `ws://localhost:8765`

### 数据模型

#### 群聊类型 (GroupType)
- `public`: 公开群聊
- `private`: 私密群聊
- `system`: 系统群聊

#### 消息类型 (MessageType)
- `text`: 文本消息
- `image`: 图片消息
- `file`: 文件消息
- `system`: 系统消息
- `voice`: 语音消息

#### 成员角色 (MemberRole)
- `owner`: 群主
- `admin`: 管理员
- `member`: 普通成员

### 群聊管理API

#### 1. 获取用户群聊列表
**接口地址**: `GET /api/chat/groups?page=1&page_size=20`

#### 2. 创建群聊
**接口地址**: `POST /api/chat/groups`

**请求参数**:
```json
{
  "name": "新群聊",
  "description": "群聊描述",
  "group_type": "public",
  "max_members": 100
}
```

#### 3. 获取群聊详情
**接口地址**: `GET /api/chat/groups/{group_id}`

#### 4. 更新群聊信息
**接口地址**: `PUT /api/chat/groups/{group_id}`

#### 5. 删除群聊
**接口地址**: `DELETE /api/chat/groups/{group_id}`

### 群聊成员管理API

#### 1. 获取群聊成员列表
**接口地址**: `GET /api/chat/groups/{group_id}/members?page=1&page_size=50`

#### 2. 添加群聊成员
**接口地址**: `POST /api/chat/groups/{group_id}/members`

**请求参数**:
```json
{
  "user_ids": [2, 3, 4]
}
```

#### 3. 更新成员信息
**接口地址**: `PUT /api/chat/groups/{group_id}/members/{member_id}`

#### 4. 移除群聊成员
**接口地址**: `DELETE /api/chat/groups/{group_id}/members/{member_id}`

#### 5. 离开群聊
**接口地址**: `POST /api/chat/groups/{group_id}/leave`

### 消息管理API

#### 1. 获取群聊消息列表
**接口地址**: `GET /api/chat/groups/{group_id}/messages?page=1&page_size=50&before_message_id=100`

#### 2. 发送群聊消息
**接口地址**: `POST /api/chat/groups/{group_id}/messages`

**Content-Type**: `multipart/form-data`

#### 3. 编辑消息
**接口地址**: `PUT /api/chat/messages/{message_id}`

#### 4. 撤回消息
**接口地址**: `DELETE /api/chat/messages/{message_id}`

### 搜索功能API

#### 1. 搜索聊天内容
**接口地址**: `GET /api/chat/search?q=keyword&type=all&group_id=1`

#### 2. 搜索用户
**接口地址**: `GET /api/chat/users/search?q=username&limit=20`

**搜索范围**:
- 全局搜索（不指定 group_id）：搜索与当前用户有共同群聊的用户
- 群聊内搜索（指定 group_id）：搜索特定群聊内的成员

### 文件上传API

#### 上传文件
**接口地址**: `POST /api/chat/upload`

**Content-Type**: `multipart/form-data`

### WebSocket接口

#### 连接建立
```javascript
const ws = new WebSocket('ws://localhost:8765?token=YOUR_JWT_TOKEN');
```

#### 客户端发送消息类型
1. **心跳检测**: `{"type": "ping"}`
2. **加入群聊**: `{"type": "join_group", "group_id": 1}`
3. **离开群聊**: `{"type": "leave_group", "group_id": 1}`
4. **标记消息已读**: `{"type": "mark_as_read", "message_id": 100}`
5. **正在输入状态**: `{"type": "typing", "group_id": 1, "is_typing": true}`

## 权限管理系统

### 用户角色定义
1. **管理员 (admin)**: 拥有系统最高权限，可访问所有功能
2. **调度员 (dispatcher)**: 负责调度任务的创建和管理，查看预测结果和需求分析
3. **运维员 (operator)**: 处理分配给自己的调度任务，查看单车历史数据
4. **普通用户 (user)**: 基础功能，可创建需求数据，查看个人信息

### 权限矩阵摘要

| 模块/功能 | 管理员 | 调度员 | 运维员 | 普通用户 |
|---------|-------|-------|-------|---------|
| **用户管理** | ✅全部 | ❌ | ❌ | 仅自己 |
| **站点管理** | ✅全部 | ❌ | ❌ | ❌ |
| **调度任务** | ✅全部 | ✅创建/分配 | ✅查看/更新自己的 | ❌ |
| **需求数据** | ✅全部 | ✅查看/创建/修改 | ✅创建 | ✅创建 |
| **预测结果** | ✅全部 | ✅查看/创建 | ❌ | ❌ |
| **单车历史** | ✅全部 | ✅全部 | ✅全部 | ❌ |

### 权限装饰器
系统提供了权限装饰器来简化权限控制：
```python
@require_role('admin', 'dispatcher')  # 指定角色列表
@require_admin()                      # 仅管理员
@require_dispatcher_or_admin()       # 调度员和管理员
@require_operator_or_admin()         # 运维员和管理员
@require_dispatcher_operator()       # 调度员和运维员
@require_any_role()                  # 所有认证用户
```

## 错误码说明

| 状态码 | 说明 | 示例 |
|--------|------|------|
| 200 | 请求成功 | 成功获取数据 |
| 201 | 创建成功 | 成功创建资源 |
| 400 | 请求参数错误 | `{"error": "用户名和密码不能为空"}` |
| 401 | 未授权 | `{"error": "用户名或密码错误"}` |
| 403 | 权限不足 | `{"error": "权限不足"}` |
| 404 | 资源不存在 | `{"error": "Resource not found"}` |
| 413 | 文件过大 | `{"error": "文件大小超过限制"}` |
| 429 | 请求频率限制 | `{"error": "请求频率过高"}` |
| 500 | 服务器内部错误 | `{"error": "Internal server error"}` |

## 数据类型说明

### 用户角色 (role)
- `admin`: 管理员
- `dispatcher`: 调度员
- `operator`: 运维员
- `user`: 普通用户

### 站点类型 (station_type)
- `canteen`: 食堂
- `library`: 图书馆
- `teaching_building`: 教学楼
- `dormitory`: 宿舍区
- `gate`: 校门

### 任务状态 (status)
- `pending`: 待处理
- `in_progress`: 进行中
- `completed`: 已完成
- `cancelled`: 已取消

### 时间格式
所有时间字段均使用 ISO 8601 格式：`YYYY-MM-DDTHH:MM:SS`

### 坐标格式
- `latitude`: 纬度，保留8位小数
- `longitude`: 经度，保留8位小数

---
**文档版本**: 1.0  
**最后更新**: 2025年12月