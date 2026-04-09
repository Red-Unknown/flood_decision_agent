/**
 * WebSocket 前端消息接收测试
 * 用于验证前端是否能正确接收 assistant_message 等事件
 */

const WS_URL = 'ws://localhost:8001/ws/chat/test_frontend_2024';

console.log('============================================================');
console.log('WebSocket 前端消息接收测试');
console.log('============================================================');

const ws = new WebSocket(WS_URL);

// 存储接收到的消息
const receivedMessages = [];

ws.onopen = () => {
  console.log('[WebSocket] 连接成功');

  // 发送测试消息
  const testMessage = {
    type: 'chat_message',
    content: '搜索关于洪水预警的最新信息',
    timestamp: Date.now() / 1000
  };

  console.log('[WebSocket] 发送消息:', testMessage.content);
  ws.send(JSON.stringify(testMessage));
};

ws.onmessage = (event) => {
  try {
    const message = JSON.parse(event.data);
    receivedMessages.push(message);
    console.log(`[WebSocket] 收到消息 [${receivedMessages.length}]: type=${message.type}`);

    // 检查是否是 assistant_message
    if (message.type === 'assistant_message') {
      console.log('[WebSocket] ✓ 收到 assistant_message!');
      console.log('[WebSocket] 内容长度:', message.content?.length || 0);
      console.log('[WebSocket] 内容预览:', message.content?.substring(0, 100) + '...');
    }

    // 检查是否是 execution_complete
    if (message.type === 'execution_complete') {
      console.log('[WebSocket] ✓ 收到 execution_complete, success=', message.success);
    }

  } catch (error) {
    console.error('[WebSocket] 解析消息失败:', error);
  }
};

ws.onerror = (error) => {
  console.error('[WebSocket] 错误:', error);
};

ws.onclose = (event) => {
  console.log('[WebSocket] 连接关闭:', event.code, event.reason);

  // 打印总结
  console.log('\n============================================================');
  console.log('测试总结');
  console.log('============================================================');
  console.log('总共收到消息数:', receivedMessages.length);

  const messageTypes = receivedMessages.map(m => m.type);
  console.log('消息类型列表:', messageTypes);

  const hasAssistantMessage = messageTypes.includes('assistant_message');
  const hasExecutionComplete = messageTypes.includes('execution_complete');

  console.log('\n关键事件检查:');
  console.log('  - assistant_message:', hasAssistantMessage ? '✓ 收到' : '✗ 未收到');
  console.log('  - execution_complete:', hasExecutionComplete ? '✓ 收到' : '✗ 未收到');

  if (hasAssistantMessage) {
    const assistantMsg = receivedMessages.find(m => m.type === 'assistant_message');
    console.log('\nassistant_message 内容:');
    console.log(assistantMsg.content);
  }
};

// 30秒后自动关闭连接
setTimeout(() => {
  console.log('\n[WebSocket] 30秒超时，关闭连接');
  ws.close();
}, 30000);
