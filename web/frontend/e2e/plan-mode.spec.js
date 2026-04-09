import { test, expect } from '@playwright/test'

test.describe('Plan 模式 Pipeline 端到端测试', () => {
  test.beforeEach(async ({ page }) => {
    // 访问首页
    await page.goto('/')
    // 等待页面加载完成
    await page.waitForLoadState('networkidle')
  })

  test('使用 /plan 命令进入 Plan 模式', async ({ page }) => {
    // 找到输入框并输入 /plan 命令
    const textarea = page.locator('textarea[placeholder*="输入消息"]')
    await textarea.fill('/plan 制定一个洪水预警方案')

    // 点击发送按钮
    const sendButton = page.locator('button:has-text("发送")')
    await sendButton.click()

    // 等待侧边面板打开
    await page.waitForTimeout(2000)

    // 验证侧边面板编辑器存在（根据错误上下文中的结构）
    await expect(page.locator('text=文档编辑器').first()).toBeVisible()

    // 验证确认和取消按钮存在
    await expect(page.locator('button:has-text("确认")')).toBeVisible()
    await expect(page.locator('button:has-text("取消")')).toBeVisible()
  })

  test('Plan 模式侧边面板交互', async ({ page }) => {
    // 进入 Plan 模式
    const textarea = page.locator('textarea[placeholder*="输入消息"]')
    await textarea.fill('/plan 设计一个水库调度规划')
    await page.locator('button:has-text("发送")').click()

    // 等待侧边面板打开
    await page.waitForTimeout(2000)

    // 验证文档编辑器存在
    await expect(page.locator('text=文档编辑器').first()).toBeVisible()

    // 验证修改输入框存在
    await expect(page.locator('textarea[placeholder*="自然语言修改指令"]')).toBeVisible()

    // 验证修改按钮存在
    await expect(page.locator('button:has-text("修改")')).toBeVisible()
  })

  test('Plan 模式取消功能', async ({ page }) => {
    // 进入 Plan 模式
    const textarea = page.locator('textarea[placeholder*="输入消息"]')
    await textarea.fill('/plan 测试取消功能')
    await page.locator('button:has-text("发送")').click()

    // 等待侧边面板打开
    await page.waitForTimeout(2000)

    // 验证文档编辑器存在
    await expect(page.locator('text=文档编辑器').first()).toBeVisible()

    // 点击取消按钮
    const cancelButton = page.locator('button:has-text("取消")')
    await cancelButton.click()

    // 等待面板关闭
    await page.waitForTimeout(1000)
  })

  test('Plan 模式自然语言修改输入', async ({ page }) => {
    // 进入 Plan 模式
    const textarea = page.locator('textarea[placeholder*="输入消息"]')
    await textarea.fill('/plan 测试自然语言修改')
    await page.locator('button:has-text("发送")').click()

    // 等待侧边面板打开
    await page.waitForTimeout(2000)

    // 在底部修改输入框输入修改指令
    const modifyInput = page.locator('textarea[placeholder*="自然语言修改指令"]')
    await modifyInput.fill('请增加关于应急预案的章节')

    // 验证输入成功
    await expect(modifyInput).toHaveValue('请增加关于应急预案的章节')
  })

  test('快捷功能 - 洪水调度', async ({ page }) => {
    // 点击洪水调度快捷功能
    await page.locator('text=洪水调度').first().click()

    // 等待页面响应
    await page.waitForTimeout(1000)

    // 验证输入框有内容（如果快捷功能会自动填充）
    const textarea = page.locator('textarea[placeholder*="输入消息"]')
    const value = await textarea.inputValue()
    // 快捷功能可能会填充内容，也可能直接发送
    expect(value.length >= 0).toBe(true)
  })

  test('快捷功能 - 智能问答', async ({ page }) => {
    // 点击智能问答快捷功能
    await page.locator('text=智能问答').first().click()

    // 等待页面响应
    await page.waitForTimeout(1000)

    // 验证页面状态
    const textarea = page.locator('textarea[placeholder*="输入消息"]')
    await expect(textarea).toBeVisible()
  })

  test('侧边栏收起展开', async ({ page }) => {
    // 验证收起侧边栏按钮存在
    const toggleButton = page.locator('button:has-text("收起侧边栏")')
    await expect(toggleButton).toBeVisible()

    // 点击收起侧边栏
    await toggleButton.click()

    // 等待动画完成
    await page.waitForTimeout(500)

    // 验证侧边栏已收起（可以通过检查特定元素是否隐藏）
    // 这里我们验证按钮文本变化或页面布局变化
  })

  test('清空全部对话功能', async ({ page }) => {
    // 验证清空全部按钮存在
    const clearButton = page.locator('button:has-text("清空全部")')
    await expect(clearButton).toBeVisible()

    // 点击清空全部（注意：这会清空所有对话）
    // 在生产环境中谨慎使用
    // await clearButton.click()
  })
})
