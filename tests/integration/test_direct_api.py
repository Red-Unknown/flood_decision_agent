"""直接测试 Kimi API"""
import os
from openai import OpenAI

def test_direct_api():
    """直接测试 API 调用"""
    api_key = os.environ.get("KIMI_API_KEY")
    
    if not api_key:
        print("❌ KIMI_API_KEY 环境变量未设置")
        return False
    
    print(f"✓ API Key: {api_key[:10]}...")
    print("\n初始化 OpenAI 客户端...")
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.moonshot.cn/v1"
    )
    
    print("✓ 客户端初始化成功")
    print("\n发送测试请求...")
    
    try:
        response = client.chat.completions.create(
            model="moonshot-v1-128k",
            messages=[
                {"role": "system", "content": "你是水利专家"},
                {"role": "user", "content": "请用100字概述洪水预警系统的关键功能"}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        
        print("✓ API 调用成功")
        print(f"\n响应内容:\n{response.choices[0].message.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ API 调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = test_direct_api()
    sys.exit(0 if success else 1)
