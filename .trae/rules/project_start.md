
## 启动方式

### 开发模式（前后端分离）

**终端1 - 启动后端：**
```bash
# 设置API Key
$env:KIMI_API_KEY="your-api-key"  # Windows
export KIMI_API_KEY="your-api-key"  # Linux/Mac

# 启动后端服务
python -m web.backend.main
```
后端运行在 http://localhost:8000

**终端2 - 启动前端开发服务器：**
```bash
cd web/frontend
npm install      # 首次运行需安装依赖
npm run dev
```
前端开发服务器运行在 http://localhost:3000

## 环境检查

运行检查脚本验证环境：
```bash
python web/deploy/check_env.py
```


