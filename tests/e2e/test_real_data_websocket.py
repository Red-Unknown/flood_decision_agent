"""基于真实 MCP 工具的 WebSocket 全流程测试

使用真实 API 获取数据，设计真实测试场景：
1. 文件系统操作（真实文件操作）
2. 文档处理（真实文档解析）
3. 网络搜索（真实搜索）

要求：真实！真实！真实！
"""

import asyncio
import json
import os
import sys
import websockets
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# ============== 启动检查 ==============
def check_api_key():
    """检查 KIMI_API_KEY 环境变量"""
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        print("=" * 60)
        print("错误: 需要 KIMI_API_KEY 环境变量")
        print("=" * 60)
        print("\n请设置环境变量:")
        print("  Windows PowerShell: $env:KIMI_API_KEY=\"your-api-key\"")
        print("  Windows CMD: set KIMI_API_KEY=your-api-key")
        print("  Linux/Mac: export KIMI_API_KEY=your-api-key")
        print("\n" + "=" * 60)
        sys.exit(1)
    return api_key


# ============== 真实测试场景 ==============

# 场景1: 文件系统操作 - 列出真实存在的目录
SCENE_FILESYSTEM = {
    "name": "文件系统操作",
    "input": "列出当前目录下的文件",
    "expected_tools": ["filesystem"],
    "expected_events": [
        "user_message_confirm",
        "intent_parsed",
        "chain_generation_stage",
        "task_graph_generated",
        "chain_generated",
        "execution_started",
        "task_update",
        "execution_progress",
        "execution_complete",
        "assistant_message"
    ]
}

# 场景2: 文档处理 - 创建并读取真实文档
SCENE_DOCUMENT = {
    "name": "文档处理",
    "input": "帮我创建一个测试文档",
    "expected_tools": ["document"],
    "expected_events": [
        "user_message_confirm",
        "intent_parsed",
        "chain_generation_stage",
        "task_graph_generated",
        "chain_generated",
        "execution_started",
        "task_update",
        "execution_progress",
        "execution_complete",
        "assistant_message"
    ]
}

# 场景3: 网络搜索 - 真实搜索
SCENE_WEB_SEARCH = {
    "name": "网络搜索",
    "input": "搜索关于洪水预警的最新信息",
    "expected_tools": ["web_search"],
    "expected_events": [
        "user_message_confirm",
        "intent_parsed",
        "chain_generation_stage",
        "task_graph_generated",
        "chain_generated",
        "execution_started",
        "task_update",
        "execution_progress",
        "execution_complete",
        "assistant_message"
    ]
}

# 场景4: 综合场景 - 文件+搜索
SCENE_COMBINED = {
    "name": "综合场景",
    "input": "搜索洪水预警信息并保存到文件",
    "expected_tools": ["web_search", "filesystem"],
    "expected_events": [
        "user_message_confirm",
        "intent_parsed",
        "chain_generation_stage",
        "task_graph_generated",
        "chain_generated",
        "execution_started",
        "task_update",
        "execution_progress",
        "execution_complete",
        "assistant_message"
    ]
}


# ============== WebSocket 测试器 ==============
class WebSocketTester:
    """WebSocket 全流程测试器"""
    
    def __init__(self, uri: str = "ws://localhost:8001/ws/chat"):
        self.uri = uri
        self.ws = None
        self.events: List[Dict[str, Any]] = []
        self.test_results: List[Dict[str, Any]] = []
        
    async def connect(self, conversation_id: str = None) -> bool:
        """建立 WebSocket 连接"""
        if conversation_id is None:
            conversation_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        full_uri = f"{self.uri}/{conversation_id}"
        print(f"\n[连接] {full_uri}")
        
        try:
            self.ws = await websockets.connect(full_uri)
            
            # 等待连接确认
            response = await asyncio.wait_for(self.ws.recv(), timeout=5.0)
            data = json.loads(response)
            print(f"[连接确认] type={data.get('type')}")
            
            return True
        except Exception as e:
            print(f"[连接失败] {e}")
            return False
    
    async def send_message(self, content: str) -> bool:
        """发送聊天消息"""
        if not self.ws:
            print("[错误] 未连接")
            return False
        
        message = {
            "type": "chat_message",
            "content": content,
        }
        
        print(f"\n[发送] {content}")
        await self.ws.send(json.dumps(message))
        return True
    
    async def receive_events(self, timeout: float = 120.0, max_events: int = 50) -> List[Dict[str, Any]]:
        """接收事件直到完成或超时"""
        self.events = []
        start_time = asyncio.get_event_loop().time()
        
        print("\n[接收事件]")
        
        while len(self.events) < max_events:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                print(f"  超时 ({timeout}s)")
                break
            
            try:
                remaining = timeout - elapsed
                response = await asyncio.wait_for(self.ws.recv(), timeout=min(remaining, 5.0))
                data = json.loads(response)
                
                event_type = data.get('type', 'unknown')
                print(f"  [{len(self.events)+1}] {event_type}")
                
                self.events.append(data)
                
                # 如果是最终消息，结束接收
                if event_type in ['assistant_message', 'error']:
                    break
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"  [错误] {e}")
                break
        
        return self.events
    
    async def close(self):
        """关闭连接"""
        if self.ws:
            await self.ws.close()
            print("\n[连接已关闭]")
    
    def validate_events(self, expected_events: List[str]) -> Dict[str, Any]:
        """验证事件顺序"""
        received_types = [e.get('type') for e in self.events]
        
        result = {
            "success": True,
            "received": received_types,
            "expected": expected_events,
            "missing": [],
            "extra": []
        }
        
        # 检查必需事件
        for event in expected_events:
            if event not in received_types:
                result["missing"].append(event)
                result["success"] = False
        
        # 检查额外事件
        for event in received_types:
            if event not in expected_events and not event.startswith("user_"):
                result["extra"].append(event)
        
        return result
    
    def validate_data_structure(self) -> Dict[str, Any]:
        """验证数据结构"""
        errors = []
        
        for event in self.events:
            event_type = event.get('type')
            
            # 验证 intent_parsed
            if event_type == 'intent_parsed':
                if 'intent' not in event:
                    errors.append("intent_parsed 缺少 intent 字段")
                elif 'task_type' not in event.get('intent', {}):
                    errors.append("intent 缺少 task_type 字段")
            
            # 验证 chain_generated
            elif event_type == 'chain_generated':
                if 'task_graph' not in event:
                    errors.append("chain_generated 缺少 task_graph 字段")
                elif 'tasks' not in event.get('task_graph', {}):
                    errors.append("task_graph 缺少 tasks 字段")
            
            # 验证 task_update
            elif event_type == 'task_update':
                if 'task_id' not in event:
                    errors.append("task_update 缺少 task_id 字段")
                if 'status' not in event:
                    errors.append("task_update 缺少 status 字段")
                if 'detail' not in event:
                    errors.append("task_update 缺少 detail 字段")
                else:
                    detail = event.get('detail', {})
                    if 'stage' not in detail:
                        errors.append("detail 缺少 stage 字段")
                    if 'message' not in detail:
                        errors.append("detail 缺少 message 字段")
            
            # 验证 execution_complete
            elif event_type == 'execution_complete':
                if 'success' not in event:
                    errors.append("execution_complete 缺少 success 字段")
                if 'summary' not in event:
                    errors.append("execution_complete 缺少 summary 字段")
            
            # 验证 assistant_message
            elif event_type == 'assistant_message':
                if 'content' not in event:
                    errors.append("assistant_message 缺少 content 字段")
        
        return {
            "success": len(errors) == 0,
            "errors": errors
        }


# ============== 测试执行 ==============
async def run_test_scene(tester: WebSocketTester, scene: Dict[str, Any]) -> Dict[str, Any]:
    """执行单个测试场景"""
    print("\n" + "=" * 60)
    print(f"测试场景: {scene['name']}")
    print("=" * 60)
    print(f"输入: {scene['input']}")
    print(f"预期工具: {scene['expected_tools']}")
    
    result = {
        "name": scene['name'],
        "input": scene['input'],
        "success": False,
        "events": [],
        "validation": {},
        "errors": []
    }
    
    try:
        # 连接
        if not await tester.connect():
            result["errors"].append("连接失败")
            return result
        
        # 发送消息
        if not await tester.send_message(scene['input']):
            result["errors"].append("发送消息失败")
            return result
        
        # 接收事件
        events = await tester.receive_events(timeout=120.0)
        result["events"] = [e.get('type') for e in events]
        
        # 验证事件顺序
        event_validation = tester.validate_events(scene['expected_events'])
        result["validation"]["events"] = event_validation
        
        if event_validation["missing"]:
            result["errors"].append(f"缺少事件: {event_validation['missing']}")
        
        # 验证数据结构
        data_validation = tester.validate_data_structure()
        result["validation"]["data"] = data_validation
        
        if data_validation["errors"]:
            result["errors"].extend(data_validation["errors"])
        
        # 检查是否有错误事件
        error_events = [e for e in events if e.get('type') == 'error']
        if error_events:
            for err in error_events:
                result["errors"].append(f"错误事件: {err.get('message', 'Unknown')}")
        
        # 最终判断
        result["success"] = len(result["errors"]) == 0
        
    except Exception as e:
        result["errors"].append(f"异常: {str(e)}")
    finally:
        await tester.close()
    
    return result


async def main():
    """主测试程序"""
    print("=" * 60)
    print("基于真实 MCP 工具的 WebSocket 全流程测试")
    print("=" * 60)
    
    # 检查 API Key
    api_key = check_api_key()
    print(f"\n✓ API Key 已配置: {api_key[:10]}...")
    
    # 测试场景列表
    scenes = [
        SCENE_FILESYSTEM,
        SCENE_DOCUMENT,
        SCENE_WEB_SEARCH,
        SCENE_COMBINED,
    ]
    
    # 执行测试
    results = []
    
    for scene in scenes:
        tester = WebSocketTester()
        result = await run_test_scene(tester, scene)
        results.append(result)
        
        # 场景间等待，避免冲突
        await asyncio.sleep(2)
    
    # 生成报告
    print("\n" + "=" * 60)
    print("测试报告")
    print("=" * 60)
    
    passed = sum(1 for r in results if r["success"])
    failed = len(results) - passed
    
    print(f"\n总计: {len(results)} 个场景")
    print(f"通过: {passed} 个")
    print(f"失败: {failed} 个")
    
    print("\n详细结果:")
    for result in results:
        status = "✓" if result["success"] else "✗"
        print(f"\n{status} {result['name']}")
        print(f"  输入: {result['input']}")
        print(f"  事件: {result['events']}")
        
        if result["errors"]:
            print(f"  错误:")
            for error in result["errors"]:
                print(f"    - {error}")
    
    print("\n" + "=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
