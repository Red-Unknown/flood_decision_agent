"""停止Web服务脚本.

读取 .web_pids.json 文件并停止对应的服务进程.
"""

import json
import os
import sys
from pathlib import Path


def stop_service(pid, name):
    """停止服务进程."""
    try:
        if sys.platform == 'win32':
            # Windows
            os.system(f'taskkill /F /PID {pid} 2>nul')
        else:
            # Linux/Mac
            os.system(f'kill -TERM {pid} 2>/dev/null')
        print(f"[OK] {name} (PID: {pid}) 已停止")
        return True
    except Exception as e:
        print(f"[警告] 停止 {name} 失败: {e}")
        return False


def main():
    """主函数."""
    print("=" * 60)
    print("停止 Web 服务")
    print("=" * 60)
    
    pid_file = Path(__file__).parent / ".web_pids.json"
    
    if not pid_file.exists():
        print("\n[信息] 没有找到进程信息文件，尝试查找并停止常见端口的服务...")
        
        # 尝试停止常见端口的服务
        ports = [8000, 8001, 8080, 3000, 3001]
        for port in ports:
            if sys.platform == 'win32':
                # Windows: 查找占用端口的进程并停止
                os.system(f'for /f "tokens=5" %a in (\'netstat -ano ^| findstr :{port} ^| findstr LISTENING\') do taskkill /F /PID %a 2>nul')
        
        print("[OK] 已尝试停止所有服务")
        return
    
    # 读取进程信息
    with open(pid_file, 'r') as f:
        pid_info = json.load(f)
    
    backend_pid = pid_info.get('backend_pid')
    frontend_pid = pid_info.get('frontend_pid')
    backend_port = pid_info.get('backend_port')
    frontend_port = pid_info.get('frontend_port')
    
    print(f"\n发现运行中的服务:")
    print(f"  后端: PID {backend_pid}, 端口 {backend_port}")
    print(f"  前端: PID {frontend_pid}, 端口 {frontend_port}")
    print()
    
    # 停止服务
    if backend_pid:
        stop_service(backend_pid, "后端服务")
    
    if frontend_pid:
        stop_service(frontend_pid, "前端服务")
    
    # 删除pid文件
    pid_file.unlink()
    print(f"\n[OK] 进程信息文件已删除")
    
    print("\n" + "=" * 60)
    print("所有服务已停止")
    print("=" * 60)


if __name__ == "__main__":
    main()
