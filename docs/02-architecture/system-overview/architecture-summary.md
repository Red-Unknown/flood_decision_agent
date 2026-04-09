# 架构摘要

## 系统概述

防汛调度智能决策 Agent 系统是一个基于 DDD（领域驱动设计）架构的智能决策支持系统。系统采用"决策链生成 Agent → 节点调度 Agent → 单元任务执行 Agent → 决策融合"的核心流程，实现从用户意图到决策方案的完整链路。

## 核心架构

### 分层架构

```
┌─────────────────────────────────────────┐
│         Interfaces (API/WebSocket)      │
│   - REST API (FastAPI)                  │
│   - WebSocket (实时通信)                │
│   - CLI (命令行接口)                    │
├─────────────────────────────────────────┤
│         Application Services            │
│   - DecisionService                     │
│   - ChatService                         │
│   - DataAcquisitionService              │
├─────────────────────────────────────────┤
│           Domain Layer                  │
│   - Entities (Decision, Task, Message)  │
│   - Value Objects (Priority, Status)    │
│   - Events (TaskCreated, Completed)     │
├─────────────────────────────────────────┤
│        Infrastructure (LLM/MCP)         │
│   - LLM Client (Kimi)                   │
│   - MCP Protocol                        │
│   - Persistence (Repository)            │
└─────────────────────────────────────────┘
```

### 核心组件

#### 1. Agent 层

- **DecisionChainGeneratorAgent**: 决策链生成 Agent
  - 意图解析（Intent Parser）
  - 任务分解（Task Decomposer）
  - 决策链优化（Chain Optimizer）
  
- **NodeSchedulerAgent**: 节点调度 Agent
  - 任务图调度
  - 依赖管理
  - 并发控制
  
- **UnitTaskExecutorAgent**: 单元任务执行 Agent
  - 工具选择和调用
  - MCP 服务集成
  - 流式执行
  
- **SummarizerAgent**: 总结 Agent
  - 执行结果汇总
  - 智能报告生成

#### 2. MCP 协议层

- **MCP Servers**: 多个专用服务
  - `filesystem`: 文件系统服务
  - `hydrology`: 水文数据服务
  - `document`: 文档处理服务
  - `hipims`: 水动力模型服务
  - `rainfall`: 降雨数据服务
  - `web_search`: 网络搜索服务
  - `yolo_vision`: 视觉识别服务
  
- **MCP Clients**: 统一客户端管理器
  - 服务发现
  - 健康检查
  - 工具调用
  
- **MCP Tools**: 工具注册和适配
  - 工具定义
  - 参数映射
  - 结果转换

#### 3. Web 层

- **Backend (FastAPI)**
  - REST API 路由
  - WebSocket 处理器
  - 对话管理
  - 会话持久化
  
- **Frontend (Vue 3)**
  - 聊天界面
  - 决策链可视化
  - 任务执行监控
  - Plan/Spec 模式

#### 4. 数据流

```
用户请求
    ↓
Intent Parser (意图解析)
    ↓
Decision Chain Generator (决策链生成)
    ↓
Task Graph Builder (任务图构建)
    ↓
Node Scheduler (节点调度)
    ↓
Unit Task Executor (单元任务执行)
    ├→ MCP Tools (MCP 工具)
    └→ Shared Data Pool (共享数据池)
    ↓
Summarizer (总结)
    ↓
用户响应
```

## 关键技术特性

### 1. DDD 分层设计

- **领域层**: 核心业务实体，无外部依赖
- **应用层**: 业务逻辑编排，协调领域对象
- **基础设施层**: 技术实现，可替换
- **接口层**: 对外接口，适配不同客户端

### 2. MCP 服务协议

- **标准化**: 统一的工具调用协议
- **可扩展**: 易于添加新服务
- **隔离性**: 服务独立运行，互不影响
- **健康检查**: 自动检测服务状态

### 3. 流式处理

- 意图解析流式输出
- 决策链生成流式展示
- 任务执行实时更新
- 结果总结流式返回

### 4. 对话管理

- 多会话并发支持
- 上下文状态保持
- 历史消息持久化
- 取消和中断处理

## 部署架构

### 开发环境

```
┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │
│  (Vue 3)    │◀────│  (FastAPI)  │
└─────────────┘     └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼─────┐ ┌───▼────┐ ┌────▼────┐
        │   LLM     │ │  MCP   │ │   DB    │
        │  (Kimi)   │ │Servers │ │(SQLite) │
        └───────────┘ └────────┘ └─────────┘
```

### 生产环境

```
┌──────────────────┐
│   Load Balancer  │
└────────┬─────────┘
         │
    ┌────▼────┐
    │ Frontend│
    │ Cluster │
    └────┬────┘
         │
    ┌────▼────┐
    │ Backend │
    │ Cluster │
    └────┬────┘
         │
    ┌────▼─────────────────────┐
    │   MCP Servers Cluster    │
    │  ┌────┐ ┌────┐ ┌────┐   │
    │  │Hydro│ │Doc │ │HIPIMS│ │
    │  └────┘ └────┘ └────┘   │
    └──────────────────────────┘
```

## 技术栈

### 后端
- **框架**: FastAPI + Uvicorn
- **LLM**: Kimi API
- **协议**: MCP (Model Context Protocol)
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **通信**: WebSocket + REST API

### 前端
- **框架**: Vue 3 + Vite
- **UI 库**: Element Plus
- **状态管理**: Pinia
- **HTTP 客户端**: Axios
- **实时通信**: WebSocket

### 基础设施
- **环境管理**: Conda
- **包管理**: pip + npm
- **测试**: pytest + Playwright
- **日志**: Python logging

## 设计原则

1. **领域驱动**: 核心业务逻辑独立于技术实现
2. **接口隔离**: 通过接口与外部系统交互
3. **依赖倒置**: 高层模块不依赖低层模块
4. **单一职责**: 每个组件只负责一个功能
5. **开闭原则**: 对扩展开放，对修改关闭

## 当前状态

### 已实现
- ✅ 核心 Agent 架构
- ✅ MCP 服务协议
- ✅ Web 前后端
- ✅ 对话管理
- ✅ 评估框架
- ✅ 工具系统

### 待实现
- ⏳ 真实数据库集成
- ⏳ 水动力模型完整接入
- ⏳ 多模型融合策略
- ⏳ 规则引擎
- ⏳ 性能优化

## 相关文档

- [详细架构](detailed-architecture.md) - 详细架构说明
- [目录结构](../directory-structure/directory-structure.md) - 项目目录结构
- [开发者指南](../../03-development/guides/developer-guide.md) - 开发最佳实践
