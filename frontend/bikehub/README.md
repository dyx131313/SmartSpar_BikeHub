# SmartSpar BikeHub Frontend

智慧共享单车调度系统前端服务 - 基于Vite + React开发环境

## 项目概述



## 技术栈

| 类别       | 技术            | 说明                             |
| ---------- | --------------- | -------------------------------- |
| 前端框架   | React + Vite    | 高性能、组件化开发，适合管理系统 |
| UI框架     | Ant Design      | 提供美观的表格、图标、弹窗组件   |
| 地图展示   | 高德地图 JS API | 中文文档友好，免费试用           |
| 可视化图表 | EChart          | 会直折线图、柱状图、热力图       |
| 网络请求   | Axios           | 统一管理接口调用                 |
| 构建与部署 | 华为云          | 打包后部署在华为云服务器上       |

## 项目结构

```
bikehub/
├─ src/
│  ├─ App.tsx        # 主组件
│  ├─ main.tsx       # 入口文件
│  ├─ vite-env.d.ts  # 类型定义
├─ index.html        # HTML 模板
├─ tsconfig.json     # TypeScript 配置
├─ vite.config.ts    # Vite 配置
```

## 快速开始

### 1.环境要求

- Nodejs  v24.11.0
- npm 11.6.1

### 2. 安装依赖

```
# 安装Nodejs请参考官网教程
https://nodejs.org

# 使用npm创建项目
npm create vite@latest SmartSpar_BikeHub -- --template react-ts

#进入项目目录并安装依赖
cd SmartSpar_BikeHub
npm install

# 运行开发服务器
npm run dev

# 运行后会看到类似输出：
VITE v5.x  ready in 300ms
Local:   http://localhost:5173/
访问上面的网址即可进行测试
```

