# 贡献指南

## Git 提交规范

本项目使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范。

### 提交格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

| 类型 | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修复bug |
| `docs` | 文档更新 |
| `style` | 代码格式（不影响代码运行的变动） |
| `refactor` | 重构（既不是新增功能，也不是修改bug） |
| `perf` | 性能优化 |
| `test` | 增加测试 |
| `chore` | 构建过程或辅助工具的变动 |
| `ci` | CI/CD 相关变动 |

### Scope 范围

| 范围 | 说明 |
|------|------|
| `agent` | Agent 相关 |
| `tools` | 工具系统 |
| `core` | 核心模块 |
| `viz` | 可视化 |
| `docs` | 文档 |
| `test` | 测试 |

### 示例

```bash
# 新功能
feat(agent): 添加总结智能体 SummarizerAgent

# 修复bug
fix(tools): 修复工具注册表不一致问题

# 文档更新
docs(readme): 更新项目进展和演示方式

# 重构
refactor(core): 优化消息传递机制
```

## 分支管理

- `main`: 主分支，稳定版本
- `develop`: 开发分支
- `feature/*`: 功能分支
- `fix/*`: 修复分支

## 提交前检查

```bash
# 运行测试
pytest

# 代码格式化
black src/
isort src/

# 代码检查
flake8 src/
```
