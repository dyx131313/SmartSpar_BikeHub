# SmartSpar BikeHub Backend

智慧共享单车调度系统后端服务 - 基于Flask + MySQL的RESTful API

## 项目概述

本项目是智慧共享单车调度系统的后端服务，提供完整的API支持，包括：
- 用户认证与权限管理
- 站点信息管理
- 需求数据采集与分析
- 调度任务管理
- 预测结果管理

## 技术栈

- **后端框架**: Flask 2.3.3
- **数据库**: MySQL 8.0+
- **ORM**: SQLAlchemy
- **认证**: JWT (JSON Web Tokens)
- **API文档**: Flask-RESTX
- **数据验证**: Marshmallow, Cerberus
- **任务队列**: Celery (可选)
- **缓存**: Redis (可选)

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
│   │   ├── user.py             # 用户模型
│   │   ├── dispatch_task.py    # 调度任务模型
│   │   └── prediction.py       # 预测结果模型
│   ├── routes/                  # API路由
│   │   ├── __init__.py
│   │   ├── stations.py         # 站点API
│   │   ├── demand_data.py      # 需求数据API
│   │   ├── users.py            # 用户API
│   │   ├── dispatch_tasks.py   # 调度任务API
│   │   └── predictions.py      # 预测结果API
│   ├── utils/                   # 工具类
│   │   ├── __init__.py
│   │   └── data_importer.py    # 数据导入工具
│   └── static/                  # 静态文件
├── database/
│   └── schema.sql               # 数据库架构
├── migrations/                  # 数据库迁移文件
├── tests/                       # 测试文件
├── requirements.txt             # Python依赖
├── run.py                      # 应用启动文件
├── sample_data.json            # 示例数据
└── README.md                   # 项目说明
```

## 快速开始

### 1. 环境要求

- Python 3.8+
- MySQL 8.0+
- pip (Python包管理器)

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

-- 创建数据库
CREATE DATABASE bikehub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（可选，推荐）
CREATE USER 'bikehub_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON bikehub.* TO 'bikehub_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 执行架构脚本

```bash
# 导入数据库架构
mysql -u root -p bikehub < database/schema.sql
```

### 4. 环境配置

创建 `.env` 文件（可选，用于环境变量配置）：

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

# 其他配置
LOG_LEVEL=INFO
CORS_ORIGINS=*
```

### 5. 初始化数据库

```bash
# 进入项目目录
cd backend

# 使用Flask命令初始化数据库
flask init-db

# 创建管理员用户
flask create-admin
```

### 6. 启动应用

```bash
# 开发模式
python run.py

# 或使用Flask命令
flask run --host=0.0.0.0 --port=5000
```

应用将在 `http://localhost:5000` 启动。

## API文档

### 认证

所有API（除了登录）都需要JWT认证。在请求头中包含：

```
Authorization: Bearer <your_jwt_token>
```

### 主要API端点

#### 用户认证
- `POST /api/auth/login` - 用户登录

#### 站点管理
- `GET /api/stations` - 获取站点列表
- `POST /api/stations` - 创建站点
- `GET /api/stations/<id>` - 获取单个站点
- `PUT /api/stations/<id>` - 更新站点
- `DELETE /api/stations/<id>` - 删除站点

#### 需求数据
- `GET /api/demand-data` - 获取需求数据
- `POST /api/demand-data` - 创建需求数据
- `POST /api/demand-data/import` - 导入需求数据文件
- `GET /api/demand-data/<id>` - 获取单个需求数据
- `PUT /api/demand-data/<id>` - 更新需求数据
- `DELETE /api/demand-data/<id>` - 删除需求数据
- `GET /api/demand-data/statistics` - 获取数据统计

#### 调度任务
- `GET /api/dispatch-tasks` - 获取调度任务列表
- `POST /api/dispatch-tasks` - 创建调度任务
- `GET /api/dispatch-tasks/<id>` - 获取单个调度任务
- `PUT /api/dispatch-tasks/<id>` - 更新调度任务
- `DELETE /api/dispatch-tasks/<id>` - 删除调度任务
- `POST /api/dispatch-tasks/<id>/assign` - 分配调度任务

#### 预测结果
- `GET /api/predictions` - 获取预测结果
- `POST /api/predictions` - 创建预测结果
- `GET /api/predictions/station/<station_id>` - 获取特定站点预测
- `GET /api/predictions/dashboard` - 获取预测看板数据

### 用户角色权限

- **管理员 (admin)**: 完全访问权限
- **调度员 (dispatcher)**: 可管理调度任务和查看数据
- **运维员 (operator)**: 只能查看和处理分配给自己的任务
- **普通用户 (user)**: 基本查看权限

## 数据格式

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
MYSQL_USER=bikehub_user
MYSQL_PASSWORD=secure_password
```

2. 使用Gunicorn启动：
```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Docker部署

```dockerfile
# Dockerfile示例
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

## 默认账户

系统会创建一个默认管理员账户：
- 用户名: `admin`
- 密码: `admin123`
- 邮箱: `admin@bikehub.com`

**重要**: 首次登录后请立即修改密码！

## 故障排除

### 常见问题

1. **数据库连接错误**
   - 检查MySQL服务是否启动
   - 验证数据库用户名和密码
   - 确认数据库已创建

2. **导入数据失败**
   - 检查JSON文件格式
   - 验证时间戳格式 (ISO 8601)
   - 确认站点是否存在

3. **JWT认证失败**
   - 检查token是否过期
   - 验证Authorization头部格式

### 日志查看

```bash
# 查看应用日志
tail -f app.log

# 使用loguru查看详细日志
python -c "from loguru import logger; logger.add('app.log'); logger.info('test')"
```

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

本项目采用MIT许可证。详见LICENSE文件。
