---
alwaysApply: false
---
### 方式一：一键启动（推荐）

```powershell
# Windows
.\web\deploy\start.ps1

# Linux/Mac
chmod +x ./web/deploy/start.sh
./web/deploy/start.sh
```

启动后自动：
1. 检查环境依赖（Python、Node.js、API Key）
2. 检测可用端口（自动避让占用端口）
3. 安装前端依赖（如需要）
4. 构建前端项目
5. 启动后端服务
6. 自动打开浏览器访问 http://localhost:8000