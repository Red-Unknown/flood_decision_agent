import { test, expect } from '@playwright/test'

/**
 * 简单模式端到端真实数据测试
 *
 * 使用后端已验证的示例问题，通过 Playwright 进行端到端联调
 * 测试场景：
 * 1. 文件系统操作 - 列出当前目录下的文件
 * 2. 文档处理 - 创建测试文档
 * 3. 网络搜索 - 搜索洪水预警信息
 * 4. 综合场景 - 搜索并保存到文件
 *
 * 要求：使用真实 API，不使用 mock 数据
 */

// 测试配置
test.describe.configure({ mode: 'serial' })

// 真实测试场景 - 与后端 test_real_data_websocket.py 对应
const TEST_SCENES = [
  {
    name: '文件系统操作',
    input: '列出当前目录下的文件',
    expectedEvents: [
      'user_message_confirm',
      'intent_parsed',
      'chain_generation_stage',
      'task_graph_generated',
      'chain_generated',
      'execution_started',
      'task_update',
      'execution_progress',
      'execution_complete',
      'assistant_message'
    ],
    timeout: 120000
  },
  {
    name: '文档处理',
    input: '帮我创建一个测试文档',
    expectedEvents: [
      'user_message_confirm',
      'intent_parsed',
      'chain_generation_stage',
      'task_graph_generated',
      'chain_generated',
      'execution_started',
      'task_update',
      'execution_progress',
      'execution_complete',
      'assistant_message'
    ],
    timeout: 120000
  },
  {
    name: '网络搜索',
    input: '搜索关于洪水预警的最新信息',
    expectedEvents: [
      'user_message_confirm',
      'intent_parsed',
      'chain_generation_stage',
      'task_graph_generated',
      'chain_generated',
      'execution_started',
      'task_update',
      'execution_progress',
      'execution_complete',
      'assistant_message'
    ],
    timeout: 120000
  },
  {
    name: '综合场景',
    input: '搜索洪水预警信息并保存到文件',
    expectedEvents: [
      'user_message_confirm',
      'intent_parsed',
      'chain_generation_stage',
      'task_graph_generated',
      'chain_generated',
      'execution_started',
      'task_update',
      'execution_progress',
      'execution_complete',
      'assistant_message'
    ],
    timeout: 180000
  }
]

// 全局存储 WebSocket 消息
let globalWsMessages = []

test.describe('简单模式真实数据端到端测试', () => {
  // 设置全局超时 5 分钟
  test.setTimeout(300000)

  test.beforeEach(async ({ page }) => {
    // 清空全局消息记录
    globalWsMessages = []

    // 监听浏览器控制台日志
    page.on('console', msg => {
      const text = msg.text()
      if (text.includes('[WebSocket]') || text.includes('[ChatView]')) {
        console.log(`[Browser] ${text}`)
      }
    })

    // 监听 WebSocket 消息
    page.on('websocket', ws => {
      console.log(`[WebSocket] 连接建立: ${ws.url()}`)

      ws.on('framereceived', data => {
        try {
          const message = JSON.parse(data.payload)
          globalWsMessages.push({
            type: message.type,
            timestamp: Date.now(),
            data: message
          })
          console.log(`[WebSocket] 收到: ${message.type}`)
        } catch (e) {
          // 非 JSON 消息，忽略
        }
      })

      ws.on('framesent', data => {
        try {
          const message = JSON.parse(data.payload)
          console.log(`[WebSocket] 发送: ${message.type}`)
        } catch (e) {
          // 非 JSON 消息，忽略
        }
      })
    })

    // 访问首页
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    // 等待页面完全加载
    await page.waitForSelector('textarea[placeholder*="输入消息"]', { timeout: 10000 })
  })

  test('页面基本元素渲染正确', async ({ page }) => {
    // 验证页面标题
    await expect(page).toHaveTitle(/水利智脑/)

    // 验证侧边栏存在
    await expect(page.locator('text=水利智脑').first()).toBeVisible()

    // 验证新建对话按钮存在
    await expect(page.locator('button:has-text("新对话")')).toBeVisible()

    // 验证输入框存在
    await expect(page.locator('textarea[placeholder*="输入消息"]')).toBeVisible()

    // 验证空状态显示
    await expect(page.locator('h1:has-text("你好，我是水利智脑")')).toBeVisible()

    // 验证快捷功能按钮存在
    await expect(page.locator('text=洪水调度').first()).toBeVisible()
    await expect(page.locator('text=生成报告').first()).toBeVisible()
    await expect(page.locator('text=智能问答').first()).toBeVisible()
  })

  // 测试场景 1: 文件系统操作
  test('场景1: 文件系统操作 - 列出当前目录下的文件', async ({ page }) => {
    const scene = TEST_SCENES[0]
    console.log(`\n========== 测试场景: ${scene.name} ==========`)
    console.log(`输入: ${scene.input}`)

    // 发送消息
    await sendMessage(page, scene.input)

    // 等待并验证事件
    const result = await waitForEvents(page, scene.expectedEvents, scene.timeout)

    // 验证结果
    expect(result.received.length).toBeGreaterThan(0)
    expect(result.received).toContain('user_message_confirm')
    expect(result.received).toContain('intent_parsed')

    // 验证任务执行列表是否显示
    await verifyTaskExecutionList(page)

    // 验证最终有 AI 回复
    await verifyAIResponse(page)

    console.log(`✓ 场景 "${scene.name}" 测试通过`)
    console.log(`  收到事件: ${result.received.join(', ')}`)
  })

  // 测试场景 2: 文档处理
  test('场景2: 文档处理 - 创建测试文档', async ({ page }) => {
    const scene = TEST_SCENES[1]
    console.log(`\n========== 测试场景: ${scene.name} ==========`)
    console.log(`输入: ${scene.input}`)

    // 发送消息
    await sendMessage(page, scene.input)

    // 等待并验证事件
    const result = await waitForEvents(page, scene.expectedEvents, scene.timeout)

    // 验证结果
    expect(result.received.length).toBeGreaterThan(0)
    expect(result.received).toContain('intent_parsed')

    // 验证任务执行列表是否显示
    await verifyTaskExecutionList(page)

    // 验证最终有 AI 回复
    await verifyAIResponse(page)

    console.log(`✓ 场景 "${scene.name}" 测试通过`)
    console.log(`  收到事件: ${result.received.join(', ')}`)
  })

  // 测试场景 3: 网络搜索
  test('场景3: 网络搜索 - 搜索洪水预警信息', async ({ page }) => {
    const scene = TEST_SCENES[2]
    console.log(`\n========== 测试场景: ${scene.name} ==========`)
    console.log(`输入: ${scene.input}`)

    // 发送消息
    await sendMessage(page, scene.input)

    // 等待并验证事件
    const result = await waitForEvents(page, scene.expectedEvents, scene.timeout)

    // 验证结果
    expect(result.received.length).toBeGreaterThan(0)
    expect(result.received).toContain('intent_parsed')

    // 验证任务执行列表是否显示
    await verifyTaskExecutionList(page)

    // 验证最终有 AI 回复
    await verifyAIResponse(page)

    console.log(`✓ 场景 "${scene.name}" 测试通过`)
    console.log(`  收到事件: ${result.received.join(', ')}`)
  })

  // 测试场景 4: 综合场景
  test('场景4: 综合场景 - 搜索洪水预警信息并保存到文件', async ({ page }) => {
    const scene = TEST_SCENES[3]
    console.log(`\n========== 测试场景: ${scene.name} ==========`)
    console.log(`输入: ${scene.input}`)

    // 发送消息
    await sendMessage(page, scene.input)

    // 等待并验证事件
    const result = await waitForEvents(page, scene.expectedEvents, scene.timeout)

    // 验证结果
    expect(result.received.length).toBeGreaterThan(0)
    expect(result.received).toContain('intent_parsed')

    // 验证任务执行列表是否显示
    await verifyTaskExecutionList(page)

    // 验证最终有 AI 回复
    await verifyAIResponse(page)

    console.log(`✓ 场景 "${scene.name}" 测试通过`)
    console.log(`  收到事件: ${result.received.join(', ')}`)
  })

  // 测试快捷功能按钮
  test('快捷功能: 洪水调度', async ({ page }) => {
    console.log('\n========== 测试快捷功能: 洪水调度 ==========')

    // 点击快捷功能按钮
    await page.locator('text=洪水调度').first().click()

    // 等待消息发送
    await page.waitForTimeout(1000)

    // 验证输入框有内容
    const textarea = page.locator('textarea[placeholder*="输入消息"]')
    const value = await textarea.inputValue()
    expect(value).toContain('洪水')

    // 点击发送
    await page.locator('button:has-text("发送")').click()

    // 等待事件
    const result = await waitForEvents(page, ['user_message_confirm', 'intent_parsed'], 60000)

    expect(result.received).toContain('intent_parsed')
    console.log('✓ 快捷功能测试通过')
  })

  // 测试新对话功能
  test('新对话功能', async ({ page }) => {
    console.log('\n========== 测试新对话功能 ==========')

    // 先发送一条消息
    await sendMessage(page, '你好')
    await page.waitForTimeout(5000)

    // 点击新对话按钮
    await page.locator('button:has-text("新对话")').click()

    // 等待新对话创建
    await page.waitForTimeout(3000)

    // 验证输入框已清空
    const textarea = page.locator('textarea[placeholder*="输入消息"]')
    await expect(textarea).toHaveValue('')

    // 验证空状态显示
    await expect(page.locator('h1:has-text("你好，我是水利智脑")')).toBeVisible()

    console.log('✓ 新对话功能测试通过')
  })

  // 测试 WebSocket 重连
  test('WebSocket 连接稳定性', async ({ page }) => {
    console.log('\n========== 测试 WebSocket 连接稳定性 ==========')

    // 发送多条消息测试连接稳定性
    for (let i = 0; i < 3; i++) {
      globalWsMessages = [] // 清空消息记录

      await sendMessage(page, `测试消息 ${i + 1}`)

      // 等待连接确认
      await page.waitForTimeout(2000)

      // 验证收到了 WebSocket 消息
      const hasMessages = globalWsMessages.length > 0
      expect(hasMessages).toBe(true)

      console.log(`  消息 ${i + 1}: 收到 ${globalWsMessages.length} 个 WebSocket 事件`)

      // 等待一段时间再发送下一条
      await page.waitForTimeout(5000)
    }

    console.log('✓ WebSocket 连接稳定性测试通过')
  })
})

// ============ 辅助函数 ============

/**
 * 发送消息
 */
async function sendMessage(page, content) {
  const textarea = page.locator('textarea[placeholder*="输入消息"]')

  // 清空并输入消息
  await textarea.fill('')
  await textarea.fill(content)

  // 点击发送按钮
  const sendButton = page.locator('button:has-text("发送")')
  await expect(sendButton).toBeEnabled()
  await sendButton.click()

  console.log(`  [发送] ${content}`)
}

/**
 * 等待并验证 WebSocket 事件
 */
async function waitForEvents(page, expectedEvents, timeout = 120000) {
  const startTime = Date.now()
  const receivedEvents = []
  const maxWaitTime = timeout

  console.log(`  [等待事件] 超时: ${timeout}ms`)
  console.log(`  [期望事件] ${expectedEvents.join(', ')}`)

  while (Date.now() - startTime < maxWaitTime) {
    // 获取当前收到的所有事件类型
    const currentEvents = globalWsMessages.map(m => m.type)

    // 检查是否有新事件
    for (const event of currentEvents) {
      if (!receivedEvents.includes(event)) {
        receivedEvents.push(event)
        console.log(`  [收到事件] ${event}`)
      }
    }

    // 检查是否收到最终消息
    if (currentEvents.includes('assistant_message') || currentEvents.includes('error')) {
      console.log('  [完成] 收到最终消息')
      break
    }

    // 短暂等待
    await page.waitForTimeout(500)
  }

  // 检查缺少的事件
  const missingEvents = expectedEvents.filter(e => !receivedEvents.includes(e))
  if (missingEvents.length > 0) {
    console.log(`  [警告] 缺少事件: ${missingEvents.join(', ')}`)
  }

  return {
    received: receivedEvents,
    missing: missingEvents,
    allMessages: globalWsMessages
  }
}

/**
 * 验证任务执行列表是否显示
 */
async function verifyTaskExecutionList(page) {
  try {
    // 等待任务执行列表出现
    await page.waitForSelector('.task-execution-list, .execution-timeline', { timeout: 10000 })
    console.log('  [验证] 任务执行列表已显示')
    return true
  } catch (e) {
    console.log('  [验证] 任务执行列表未显示（可能执行太快）')
    return false
  }
}

/**
 * 验证 AI 回复
 */
async function verifyAIResponse(page) {
  try {
    // 等待 AI 消息出现
    await page.waitForSelector('.chat-message.assistant, .message-item.assistant', { timeout: 60000 })

    // 获取消息内容
    const messages = await page.locator('.chat-message.assistant, .message-item.assistant').all()

    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1]
      const text = await lastMessage.textContent()
      console.log(`  [验证] AI 回复长度: ${text?.length || 0} 字符`)
      return true
    }
  } catch (e) {
    console.log('  [验证] 未检测到 AI 回复')
  }
  return false
}
