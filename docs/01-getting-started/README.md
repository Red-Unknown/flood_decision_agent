# 快速入门

欢迎使用防汛调度智能决策 Agent 系统！本指南将帮助您快速上手。

## 前置要求

- Python 3.11+
- Conda（推荐）或 pip
- Node.js 18+（用于前端开发）
- Kimi API Key

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/Red-Unknown/flood_decision_agent.git
cd flood_decision_agent
```

### 2. 创建 Conda 环境

```powershell
# 使用提供的脚本一键安装
.\scripts\setup_env.ps1

# 或手动创建
conda env create -f environment.yml
conda activate intelligent_decision
```

### 3. 安装依赖

```powershell
# Python 依赖
pip install -r requirements.txt

# 前端依赖（如需开发前端）
cd web/frontend
npm install
```

### 4. 配置 API Key

```powershell
# 临时设置（当前会话有效）
$env:KIMI_API_KEY="your_api_key"

# 永久设置
setx KIMI_API_KEY "your_api_key"
```

## 快速开始

### 方式一：运行命令行示例

```powershell
# 运行可视化演示
python examples\run_visualized_demo.py 1

# 运行交互式聊天
python examples\interactive_chat.py
```

### 方式二：启动 Web 界面

```powershell
# 启动后端
python -m web.backend.main

# 新终端启动前端
cd web/frontend
npm run dev
```

访问 http://localhost:3000 开始使用。

## 第一个决策任务

### 示例 1：洪水预警分析

```python
from flood_decision_agent.app import VisualizedPipeline

async def main():
    pipeline = VisualizedPipeline()
    result = await pipeline.run("分析金坛地区的洪水风险")
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### 示例 2：水库调度

```python
from flood_decision_agent.app import VisualizedPipeline

async def main():
    pipeline = VisualizedPipeline()
    result = await pipeline.run("制定太浦河水库的调度方案")
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## 运行测试

```powershell
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/agents/ -v

# 运行覆盖率测试
pytest tests/ --cov=src/flood_decision_agent --cov-report=html
```

## 常见问题

### Q: 如何查看 API Key 是否配置成功？

```python
import os
print(os.getenv('KIMI_API_KEY'))
# 如果输出 None 或空字符串，说明未配置成功
```

### Q: 前端无法连接后端？

检查后端是否在运行：
```powershell
# 后端默认运行在 http://localhost:8000
curl http://localhost:8000/api/health
```

### Q: MCP 服务启动失败？

检查 MCP 配置文件：
```powershell
# 查看 MCP 服务器配置
cat src/flood_decision_agent/mcp/configs/mcp_servers.json
```

## 下一步

- 阅读 [架构文档](../02-architecture/system-overview/architecture-summary.md) 了解系统架构
- 查看 [开发者指南](../03-development/guides/developer-guide.md) 学习开发最佳实践
- 参考 [API 参考](../04-api-reference/chain-generation-api.md) 使用编程接口
- 浏览 [示例代码](../../examples/) 学习更多使用场景

## 获取帮助

- 查看 [文档中心](README.md) 获取更多文档
- 在 GitHub 提交 [Issue](https://github.com/Red-Unknown/flood_decision_agent/issues)
- 查看 [项目 README](../../README.md) 了解项目概况
