# 测试目录结构

本目录存放所有测试代码，采用垂直结构组织。

## 目录结构

```
tests/
├── api/              # API相关测试
│   ├── comprehensive_api_test.py
│   ├── test_all_apis.py
│   ├── test_chain_generation_api.py
│   ├── test_frontend_apis.py
│   ├── test_list_tools.py
│   └── test_new_apis.py
├── agents/           # Agent相关测试
├── core/             # 核心模块测试
├── data/             # 测试数据文件
├── debug/            # 调试脚本
│   ├── debug_mcp_config.py
│   ├── debug_mcp_connection.py
│   └── debug_rainfall_tools.py
├── e2e/              # 端到端测试
├── evaluation/       # 评估相关测试
├── integration/      # 集成测试
├── mcp/              # MCP相关测试
├── output/           # 测试输出文件
├── plan/             # Plan模式测试
├── scripts/          # 测试辅助脚本
├── unit/             # 单元测试
├── websocket/        # WebSocket测试
│   ├── test_debug_websocket.py
│   └── test_websocket_live.py
├── conftest.py       # pytest配置
└── README.md         # 本文件
```

## 约定

- 本目录为 Python 包，各子目录需放置 `__init__.py`
- pytest 覆盖率以核心模块为准（目标 ≥80%）
- 测试文件命名规范：`test_*.py`
- 根目录下仅保留 `conftest.py`、`README.md` 和 `__init__.py`
