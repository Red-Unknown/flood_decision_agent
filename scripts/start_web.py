"""启动Web服务脚本 - 自动选择空闲端口.

该脚本会自动:
1. 查找可用的后端端口
2. 启动后端服务
3. 更新前端配置中的代理端口
4. 查找可用的前端端口
5. 启动前端服务
"""

import os
import sys
import socket
import subprocess
import time
import json
from pathlib import Path


def find_free_port(start_port=8000, max_port=9000):
    """查找可用的端口."""
    for port in range(start_port, max_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"无法找到可用端口 (范围: {start_port}-{max_port})")


def update_frontend_proxy_config(backend_port):
    """更新前端vite配置中的代理端口."""
    vite_config_path = Path(__file__).parent.parent / "web" / "frontend" / "vite.config.js"
    
    if not vite_config_path.exists():
        print(f"警告: 找不到vite配置文件: {vite_config_path}")
        return
    
    content = vite_config_path.read_text(encoding='utf-8')
    
    # 替换代理目标端口
    import re
    content = re.sub(
        r"target:\s*['"]http://localhost:\d+['"]",
        f"target: 'http://localhost:{backend_port}'",
        content
    )
    content = re.sub(
        r"target:\s*['"]ws://localhost:\d+['"]",
        f"target: 'ws://localhost:{backend_port}'",
        content
    )
    
    vite_config_path.write_text(content, encoding='utf-8')
    print(f"[OK] 前端代理配置已更新到端口 {backend_port}")


def start_backend(port):
    """启动后端服务."""
    project_root = Path(__file__).parent.parent
    
    # 设置环境变量
    env = os.environ.copy()
    env['PORT'] = str(port)
    
    # 启动后端
    backend_script = project_root / "start_backend.py"
    
    if sys.platform == 'win32':
        # Windows
        cmd = ['python', str(backend_script)]
    else:
        # Linux/Mac
        cmd = ['python3', str(backend_script)]
    
    process = subprocess.Popen(
        cmd,
        cwd=project_root,
        env=env,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    )
    
    return process


def start_frontend(port):
    """启动前端服务."""
    frontend_dir = Path(__file__).parent.parent / "web" / "frontend"
    
    if sys.platform == 'win32':
        # Windows
        cmd = ['cmd', '/c', 'start', 'npm', 'run', 'dev', '--', '--port', str(port)]
    else:
        # Linux/Mac
        cmd = ['npm', 'run', 'dev', '--', '--port', str(port)]
    
    process = subprocess.Popen(
        cmd,
        cwd=frontend_dir,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    )
    
    return process


def wait_for_server(port, timeout=30):
    """等待服务器启动."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('localhost', port))
                return True
        except:
            time.sleep(0.5)
    return False


def main():
    """主函数."""
    print("=" * 60)
    print("水利智脑 Web服务启动脚本")
    print("=" * 60)
    
    try:
        # 1. 查找后端端口
        print("\n[1/5] 查找可用的后端端口...")
        backend_port = find_free_port(8000, 9000)
        print(f"[OK] 后端端口: {backend_port}")
        
        # 2. 更新前端配置
        print("\n[2/5] 更新前端代理配置...")
        update_frontend_proxy_config(backend_port)
        
        # 3. 启动后端
        print("\n[3/5] 启动后端服务...")
        backend_process = start_backend(backend_port)
        print(f"[OK] 后端服务已启动 (PID: {backend_process.pid})")
        
        # 等待后端启动
        print("    等待后端服务就绪...")
        if wait_for_server(backend_port, timeout=30):
            print(f"[OK] 后端服务已就绪: http://localhost:{backend_port}")
        else:
            print("[警告] 后端服务启动超时，请手动检查")
        
        # 4. 查找前端端口
        print("\n[4/5] 查找可用的前端端口...")
        frontend_port = find_free_port(3000, 3100)
        print(f"[OK] 前端端口: {frontend_port}")
        
        # 5. 启动前端
        print("\n[5/5] 启动前端服务...")
        frontend_process = start_frontend(frontend_port)
        print(f"[OK] 前端服务已启动 (PID: {frontend_process.pid})")
        
        # 等待前端启动
        print("    等待前端服务就绪...")
        time.sleep(3)  # 给npm一些启动时间
        
        print("\n" + "=" * 60)
        print("服务启动完成!")
        print("=" * 60)
        print(f"\n前端地址: http://localhost:{frontend_port}")
        print(f"后端地址: http://localhost:{backend_port}")
        print(f"API文档: http://localhost:{backend_port}/docs")
        print("\n按 Ctrl+C 停止服务")
        print("=" * 60)
        
        # 保存进程信息到文件，方便后续停止
        pid_info = {
            'backend_pid': backend_process.pid,
            'frontend_pid': frontend_process.pid,
            'backend_port': backend_port,
            'frontend_port': frontend_port,
        }
        
        pid_file = Path(__file__).parent / ".web_pids.json"
        with open(pid_file, 'w') as f:
            json.dump(pid_info, f)
        
        print(f"\n[信息] 进程信息已保存到: {pid_file}")
        
        # 等待用户中断
        try:
            while True:
                time.sleep(1)
                # 检查进程是否还在运行
                if backend_process.poll() is not None:
                    print("\n[警告] 后端服务已停止")
                    break
        except KeyboardInterrupt:
            print("\n\n正在停止服务...")
            backend_process.terminate()
            frontend_process.terminate()
            print("[OK] 服务已停止")
            
            # 删除pid文件
            if pid_file.exists():
                pid_file.unlink()
        
    except Exception as e:
        print(f"\n[错误] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
