# 聊天用户搜索接口文档

## 接口概述

成功为 SmartSpar BikeHub 后端添加了 `/api/chat/users/search` 接口，用于在聊天系统中搜索用户。

## 接口详情

### 端点
```
GET /api/chat/users/search
```

### 认证要求
- 需要有效的 JWT Token
- 通过 `Authorization: Bearer <token>` 头部传递

### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| q | string | 是 | - | 搜索关键词，最少2个字符 |
| page | integer | 否 | 1 | 页码 |
| page_size | integer | 否 | 20 | 每页数量，最大100 |
| group_id | integer | 否 | - | 可选：在特定群聊内搜索 |

### 搜索范围

#### 1. 全局搜索（不指定 group_id）
- 搜索与当前用户有共同群聊的用户
- 搜索范围：用户名、全名、邮箱
- 安全性：只能搜索到有共同群聊的用户

#### 2. 群聊内搜索（指定 group_id）
- 搜索特定群聊内的成员
- 需要是该群聊的成员才能搜索
- 搜索范围：群聊内所有成员的用户名、全名、邮箱

### 响应格式

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

### 响应字段说明

#### 用户字段
- `id`: 用户ID
- `username`: 用户名
- `full_name`: 全名
- `email`: 邮箱
- `role`: 用户角色
- `is_active`: 是否激活
- `email_verified`: 邮箱是否验证
- `created_at`: 创建时间

#### 关系字段
- `mutual_groups`: 与当前用户的共同群聊数量
- `already_in_contact`: 是否已在联系人中（在共同群聊中）

#### 分页字段
- `total`: 总结果数
- `page`: 当前页码
- `page_size`: 每页数量
- `has_more`: 是否还有更多结果
- `query`: 搜索关键词

### 错误响应

#### 400 Bad Request
```json
{
  "error": "搜索关键词不能为空"
}
```

```json
{
  "error": "搜索关键词至少需要2个字符"
}
```

#### 401 Unauthorized
```json
{
  "error": "Token has expired"
}
```

#### 403 Forbidden
```json
{
  "error": "您不是该群聊的成员"
}
```

#### 500 Internal Server Error
```json
{
  "error": "搜索用户失败"
}
```

## 使用示例

### 1. 基本用户搜索

```bash
curl -X GET "http://localhost:5000/api/chat/users/search?q=test" \
  -H "Authorization: Bearer <your-jwt-token>"
```

### 2. 分页搜索

```bash
curl -X GET "http://localhost:5000/api/chat/users/search?q=test&page=2&page_size=10" \
  -H "Authorization: Bearer <your-jwt-token>"
```

### 3. 群聊内搜索

```bash
curl -X GET "http://localhost:5000/api/chat/users/search?q=test&group_id=123" \
  -H "Authorization: Bearer <your-jwt-token>"
```

### 4. 搜索中文用户名

```bash
curl -X GET "http://localhost:5000/api/chat/users/search?q=张三" \
  -H "Authorization: Bearer <your-jwt-token>"
```

### 5. 邮箱搜索

```bash
curl -X GET "http://localhost:5000/api/chat/users/search?q=@bikehub.com" \
  -H "Authorization: Bearer <your-jwt-token>"
```

## 技术实现

### 核心功能
1. **安全搜索**: 只搜索用户有权限查看的用户（共同群聊成员）
2. **多字段搜索**: 支持用户名、全名、邮箱的模糊搜索
3. **智能排序**: 精确匹配优先，然后按用户名排序
4. **关系信息**: 返回共同群聊数量等社交关系信息
5. **分页支持**: 高效的分页查询，避免大数据量问题

### 安全特性
- JWT 身份验证
- 权限控制：只能搜索有接触的用户
- SQL 注入防护：使用参数化查询
- 输入验证：关键词长度限制

### 性能优化
- 数据库索引优化
- 分页查询减少数据传输
- 结果数量限制
- 高效的 SQL 查询

## 与现有功能的集成

### 1. 与聊天系统集成
- 可以直接在聊天界面搜索用户
- 支持创建新对话或添加群聊成员
- 显示与搜索用户的社交关系

### 2. 与用户管理系统集成
- 基于现有用户模型和数据
- 兼容现有角色权限系统
- 支持用户状态信息

### 3. 与群聊功能集成
- 支持在特定群聊内搜索成员
- 显示群聊关系信息
- 支持群聊管理功能

## 测试验证

### 功能测试用例
- [x] 空搜索关键词验证
- [x] 单字符搜索验证
- [x] 正常搜索功能
- [x] 中文搜索支持
- [x] 精确匹配功能
- [x] 邮箱搜索功能
- [x] 分页功能
- [x] 群聊内搜索
- [x] 权限控制
- [x] 关系信息返回

### 性能测试
- [ ] 大量用户数据的搜索性能
- [ ] 并发搜索请求处理
- [ ] 数据库查询优化验证

## 部署说明

### 环境要求
- Flask 3.1.0+
- MySQL 8.0+ 或 SQLite（测试环境）
- JWT 扩展
- 现有的聊天系统数据库表

### 配置要求
- 数据库连接配置
- JWT 密钥配置
- 用户认证系统集成

### 数据库依赖
- `users` 表（用户基本信息）
- `chat_groups` 表（群聊信息）
- `chat_group_members` 表（群聊成员关系）

## 后续扩展建议

### 1. 搜索功能增强
- 全文搜索支持
- 搜索历史记录
- 高级搜索过滤器

### 2. 社交功能
- 好友推荐算法
- 基于关系的结果排序
- 用户标签和分类

### 3. 性能优化
- 搜索结果缓存
- 异步搜索处理
- 搜索索引优化

---

**实现时间**: 2025年12月
**版本**: v1.0
**兼容性**: 与现有聊天系统完全兼容