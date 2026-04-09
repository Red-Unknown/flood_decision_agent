import { test, expect } from '@playwright/test'

/**
 * WebSocket 调试测试
 */

test.describe('WebSocket 调试', () => {
  test.setTimeout(60000)

  test('检查 WebSocket 消息流', async ({ page }) => {
    // 启用详细的控制台日志
    page.on('console', msg => {
      console.log(`[Browser Console] ${msg.type()}: ${msg.text()}`)
    })

    page.on('pageerror', error => {
      console.error(`[Browser Error] ${error.message}`)
    })

    // 收集 WebSocket 消息
    const wsMessages = []

    page.on('websocket', ws => {
      console.log(`[WebSocket] 连接: ${ws.url()}`)

      ws.on('framereceived', data => {
        console.log(`[WebSocket] 收到帧: ${data.payload.substring(0, 100)}`)
        try {
          const message = JSON.parse(data.payload)
          wsMessages.push({
            type: message.type,
            timestamp: Date.now(),
            data: message
          })
        } catch (e) {
          console.log(`[WebSocket] 非 JSON 数据: ${data.payload}`)
        }
      })

      ws.on('framesent', data => {
        console.log(`[WebSocket] 发送帧: ${data.payload}`)
      })

      ws.on('close', () => {
        console.log('[WebSocket] 连接关闭')
      })

      ws.on('error', error => {
        console.error(`[WebSocket] 错误: ${error}`)
      })
    })

    // 打开页面
    console.log('[Test] 打开页面...')
    await page.goto('http://localhost:3001')
    await page.waitForTimeout(3000)

    // 在浏览器中执行脚本，监听 window 的 WebSocket
    await page.evaluate(() => {
      // 保存原始的 WebSocket
      const OriginalWebSocket = window.WebSocket

      // 重写 WebSocket
      window.WebSocket = function(url, protocols) {
        console.log(`[WebSocket Hook] 创建连接: ${url}`)
        const ws = new OriginalWebSocket(url, protocols)

        const originalSend = ws.send.bind(ws)
        ws.send = function(data) {
          console.log(`[WebSocket Hook] 发送: ${data}`)
          return originalSend(data)
        }

        ws.addEventListener('message', (event) => {
          console.log(`[WebSocket Hook] 收到: ${event.data.substring(0, 200)}`)
        })

        ws.addEventListener('error', (error) => {
          console.error(`[WebSocket Hook] 错误:`, error)
        })

        ws.addEventListener('close', (event) => {
          console.log(`[WebSocket Hook] 关闭: code=${event.code}, reason=${event.reason}`)
        })

        return ws
      }
      window.WebSocket.prototype = OriginalWebSocket.prototype
    })

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

    console.log('[Test] 等待 30 秒...')
    await page.waitForTimeout(30000)

    // 分析结果
    console.log('\n========== WebSocket 消息统计 ==========')
    console.log(`总共收到 ${wsMessages.length} 条消息`)

    wsMessages.forEach((msg, index) => {
      console.log(`[${index + 1}] ${msg.type}`)
    })

    // 检查关键消息
    const hasAssistantMessage = wsMessages.some(m => m.type === 'assistant_message')
    const hasExecutionComplete = wsMessages.some(m => m.type === 'execution_complete')

    console.log('\n关键事件:')
    console.log(`  - assistant_message: ${hasAssistantMessage ? '✓' : '✗'}`)
    console.log(`  - execution_complete: ${hasExecutionComplete ? '✓' : '✗'}`)

    // 截图
    await page.screenshot({ path: 'test-results/debug-websocket.png', fullPage: true })

    console.log('\n========== 测试完成 ==========')
  })
})
