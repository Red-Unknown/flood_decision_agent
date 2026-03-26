### REST API

| 方法     | 路径                               | 说明          |
| ------ | -------------------------------- | ----------- |
| GET    | /api/health                      | 健康检查        |
| GET    | /api/conversations               | 获取对话列表      |
| POST   | /api/conversations               | 创建新对话       |
| GET    | /api/conversations/{id}          | 获取对话详情      |
| DELETE | /api/conversations/{id}          | 删除对话        |
| POST   | /api/chat                        | 发送消息（SSE流式） |
| GET    | /api/conversations/{id}/messages | 获取消息历史      |

### WebSocket API

```
WS /ws/chat/{conversation_id}
```
