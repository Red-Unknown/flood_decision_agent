"""交互式多轮对话示例.

支持多轮对话、上下文保持和流程调整。
"""

from __future__ import annotations

import sys
from typing import Optional

from flood_decision_agent.app.visualized_pipeline import VisualizedPipeline
from flood_decision_agent.conversation.manager import ConversationManager
from flood_decision_agent.infra.kimi_guard import require_kimi_api_key


def create_pipeline():
    """创建Pipeline实例."""
    return VisualizedPipeline(visualizer=None)


def print_banner():
    """打印欢迎信息."""
    print("\n" + "=" * 70)
    print("  水利智脑 - 交互式多轮对话")
    print("=" * 70)
    print("\n支持功能：")
    print("  • 多轮对话，自动保持上下文")
    print("  • 智能识别追问、补充、新话题")
    print("  • 流式输出，实时显示AI回答")
    print("\n操作提示：")
    print("  • 输入 'exit' 或 'quit' 退出")
    print("  • 输入 'new' 开启新对话")
    print("  • 输入 'status' 查看对话状态")
    print("  • 输入 'clear' 清空当前对话")
    print("=" * 70 + "\n")


def main():
    """主函数."""
    # 检查API Key
    try:
        require_kimi_api_key()
    except SystemExit:
        print("错误：需要配置 KIMI_API_KEY 环境变量")
        sys.exit(1)
    
    print_banner()
    
    # 创建对话管理器
    manager = ConversationManager(
        pipeline_factory=create_pipeline,
        max_conversations=10,
        conversation_timeout=1800,  # 30分钟
    )
    
    # 当前对话ID
    conversation_id: Optional[str] = None
    
    print("[系统] 已创建新对话，请输入您的问题...\n")
    
    while True:
        try:
            # 获取用户输入
            user_input = input("您: ").strip()
            
            if not user_input:
                continue
            
            # 处理特殊命令
            if user_input.lower() in ['exit', 'quit', '退出']:
                print("\n[系统] 感谢使用，再见！")
                break
            
            elif user_input.lower() == 'new':
                conversation_id = None
                print("\n[系统] 已开启新对话\n")
                continue
            
            elif user_input.lower() == 'status':
                if conversation_id:
                    summary = manager.get_conversation_summary(conversation_id)
                    if summary:
                        print(f"\n[对话状态]")
                        print(f"  对话ID: {summary['conversation_id']}")
                        print(f"  状态: {summary['status']}")
                        print(f"  轮数: {summary['turn_count']}")
                        print(f"  当前任务: {summary['current_task']}")
                        print(f"  持续时间: {summary['duration_minutes']:.1f} 分钟")
                        print()
                    else:
                        print("\n[系统] 对话不存在或已过期\n")
                else:
                    print("\n[系统] 当前无活跃对话\n")
                continue
            
            elif user_input.lower() == 'clear':
                if conversation_id:
                    manager.end_conversation(conversation_id)
                    print("\n[系统] 已清空当前对话\n")
                    conversation_id = None
                else:
                    print("\n[系统] 当前无活跃对话\n")
                continue
            
            # 处理用户输入
            print()  # 空行
            result = manager.process_input(
                conversation_id=conversation_id,
                user_input=user_input
            )
            
            # 保存对话ID
            conversation_id = result.get("conversation_id")
            
            # 显示流程信息
            if result.get("is_new_conversation"):
                print(f"[系统] 新对话已创建 (ID: {conversation_id})")
            
            flow_action = result.get("flow_action", "unknown")
            if flow_action == "expand_task":
                print("[系统] 识别为追问/补充，继续当前话题")
            elif flow_action == "new_task":
                print("[系统] 识别为新话题，开始新任务")
            
            print()
            
        except KeyboardInterrupt:
            print("\n\n[系统] 收到中断信号，正在退出...")
            break
        except Exception as e:
            print(f"\n[错误] {str(e)}\n")


if __name__ == "__main__":
    main()
