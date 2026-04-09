"""启动后端服务的脚本"""
import subprocess
import sys
import os

# 设置工作目录
os.chdir(r"f:\college\sophomore\academic")

# 启动服务器
proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "web.backend.main:app", "--host", "0.0.0.0", "--port", "8001"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

print(f"Started server with PID: {proc.pid}")
print("Waiting for server to start...")

import time
time.sleep(15)

# 检查进程状态
if proc.poll() is None:
    print("Server is running!")
else:
    print(f"Server exited with code: {proc.returncode}")
    # 打印输出
    stdout, _ = proc.communicate()
    print("Output:", stdout)
