"""快速验证参数传递修复"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.flood_decision_agent.core.shared_data_pool import SharedDataPool
from src.flood_decision_agent.agents.intent_parser.parser import IntentParser

# 1. 模拟 IntentParser 解析
parser = IntentParser()
intent = parser.parse("查询金坛天气")
print(f"Intent解析结果:")
print(f"  goal: {intent.goal}")

# 2. 模拟 Pipeline 存储到 data_pool
data_pool = SharedDataPool()
user_input = "查询金坛天气"

if intent and intent.goal:
    for key, value in intent.goal.items():
        if value and isinstance(value, str) and value.strip():
            data_pool.set(key, value, source="intent_goal")
            print(f"存储到data_pool: {key}={value}, source=intent_goal")

# 3. 验证 data_pool 中的值
print(f"\n验证data_pool:")
print(f"  city: {data_pool.get('city')}")
print(f"  description: {data_pool.get('description')}")
print(f"  raw_user_input: {data_pool.get('raw_user_input')}")
print(f"  city来源: {data_pool.get_source('city')}")

# 4. 模拟 executor 获取参数
city = data_pool.get('city') or data_pool.get('station')
if city:
    print(f"\n✅ 参数传递成功: city={city}")
else:
    print(f"\n⚠️ 参数传递失败，使用默认: city=北京")
