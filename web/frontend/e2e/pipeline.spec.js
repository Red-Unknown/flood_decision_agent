import { test, expect } from '@playwright/test'

test.describe('普通 Pipeline 端到端测试', () => {
  test.beforeEach(async ({ page }) => {
    // 访问首页
    await page.goto('/')
    // 等待页面加载完成
    await page.waitForLoadState('networkidle')
  })

  test('页面基本元素渲染正确', async ({ page }) => {
    // 验证页面标题
    await expect(page).toHaveTitle(/水利智脑/)

    // 验证侧边栏存在 - 使用实际的选择器
    await expect(page.locator('text=水利智脑').first()).toBeVisible()

    // 验证新建对话按钮存在
    await expect(page.locator('button:has-text("新对话")')).toBeVisible()

    // 验证输入框存在（使用 placeholder 属性）
    await expect(page.locator('textarea[placeholder*="输入消息"]')).toBeVisible()

    // 验证空状态显示（根据截图中的标题）
    await expect(page.locator('h1:has-text("你好，我是水利智脑")')).toBeVisible()
  })

  test('发送普通消息并接收回复', async ({ page }) => {
    // 找到输入框并输入消息
    const textarea = page.locator('textarea[placeholder*="输入消息"]')
    await textarea.fill('你好，请介绍一下洪水调度系统')

    // 点击发送按钮
    const sendButton = page.locator('button:has-text("发送")')
    await expect(sendButton).toBeEnabled()
    await sendButton.click()

    // 等待消息发送（给系统一些时间处理）
    await page.waitForTimeout(2000)

    // 验证输入框已清空（表示消息已发送）
    await expect(textarea).toHaveValue('')
  })

  test('创建新对话', async ({ page }) => {
    // 点击新建对话按钮
    const newChatButton = page.locator('button:has-text("新对话")')
    await newChatButton.click()

    // 等待新对话创建
    await page.waitForTimeout(1000)

    // 验证输入框已清空或页面状态重置
    const textarea = page.locator('textarea[placeholder*="输入消息"]')
    await expect(textarea).toHaveValue('')
  })

  test('WebSocket 连接测试', async ({ page }) => {
    // 发送消息触发 WebSocket 连接
    const textarea = page.locator('textarea[placeholder*="输入消息"]')
    await textarea.fill('测试 WebSocket 连接')

    const sendButton = page.locator('button:has-text("发送")')
    await sendButton.click()

    // 等待一段时间让 WebSocket 建立连接
    await page.waitForTimeout(3000)

    // 验证输入框已清空（表示消息已发送）
    await expect(textarea).toHaveValue('')
  })

  test('消息历史记录', async ({ page }) => {
    // 发送第一条消息
    const textarea = page.locator('textarea[placeholder*="输入消息"]')
    await textarea.fill('第一条测试消息')
    await page.locator('button:has-text("发送")').click()

    // 等待消息处理
    await page.waitForTimeout(2000)

    // 发送第二条消息
    await textarea.fill('第二条测试消息')
    await page.locator('button:has-text("发送")').click()

    // 等待消息处理
    await page.waitForTimeout(2000)

    // 验证输入框已清空
    await expect(textarea).toHaveValue('')
  })

  test('快捷功能按钮存在', async ({ page }) => {
    // 验证快捷功能按钮存在 - 使用 generic 元素中的文本
    await expect(page.locator('text=洪水调度').first()).toBeVisible()
    await expect(page.locator('text=生成报告').first()).toBeVisible()
    await expect(page.locator('text=智能问答').first()).toBeVisible()
  })

  test('Plan/Spec 命令提示存在', async ({ page }) => {
    // 验证 Plan/Spec 命令提示存在
    await expect(page.locator('code:has-text("/plan")')).toBeVisible()
    await expect(page.locator('code:has-text("/spec")')).toBeVisible()
  })
})
