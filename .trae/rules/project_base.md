# 项目规则（flood_decision_agent）

## 语言
- 所有回答与 Markdown 文档均使用中文

## 路径
- 代码中所有文件读写路径使用相对路径（基于项目根目录运行）

## 运行门控
- 所有示例、调试与正式运行入口在启动时必须检查环境变量 KIMI_API_KEY
- 若未配置，启动时直接输出 `需要kimi_api_key` 并以退出码 1 结束

## 环境与命令
- Conda 环境名：intelligent_decision
- Python 版本：3.11
- 推荐初始化：运行 `.\scripts\setup_env.ps1`
- 运行示例：`python .\examples\quick_start.py`
- 运行调试：`python .\debug\run_debug.py`

## 代码规范
- 代码风格：PEP8
- 提交前：必须通过 pre-commit（black/isort/flake8）
- 单元测试：pytest，覆盖率目标 ≥80%

## 调用时机
- 新增依赖或修改环境：同步更新 requirements.txt 与 environment.yml，并更新 setup_env.ps1 的流程（如需）
- 新增/变更入口脚本：必须加入 KIMI_API_KEY 门控
- 修改核心算法或 Agent 行为：必须补充/更新 tests 并确保 pytest 通过

## 测试文件
- 所有测试文件均放在 `./tests` 目录下
- 测试文件名格式：`test_*.py`
- 在`./tests` 目录下，整理测试文件到文件夹中
- 测试采用统一入口 `./tests/run_tests.py`，获取真实api_key后运行

