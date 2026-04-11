"""简单测试：验证参数传递"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 模拟 Pipeline 中的逻辑
from src.flood_decision_agent.agents.intent_parser.parser import IntentParser
from src.flood_decision_agent.core.shared_data_pool import SharedDataPool

# 1. 模拟 IntentParser 解析结果（metadata["intent"] = {...}）
parser = IntentParser()
intent = parser.parse("查询金坛天气")

# 2. 模拟 metadata["intent"] 字典
metadata = {
    "task_type": "weather_forecast",
    "goal": intent.goal,
    "constraints": intent.constraints,
}

# 3. 模拟 Pipeline 中的参数提取逻辑
data_pool = SharedDataPool()
user_input = "查询金坛天气"

intent_from_metadata = metadata  # 这是一个字典，不是 TaskIntent 对象

if intent_from_metadata:
    if hasattr(intent_from_metadata, 'goal'):
        intent_goal = intent_from_metadata.goal
    elif isinstance(intent_from_metadata, dict):
        intent_goal = intent_from_metadata.get('goal', {})
    else:
        intent_goal = {}
    
    if intent_goal:
        for key, value in intent_goal.items():
            if value and isinstance(value, str) and value.strip():
                data_pool.set(key, value, source="intent_goal")
                print(f"[INFO] 从 intent.goal 提取参数: {key}={value}")

# 4. 验证
city = data_pool.get('city')
print(f"\n结果: city = {city}")
print(f"预期: 金坛")
print(f"测试: {'✅ 通过' if city == '金坛' else '❌ 失败'}")
