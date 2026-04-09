import { defineConfig, devices } from '@playwright/test'

/**
 * Playwright 配置
 *
 * 简单模式端到端测试配置
 * - 使用真实后端服务 (端口 8001)
 * - 前端开发服务器 (端口 3001)
 */

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false, // 串行执行，避免测试间相互影响
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1, // 单 worker，确保测试顺序执行
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list']
  ],
  use: {
    baseURL: 'http://localhost:3001',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    viewport: { width: 1280, height: 720 },
    actionTimeout: 30000,
    navigationTimeout: 30000,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  // 开发服务器配置 - 使用已运行的服务
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3001',
    reuseExistingServer: true, // 复用已存在的服务器
    timeout: 120000,
  },
})
