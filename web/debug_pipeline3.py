#!/usr/bin/env python
"""Pipeline调试脚本 - Windows兼容版."""

import os
import sys
import traceback

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 获取API Key
api_key = os.environ.get('KIMI_API_KEY')
if not api_key:
    print("错误: KIMI_API_KEY 环境变量未设置")
    sys.exit(1)

print(f"KIMI_API_KEY: {api_key[:20]}...")
os.environ['KIMI_API_KEY'] = api_key

from flood_decision_agent.app.visualized_pipeline import VisualizedPipeline


def test_pipeline_simple():
    """简化版Pipeline测试."""
    print("\n" + "="*60)
    print("Pipeline调试测试")
    print("="*60 + "\n")
    
    try:
        print("创建Pipeline...")
        pipeline = VisualizedPipeline(
            visualizer=None,  # 不使用可视化器
            seed=42,
            enable_visualization=False,
        )
        print("[OK] Pipeline创建成功\n")
        
        # 执行Pipeline
        message = "分析当前降雨情况"
        print(f"执行Pipeline，输入: {message}")
        print("-"*60)
        
        result = pipeline.run({
            "type": "natural_language",
            "input": message,
        })
        
        print("-"*60)
        print(f"\nPipeline执行结果:")
        print(f"  success: {result.success}")
        print(f"  data_pool_snapshot keys: {list(result.data_pool_snapshot.keys()) if result.data_pool_snapshot else 'None'}")
        print(f"  execution_summary: {result.execution_summary}")
        
        if not result.success:
            print("\n[FAIL] Pipeline执行失败")
            if result.data_pool_snapshot and 'error' in result.data_pool_snapshot:
                print(f"  错误信息: {result.data_pool_snapshot['error']}")
            return False
        else:
            print("\n[OK] Pipeline执行成功")
            return True
            
    except Exception as e:
        print(f"\n[ERROR] 执行异常: {e}")
        print("\n详细错误堆栈:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pipeline_simple()
    sys.exit(0 if success else 1)
