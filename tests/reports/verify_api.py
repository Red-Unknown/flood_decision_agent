import os
from openai import OpenAI

api_key = os.environ.get("KIMI_API_KEY", "")
print(f"API Key: {api_key[:20]}...")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.moonshot.cn/v1"
)

try:
    response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[{"role": "user", "content": "你好"}],
        max_tokens=10
    )
    print(f"API 验证成功: {response.choices[0].message.content}")
except Exception as e:
    print(f"API 验证失败: {e}")
