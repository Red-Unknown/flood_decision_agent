"""启动后端服务"""
import os
os.environ['KIMI_API_KEY'] = 'sk-test-key-for-debug'

import uvicorn
from web.backend.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
