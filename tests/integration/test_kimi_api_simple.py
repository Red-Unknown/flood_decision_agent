"""简单的 Kimi API 测试"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_kimi_api():
    """测试 Kimi API 调用"""
    api_key = os.environ.get("KIMI_API_KEY")
    
    if not api_key:
        print("❌ KIMI_API_KEY 环境变量未设置")
        return False
    
    print(f"✓ API Key 已配置: {api_key[:10]}...")
    
    try:
        from flood_decision_agent.infrastructure.llm.kimi_client import KimiClient
        
        print("\n初始化 KimiClient...")
        client = KimiClient()
        print("✓ KimiClient 初始化成功")
        
        print("\n测试简单调用...")
        response = client.complete(
            prompt="你好，请用一句话介绍自己",
            system_message="你是一个有帮助的助手",
            temperature=0.7,
            max_tokens=100,
        )
        print(f"✓ API 调用成功")
        print(f"\n响应内容:\n{response}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_kimi_api()
    sys.exit(0 if success else 1)
