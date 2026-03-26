"""环境检查脚本.

检查运行Web服务所需的环境依赖。
"""

from __future__ import annotations

import os
import subprocess
import sys


def check_python_version() -> bool:
    """检查Python版本."""
    required_version = (3, 11)
    current_version = sys.version_info[:2]

    if current_version >= required_version:
        print(f"✓ Python版本: {sys.version.split()[0]} (满足要求 >= 3.11)")
        return True
    else:
        print(f"✗ Python版本: {sys.version.split()[0]} (需要 >= 3.11)")
        return False


def check_node_version() -> bool:
    """检查Node.js版本."""
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        version = result.stdout.strip().lstrip("v")
        major_version = int(version.split(".")[0])

        if major_version >= 18:
            print(f"✓ Node.js版本: {version} (满足要求 >= 18)")
            return True
        else:
            print(f"✗ Node.js版本: {version} (需要 >= 18)")
            return False
    except FileNotFoundError:
        print("✗ Node.js未安装")
        return False
    except subprocess.CalledProcessError:
        print("✗ 无法获取Node.js版本")
        return False


def check_conda_env() -> bool:
    """检查Conda环境."""
    conda_env = os.environ.get("CONDA_DEFAULT_ENV", "")
    if conda_env:
        print(f"✓ Conda环境: {conda_env}")
        return True
    else:
        print("⚠ 未检测到Conda环境（建议激活conda环境）")
        return True  # 警告但不阻止


def check_python_packages() -> bool:
    """检查Python依赖包."""
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package.lower())
        except ImportError:
            missing.append(package)

    if missing:
        print(f"✗ 缺少Python包: {', '.join(missing)}")
        print(f"  请运行: pip install {' '.join(missing)}")
        return False
    else:
        print("✓ Python依赖包已安装")
        return True


def check_kimi_api_key() -> bool:
    """检查KIMI_API_KEY环境变量."""
    api_key = os.getenv("KIMI_API_KEY", "").strip()
    if api_key:
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"✓ KIMI_API_KEY已配置: {masked_key}")
        return True
    else:
        print("✗ KIMI_API_KEY未配置")
        print("  请设置环境变量: $env:KIMI_API_KEY='your-api-key'")
        return False


def check_frontend_deps() -> bool:
    """检查前端依赖."""
    frontend_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "frontend",
    )
    node_modules = os.path.join(frontend_dir, "node_modules")

    if os.path.exists(node_modules):
        print("✓ 前端依赖已安装 (node_modules存在)")
        return True
    else:
        print("⚠ 前端依赖未安装")
        print(f"  请在 {frontend_dir} 目录运行: npm install")
        return False


def find_available_port(start_port: int = 8000, max_port: int = 8010) -> int:
    """查找可用端口."""
    import socket

    for port in range(start_port, max_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                continue

    return -1


def main():
    """主函数."""
    print("=" * 50)
    print("水利智脑 Web服务 - 环境检查")
    print("=" * 50)
    print()

    checks = [
        ("Python版本", check_python_version),
        ("Node.js版本", check_node_version),
        ("Conda环境", check_conda_env),
        ("Python依赖", check_python_packages),
        ("KIMI_API_KEY", check_kimi_api_key),
        ("前端依赖", check_frontend_deps),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n检查 {name}...")
        results.append(check_func())

    print("\n" + "=" * 50)

    # 检查端口
    print("\n检查可用端口...")
    available_port = find_available_port()
    if available_port > 0:
        print(f"✓ 可用端口: {available_port}")
    else:
        print("✗ 端口 8000-8010 均被占用，请手动指定端口")

    print("\n" + "=" * 50)

    # 总结
    if all(results):
        print("\n✓ 所有检查通过，环境准备就绪！")
        return 0
    else:
        print("\n✗ 部分检查未通过，请根据提示修复后重试")
        return 1


if __name__ == "__main__":
    sys.exit(main())
