# 基础API实现与联调 - 子Issue清单

## 总体目标
完成基础API的本地启动、测试验证和前端联调准备工作。


---

## Issue 1: 后端服务启动验证 

### 前置依赖
- [ ] 数据库已由数据库组完成初始化（包含表结构和管理员用户创建）

### 任务描述
确保后端服务能够在本地正常启动，API路由正确注册，为后续API测试做准备。

### 完成标准
- [ ] 执行 `python run.py` 后端服务成功启动在 `http://localhost:5000`
- [ ] 验证 MySQL 数据库连接正常（无需初始化，只需连接测试）
- [ ] 检查启动日志无严重错误信息
- [ ] 确认管理员账号可以正常登录（依赖数据库组已创建）
- [ ] 验证所有API蓝图正确注册

### 验证步骤
```bash
# 1. 进入后端目录
cd backend

# 2. 启动服务
python run.py

# 3. 测试数据库连接（可选）
# 4. 验证管理员登录（在Issue 2中详细测试）
```

### 预期输出
- 服务在 5000 端口正常运行
- 数据库连接成功，无连接错误
- 所有API路由（/api/stations, /api/auth/login等）正确注册
- 启动日志显示Flask应用和数据库初始化成功   √

### 可能遇到的问题
- MySQL 连接失败：检查数据库服务是否启动，确认 .env 配置
- 端口被占用：修改端口或关闭占用进程
- 依赖缺失：运行 `pip install -r requirements.txt`
- 数据库未初始化：联系数据库组确认数据库状态
- 端口被占用：修改端口或关闭占用进程
- 依赖缺失：运行 `pip install -r requirements.txt`

---

## Issue 2: 登录API测试与Token获取 

### 任务描述
测试用户登录API，验证JWT token生成和返回。

### 完成标准
- [ ] 使用管理员账号成功调用 `POST /api/auth/login`
- [ ] 正确返回 `access_token` 和用户信息
- [ ] 验证token格式正确（Bearer token）
- [ ] 记录token用于后续API测试

### 测试用例

#### 正常登录
```bash
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**预期响应:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@bikehub.com",
    "role": "admin"
  }
}
```

#### 异常情况测试
- [ ] 错误密码返回 401
- [ ] 空用户名/密码返回 400
- [ ] 不存在的用户返回 401

### 验证步骤
1. 使用 Postman 或 curl 发送登录请求
2. 复制 `access_token` 值
3. 验证token可以解析（可选：使用 jwt.io 验证）

---

## Issue 3: 核心只读API测试（最小联调闭环）

### 任务描述
测试站点相关的核心只读API，建立前后端联调的最小闭环。

### 完成标准
- [ ] 成功调用 `GET /api/stations`（带token认证）
- [ ] 验证分页参数 `page` 和 `per_page` 正常工作
- [ ] 成功调用 `GET /api/stations/{id}` 获取站点详情
- [ ] 响应数据格式符合前端预期
- [ ] 可选：测试 `GET /api/demand-data`, `GET /api/dispatch-tasks`, `GET /api/predictions`

### 测试用例

#### 1. 获取站点列表（带认证）
```bash
GET http://localhost:5000/api/stations?page=1&per_page=20
Authorization: Bearer <access_token>
```

**预期响应:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "食堂站点",
      "station_type": "canteen",
      "latitude": 31.2304,
      "longitude": 121.4737,
      "capacity": 30,
      ...
    }
  ],
  "total": 5,
  "pages": 1,
  "current_page": 1,
  "per_page": 20
}
```

#### 2. 获取站点详情
```bash
GET http://localhost:5000/api/stations/1
Authorization: Bearer <access_token>
```

**预期响应:**
```json
{
  "id": 1,
  "name": "食堂站点",
  "station_type": "canteen",
  ...
}
```

#### 3. 异常情况测试
- [ ] 不带token返回 401
- [ ] 无效token返回 401
- [ ] 不存在的站点ID返回 404

### 验证步骤
1. 在请求头中添加 `Authorization: Bearer <token>`
2. 测试分页功能（page=1, page=2等）
3. 验证响应JSON格式正确
4. 检查错误处理是否正常

---

## Issue 4: Postman集合准备与前端联调文档 ⏱️ 1天

### 任务描述
创建完整的Postman API集合，编写前端联调文档，为前后端联调做准备。

### 完成标准
- [ ] 创建 Postman Collection，包含所有核心API
- [ ] 配置环境变量（baseUrl, token）
- [ ] 实现token自动获取流程（登录→提取token→自动设置到后续请求）
- [ ] 编写前端联调指南文档
- [ ] 记录已知问题和注意事项
- [ ] 与前端约定联调时间和流程

### Postman Collection 结构

```
📁 SmartSpar BikeHub API
├── 📁 Authentication
│   └── POST Login
├── 📁 Stations
│   ├── GET List Stations
│   ├── GET Station Detail
│   ├── POST Create Station
│   ├── PUT Update Station
│   └── DELETE Station
├── 📁 Demand Data
│   ├── GET List Demand Data
│   ├── POST Create Demand Data
│   └── GET Statistics
├── 📁 Dispatch Tasks
│   ├── GET List Tasks
│   ├── POST Create Task
│   └── POST Assign Task
└── 📁 Predictions
    ├── GET List Predictions
    └── GET Dashboard
```

### Postman 环境变量配置
```json
{
  "baseUrl": "http://localhost:5000",
  "token": "{{从登录响应中提取}}"
}
```

### 前端联调指南文档要点
1. **环境准备**
   - 后端服务地址：`http://localhost:5000`
   - API基础路径：`/api`
   - 认证方式：Bearer Token

2. **联调流程**
   ```
   登录 → 获取token → 调用站点列表 → 调用站点详情
   ```

3. **注意事项**
   - Token有效期为24小时
   - 所有API（除登录外）都需要在Header中携带token
   - CORS已配置允许 `http://localhost:3000` 和 `http://localhost:5173`

4. **常见问题处理**
   - 401错误：检查token是否正确传递
   - 404错误：检查API路径是否正确
   - CORS错误：检查后端CORS配置

### 交付物
- [ ] Postman Collection JSON文件（导出）
- [ ] Postman Environment JSON文件
- [ ] 前端联调指南文档（`FRONTEND_INTEGRATION.md`）
- [ ] 联调测试检查清单

### 验证步骤
1. 在Postman中导入Collection和Environment
2. 执行完整流程：登录→站点列表→站点详情
3. 验证所有请求能正常响应
4. 与前端同学确认联调时间

---

## 进度跟踪

| Issue | 状态 | 开始时间 | 完成时间 | 备注 |
|-------|------|----------|----------|------|
| Issue 1: 数据库初始化与启动 | ⬜ 待开始 | - | - | |
| Issue 2: 登录API测试 | ⬜ 待开始 | - | - | |
| Issue 3: 核心只读API测试 | ⬜ 待开始 | - | - | |
| Issue 4: Postman集合准备 | ⬜ 待开始 | - | - | |

**状态说明**: ⬜ 待开始 | 🟡 进行中 | ✅ 已完成 | ❌ 阻塞

---

## 备注

- 每个Issue建议独立完成，完成后及时更新状态
- 遇到问题及时记录，便于后续处理
- 与前端联调前，确保所有核心API都已测试通过
