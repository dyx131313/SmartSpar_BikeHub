# SmartSpar BikeHub 重构报告草稿

## 1. 重构总体思路

### 1.1 重构原因

SmartSpar BikeHub 原项目已经具备共享单车站点、调度任务、需求预测、用户与反馈管理等业务功能，但在本地运行、代码结构、前端体验和测试可重复性上存在明显问题：

- 本地启动依赖不清晰，前后端、MySQL、预测模块之间缺少统一运行说明。
- 后端部分路由函数承担过多职责，混合了权限校验、参数解析、业务规则、数据库提交和响应拼装。
- 预测模型路径、上传路径等配置散落在业务代码中，维护成本较高。
- 前端保留了模板项目痕迹，界面风格不统一，登录、侧栏、仪表盘和表格页面不够像运营调度系统。
- TypeScript 构建、ESLint、pytest 和浏览器验收缺少稳定基线。

因此，本次重构目标不是完全推倒重写，而是采用“作业高性价比”策略：优先保证项目可运行、可构建、可测试，再针对高收益坏味道做结构调整和前端体验优化。

### 1.2 重构计划

本次重构按四个阶段推进：

1. 运行基线恢复：搭建本地 Python/Node/MySQL 环境，修复依赖安装、数据库初始化、测试账号和系统时间问题。
2. 后端结构重构：抽取统一响应、权限装饰器、路径配置和服务层，减少路由函数复杂度。
3. 前端体验重构：修复 TypeScript 构建，清理模板痕迹，调整登录页、侧栏、仪表盘、表格和设置页面为运营中台风格。
4. 测试与文档沉淀：补充运行手册、重构记录、测试报告和本报告草稿，记录命令结果与已知限制。

### 1.3 重构分工

建议在最终报告中按如下方式填写小组贡献：

| 成员 | 主要贡献 |
| --- | --- |
| 成员 A | 后端路由重构、服务层抽取、权限与响应工具、测试修复 |
| 成员 B | 前端页面美化、构建修复、需求管理与预测页面验收 |
| 成员 C | 本地环境配置、MySQL 初始化、预测数据准备、运行手册 |
| 成员 D | 文档整理、测试报告、最终报告和展示材料 |

> 注：这里先保留为模板，提交前替换成真实姓名和贡献比例。

### 1.4 测试计划

测试采用“命令行自动测试 + 浏览器人工/半自动验收 + 接口烟测”的组合：

- 前端：`npm run lint`、`npm run build`、浏览器访问登录页、仪表盘、站点管理、调度管理、需求管理、设置页面。
- 后端：`pytest` 覆盖 A* 路径、基础 API、数据库连接、用户搜索、聊天搜索、路由和集成测试。
- 集成：前后端同时启动，使用 `admin/admin123` 登录，验证需求管理、预测结果、系统时间和地图展示。
- 预测：验证 `DLinear`、`TiDE`、`TimesNet` 预测入口可见，`DLinear` 参数和 future 接口返回 200，并在页面渲染预测结果。

## 2. 重构具体介绍

### 2.1 高层重构：体系结构调整

#### 2.1.1 后端分层调整

原后端路由中存在大量“胖路由”问题。重构后引入更清晰的分层：

- Route 层：负责 HTTP 参数接收、权限入口和响应返回。
- Service 层：承载调度任务、仪表盘聚合等业务逻辑。
- Utils 层：提供统一响应、权限装饰器和数据库辅助能力。
- Config 层：集中管理预测模型、上传目录、静态资源等路径。
- Registry/服务辅助层：集中维护预测模型清单，减少新增模型时的多处修改。

新增或重点修改模块：

- `backend/app/utils/response.py`
- `backend/app/utils/decorators.py`
- `backend/app/config/paths.py`
- `backend/app/services/task_service.py`
- `backend/app/services/dashboard_service.py`
- `backend/app/services/prediction_registry.py`

#### 2.1.2 前端页面结构调整

前端保留原有 React + TanStack Router + shadcn/ui 技术栈，但视觉方向调整为“运营调度中台”：

- 登录页和侧栏去除模板化内容，替换为 BikeHub 业务文案。
- 仪表盘突出任务数量、站点状态、预测需求和地图视图。
- 设置页面整合原主题抽屉内容，让外观和布局设置从侧边弹窗进入正式设置页。
- 表格页统一搜索、筛选、按钮、空状态和表格密度。

#### 2.1.3 运行配置调整

为避免本机 MySQL 3306 权限冲突，本地验证使用项目级 MySQL 实例：

- MySQL：`127.0.0.1:3307`
- 后端：`http://127.0.0.1:5000`
- 前端：`http://127.0.0.1:5173`

系统时间接口统一返回：

```text
GET /api/system/time
```

用于预测数据、仪表盘和验收截图保持一致。

### 2.2 低层重构：设计模式、代码味道与 Bug 修正

#### 2.2.1 统一响应与错误处理

重构前，多个路由自行拼装 JSON 响应，错误格式不统一。重构后新增响应工具：

- `success_response`
- `error_response`
- 分页响应工具
- 通用路由错误装饰器

收益：

- 降低重复代码。
- 前端能更稳定地解析错误信息。
- 测试更容易断言响应结构。

#### 2.2.2 权限装饰器

重构前，用户、站点、任务等路由重复判断 JWT 和角色。重构后抽取：

- `require_roles`
- `require_admin`
- `require_dispatcher_or_admin`

收益：

- 权限逻辑集中维护。
- 路由函数更聚焦业务。
- 降低不同接口权限判断不一致的风险。

#### 2.2.3 服务层抽取

`dispatch_tasks.py` 原本同时处理任务校验、派发、库存变更、历史记录和数据库提交。重构后将核心逻辑迁移到 `TaskService`。

仪表盘聚合逻辑迁移到 `DashboardService`，负责聚合站点、预测、库存、任务状态等数据。

收益：

- Route 层更轻。
- 业务逻辑可测试性更好。
- 后续新增调度规则或预测指标时不用修改大量路由代码。

#### 2.2.4 路径配置集中化

预测模型文件和上传目录原来存在硬编码路径。重构后通过 `backend/app/config/paths.py` 管理：

- 预测 checkpoint 路径
- 上传目录
- 静态资源目录

收益：

- 减少 Windows 路径和相对路径问题。
- 预测接口、仪表盘接口共享同一套路径规则。

同时新增 `backend/app/services/prediction_registry.py`，将 `DLinear`、`TiDE`、`TimesNet` 等模型名称及参数/future 文件位置集中管理，并新增 `/api/predictions/models` 接口，作为后续策略模式或工厂模式重构的过渡。

#### 2.2.5 预测模块降级启动

原 scheduler 在缺少 `torch` 时可能导致 Flask 启动失败。重构后改为可选依赖降级：

- Web 服务可以先启动。
- 缺少深度学习依赖时跳过预测训练/调度任务，并输出清晰日志。
- 已生成的 future JSON 仍可被预测接口读取。

#### 2.2.6 前端构建与路由 Bug 修复

修复内容包括：

- 补充 TanStack Table `ColumnMeta.title` 类型。
- 修复表单 resolver 类型兼容问题。
- 统一数字/字符串筛选值。
- 修复需求管理旧路径 `/demand_management` 导致的 TanStack Router active match 崩溃，改为兼容跳转到 `/demand-management`。
- 修复 React Hook 规则问题，包括 `useConfirm` 调用位置、WebSocket 重连和输入防抖、地图初始化顺序。

#### 2.2.7 前端视觉修缮

主要调整：

- 清理默认用户 `satnaing`、Acme/Clerk 示例和英文模板残留。
- 优化登录页中文文案。
- 调整侧栏、背景、卡片、按钮、状态色，使整体更接近调度运营系统。
- 仪表盘增加更清晰的业务摘要、任务状态卡片和地图 fallback。
- 设置页面融合主题、侧栏、布局、方向设置。

### 2.3 文档修订

本次新增或修订文档：

- `docs/LOCAL_RUNBOOK.md`：本地启动、端口、MySQL、账号和验证命令。
- `docs/REFACTORING_RECORD.md`：记录问题、重构手法、涉及模块、测试结果和已知限制。
- `docs/TEST_REPORT.md`：记录最终测试命令、结果和风险。
- `docs/REFACTORING_REPORT_DRAFT.md`：本报告草稿。

## 3. 重构后的源码、文档、测试报告和贡献

### 3.1 源码链接

最终提交时填写仓库链接：

```text
<填写 GitHub/Gitee/课程平台源码链接>
```

关键源码位置：

- 后端入口：`backend/run.py`
- 后端应用：`backend/app`
- 后端服务层：`backend/app/services`
- 后端工具：`backend/app/utils`
- 前端入口：`frontend/bikehub/src`
- 前端页面：`frontend/bikehub/src/features`

### 3.2 文档

交付文档建议包括：

- `docs/REFACTORING_REPORT_DRAFT.md`
- `docs/TEST_REPORT.md`
- `docs/LOCAL_RUNBOOK.md`
- `docs/REFACTORING_RECORD.md`
- 后端 API 文档和预测运行指南

### 3.3 测试报告

最新测试结果摘要：

| 测试项 | 命令/方式 | 结果 |
| --- | --- | --- |
| 前端 Lint | `npm run lint` | 通过，0 errors，保留 warnings |
| 前端构建 | `npm run build` | 通过，Vite 大 chunk warning |
| 后端单元/集成测试 | `.venv\Scripts\python.exe -m pytest` | 20 passed, 4 skipped |
| 系统时间接口 | `GET /api/system/time` | 通过 |
| 登录 | `admin/admin123` | 通过 |
| 需求管理 | `/demand-management` | 通过 |
| 旧需求路径兼容 | `/demand_management` | 跳转到新路径，通过 |
| 预测页面 | 点击“预测需求” | DLinear/TiDE/TimesNet 可见，DLinear 数据渲染 |

详细内容见 `docs/TEST_REPORT.md`。

### 3.4 已知限制

- 前端仍有 ESLint warnings，主要是历史模板残留、`any` 类型、未使用 import、console 调试和部分 hook 依赖提示；当前不阻塞 lint 退出码、构建和运行。
- Vite 构建提示部分 chunk 大于 500 KB，后续可通过路由级动态导入和 manualChunks 优化。
- 深度学习训练依赖属于可选环境，本次重点保证已有预测结果读取和页面展示可用。
- 当前本地数据库使用 3307 端口，提交部署前需要按目标环境调整 `.env`。

## 4. 总结

本次重构完成了从“能否跑起来不稳定”到“可运行、可构建、可测试、可说明”的转变。后端通过服务层、权限装饰器、统一响应和路径配置降低了维护复杂度；前端通过构建修复、运营中台化视觉调整和关键路由 Bug 修复改善了用户体验；测试和文档则为课程作业验收提供了可复现证据。
