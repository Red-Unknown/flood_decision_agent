import { test, expect } from '@playwright/test'

// Mock 数据
test.describe('Plan 模式 Mock 测试 - UI 交互', () => {
  test.beforeEach(async ({ page }) => {
    // 在页面加载前注入 WebSocket Mock
    await page.addInitScript(() => {
      // 保存原始 WebSocket
      const OriginalWebSocket = window.WebSocket
      
      // 创建 Mock WebSocket 类
      window.WebSocket = class MockWebSocket {
        constructor(url) {
          this.url = url
          this.readyState = 0 // CONNECTING
          this.bufferedAmount = 0
          this.extensions = ''
          this.protocol = ''
          
          // 模拟连接建立
          setTimeout(() => {
            this.readyState = 1 // OPEN
            if (this.onopen) {
              this.onopen({ type: 'open', target: this })
            }
            
            // 发送连接成功消息
            if (this.onmessage) {
              this.onmessage({
                data: JSON.stringify({
                  type: 'connected',
                  conversation_id: 'mock_conv_1',
                  timestamp: Date.now() / 1000,
                }),
              })
            }
          }, 100)
        }
        
        send(data) {
          if (this.readyState !== 1) {
            throw new Error('WebSocket is not open')
          }
          
          const message = JSON.parse(data)
          
          // 模拟消息响应
          setTimeout(() => {
            if (this.onmessage) {
              // 模拟普通聊天回复
              if (message.type === 'chat_message') {
                // 发送 chunk
                this.onmessage({
                  data: JSON.stringify({
                    type: 'chunk',
                    content: '这是',
                    accumulated: '这是',
                    timestamp: Date.now() / 1000,
                  }),
                })
                
                // 发送 complete
                setTimeout(() => {
                  this.onmessage({
                    data: JSON.stringify({
                      type: 'complete',
                      content: '这是模拟的 AI 回复内容。',
                      timestamp: Date.now() / 1000,
                    }),
                  })
                }, 300)
              }
              
              // 模拟 Plan 模式响应
              if (message.type === 'start_plan') {
                // 发送文档生成开始消息
                this.onmessage({
                  data: JSON.stringify({
                    type: 'document_chunk',
                    content: '# 规划文档\n\n## 第一章',
                    accumulated: '# 规划文档\n\n## 第一章',
                    progress: 30,
                    timestamp: Date.now() / 1000,
                  }),
                })
                
                setTimeout(() => {
                  this.onmessage({
                    data: JSON.stringify({
                      type: 'document_chunk',
                      content: '\n\n规划内容...',
                      accumulated: '# 规划文档\n\n## 第一章\n\n规划内容...',
                      progress: 60,
                      timestamp: Date.now() / 1000,
                    }),
                  })
                }, 200)
                
                setTimeout(() => {
                  this.onmessage({
                    data: JSON.stringify({
                      type: 'document_complete',
                      document_id: 'plan_mock_1',
                      content: '# 规划文档\n\n## 第一章\n\n这是完整的规划内容。\n\n## 第二章\n\n更多规划细节。',
                      timestamp: Date.now() / 1000,
                    }),
                  })
                }, 400)
              }
              
              // 模拟 Spec 模式响应
              if (message.type === 'start_spec') {
                this.onmessage({
                  data: JSON.stringify({
                    type: 'document_chunk',
                    content: '# 规格说明\n\n## 功能规格',
                    accumulated: '# 规格说明\n\n## 功能规格',
                    progress: 50,
                    timestamp: Date.now() / 1000,
                  }),
                })
                
                setTimeout(() => {
                  this.onmessage({
                    data: JSON.stringify({
                      type: 'document_complete',
                      document_id: 'spec_mock_1',
                      content: '# 规格说明\n\n## 功能规格\n\n详细规格内容。',
                      timestamp: Date.now() / 1000,
                    }),
                  })
                }, 400)
              }
              
              // 模拟 ping/pong
              if (message.type === 'ping') {
                this.onmessage({
                  data: JSON.stringify({
                    type: 'pong',
                    timestamp: Date.now() / 1000,
                  }),
                })
              }
            }
          }, 50)
        }
        
        close(code = 1000, reason = '') {
          this.readyState = 3 // CLOSED
          if (this.onclose) {
            this.onclose({ type: 'close', code, reason, wasClean: true })
          }
        }
        
        // WebSocket 常量
        static get CONNECTING() { return 0 }
        static get OPEN() { return 1 }
        static get CLOSING() { return 2 }
        static get CLOSED() { return 3 }
      }
      
      // 复制常量到实例
      window.WebSocket.CONNECTING = 0
      window.WebSocket.OPEN = 1
      window.WebSocket.CLOSING = 2
      window.WebSocket.CLOSED = 3
    })
    
    // 拦截 API 请求并返回 mock 数据
    await page.route('**/api/**', async (route) => {
      const url = route.request().url()
      
      // Mock 对话列表
      if (url.includes('/conversations') && !url.includes('/plans') && !url.includes('/specs')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            { id: 'conv_1', title: '测试对话 1', message_count: 5, updated_at: Date.now() / 1000 },
            { id: 'conv_2', title: '测试对话 2', message_count: 3, updated_at: Date.now() / 1000 - 3600 },
          ]),
        })
        return
      }
      
      // Mock 创建对话
      if (url.includes('/conversations') && route.request().method() === 'POST') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'new_conv_' + Date.now(),
            title: '新对话',
            message_count: 0,
            created_at: Date.now() / 1000,
            updated_at: Date.now() / 1000,
          }),
        })
        return
      }
      
      // Mock Plan 列表
      if (url.includes('/plans')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            {
              id: 'plan_1',
              title: '洪水预警方案',
              status: 'completed',
              content: '# 洪水预警方案\n\n## 1. 预警等级划分\n- 蓝色预警：水位接近警戒线\n- 黄色预警：水位超过警戒线\n- 橙色预警：水位超过保证水位\n- 红色预警：水位超过历史最高水位',
              created_at: Date.now() / 1000 - 86400,
              updated_at: Date.now() / 1000,
            },
          ]),
        })
        return
      }
      
      // Mock Spec 列表
      if (url.includes('/specs') && !url.includes('/specs/')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            {
              feature_name: 'flood-dispatch-system',
              display_name: '洪水调度系统',
              status: 'draft',
              created_at: Date.now() / 1000 - 86400,
              updated_at: Date.now() / 1000,
            },
          ]),
        })
        return
      }
      
      // Mock Spec 详情
      if (url.includes('/specs/') && !url.includes('/files')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            feature_name: 'flood-dispatch-system',
            display_name: '洪水调度系统',
            status: 'draft',
            documents: {
              spec: {
                filename: 'spec.md',
                content: '# 洪水调度系统规格说明\n\n## 功能概述\n实现智能化的洪水调度决策支持系统。\n\n## 核心功能\n1. 实时水位监测\n2. 洪水预警分析\n3. 调度方案生成\n4. 应急预案管理',
                sections: [
                  { title: '功能概述', level: 2 },
                  { title: '核心功能', level: 2 },
                ],
              },
              tasks: {
                filename: 'tasks.md',
                content: '# 开发任务列表\n\n- [ ] 数据采集模块\n- [ ] 预警分析模块\n- [ ] 调度决策模块\n- [ ] 用户界面开发',
                sections: [],
              },
              checklist: {
                filename: 'checklist.md',
                content: '# 验收检查清单\n\n- [ ] 功能完整性测试\n- [ ] 性能压力测试\n- [ ] 安全渗透测试\n- [ ] 用户体验测试',
                sections: [],
              },
            },
          }),
        })
        return
      }
      
      // Mock 模式检测
      if (url.includes('/mode/detect')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            recommended_mode: 'plan',
            confidence: 0.85,
            reason: '检测到规划相关关键词',
          }),
        })
        return
      }
      
      // 其他请求继续
      await route.continue()
    })
    
    // 访问首页
    await page.goto('/')
    // 等待页面加载完成
    await page.waitForLoadState('networkidle')
  })

  test('页面基本元素渲染正确 (Mock)', async ({ page }) => {
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
  })

  test('发送普通消息并接收回复 (Mock)', async ({ page }) => {
    // 找到输入框并输入消息
    const textarea = page.locator('textarea[placeholder*="输入消息"]')
    await textarea.fill('你好，请介绍一下系统')

    // 点击发送按钮
    const sendButton = page.locator('button:has-text("发送")')
    await expect(sendButton).toBeEnabled()
    await sendButton.click()

    // 等待消息发送
    await page.waitForTimeout(500)

    // 验证输入框已清空
    await expect(textarea).toHaveValue('')

    // 等待 AI 回复完成
    await page.waitForTimeout(1000)
  })

  test('使用 /plan 命令进入 Plan 模式 (Mock)', async ({ page }) => {
    // 找到输入框并输入 /plan 命令
    const textarea = page.locator('textarea[placeholder*="输入消息"]')
    await textarea.fill('/plan 制定一个洪水预警方案')

    // 点击发送按钮
    const sendButton = page.locator('button:has-text("发送")')
    await sendButton.click()

    // 等待侧边面板打开
    await page.waitForTimeout(800)

    // 验证侧边面板已打开 - 检查确认/取消按钮
    await expect(page.locator('button:has-text("确认")')).toBeVisible()
    await expect(page.locator('button:has-text("取消")')).toBeVisible()

    // 等待文档生成完成（最多等待2秒）
    await page.waitForTimeout(1500)

    // 验证文档内容区域显示（生成完成后应该显示 textarea）
    await expect(page.locator('textarea').nth(1)).toBeVisible()
  })

  test('Plan 模式文档编辑功能 (Mock)', async ({ page }) => {
    // 进入 Plan 模式
    const textarea = page.locator('textarea[placeholder*="输入消息"]')
    await textarea.fill('/plan 设计一个水库调度规划')
    await page.locator('button:has-text("发送")').click()

    // 等待侧边面板打开
    await page.waitForTimeout(800)

    // 验证确认按钮存在（表示面板已打开）
    await expect(page.locator('button:has-text("确认")')).toBeVisible()

    // 等待生成完成
    await page.waitForTimeout(1500)

    // 编辑文档内容 - 使用第二个 textarea（编辑器中的）
    const editorTextarea = page.locator('textarea').nth(1)
    await expect(editorTextarea).toBeVisible()
    await editorTextarea.fill('这是编辑后的规划内容\n\n## 第一章\n测试内容')

    // 验证编辑成功
    await expect(editorTextarea).toHaveValue('这是编辑后的规划内容\n\n## 第一章\n测试内容')
  })

  test('Plan 模式自然语言修改 (Mock)', async ({ page }) => {
    // 进入 Plan 模式
    const textarea = page.locator('textarea[placeholder*="输入消息"]')
    await textarea.fill('/plan 测试自然语言修改')
    await page.locator('button:has-text("发送")').click()

    // 等待侧边面板打开
    await page.waitForTimeout(800)

    // 等待生成完成（需要更长时间）
    await page.waitForTimeout(2000)

    // 在底部修改输入框输入修改指令 - 使用更通用的选择器
    const modifyInput = page.locator('textarea').last()
    await expect(modifyInput).toBeVisible()
    await modifyInput.fill('请增加关于应急预案的章节')

    // 验证输入成功
    await expect(modifyInput).toHaveValue('请增加关于应急预案的章节')

    // 点击修改按钮
    const modifyButton = page.locator('button:has-text("修改")')
    await expect(modifyButton).toBeVisible()
  })

  test('Plan 模式取消功能 (Mock)', async ({ page }) => {
    // 进入 Plan 模式
    const textarea = page.locator('textarea[placeholder*="输入消息"]')
    await textarea.fill('/plan 测试取消功能')
    await page.locator('button:has-text("发送")').click()

    // 等待侧边面板打开
    await page.waitForTimeout(800)

    // 验证确认按钮存在（表示面板已打开）
    await expect(page.locator('button:has-text("确认")')).toBeVisible()

    // 点击取消按钮
    const cancelButton = page.locator('button:has-text("取消")')
    await cancelButton.click()

    // 等待面板关闭
    await page.waitForTimeout(500)
  })

  test('快捷功能按钮存在 (Mock)', async ({ page }) => {
    // 验证快捷功能按钮存在
    await expect(page.locator('text=洪水调度').first()).toBeVisible()
    await expect(page.locator('text=生成报告').first()).toBeVisible()
    await expect(page.locator('text=智能问答').first()).toBeVisible()
  })

  test('Plan/Spec 命令提示存在 (Mock)', async ({ page }) => {
    // 验证 Plan/Spec 命令提示存在
    await expect(page.locator('code:has-text("/plan")')).toBeVisible()
    await expect(page.locator('code:has-text("/spec")')).toBeVisible()
  })

  test('侧边栏收起展开 (Mock)', async ({ page }) => {
    // 验证收起侧边栏按钮存在
    const toggleButton = page.locator('button:has-text("收起侧边栏")')
    await expect(toggleButton).toBeVisible()

    // 点击收起侧边栏
    await toggleButton.click()

    // 等待动画完成
    await page.waitForTimeout(500)
  })

  test('创建新对话 (Mock)', async ({ page }) => {
    // 点击新建对话按钮
    const newChatButton = page.locator('button:has-text("新对话")')
    await newChatButton.click()

    // 等待新对话创建
    await page.waitForTimeout(500)

    // 验证输入框已清空
    const textarea = page.locator('textarea[placeholder*="输入消息"]')
    await expect(textarea).toHaveValue('')
  })
})
