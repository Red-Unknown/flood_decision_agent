"""启动后端服务"""
import os
import sys

sys.path.insert(0, str(__file__.rsplit(os.sep, 1)[0]))

os.environ['DEV_MODE'] = '1'

from src.flood_decision_agent.infrastructure.config_loader import get_api_key
get_api_key("KIMI_API_KEY")

from web.backend.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
