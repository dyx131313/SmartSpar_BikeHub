# SmartSpar BikeHub Backend

智慧共享单车调度系统后端服务 - 基于Flask + MySQL的RESTful API

## 项目概述

本项目是智慧共享单车调度系统的后端服务，提供完整的API支持，包括：
- 用户认证与权限管理
- 站点信息管理
- 需求数据采集与分析
- 调度任务管理
- 预测结果管理
- 实时群聊通信系统
- 文件上传与管理

## 技术栈

- **后端框架**: Flask 3.1.0
- **数据库**: MySQL 8.0+
- **ORM**: SQLAlchemy
- **认证**: JWT (JSON Web Tokens)
- **API文档**: Flask-RESTX + OpenAPI 3.0
- **数据验证**: Marshmallow, Cerberus
- **实时通信**: WebSocket (Socket.IO)
- **文件上传**: Flask-Uploads
- **缓存**: Redis (可选)
- **任务队列**: Celery (可选)

## 项目结构

```
backend/
├── app/
│   ├── __init__.py              # Flask应用工厂
│   ├── config/                  # 配置文件
│   │   ├── __init__.py
│   │   └── config.py
│   ├── models/                  # 数据模型
│   │   ├── __init__.py
│   │   ├── station.py          # 站点模型
│   │   ├── demand_data.py      # 需求数据模型
│   │   ├── user.py             # 用户模型(增强版，包含头像)
│   │   ├── dispatch_task.py    # 调度任务模型
│   │   ├── prediction.py       # 预测结果模型(增强版)
│   │   ├── bike_history.py     # 站点单车历史信息模型
│   │   ├── alert.py            # 警报模型
│   │   ├── chat_models.py      # 群聊数据模型
│   │   └── chat_message.py     # 聊天消息模型
│   ├── routes/                  # API路由
│   │   ├── __init__.py
│   │   ├── stations.py         # 站点API
│   │   ├── demand_data.py      # 需求数据API
│   │   ├── users.py            # 用户API（包含头像上传）
│   │   ├── dispatch_tasks.py   # 调度任务API
│   │   ├── predictions.py      # 预测结果API
│   │   ├── bike_history.py     # 单车历史信息API
│   │   ├── auth.py             # 认证API（登录/登出）
│   │   ├── chat.py             # 群聊功能API
│   │   └── websocket.py        # WebSocket实时通信
│   ├── utils/                   # 工具类
│   │   ├── __init__.py
│   │   ├── data_importer.py    # 数据导入工具
│   │   ├── file_uploader.py    # 文件上传工具
│   │   └── websocket_service.py # WebSocket服务
│   └── static/                  # 静态文件
│       └── uploads/            # 上传文件目录
│           ├── avatars/        # 用户头像
│           └── chat/           # 聊天文件
├── database/
│   ├── schema.sql               # 原始数据库架构
│   ├── schema_final.sql         # 更新后的数据库架构
│   └── chat_schema.sql         # 群聊数据库架构
├── migrations/                  # 数据库迁移文件
├── tests/                       # 测试文件
├── requirements.txt             # Python依赖
├── run.py                      # 应用启动文件
├── run_websocket.py            # WebSocket服务器启动文件
├── sample_data.json            # 示例数据
└── README.md                   # 项目说明
```

## 快速开始

### 1. 环境要求

- Python 3.10+
- MySQL 8.0+
- Node.js 16+ (前端可选)
- Redis (可选，用于缓存和WebSocket)

### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 数据库配置

#### 创建数据库

```sql
-- 登录MySQL
mysql -u root -p

-- 创建生产数据库
CREATE DATABASE bikehub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建开发数据库（开发环境使用）
CREATE DATABASE bikehub_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（可选，推荐）
CREATE USER 'bikehub_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON bikehub.* TO 'bikehub_user'@'localhost';
GRANT ALL PRIVILEGES ON bikehub_dev.* TO 'bikehub_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 执行架构脚本

```bash
# 导入生产数据库架构（使用更新版本）
mysql -u root -p bikehub < database/schema_final.sql
mysql -u root -p bikehub < database/chat_schema.sql

# 导入开发数据库架构（开发环境使用）
mysql -u root -p bikehub_dev < database/schema_final.sql
mysql -u root -p bikehub_dev < database/chat_schema.sql
```

### 4. 环境配置

**重要说明**：本项目使用不同的数据库配置环境：
- **开发环境** (FLASK_ENV=development): 使用 `bikehub_dev` 数据库
- **生产环境** (FLASK_ENV=production): 使用 `bikehub` 数据库
- **测试环境** (FLASK_ENV=testing): 使用内存数据库

创建 `.env` 文件：

```env
# Flask配置
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# 数据库配置
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=bikehub

# WebSocket配置
WEBSOCKET_HOST=localhost
WEBSOCKET_PORT=8765

# 文件上传配置
MAX_CONTENT_LENGTH=10485760  # 10MB
UPLOAD_FOLDER=static/uploads
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,pdf,doc,docx,txt,zip,rar

# 群聊配置
CHAT_MAX_FILE_SIZE=10485760  # 10MB
CHAT_MAX_MEMBERS=500
CHAT_MESSAGE_RETENTION_DAYS=90

# 其他配置
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 5. 初始化数据库

```bash
# 进入项目目录
cd backend

# 使用Flask命令初始化数据库
flask init-db

# 创建管理员用户
flask create-admin

# 创建测试用户（调度员、运维员等）
flask create-test-users
```

### 6. 启动应用

```bash
# 启动后端API服务（终端1）
python run.py

# 启动WebSocket服务器（终端2）
python run_websocket.py
```

应用将在 `http://localhost:5000` 启动，WebSocket服务在 `ws://localhost:8765`。

## API文档

### 认证

所有API（除了登录）都需要JWT认证。在请求头中包含：

```
Authorization: Bearer <your_jwt_token>
```

### 主要API端点

#### 1. 用户认证
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出

#### 2. 用户管理
- `GET /api/users/profile` - 获取用户个人信息
- `PUT /api/users/profile` - 更新用户信息
- `POST /api/users/avatar` - 上传用户头像
- `DELETE /api/users/avatar` - 删除用户头像
- `GET /api/chat/users/search` - 搜索聊天用户

#### 3. 站点管理
- `GET /api/stations` - 获取站点列表（支持分页）
- `POST /api/stations` - 创建站点
- `GET /api/stations/<id>` - 获取单个站点详情
- `PUT /api/stations/<id>` - 更新站点
- `DELETE /api/stations/<id>` - 删除站点

#### 4. 需求数据
- `GET /api/demand-data` - 获取需求数据（支持分页）
- `POST /api/demand-data` - 创建需求数据
- `POST /api/demand-data/import` - 导入需求数据文件
- `GET /api/demand-data/<id>` - 获取单个需求数据
- `PUT /api/demand-data/<id>` - 更新需求数据
- `DELETE /api/demand-data/<id>` - 删除需求数据
- `GET /api/demand-data/statistics` - 获取数据统计

#### 5. 调度任务
- `GET /api/dispatch-tasks` - 获取调度任务列表（支持过滤和分页）
- `POST /api/dispatch-tasks` - 创建调度任务
- `GET /api/dispatch-tasks/<id>` - 获取单个调度任务详情
- `PUT /api/dispatch-tasks/<id>` - 更新调度任务
- `DELETE /api/dispatch-tasks/<id>` - 删除调度任务
- `POST /api/dispatch-tasks/<id>/assign` - 分配调度任务

#### 6. 预测结果
- `GET /api/predictions` - 获取预测结果
- `POST /api/predictions` - 创建预测结果
- `GET /api/predictions/station/<station_id>` - 获取特定站点预测
- `GET /api/predictions/dashboard` - 获取预测看板数据

#### 7. 单车历史信息
- `GET /api/bike-history` - 获取单车历史数据
- `POST /api/bike-history` - 创建单车历史记录
- `GET /api/bike-history/<id>` - 获取单车历史记录详情
- `PUT /api/bike-history/<id>` - 更新单车历史记录
- `DELETE /api/bike-history/<id>` - 删除单车历史记录
- `GET /api/bike-history/station/<station_id>/latest` - 获取站点最新记录
- `GET /api/bike-history/statistics` - 获取历史统计信息
- `POST /api/bike-history/batch` - 批量创建历史记录

#### 8. 群聊功能
- `GET /api/chat/groups` - 获取用户群聊列表
- `POST /api/chat/groups` - 创建群聊
- `GET /api/chat/groups/<group_id>` - 获取群聊详情
- `PUT /api/chat/groups/<group_id>` - 更新群聊信息
- `DELETE /api/chat/groups/<group_id>` - 删除群聊
- `GET /api/chat/groups/<group_id>/members` - 获取群聊成员列表
- `POST /api/chat/groups/<group_id>/members` - 添加群聊成员
- `DELETE /api/chat/groups/<group_id>/members/<member_id>` - 移除群聊成员
- `POST /api/chat/groups/<group_id>/leave` - 离开群聊
- `GET /api/chat/groups/<group_id>/messages` - 获取群聊消息列表
- `POST /api/chat/groups/<group_id>/messages` - 发送群聊消息
- `PUT /api/chat/messages/<message_id>` - 编辑消息
- `DELETE /api/chat/messages/<message_id>` - 撤回消息
- `POST /api/chat/messages/<message_id>/read` - 标记消息为已读
- `POST /api/chat/groups/<group_id>/read-all` - 标记所有消息为已读
- `GET /api/chat/search` - 搜索聊天内容
- `GET /api/chat/statistics` - 获取聊天统计
- `GET /api/chat/unread-count` - 获取未读消息数量
- `POST /api/chat/upload` - 上传聊天文件
- `GET /api/chat/admin/groups` - 管理员获取所有群聊
- `DELETE /api/chat/admin/groups/<group_id>` - 管理员删除群聊
- `POST /api/chat/admin/groups/<group_id>/disable` - 管理员禁用群聊
- `POST /api/chat/admin/groups/<group_id>/enable` - 管理员启用群聊

### 用户角色权限

#### 支持的角色类型
- `admin` - 管理员：拥有所有权限
- `dispatcher` - 调度员：可以创建、分配、管理调度任务
- `operator` - 运维员：只能查看和更新分配给自己的任务
- `user` - 普通用户：只有基本权限

#### 权限矩阵

| 操作 | Admin | Dispatcher | Operator | User |
|------|-------|------------|----------|------|
| 查看所有站点 | ✅ | ✅ | ✅ | ✅ |
| 创建/更新/删除站点 | ✅ | ❌ | ❌ | ❌ |
| 查看所有调度任务 | ✅ | 部分任务 | 分配给自己的任务 | ❌ |
| 创建调度任务 | ✅ | ✅ | ❌ | ❌ |
| 查看任务详情 | ✅ | 相关任务 | 分配给自己的任务 | ❌ |
| 更新调度任务 | ✅ | 所有字段 | 仅状态 | ❌ |
| 删除调度任务 | ✅ | 自己创建的 | ❌ | ❌ |
| 分配调度任务 | ✅ | ✅ | ❌ | ❌ |
| 创建群聊 | ✅ | ✅ | ✅ | ✅ |
| 管理群聊 | ✅ | 自己创建的 | 自己创建的 | 自己创建的 |
| 发送消息 | ✅ | ✅ | ✅ | ✅ |
| 管理聊天文件 | ✅ | ✅ | ✅ | ✅ |

### 创建测试用户命令

```bash
# 创建所有测试用户
flask create-test-users

# 单独创建调度员
flask create-dispatcher

# 单独创建运维员
flask create-operator
```

## 数据格式

### 用户登录

```json
{
  "username": "admin",
  "password": "admin123"
}
```

响应：
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

### 用户头像上传

请求：`multipart/form-data`
- `avatar`：头像文件（JPG/PNG/GIF，最大5MB）

响应：
```json
{
  "message": "头像上传成功",
  "data": {
    "avatar_url": "/uploads/avatars/1_abcd1234.jpg"
  }
}
```

### 需求数据格式

```json
{
  "timestamp": "2025-07-01 08:00:00",
  "station_type": "canteen",
  "weekday": 2,
  "is_holiday": 0,
  "weather": "rain",
  "temp": 28.4,
  "demand": 14,
  "station_id": 1
}
```

### 站点数据格式

```json
{
  "name": "食堂站点",
  "station_type": "canteen",
  "latitude": 31.2304,
  "longitude": 121.4737,
  "capacity": 30,
  "description": "食堂门口共享单车停放点"
}
```

### 调度任务数据格式

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

### 单车历史信息格式

```json
{
  "station_id": 1,
  "timestamp": "2025-07-01 08:00:00",
  "available_bikes": 15,
  "available_docks": 15,
  "total_bikes": 30,
  "total_docks": 30,
  "is_station_active": true,
  "last_report_time": "2025-07-01 08:00:00"
}
```

### 群聊数据格式

#### 创建群聊
```json
{
  "name": "运维交流群",
  "description": "运维人员交流群",
  "group_type": "private",
  "max_members": 100
}
```

#### 发送消息
```json
{
  "content": "大家好！",
  "message_type": "text",
  "reply_to_id": null
}
```

### 用户搜索响应格式

```json
{
  "users": [
    {
      "id": 1,
      "username": "testuser1",
      "full_name": "测试用户1",
      "email": "test1@bikehub.com",
      "role": "user",
      "is_active": true,
      "email_verified": true,
      "created_at": "2024-01-01T00:00:00",
      "mutual_groups": 3,
      "already_in_contact": false
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 20,
  "has_more": true,
  "query": "test"
}
```

## WebSocket实时通信

### 连接方式

```javascript
const ws = new WebSocket('ws://localhost:8765?token=YOUR_JWT_TOKEN');
```

### 消息类型

#### 客户端发送：
1. **心跳检测**
```json
{
  "type": "ping"
}
```

2. **加入群聊**
```json
{
  "type": "join_group",
  "group_id": 1
}
```

3. **离开群聊**
```json
{
  "type": "leave_group",
  "group_id": 1
}
```

4. **正在输入状态**
```json
{
  "type": "typing",
  "group_id": 1,
  "is_typing": true
}
```

#### 服务端推送：
1. **新消息通知**
```json
{
  "type": "new_message",
  "data": {
    "message_id": 101,
    "group_id": 1,
    "sender_id": 2,
    "sender_name": "张三",
    "message_type": "text",
    "content": "Hello World"
  }
}
```

2. **用户状态变化**
```json
{
  "type": "user_status_changed",
  "data": {
    "user_id": 2,
    "status": "online"
  }
}
```

3. **成员加入/离开**
```json
{
  "type": "member_joined",
  "data": {
    "group_id": 1,
    "member": {
      "user_id": 3,
      "username": "newuser"
    }
  }
}
```

## 数据导入

### 从JSON文件导入

```bash
# 使用API导入
curl -X POST http://localhost:5000/api/demand-data/import \
  -H "Authorization: Bearer <token>" \
  -F "file=@sample_data.json"
```

### 使用数据导入工具

```python
from app.utils.data_importer import DataImporter

# 导入JSON文件
result = DataImporter.import_demand_data_from_json('sample_data.json')

# 创建示例数据
result = DataImporter.create_sample_data()

# 创建管理员用户
result = DataImporter.create_admin_user()
```

## 开发指南

### 代码规范

```bash
# 代码格式化
black .

# 导入排序
isort .

# 代码检查
flake8 .
```

### 测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app tests/

# 测试调度任务API
python test_dispatch_tasks.py

# 测试群聊功能
python test_chat_api.py
```

### 数据库迁移

```bash
# 初始化迁移
flask db init

# 创建迁移
flask db migrate -m "描述信息"

# 应用迁移
flask db upgrade
```

## 部署

### 生产环境配置

1. 设置环境变量：
```env
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-jwt-secret-key-here
MYSQL_USER=bikehub_user
MYSQL_PASSWORD=secure_password
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=8765
REDIS_URL=redis://localhost:6379/0
```

2. 使用Gunicorn启动：
```bash
# 启动API服务
gunicorn -w 4 -b 0.0.0.0:5000 run:app

# 启动WebSocket服务
python run_websocket.py
```

### Docker部署

```dockerfile
# Dockerfile示例
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000 8765

# 启动脚本
CMD ["sh", "-c", "gunicorn -w 4 -b 0.0.0.0:5000 run:app & python run_websocket.py"]
```

### 数据库优化

```sql
-- 为常用查询添加索引
CREATE INDEX idx_chat_messages_group_created ON chat_messages(group_id, created_at);
CREATE INDEX idx_chat_group_members_user_group ON chat_group_members(user_id, group_id);
CREATE INDEX idx_dispatch_tasks_status ON dispatch_tasks(status);
CREATE INDEX idx_demand_data_timestamp ON demand_data(timestamp);
```

## 默认账户

系统会创建以下默认账户：

- **管理员**
  - 用户名: `admin`
  - 密码: `admin123`
  - 邮箱: `admin@bikehub.com`

- **调度员** (通过命令创建)
  - 用户名: `dispatcher`
  - 密码: `dispatcher123`
  - 邮箱: `dispatcher@bikehub.com`

- **运维员** (通过命令创建)
  - 用户名: `operator`
  - 密码: `operator123`
  - 邮箱: `operator@bikehub.com`

**重要**: 首次登录后请立即修改密码！

## 故障排除

### 常见问题

1. **数据库连接错误**
   - 检查MySQL服务是否启动：`sudo systemctl status mysql`
   - 验证数据库用户名和密码
   - 确认数据库已创建：`mysql -u root -p -e "SHOW DATABASES;"`

2. **导入数据失败**
   - 检查JSON文件格式
   - 验证时间戳格式 (ISO 8601)
   - 确认站点是否存在

3. **JWT认证失败**
   - 检查token是否过期
   - 验证Authorization头部格式
   - 确认JWT_SECRET_KEY配置正确

4. **WebSocket连接失败**
   - 检查端口8765是否开放：`netstat -tlnp | grep 8765`
   - 验证JWT Token是否有效
   - 检查防火墙设置

5. **文件上传失败**
   - 检查文件大小限制
   - 验证文件类型是否允许
   - 确认上传目录权限：`chmod 755 static/uploads`

### 日志查看

```bash
# 查看应用日志
tail -f app.log

# 查看WebSocket日志
tail -f websocket.log

# 使用loguru查看详细日志
python -c "from loguru import logger; logger.add('app.log'); logger.info('test')"
```

### 健康检查

```bash
# API健康检查
curl http://localhost:5000/api/health

# 数据库连接检查
curl http://localhost:5000/api/health/db

# WebSocket连接测试
curl http://localhost:5000/api/health/websocket
```

## 性能优化建议

### 1. 数据库优化
- 为常用查询字段添加索引
- 定期清理历史数据
- 使用数据库连接池

### 2. 缓存策略
- 使用Redis缓存热点数据
- 实现查询结果缓存
- 缓存用户会话信息

### 3. 文件存储优化
- 使用CDN加速静态资源
- 实现文件分片上传
- 图片压缩和格式转换

### 4. WebSocket优化
- 实现连接心跳检测
- 连接数限制和负载均衡
- 消息队列处理大量并发

## 安全考虑

### 1. 认证安全
- JWT Token有效期24小时
- 支持Token刷新机制
- 实现登录失败限制

### 2. 数据安全
- SQL注入防护（参数化查询）
- XSS攻击防护
- CSRF Token验证

### 3. 文件安全
- 文件类型和大小验证
- 病毒扫描（可选）
- 访问权限控制

### 4. API安全
- 请求频率限制
- 输入数据验证
- 敏感信息过滤

## 更新日志

### v1.0.0 (2025-01-15)
- 初始版本发布
- 基础API功能
- 用户认证系统
- 站点管理功能

### v1.1.0 (2025-01-20)
- 调度任务管理
- 群聊功能
- 文件上传支持
- WebSocket实时通信
- 用户头像功能
- 高级搜索功能

### v1.2.0 (计划中)
- 语音消息支持
- 视频通话功能
- 消息加密
- 群聊公告功能
- 移动端优化

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

### 开发规范
- 遵循PEP 8代码规范
- 编写单元测试
- 更新相关文档
- 添加类型注解（Type Hints）

### 测试要求
- 所有新增功能必须包含测试用例
- 保持测试覆盖率在80%以上
- 测试文件命名规范：`test_模块名.py`

## 技术支持

- **文档**: 查看完整文档 `docs/` 目录
- **Issues**: 提交GitHub Issues
- **Email**: support@bikehub.com
- **Slack**: bikehub-support.slack.com

## 许可证

本项目采用MIT许可证。详见LICENSE文件。

---

**文档版本**: v1.1.0  
**最后更新**: 2025-01-20  
**维护者**: SmartSpar BikeHub 开发团队