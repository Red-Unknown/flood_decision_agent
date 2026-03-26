"""Pipeline调试脚本.

定位Pipeline执行失败的具体原因。
"""

import os
import sys
import traceback

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 获取API Key
api_key = os.environ.get('KIMI_API_KEY')
print(f"KIMI_API_KEY: {api_key[:20]}..." if api_key else "未设置")

# 设置环境变量
os.environ['KIMI_API_KEY'] = api_key

from flood_decision_agent.app.visualized_pipeline import VisualizedPipeline

# 创建简单的事件收集器
class DebugEventCollector:
    def __init__(self):
        self.events = []
        
    def on_pipeline_start(self, context=None):
        print(f"[DEBUG] Pipeline开始: {context}")
        self.events.append(("pipeline_start", context))
        
    def on_task_graph_created(self, task_graph):
        nodes = task_graph.get_all_nodes()
        print(f"[DEBUG] 任务图创建完成，节点数: {len(nodes)}")
        self.events.append(("task_graph_created", len(nodes)))
        
    def on_node_started(self, node_id, agent_id, task_info=None):
        print(f"[DEBUG] 节点开始: {node_id}, Agent: {agent_id}")
        self.events.append(("node_started", node_id, agent_id))
        
    def on_node_completed(self, node_id, agent_id, duration_ms, output_summary="", task_info=None):
        print(f"[DEBUG] 节点完成: {node_id}, 耗时: {duration_ms}ms")
        self.events.append(("node_completed", node_id, duration_ms))
        
    def on_node_failed(self, node_id, agent_id, error_message, retry_count=0, task_info=None):
        print(f"[DEBUG] 节点失败: {node_id}, 错误: {error_message}")
        self.events.append(("node_failed", node_id, error_message))
        
    def on_agent_called(self, caller_agent, callee_agent, input_summary="", output_summary=""):
        print(f"[DEBUG] Agent调用: {caller_agent} -> {callee_agent}")
        self.events.append(("agent_called", caller_agent, callee_agent))
        
    def on_pipeline_completed(self, success=True, summary=None):
        print(f"[DEBUG] Pipeline完成: success={success}")
        self.events.append(("pipeline_completed", success))


# 创建包装器
class VisualizerWrapper:
    def __init__(self, collector):
        self.collector = collector
        self.enabled = True

    def on_pipeline_start(self, context=None):
        self.collector.on_pipeline_start(context)

    def on_task_graph_created(self, task_graph):
        self.collector.on_task_graph_created(task_graph)

    def on_node_started(self, node_id, agent_id, task_info=None):
        self.collector.on_node_started(node_id, agent_id, task_info)

    def on_node_completed(self, node_id, agent_id, duration_ms, output_summary="", task_info=None):
        self.collector.on_node_completed(node_id, agent_id, duration_ms, output_summary, task_info)

    def on_node_failed(self, node_id, agent_id, error_message, retry_count=0, task_info=None):
        self.collector.on_node_failed(node_id, agent_id, error_message, retry_count, task_info)

    def on_agent_called(self, caller_agent, callee_agent, input_summary="", output_summary=""):
        self.collector.on_agent_called(caller_agent, callee_agent, input_summary, output_summary)

    def on_pipeline_completed(self, success=True, summary=None):
        self.collector.on_pipeline_completed(success, summary)


def test_pipeline():
    """测试Pipeline执行."""
    print("\n" + "="*60)
    print("Pipeline调试测试")
    print("="*60 + "\n")
    
    try:
        # 创建事件收集器
        collector = DebugEventCollector()
        wrapper = VisualizerWrapper(collector)
        
        # 创建Pipeline
        print("创建Pipeline...")
        pipeline = VisualizedPipeline(
            visualizer=wrapper,
            seed=42,
            enable_visualization=True,
        )
        print("✓ Pipeline创建成功\n")
        
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
        print(f"  data_pool_snapshot: {result.data_pool_snapshot}")
        print(f"  execution_summary: {result.execution_summary}")
        
        # 打印所有事件
        print(f"\n事件记录 ({len(collector.events)} 个):")
        for event in collector.events:
            print(f"  {event}")
            
    except Exception as e:
        print(f"\n✗ 执行失败: {e}")
        print("\n详细错误堆栈:")
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = test_pipeline()
    sys.exit(0 if success else 1)
