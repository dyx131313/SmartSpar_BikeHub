# 调度任务 API 文档

## 概述

本文档描述了调度任务管理的完整API接口，支持调度任务的增删改查功能，并包含完整的用户角色权限控制。

## 用户角色

### 支持的角色类型
- `admin` - 管理员：拥有所有权限
- `dispatcher` - 调度员：可以创建、分配、管理调度任务
- `operator` - 运维员：只能查看和更新分配给自己的任务
- `user` - 普通用户：只有基本权限

### 创建用户命令
```bash
# 创建所有测试用户
flask create-test-users

# 单独创建调度员
flask create-dispatcher

# 单独创建运维员
flask create-operator
```

## API 接口

### 1. 创建调度任务

**接口地址**: `POST /api/dispatch-tasks`

**权限要求**: 调度员(dispatcher)或管理员(admin)

**请求头**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**请求体**:
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

**字段说明**:
- `task_name` (必需): 任务名称，最大100字符
- `from_station_id` (可选): 起点站点ID
- `to_station_id` (可选): 终点站点ID
- `bike_count` (必需): 调度单车数量，默认0
- `priority` (可选): 优先级(1-5)，默认1
- `assigned_to` (可选): 分配给的运维员ID

**响应示例**:
```json
{
  "message": "调度任务创建成功",
  "data": {
    "id": 1,
    "task_name": "教学楼到宿舍区单车调度",
    "from_station_id": 3,
    "to_station_id": 4,
    "from_station": {...},
    "to_station": {...},
    "bike_count": 15,
    "priority": 2,
    "status": "pending",
    "assigned_to": 3,
    "assignee": {...},
    "created_by": 2,
    "creator": {...},
    "created_at": "2025-11-15T10:30:00",
    "updated_at": "2025-11-15T10:30:00"
  }
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

**响应示例**:
```json
{
  "data": [
    {
      "id": 1,
      "task_name": "教学楼到宿舍区单车调度",
      "from_station_id": 3,
      "to_station_id": 4,
      "bike_count": 15,
      "priority": 2,
      "status": "pending",
      "assigned_to": 3,
      "created_by": 2,
      "created_at": "2025-11-15T10:30:00",
      "updated_at": "2025-11-15T10:30:00"
    }
  ],
  "total": 1,
  "pages": 1,
  "current_page": 1,
  "per_page": 20
}
```

### 3. 获取单个调度任务

**接口地址**: `GET /api/dispatch-tasks/<id>`

**权限要求**: 根据角色权限控制

**响应示例**:
```json
{
  "data": {
    "id": 1,
    "task_name": "教学楼到宿舍区单车调度",
    "from_station_id": 3,
    "to_station_id": 4,
    "from_station": {
      "id": 3,
      "name": "教学楼站点",
      "station_type": "teaching_building",
      "latitude": 39.9042,
      "longitude": 116.4074,
      "capacity": 30
    },
    "to_station": {
      "id": 4,
      "name": "宿舍区站点",
      "station_type": "dormitory",
      "latitude": 39.9052,
      "longitude": 116.4084,
      "capacity": 40
    },
    "bike_count": 15,
    "priority": 2,
    "status": "pending",
    "assigned_to": 3,
    "assignee": {
      "id": 3,
      "username": "operator",
      "role": "operator",
      "full_name": "运维员"
    },
    "created_by": 2,
    "creator": {
      "id": 2,
      "username": "dispatcher",
      "role": "dispatcher",
      "full_name": "调度员"
    },
    "created_at": "2025-11-15T10:30:00",
    "updated_at": "2025-11-15T10:30:00"
  }
}
```

### 4. 更新调度任务

**接口地址**: `PUT /api/dispatch-tasks/<id>`

**权限要求**: 根据角色限制更新字段

**请求体**:
```json
{
  "task_name": "更新后的任务名称",
  "bike_count": 20,
  "priority": 3,
  "status": "in_progress"
}
```

**权限说明**:
- **运维员(operator)**: 只能更新任务状态为 `in_progress` 或 `completed`
- **调度员(dispatcher)**: 可以更新所有字段
- **管理员(admin)**: 可以更新所有字段

### 5. 删除调度任务

**接口地址**: `DELETE /api/dispatch-tasks/<id>`

**权限要求**: 管理员或任务创建者(调度员)

**响应示例**:
```json
{
  "message": "调度任务删除成功"
}
```

### 6. 分配调度任务

**接口地址**: `POST /api/dispatch-tasks/<id>/assign`

**权限要求**: 调度员或管理员

**请求体**:
```json
{
  "operator_id": 3
}
```

**响应示例**:
```json
{
  "message": "任务分配成功",
  "data": {
    "id": 1,
    "task_name": "教学楼到宿舍区单车调度",
    "status": "pending",
    "assigned_to": 3,
    ...
  }
}
```

## 任务状态

### 支持的状态
- `pending` - 待处理
- `in_progress` - 进行中
- `completed` - 已完成
- `cancelled` - 已取消

### 状态流转规则
- 新创建的任务默认为 `pending`
- 运维员可以将任务更新为 `in_progress` 或 `completed`
- 调度员和管理员可以将任务设置为任意状态

## 权限矩阵

| 操作 | Admin | Dispatcher | Operator | User |
|------|-------|------------|----------|------|
| 查看所有任务 | ✅ | 部分任务 | 分配给自己的任务 | ❌ |
| 创建任务 | ✅ | ✅ | ❌ | ❌ |
| 查看任务详情 | ✅ | 相关任务 | 分配给自己的任务 | ❌ |
| 更新任务 | ✅ | 所有字段 | 仅状态 | ❌ |
| 删除任务 | ✅ | 自己创建的 | ❌ | ❌ |
| 分配任务 | ✅ | ✅ | ❌ | ❌ |

## 错误响应

### 常见错误码
- `400` - 请求参数错误
- `401` - 未认证或token过期
- `403` - 权限不足
- `404` - 资源不存在
- `500` - 服务器内部错误

### 错误响应格式
```json
{
  "error": "错误描述信息"
}
```

## 使用示例

### JavaScript/Axios 示例

```javascript
// 登录获取token
const loginResponse = await axios.post('/api/auth/login', {
  username: 'dispatcher',
  password: 'dispatcher123'
});
const token = loginResponse.data.access_token;

// 设置请求头
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};

// 创建调度任务
const taskData = {
  task_name: "教学楼到宿舍区单车调度",
  from_station_id: 3,
  to_station_id: 4,
  bike_count: 15,
  priority: 2,
  assigned_to: 3
};

const createResponse = await axios.post('/api/dispatch-tasks', taskData, { headers });
console.log('任务创建成功:', createResponse.data);

// 获取任务列表
const listResponse = await axios.get('/api/dispatch-tasks', { headers });
console.log('任务列表:', listResponse.data.data);
```

### Python/Requests 示例

```python
import requests

# 登录获取token
login_response = requests.post('http://localhost:5000/api/auth/login', json={
    'username': 'dispatcher',
    'password': 'dispatcher123'
})
token = login_response.json()['access_token']

# 设置请求头
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# 创建调度任务
task_data = {
    'task_name': '教学楼到宿舍区单车调度',
    'from_station_id': 3,
    'to_station_id': 4,
    'bike_count': 15,
    'priority': 2,
    'assigned_to': 3
}

create_response = requests.post('http://localhost:5000/api/dispatch-tasks',
                              json=task_data, headers=headers)
print('任务创建成功:', create_response.json())

# 获取任务列表
list_response = requests.get('http://localhost:5000/api/dispatch-tasks', headers=headers)
print('任务列表:', list_response.json()['data'])
```

## 测试

运行测试脚本验证API功能：

```bash
# 确保后端服务运行
python run.py

# 在另一个终端运行测试
python test_dispatch_tasks.py
```

测试脚本会自动测试所有API接口和权限控制。