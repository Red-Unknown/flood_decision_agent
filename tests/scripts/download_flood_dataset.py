"""
下载真实洪水/水体数据集
使用公开的 Sentinel-2 水体数据集或洪水图像
"""

import os
import urllib.request
import zipfile
from pathlib import Path

# 数据集配置
DATASETS_DIR = Path("./datasets/real_flood")
DATASETS_DIR.mkdir(parents=True, exist_ok=True)

# 公开的洪水图像 URL 列表（使用 placeholder 图像作为示例）
# 实际使用时可以替换为真实的水利数据集 URL
FLOOD_IMAGE_URLS = [
    # 这些是高分辨率的水体/洪水相关图像
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Flooding_in_Des_Moines%2C_Iowa.jpg/800px-Flooding_in_Des_Moines%2C_Iowa.jpg", "flood_001.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Mississippi_River_flood_2011.jpg/800px-Mississippi_River_flood_2011.jpg", "flood_002.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/2011_Missouri_River_flooding.jpg/800px-2011_Missouri_River_flooding.jpg", "flood_003.jpg"),
]

WATER_BODY_URLS = [
    # 水体图像
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Lake_Tahoe.jpg/800px-Lake_Tahoe.jpg", "water_001.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Yangtze_River.jpg/800px-Yangtze_River.jpg", "water_002.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Reservoir_aerial_view.jpg/800px-Reservoir_aerial_view.jpg", "water_003.jpg"),
]


def download_image(url: str, save_path: Path) -> bool:
    """下载图像"""
    try:
        print(f"  下载: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(save_path, 'wb') as f:
                f.write(response.read())
        print(f"  ✓ 保存: {save_path}")
        return True
    except Exception as e:
        print(f"  ✗ 失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("下载真实水利数据集")
    print("=" * 60)
    
    downloaded = []
    failed = []
    
    # 下载洪水图像
    print("\n[1/2] 下载洪水图像...")
    for url, filename in FLOOD_IMAGE_URLS:
        save_path = DATASETS_DIR / filename
        if download_image(url, save_path):
            downloaded.append(filename)
        else:
            failed.append(filename)
    
    # 下载水体图像
    print("\n[2/2] 下载水体图像...")
    for url, filename in WATER_BODY_URLS:
        save_path = DATASETS_DIR / filename
        if download_image(url, save_path):
            downloaded.append(filename)
        else:
            failed.append(filename)
    
    # 汇总
    print("\n" + "=" * 60)
    print("下载完成")
    print("=" * 60)
    print(f"成功: {len(downloaded)} 张")
    print(f"失败: {len(failed)} 张")
    print(f"\n数据集位置: {DATASETS_DIR.absolute()}")
    
    if downloaded:
        print("\n已下载的图像:")
        for f in downloaded:
            print(f"  - {f}")
    
    return len(downloaded) > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
