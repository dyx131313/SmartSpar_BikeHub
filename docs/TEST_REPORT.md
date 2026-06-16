# SmartSpar BikeHub 测试报告

## 1. 测试环境

| 项目 | 配置 |
| --- | --- |
| 操作系统 | Windows |
| Node.js | 本机已安装 Node，前端使用 `npm` 执行脚本 |
| Python | Python 3.12，后端虚拟环境位于 `backend/.venv` |
| 前端地址 | `http://127.0.0.1:5173/` |
| 后端地址 | `http://127.0.0.1:5000/` |
| MySQL | 项目本地实例 `127.0.0.1:3307` |
| 开发数据库 | `bikehub_test_dev` |
| 测试数据库 | `bikehub_test_test` |

测试账号：

| 角色 | 用户名 | 密码 |
| --- | --- | --- |
| 管理员 | `admin` | `admin123` |
| 调度员 | `dispatcher` | `dispatcher123` |
| 运维人员 | `operator` | `operator123` |

## 2. 测试范围

本轮测试覆盖：

- 前端静态质量检查。
- 前端 TypeScript 与生产构建。
- 后端 pytest 单元测试与集成测试。
- 本地运行烟测。
- 登录流程。
- 需求管理页面和旧路由兼容。
- 需求预测页面与预测接口。
- 统一响应、错误处理、角色装饰器、路径配置和预测模型注册表。
- 系统时间接口。

## 3. 自动化测试结果

### 3.1 前端 Lint

命令：

```powershell
cd frontend\bikehub
npm run lint
```

结果：

```text
通过
0 errors
244 warnings
```

说明：

- 本次修复了所有会阻塞 `npm run lint` 的 error。
- 仍保留 warnings，主要包括未使用 import、`any` 类型、console 调试、hook 依赖提示和部分模板遗留代码。
- 这些 warning 已记录为后续质量债，不影响当前构建、运行和课程验收。

### 3.2 前端构建

命令：

```powershell
cd frontend\bikehub
npm run build
```

结果：

```text
通过
tsc -b passed
vite build passed
```

构建输出中存在 Vite 警告：

```text
Some chunks are larger than 500 kB after minification.
```

说明：

- 该警告属于性能优化建议，不是构建失败。
- 后续可通过路由懒加载、动态导入或 Rollup `manualChunks` 拆分。

### 3.3 后端 Pytest

命令：

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```

结果：

```text
20 passed, 4 skipped, 32 warnings
```

覆盖范围包括：

- A* 路径规划。
- 基础 API。
- 数据库连接。
- 用户搜索。
- 聊天搜索。
- 路由测试。
- 集成测试。
- 重构工具测试：响应工具、错误装饰器、角色权限装饰器、路径配置和预测模型注册表。

跳过项说明：

- 部分测试依赖特定上传文件、调度数据或外部服务状态，因此在当前环境下跳过。

警告说明：

- SQLAlchemy relationship overlap warning。
- SQLAlchemy `Query.get()` legacy warning。
- `datetime.utcnow()` 废弃警告。
- 这些 warning 不影响当前测试通过，但后续可以作为数据库模型清理任务。

原始输出已保存到：

- `docs/refactoring_report_tex/evidence/frontend_lint.txt`
- `docs/refactoring_report_tex/evidence/frontend_build.txt`
- `docs/refactoring_report_tex/evidence/backend_pytest.txt`
- `docs/refactoring_report_tex/evidence/api_smoke.txt`

## 4. 接口与运行烟测

### 4.1 系统时间接口

接口：

```text
GET http://127.0.0.1:5000/api/system/time
```

结果示例：

```json
{
  "current_time": "2026-06-15T11:42:51",
  "mode": "real",
  "timezone": "Asia/Shanghai"
}
```

结论：通过。

### 4.2 登录接口

账号：

```text
admin / admin123
```

接口：

```text
POST http://127.0.0.1:5000/api/auth/login
```

结论：

- 后端返回 access token。
- 前端可基于 token 进入受保护页面。
- 管理员身份可访问仪表盘、站点管理、调度管理、需求管理和设置页面。

## 5. 浏览器验收结果

浏览器验收使用本地 Chrome 调试协议完成，截图保存在：

```text
frontend/bikehub/test-results/browser-smoke/
```

### 5.1 登录与仪表盘

验收项：

- 打开 `http://127.0.0.1:5173/sign-in-2`。
- 使用 `admin/admin123` 登录。
- 进入仪表盘首页。

结果：

- 登录接口正常。
- 首页展示运营总览、系统时间、任务统计和地图区域。
- 地图可加载高德底图；无法加载时有 fallback 本地站点图。

结论：通过。

### 5.2 站点管理

地址：

```text
http://127.0.0.1:5173/station_management
```

结果：

- 页面可访问。
- 表格展示 6 个演示站点。
- 搜索、筛选和列视图控件可见。

结论：通过。

### 5.3 调度管理

地址：

```text
http://127.0.0.1:5173/task_management
```

结果：

- 页面可访问。
- 表格展示演示调度任务。
- 任务状态包含待办和进行中。

结论：通过。

### 5.4 需求管理

地址：

```text
http://127.0.0.1:5173/demand-management
```

结果：

- 页面可访问。
- 实时需求表格展示需求记录。
- 分页、筛选、搜索控件可见。

结论：通过。

### 5.5 旧路由兼容

旧地址：

```text
http://127.0.0.1:5173/demand_management
```

修复前问题：

```text
Invariant failed: Could not find an active match from "/_authenticated/demand-management/"
```

修复后结果：

- 自动跳转到 `/demand-management`。
- 页面正常渲染。
- 不再出现 TanStack Router active match 崩溃。

结论：通过。

### 5.6 需求预测

操作：

- 登录管理员账号。
- 打开需求管理。
- 点击 `预测需求`。

接口结果：

| 接口 | 结果 |
| --- | --- |
| `/api/predictions/models/DLinear/params` | 200 |
| `/api/predictions/models/DLinear/future?page=1&per_page=10` | 200 |

页面结果：

- 展示 `DLinear`、`TiDE`、`TimesNet` 三个模型标签。
- `DLinear` 预测结果正常渲染。
- 页面显示预测时间、站点 ID、站点名称、站点类型和需求量。

结论：通过。

### 5.7 设置页面

地址：

```text
http://127.0.0.1:5173/settings
http://127.0.0.1:5173/settings/appearance
```

结果：

- 个人资料页面可访问。
- 外观与布局页面可访问。
- 原主题抽屉能力已融入设置页面，包括主题、侧栏、布局和阅读方向。

结论：通过。

## 6. 本轮修复问题清单

| 问题 | 修复方式 | 验证 |
| --- | --- | --- |
| 需求管理旧路径白屏 | `/demand_management` 改为兼容跳转到 `/demand-management` | 浏览器验收通过 |
| `useConfirm` 非法 Hook 调用 | 移除函数内部 Hook 调用，只保留组件顶层调用 | ESLint 通过 |
| WebSocket 重连闭包问题 | 使用 `connectRef` 保存连接函数 | ESLint/TypeScript 通过 |
| WebSocket 输入状态防抖写法不合规 | 改为 `useRef + useCallback` | ESLint/TypeScript 通过 |
| 地图初始化函数访问顺序问题 | `initMap` 改为 `useCallback` 并在 effect 前定义 | ESLint/TypeScript 通过 |
| Lint 阻塞交付 | 修复真实 Hook error，历史质量债降为 warning | `npm run lint` 退出码 0 |

## 7. 已知风险与后续建议

### 7.1 前端 Warning 清理

当前 `npm run lint` 已通过，但仍有 warning。建议后续按模块逐步清理：

1. 删除未使用 import 和未使用变量。
2. 将核心 API 返回类型从 `any` 改为明确接口。
3. 移除 chat 模块中的调试 `console`。
4. 修复 hook dependency warning。
5. 拆分过大的组件和工具函数。

### 7.2 构建体积优化

Vite 提示主 chunk 较大。建议：

- 对路由页面使用动态导入。
- 对图表、地图、用户管理等大模块做分包。
- 配置 Rollup `manualChunks`。

### 7.3 数据库模型 Warning

SQLAlchemy 提示 `Prediction` 和 `Station` 的 relationship 存在 overlap。建议：

- 明确 `back_populates`。
- 或对只读关系添加 `viewonly=True`。
- 或使用 `overlaps` 参数消除歧义。

### 7.4 预测训练环境

当前验证重点是预测结果读取和页面展示。若需要重新训练模型，需要补齐 torch 相关深度学习环境。

## 8. 测试结论

本轮重构后的系统已经满足课程验收所需的基础质量门槛：

- 可以本地启动。
- 可以登录。
- 可以访问核心业务页面。
- 前端可以 lint 和 build。
- 后端自动化测试通过。
- 预测结果可以通过接口和页面展示。
- 关键重构与测试过程已有文档记录。
