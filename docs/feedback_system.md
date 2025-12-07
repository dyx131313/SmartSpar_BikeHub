# 反馈系统设计与使用文档

## 1. 功能概述

反馈系统允许不同角色的用户提交问题和建议，并由管理员进行统一管理和处理。

### 主要功能点
*   **用户反馈**: 普通用户可以提交使用过程中的问题或建议。
*   **调度异常反馈**: 调度员可以提交调度过程中遇到的异常情况。
*   **反馈管理**: 管理员可以查看所有反馈，并进行状态更新和处理回复。
*   **状态追踪**: 支持反馈状态流转（待处理 -> 处理中 -> 已解决/已关闭）。

## 2. 权限设计

| 角色 | 提交反馈 | 查看反馈 | 处理反馈 | 备注 |
| :--- | :---: | :---: | :---: | :--- |
| **Admin (管理员)** | ✅ | ✅ (所有) | ✅ | 拥有最高权限，可查看和处理所有反馈 |
| **Dispatcher (调度员)** | ✅ (调度异常) | ✅ (仅自己) | ❌ | 提交调度相关的异常反馈 |
| **Operator (运维员)** | ✅ (用户反馈) | ✅ (仅自己) | ❌ | 也可以提交一般反馈 |
| **User (普通用户)** | ✅ (用户反馈) | ✅ (仅自己) | ❌ | 提交使用体验相关反馈 |

## 3. 数据模型

### Feedback (反馈)

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | Integer | 主键 |
| `user_id` | Integer | 提交人ID (外键) |
| `category` | Enum | 类型: `user_feedback` (用户反馈), `dispatcher_issue` (调度异常) |
| `title` | String | 标题 |
| `content` | Text | 详细内容 |
| `status` | Enum | 状态: `pending`, `processing`, `resolved`, `closed` |
| `created_at` | DateTime | 创建时间 |
| `resolution_notes`| Text | 处理结果备注 |
| `resolved_by` | Integer | 处理人ID (管理员) |
| `resolved_at` | DateTime | 处理时间 |

## 4. API 接口

### 4.1 提交反馈
*   **URL**: `POST /api/feedback`
*   **Auth**: Required
*   **Body**:
    ```json
    {
        "title": "无法开锁",
        "content": "在西门站点扫描车辆二维码无反应...",
        "category": "user_feedback" // 可选，管理员可指定，普通用户默认为user_feedback，调度员默认为dispatcher_issue
    }
    ```

### 4.2 获取反馈列表
*   **URL**: `GET /api/feedback`
*   **Auth**: Required
*   **Query Params**:
    *   `page`: 页码
    *   `per_page`: 每页数量
    *   `status`: 状态筛选
    *   `category`: 类型筛选
*   **Response**: 分页返回反馈列表。非管理员只返回自己提交的数据。

### 4.3 更新反馈 (管理员)
*   **URL**: `PUT /api/feedback/<id>`
*   **Auth**: Admin only
*   **Body**:
    ```json
    {
        "status": "resolved",
        "resolution_notes": "已安排运维人员检修，并在后台退还了费用。"
    }
    ```

## 5. 前端页面

*   **路由**: `/_authenticated/feedback`
*   **入口**: 侧边栏 -> 控制面板 -> 反馈管理
*   **主要组件**:
    *   `FeedbackTable`: 展示反馈列表，支持状态和类型筛选。
    *   `FeedbackDialogs`: 包含提交反馈、查看详情、处理反馈的弹窗表单。

## 6. 使用流程

1.  **用户/调度员提交**: 点击右上角“提交反馈”，填写标题和内容。
2.  **管理员查看**: 登录后台，进入反馈管理页面，查看状态为“待处理”的条目。
3.  **管理员处理**: 点击列表行右侧的操作按钮（...），选择“处理反馈”，填写处理结果并更新状态为“已解决”。
4.  **结果反馈**: 用户可以在自己的列表中点击“查看详情”看到管理员的处理回复。



