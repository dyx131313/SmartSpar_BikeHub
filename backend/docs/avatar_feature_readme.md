# 用户头像功能实现文档

## 功能概述

本功能为 SmartSpar BikeHub 应用增加了用户头像上传和管理功能，包括：

1. **头像上传**：支持 JPG、PNG、GIF 格式的图片上传，文件大小限制为 5MB
2. **头像显示**：在导航栏和个人信息页面显示用户头像
3. **头像删除**：支持删除已上传的头像
4. **头像更新**：可以随时更换头像

## 后端实现

### 1. 数据库模型更新

在 `app/models/user.py` 中为 User 模型添加了 `avatar_url` 字段：

```python
avatar_url = db.Column(db.String(255), comment='头像URL')
```

### 2. API 接口

#### 2.1 上传头像
- **接口**：`POST /api/users/avatar`
- **认证**：需要 JWT 认证
- **请求**：multipart/form-data，包含 `avatar` 字段（文件）
- **响应**：
  ```json
  {
    "message": "头像上传成功",
    "data": {
      "avatar_url": "/uploads/avatars/用户ID_随机字符串.扩展名"
    }
  }
  ```

#### 2.2 删除头像
- **接口**：`DELETE /api/users/avatar`
- **认证**：需要 JWT 认证
- **响应**：
  ```json
  {
    "message": "头像删除成功"
  }
  ```

### 3. 文件存储

- 头像文件存储在 `static/uploads/avatars/` 目录下
- 文件名格式：`{用户ID}_{UUID}.{扩展名}`
- 自动删除旧头像文件
- 提供 `/uploads/avatars/{filename}` 路径访问头像

### 4. 安全特性

- 文件类型验证（MIME 和扩展名双重验证）
- 文件大小限制（5MB）
- 文件名安全处理（使用 secure_filename）
- 路径遍历攻击防护

## 前端实现

### 1. 组件结构

#### 1.1 AvatarUploader 组件
位置：`src/features/settings/profile/avatar-uploader.tsx`

功能：
- 头像预览
- 文件选择对话框
- 上传进度显示
- 删除头像功能
- 响应式设计

#### 1.2 个人信息页面
位置：`src/features/settings/profile/profile-form.tsx`

集成了头像上传组件，提供：
- 用户信息获取和表单填充
- 头像URL状态管理
- 与后端API的交互

### 2. 样式特性

- 使用 Tailwind CSS 实现响应式设计
- 渐变背景的头像占位符
- 悬停效果和过渡动画
- 模态对话框布局

### 3. 用户体验

- 拖拽上传支持（通过文件选择器）
- 实时预览
- 文件类型和大小验证
- 错误提示和成功反馈
- 自动刷新显示最新头像

## 集成步骤

### 后端部署

1. 运行数据库迁移：
   ```bash
   flask db upgrade
   ```

2. 确保目录权限：
   ```bash
   mkdir -p static/uploads/avatars
   chmod 755 static/uploads/avatars
   ```

### 前端部署

1. 确保所有依赖已安装：
   ```bash
   npm install
   ```

2. 构建前端应用：
   ```bash
   npm run build
   ```

## 测试建议

### 功能测试
1. 上传不同格式的图片（JPG、PNG、GIF）
2. 测试文件大小限制（5MB）
3. 测试非图片文件上传
4. 测试头像删除功能
5. 测试头像更新功能

### UI 测试
1. 检查导航栏头像显示
2. 检查个人信息页面头像显示
3. 测试响应式布局
4. 测试加载状态和错误状态

### 集成测试
1. 完整的用户头像上传流程
2. 页面刷新后头像保持
3. 多设备头像同步

## 注意事项

1. **文件命名**：头像文件使用 UUID 避免文件名冲突
2. **性能考虑**：建议对头像进行尺寸压缩和格式转换
3. **安全考虑**：生产环境应考虑使用云存储服务
4. **兼容性**：确保支持所有现代浏览器

## 未来扩展

1. 头像裁剪功能
2. 多种头像尺寸生成
3. 头像 CDN 支持
4. 头像审核机制