import { test, expect } from '@playwright/test'

/**
 * AI 消息显示诊断测试
 */

test.describe('AI 消息显示诊断', () => {
  test.setTimeout(120000)

  test('检查 AI 消息是否正确显示', async ({ page }) => {
    // 收集所有 WebSocket 消息
    const wsMessages = []

    // 监听 WebSocket
    page.on('websocket', ws => {
      console.log(`[WebSocket] 连接: ${ws.url()}`)

      ws.on('framereceived', data => {
        try {
          const message = JSON.parse(data.payload)
          console.log(`[WebSocket] 收到: ${message.type}`)
          wsMessages.push(message)
        } catch (e) {
          console.log(`[WebSocket] 收到(非JSON): ${data.payload}`)
        }
      })
    })

    // 打开页面
    console.log('[Test] 打开页面...')
    await page.goto('http://localhost:3001')
    await page.waitForLoadState('networkidle')

    // 等待页面加载完成
    await page.waitForTimeout(2000)

    // 输入测试消息
    const testInput = '搜索关于洪水预警的最新信息'
    console.log(`[Test] 输入: ${testInput}`)

    // 找到输入框并输入
    const input = page.locator('.chat-input textarea, [placeholder*="输入"], .el-textarea__inner').first()
    await input.waitFor({ state: 'visible', timeout: 10000 })
    await input.fill(testInput)

    // 点击发送按钮
    const sendButton = page.locator('.send-btn, button:has-text("发送"), .el-button:has(.el-icon-s-promotion)').first()
    await sendButton.click()

    console.log('[Test] 等待响应...')

    // 等待一段时间让决策链执行
    await page.waitForTimeout(30000)

    // 分析结果
    console.log('\n========== WebSocket 消息分析 ==========')
    console.log(`总共收到 ${wsMessages.length} 条消息`)

    const messageTypes = wsMessages.map(m => m.type)
    console.log('消息类型:', messageTypes)

    // 检查关键消息
    const hasAssistantMessage = messageTypes.includes('assistant_message')
    const hasExecutionComplete = messageTypes.includes('execution_complete')

    console.log('\n关键事件:')
    console.log(`  - assistant_message: ${hasAssistantMessage ? '✓ 收到' : '✗ 未收到'}`)
    console.log(`  - execution_complete: ${hasExecutionComplete ? '✓ 收到' : '✗ 未收到'}`)

    if (hasAssistantMessage) {
      const assistantMsg = wsMessages.find(m => m.type === 'assistant_message')
      console.log('\nassistant_message 内容长度:', assistantMsg.content?.length || 0)
      console.log('内容预览:', assistantMsg.content?.substring(0, 200) + '...')
    }

    // 检查页面上的 AI 消息
    console.log('\n========== 页面元素分析 ==========')

    // 截图
    await page.screenshot({ path: 'test-results/diagnose-ai-message.png', fullPage: true })

    // 检查消息列表
    const messages = await page.locator('.message, .chat-message, [class*="message"]').count()
    console.log(`页面上的消息数量: ${messages}`)

    // 检查 AI 回复内容
    const assistantMessages = await page.locator('.message-assistant, .assistant-message, [class*="assistant"]').count()
    console.log(`AI 消息数量: ${assistantMessages}`)

    // 获取页面文本内容
    const pageText = await page.textContent('body')
    const hasTaskExecution = pageText.includes('任务执行过程')
    const hasExecutionTimeline = pageText.includes('执行过程时间线')

    console.log(`\n页面元素检查:`)
    console.log(`  - 任务执行过程: ${hasTaskExecution ? '✓ 显示' : '✗ 未显示'}`)
    console.log(`  - 执行过程时间线: ${hasExecutionTimeline ? '✓ 显示' : '✗ 未显示'}`)

    // 断言
    expect(hasAssistantMessage, '应该收到 assistant_message').toBe(true)
    expect(hasExecutionComplete, '应该收到 execution_complete').toBe(true)

    console.log('\n========== 测试完成 ==========')
  })
})
