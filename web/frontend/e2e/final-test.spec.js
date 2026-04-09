import { test, expect } from '@playwright/test'

test.describe('最终验证测试', () => {
  test.setTimeout(120000)

  test('验证 AI 消息正确显示', async ({ page }) => {
    const wsMessages = []

    page.on('websocket', ws => {
      ws.on('framereceived', data => {
        try {
          const message = JSON.parse(data.payload)
          wsMessages.push({ type: message.type, time: Date.now() })
        } catch (e) {}
      })
    })

    await page.goto('http://localhost:3001')
    await page.waitForTimeout(2000)

    // 输入并发送
    const input = page.locator('.chat-input textarea, [placeholder*="输入"], .el-textarea__inner').first()
    await input.waitFor({ state: 'visible', timeout: 10000 })
    await input.fill('调研当前金坛降雨情况')
    
    const sendButton = page.locator('.send-btn, button:has-text("发送"), .el-button:has(.el-icon-s-promotion)').first()
    await sendButton.click()

    // 等待 35 秒
    await page.waitForTimeout(35000)

    // 分析结果
    console.log('\n========== WebSocket 消息统计 ==========')
    console.log(`总共收到 ${wsMessages.length} 条消息`)
    
    wsMessages.forEach((msg, i) => {
      console.log(`[${i + 1}] ${msg.type}`)
    })

    const hasAssistantMessage = wsMessages.some(m => m.type === 'assistant_message')
    const hasExecutionComplete = wsMessages.some(m => m.type === 'execution_complete')

    console.log('\n关键事件:')
    console.log(`  - assistant_message: ${hasAssistantMessage ? '✓' : '✗'}`)
    console.log(`  - execution_complete: ${hasExecutionComplete ? '✓' : '✗'}`)

    // 截图
    await page.screenshot({ path: 'test-results/final-test.png', fullPage: true })

    // 检查页面上的 AI 消息
    const assistantMessages = await page.locator('.message-assistant, .assistant-message, [class*="assistant"]').count()
    console.log(`\n页面上的 AI 消息数量: ${assistantMessages}`)

    // 断言
    expect(hasAssistantMessage, '应该收到 assistant_message').toBe(true)
    expect(hasExecutionComplete, '应该收到 execution_complete').toBe(true)
  })
})
