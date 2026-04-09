# Plan/Spec 模式部署文档

## 概述

本文档描述 Plan/Spec 模式增强功能的部署步骤和配置要求。

## 系统要求

### 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|---------|---------|
| CPU | 4核 | 8核 |
| 内存 | 8GB | 16GB |
| 磁盘 | 50GB SSD | 100GB SSD |

### 软件要求

- Python 3.11+
- Conda 环境: `intelligent_decision`
- 依赖包: 见 `requirements.txt`

## 部署步骤

### 1. 环境准备

```bash
# 激活 Conda 环境
conda activate intelligent_decision

# 更新依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 必需
export KIMI_API_KEY="your-api-key"

# 可选配置
export MODE_DETECTOR_THRESHOLD_SIMPLE=50
export MODE_DETECTOR_THRESHOLD_PLAN=200
export CHECKPOINT_STORAGE_TYPE="memory"  # memory | file
export CHECKPOINT_TTL=3600  # 断点过期时间（秒）
```

### 3. 目录结构检查

确保以下目录存在：

```
.
├── plans/              # Plan 文档存储
├── .trae/specs/        # Spec 文档存储
├── checkpoints/        # 断点状态存储（如使用文件存储）
└── logs/               # 日志目录
```

### 4. 服务启动

```bash
# 启动后端服务
python -m web.backend.main

# 或使用脚本
.\scripts\start_server.ps1  # Windows
./scripts/start_server.sh    # Linux/Mac
```

## 配置参数

### 模式识别器配置

在 `configs/app.yaml` 中添加：

```yaml
mode_detector:
  thresholds:
    simple: 50      # 字符数阈值
    plan: 200       # 字符数阈值
  weights:
    technical: 1.5
    architecture: 2.0
    multi_goal: 1.3
```

### 断点接续配置

```yaml
checkpoint:
  storage_type: "memory"  # memory | file | redis
  ttl: 3600              # 过期时间（秒）
  auto_save_interval: 30 # 自动保存间隔（秒）
  max_checkpoints: 100   # 最大断点数
```

### 链路优化器配置

```yaml
optimizers:
  simple:
    reliability_threshold: 0.6
    max_alternatives: 1
  
  plan:
    reliability_threshold: 0.75
    max_alternatives: 3
    max_iterations: 2
```

## 验证部署

### 1. 健康检查

```bash
curl http://localhost:8000/api/health
```

预期响应：
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "features": ["mode_detection", "checkpoint", "cancel_handler"]
}
```

### 2. 模式识别测试

```bash
curl -X POST http://localhost:8000/api/mode/detect \
  -H "Content-Type: application/json" \
  -d '{"user_input": "设计一个洪水预警系统"}'
```

### 3. 断点接续测试

```bash
# 创建断点
curl -X POST http://localhost:8000/api/plans/test-plan/cancel \
  -H "Content-Type: application/json" \
  -d '{"reason": "manual_cancel", "preserve_state": true}'

# 恢复断点
curl -X POST http://localhost:8000/api/resume \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-session-id"}'
```

## 回滚方案

### 方案一：配置回滚

```bash
# 备份当前配置
cp configs/app.yaml configs/app.yaml.backup

# 恢复默认配置
cp configs/app.yaml.default configs/app.yaml

# 重启服务
python -m web.backend.main
```

### 方案二：版本回滚

```bash
# 回滚到上一版本
git checkout HEAD~1 -- src/flood_decision_agent/agents/decision_chain/

# 重启服务
python -m web.backend.main
```

### 方案三：功能开关

在 `configs/app.yaml` 中禁用新功能：

```yaml
features:
  mode_detection: false
  checkpoint_resumption: false
  cancel_handler: false
```

## 监控指标

### 关键指标

| 指标 | 说明 | 告警阈值 |
|------|------|---------|
| mode_detection_latency | 模式识别延迟 | > 100ms |
| checkpoint_save_success | 断点保存成功率 | < 99% |
| session_recovery_rate | 会话恢复成功率 | < 95% |

### 日志位置

```
logs/
├── app.log           # 应用日志
├── mode_detector.log # 模式识别日志
├── checkpoint.log    # 断点接续日志
└── api.log           # API 请求日志
```

## 故障排查

### 常见问题

#### 1. 模式识别不准确

**症状**: 简单问题被识别为 plan 模式

**排查**:
```bash
# 检查阈值配置
grep -A 5 "mode_detector" configs/app.yaml

# 查看识别日志
tail -f logs/mode_detector.log
```

**解决**: 调整 `thresholds.simple` 参数

#### 2. 断点无法恢复

**症状**: 恢复会话时返回 404

**排查**:
```bash
# 检查断点是否存在
curl http://localhost:8000/api/sessions/{session_id}/status

# 检查存储配置
grep -A 3 "checkpoint" configs/app.yaml
```

**解决**: 
- 检查 `checkpoint.ttl` 是否过短
- 确认存储类型配置正确

#### 3. 取消命令无效

**症状**: 发送"取消"后任务继续执行

**排查**:
```bash
# 检查取消处理器日志
tail -f logs/app.log | grep -i cancel
```

**解决**: 确认 `CancelHandler` 已正确初始化

## 性能优化

### 1. 模式识别缓存

启用 LRU 缓存：

```python
# 在 mode_detector.py 中
from functools import lru_cache

@lru_cache(maxsize=1000)
def detect(user_input: str) -> str:
    ...
```

### 2. 断点存储优化

对于高并发场景，使用 Redis：

```yaml
checkpoint:
  storage_type: "redis"
  redis:
    host: "localhost"
    port: 6379
    db: 0
```

### 3. 异步处理

启用异步模式识别：

```python
# 在 generator.py 中
async def generate_with_mode(...):
    mode = await asyncio.to_thread(
        self.mode_detector.detect, user_input
    )
```

## 安全注意事项

1. **API 密钥保护**: 确保 `KIMI_API_KEY` 不暴露在日志中
2. **会话隔离**: 不同用户的断点数据应隔离存储
3. **输入验证**: 所有用户输入需经过验证和清理
4. **速率限制**: 对模式识别 API 添加速率限制

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.0.0 | 2026-03-26 | 初始版本，支持模式识别、断点接续、取消机制 |
