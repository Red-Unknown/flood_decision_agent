# flood_decision_agent

面向防汛调度的智能决策科研原型工程。项目采用 DDD（领域驱动设计）架构，结合 Web 前后端分离和 MCP（Model Context Protocol）服务协议，实现完整的决策链生成、节点调度和任务执行能力。

## 项目进展

### 已实现功能

#### 1. 核心 Agent 架构
- **DecisionChainGeneratorAgent**: 决策链生成 Agent，基于 LLM 进行意图解析和任务分解
- **NodeSchedulerAgent**: 节点调度 Agent，负责任务图的调度和执行
- **UnitTaskExecutionAgent**: 单元任务执行 Agent，支持动态工具选择和执行
- **SummarizerAgent**: 总结智能体，对执行过程和结果进行智能总结

#### 2. 意图解析与任务分解
- 使用 Kimi LLM 进行自然语言意图识别
- 支持流式输出，实时显示 AI 思考过程
- 基于 prefix mode 引导 JSON 格式输出
- 支持 10+ 种业务类型（洪水预警、水库调度、数据查询等）

#### 3. MCP 服务协议
- **MCP Servers**: 实现多个专用服务（filesystem, hydrology, document, hipims, rainfall, web_search, yolo_vision）
- **MCP Clients**: 统一的客户端管理器，支持服务发现和健康检查
- **MCP Tools**: 工具注册和动态调用机制
- **MCP Logging**: 完整的日志系统和错误处理

#### 4. Web 前后端
- **后端**: FastAPI REST API + WebSocket 实时通信
- **前端**: Vue 3 + Element Plus + Pinia 状态管理
- **API**: 对话管理、决策链生成、任务执行、Plan/Spec 模式
- **WebSocket**: 实时消息推送和流式输出

#### 5. 工具系统
- **专用工具**: 数据采集、预测预报、计算分析、决策生成等（10 种）
- **通用查询工具**: 使用 LLM 直接回答任意问题
- **MCP 工具**: 通过 MCP 协议调用的外部服务
- 工具注册中心支持动态注册和查询
- 支持工具执行策略：single、parallel、fallback、ensemble

#### 6. 可视化展示
- PowerShell 终端可视化，支持 ANSI 颜色
- 显示 Agent 调用链和数据流
- 展示决策链任务列表和执行状态
- 实时显示任务执行进度（打勾标记）
- Web 界面实时进度展示

#### 7. 流式输出
- 意图解析流式输出
- 决策链生成流式输出
- 任务执行流式输出
- 通用查询流式输出
- 执行总结流式输出

#### 8. 评估框架
- 评估指标体系
- 测试用例管理
- 场景定义
- 报告生成

## 快速开始

### 1. 环境配置

#### 方法一：一键安装（推荐）

进入项目根目录，运行 PowerShell 脚本：

```powershell
.\scripts\setup_env.ps1
```

#### 方法二：手动安装

```powershell
# 创建 Conda 环境
conda env create -f environment.yml

# 激活环境
conda activate intelligent_decision

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key

需要在系统环境变量中配置 Kimi API Key：

```powershell
# Windows PowerShell
$env:KIMI_API_KEY="your_api_key"

# 永久设置（推荐）
setx KIMI_API_KEY "your_api_key"
```

重新打开 PowerShell 终端使配置生效。

### 3. 启动 Web 服务

#### 方法一：使用启动脚本

```powershell
# 启动后端和前端
python scripts\start_web.py
```

#### 方法二：分别启动

**终端 1 - 启动后端：**
```powershell
python -m web.backend.main
```
后端运行在 http://localhost:8000

**终端 2 - 启动前端：**
```powershell
cd web/frontend
npm install      # 首次运行
npm run dev
```
前端运行在 http://localhost:3000

### 4. 运行示例

```powershell
# 示例 1: 洪水预警分析
python .\examples\run_visualized_demo.py 1

# 示例 2: 水库联合调度
python .\examples\run_visualized_demo.py 2

# 示例 3: 数据查询
python .\examples\run_visualized_demo.py 3

# 示例 4: 洪水风险评估
python .\examples\run_visualized_demo.py 4

# 示例 5: 应急响应决策
python .\examples\run_visualized_demo.py 5

# 示例 6: 自定义问题（通用查询）
python .\examples\run_visualized_demo.py 6 "河海大学怎么样？"

# 运行所有预设示例
python .\examples\run_visualized_demo.py all
```

### 5. 运行测试

```powershell
# 运行所有测试
cd tests
python run_tests.py

# 运行特定测试
pytest tests/agents/test_decision_chain_generator.py -v
```

## 目录结构

```
flood_decision_agent/
├── configs/                    # 集中式配置管理
├── src/flood_decision_agent/   # 核心业务代码
│   ├── domain/                 # 领域层 - 核心业务实体
│   ├── application/            # 应用层 - 业务逻辑编排
│   ├── infrastructure/         # 基础设施层
│   ├── mcp/                    # MCP 协议层
│   ├── agents/                 # 智能体层
│   ├── evaluation/             # 评估框架
│   ├── interfaces/             # 接口适配层
│   ├── shared/                 # 共享组件
│   ├── conversation/           # 对话管理
│   └── visualization/          # 可视化
├── web/                        # Web 应用
│   ├── backend/                # 后端服务
│   └── frontend/               # 前端应用
├── tests/                      # 测试目录
├── resources/                  # 资源文件
├── docs/                       # 文档
├── scripts/                    # 脚本工具
├── debug/                      # 调试工具
├── examples/                   # 示例代码
├── logs/                       # 日志文件
└── notebooks/                  # Jupyter notebooks
```

详细目录结构说明请参考 [目录结构文档](docs/02-architecture/directory-structure/directory-structure.md)

## 技术架构

### 分层架构

```
┌─────────────────────────────────────────┐
│         Interfaces (API/WebSocket)      │
├─────────────────────────────────────────┤
│         Application Services            │
├─────────────────────────────────────────┤
│           Domain Layer                  │
├─────────────────────────────────────────┤
│        Infrastructure (LLM/MCP)         │
└─────────────────────────────────────────┘
```

### 核心组件

- **Domain Layer**: 业务实体（Decision, Task, Message, Conversation）
- **Application Layer**: 业务逻辑编排和服务
- **Infrastructure Layer**: LLM 客户端、MCP 协议、数据持久化
- **Agents Layer**: 各类智能体实现
- **Interfaces Layer**: REST API 和 WebSocket 接口

### 数据流

```
用户请求 → Intent Parser → Decision Chain Generator 
       → Task Graph Builder → Node Scheduler 
       → Unit Task Executor (MCP Tools) 
       → Summarizer → 用户
```

## 开发规范

### 代码风格
- 代码风格：PEP8
- 格式化：black + isort
- 代码检查：flake8

### 提交前检查

```powershell
# 运行 pre-commit
pre-commit run --all-files

# 运行测试
pytest tests/ -v

# 检查代码风格
flake8 src/
```

### 环境变量门控

所有示例、调试与正式运行入口在启动时必须检查环境变量 `KIMI_API_KEY`，若未配置，启动时直接输出 `需要 kimi_api_key` 并以退出码 1 结束。

## 测试

### 测试类型

- **单元测试**: `tests/agents/`, `tests/core/`, `tests/api/`
- **集成测试**: `tests/integration/`
- **端到端测试**: `tests/e2e/`
- **MCP 测试**: `tests/mcp/`
- **调试测试**: `tests/debug/`

### 运行测试

```powershell
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/agents/ -v

# 运行覆盖率测试
pytest tests/ --cov=src/flood_decision_agent --cov-report=html
```

## 文档

- **入门指南**: [docs/01-getting-started/](docs/01-getting-started/)
- **架构文档**: [docs/02-architecture/](docs/02-architecture/)
- **开发指南**: [docs/03-development/](docs/03-development/)
- **API 参考**: [docs/04-api-reference/](docs/04-api-reference/)
- **部署文档**: [docs/05-deployment/](docs/05-deployment/)
- **技术规范**: [docs/06-specifications/](docs/06-specifications/)
- **MCP 文档**: [docs/mcp/](docs/mcp/)

## 更新日志

### v2.0.0 (2026-04-09) - 架构重构

**新增功能：**
- ✅ Web 前后端分离架构
- ✅ MCP 服务协议完整实现
- ✅ DDD 分层架构重构
- ✅ 评估框架
- ✅ 对话管理和会话持久化
- ✅ Plan/Spec 模式支持

**架构改进：**
- ✅ 项目目录结构优化
- ✅ 文件归档规范化
- ✅ 测试分类整理
- ✅ 文档系统化

**技术栈：**
- 后端：FastAPI + Uvicorn
- 前端：Vue 3 + Element Plus + Pinia
- 通信：REST API + WebSocket
- LLM：Kimi API
- 协议：MCP (Model Context Protocol)

### v1.0.0 - 初始版本

- ✅ 核心 Agent 架构实现
- ✅ 意图解析与任务分解
- ✅ 工具系统
- ✅ 终端可视化
- ✅ 流式输出

## 注意事项

- 若未配置 API Key，程序启动时会直接输出：`需要 kimi_api_key`
- 通用查询工具会调用真实 LLM API，可能产生费用
- 流式输出需要稳定的网络连接
- MCP 服务需要正确配置服务器地址和端口

## 联系方式

- 项目仓库：https://github.com/Red-Unknown/flood_decision_agent
- 问题反馈：请在 GitHub 提交 Issue

## 许可证

本项目仅供科研和学习使用。
