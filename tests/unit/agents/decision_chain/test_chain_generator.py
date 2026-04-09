"""
ChainGenerator 单元测试

测试流式决策链生成器的各种功能。
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from flood_decision_agent.agents.decision_chain.chain_generator import (
    ChainGenerator,
    GenerationEvent,
    GenerationResult,
    GenerationStage,
)
from flood_decision_agent.agents.intent_parser.parser import TaskIntent
from flood_decision_agent.agents.decision_chain.task_decomposer import TaskType
from flood_decision_agent.core.task_graph import TaskGraph


class TestChainGenerator:
    """测试 ChainGenerator 类"""

    @pytest.fixture
    def generator(self):
        """创建 ChainGenerator 实例"""
        return ChainGenerator()

    @pytest.fixture
    def mock_intent(self):
        """创建模拟意图"""
        intent = Mock(spec=TaskIntent)
        intent.task_type = TaskType.DATA_COLLECTION
        intent.goal = {"description": "测试目标", "params": {}}
        intent.constraints = []
        intent.error_message = None
        return intent

    @pytest.mark.asyncio
    async def test_generate_normal_mode(self, generator, mock_intent):
        """测试普通模式生成"""
        with patch.object(generator._intent_parser, 'parse_natural_language', return_value=mock_intent):
            with patch.object(generator._base_generator, '_decompose_tasks', return_value=[]):
                with patch.object(generator._base_generator, '_optimize_chain', return_value=([], 0.8, [])):
                    with patch.object(generator._base_generator, '_build_task_graph', return_value=TaskGraph()):
                        events = []
                        async for event in generator.generate("测试输入"):
                            events.append(event)
                            assert isinstance(event, GenerationEvent)
                            assert isinstance(event.stage, GenerationStage)
                            assert 0.0 <= event.progress <= 1.0
                        
                        # 验证事件序列
                        stages = [e.stage for e in events]
                        assert GenerationStage.INTENT_PARSING in stages
                        assert GenerationStage.COMPLETED in stages
                        
                        # 验证最终结果
                        result = generator.get_last_result()
                        assert result is not None
                        assert isinstance(result.task_graph, TaskGraph)

    @pytest.mark.asyncio
    async def test_generate_with_intent_error(self, generator):
        """测试意图解析错误处理"""
        error_intent = Mock(spec=TaskIntent)
        error_intent.error_message = "意图解析失败"
        
        with patch.object(generator._intent_parser, 'parse_natural_language', return_value=error_intent):
            events = []
            async for event in generator.generate("测试输入"):
                events.append(event)
            
            # 验证错误事件
            error_events = [e for e in events if e.stage == GenerationStage.ERROR]
            assert len(error_events) > 0
            
            # 验证结果
            result = generator.get_last_result()
            assert result is not None
            assert not result.success
            assert "意图解析失败" in result.error_message

    @pytest.mark.asyncio
    async def test_generate_from_plan(self, generator):
        """测试 Plan 模式生成"""
        plan_document = """
# 实施步骤

1. **数据收集**（预计耗时：1天）
   - 具体内容：收集水位数据
   - 交付物：数据报告

2. **数据分析**（预计耗时：2天）
   - 具体内容：分析水位趋势
   - 交付物：分析报告
"""
        
        with patch.object(generator._base_generator, '_extract_implementation_steps', return_value=["步骤1", "步骤2"]):
            with patch.object(generator._base_generator, '_steps_to_task_nodes', return_value=[]):
                with patch.object(generator._base_generator, '_optimize_chain', return_value=([], 0.75, [])):
                    with patch.object(generator._base_generator, '_build_task_graph', return_value=TaskGraph()):
                        events = []
                        async for event in generator.generate_from_plan(plan_document, "测试输入"):
                            events.append(event)
                        
                        # 验证事件序列
                        stages = [e.stage for e in events]
                        assert GenerationStage.INTENT_PARSING in stages
                        assert GenerationStage.COMPLETED in stages

    @pytest.mark.asyncio
    async def test_generate_from_plan_empty_steps(self, generator):
        """测试 Plan 模式空步骤处理"""
        with patch.object(generator._base_generator, '_extract_implementation_steps', return_value=[]):
            events = []
            async for event in generator.generate_from_plan("空文档", "测试输入"):
                events.append(event)
            
            # 验证错误事件
            error_events = [e for e in events if e.stage == GenerationStage.ERROR]
            assert len(error_events) > 0
            
            result = generator.get_last_result()
            assert not result.success

    @pytest.mark.asyncio
    async def test_generate_from_spec(self, generator):
        """测试 Spec 模式生成"""
        spec_document = """
# 规格说明

## 功能概述
实现水位监测功能

## 任务分解
1. **数据采集**
2. **数据处理**
"""
        
        # Spec 模式复用 Plan 模式逻辑
        with patch.object(generator._base_generator, '_extract_implementation_steps', return_value=["步骤1"]):
            with patch.object(generator._base_generator, '_steps_to_task_nodes', return_value=[]):
                with patch.object(generator._base_generator, '_optimize_chain', return_value=([], 0.8, [])):
                    with patch.object(generator._base_generator, '_build_task_graph', return_value=TaskGraph()):
                        events = []
                        async for event in generator.generate_from_spec(spec_document, "测试输入"):
                            events.append(event)
                        
                        # 验证事件序列
                        stages = [e.stage for e in events]
                        assert GenerationStage.COMPLETED in stages

    def test_get_last_result_before_generation(self, generator):
        """测试生成前获取结果"""
        result = generator.get_last_result()
        assert result is None

    def test_reset(self, generator):
        """测试重置功能"""
        # 设置一些状态
        generator._last_result = GenerationResult(
            task_graph=TaskGraph(),
            metadata={},
            success=True,
        )
        
        # 重置
        generator.reset()
        
        # 验证状态已清除
        assert generator.get_last_result() is None

    @pytest.mark.asyncio
    async def test_generate_exception_handling(self, generator):
        """测试异常处理"""
        with patch.object(generator._intent_parser, 'parse_natural_language', side_effect=Exception("测试异常")):
            events = []
            async for event in generator.generate("测试输入"):
                events.append(event)
            
            # 验证错误事件
            error_events = [e for e in events if e.stage == GenerationStage.ERROR]
            assert len(error_events) > 0
            assert "测试异常" in error_events[0].message
            
            # 验证结果
            result = generator.get_last_result()
            assert not result.success
            assert "测试异常" in result.error_message


class TestGenerationEvent:
    """测试 GenerationEvent 数据类"""

    def test_event_creation(self):
        """测试事件创建"""
        event = GenerationEvent(
            stage=GenerationStage.INTENT_PARSING,
            progress=0.5,
            message="测试消息",
            data={"key": "value"},
        )
        
        assert event.stage == GenerationStage.INTENT_PARSING
        assert event.progress == 0.5
        assert event.message == "测试消息"
        assert event.data == {"key": "value"}

    def test_event_without_data(self):
        """测试无数据事件"""
        event = GenerationEvent(
            stage=GenerationStage.COMPLETED,
            progress=1.0,
            message="完成",
        )
        
        assert event.data is None


class TestGenerationResult:
    """测试 GenerationResult 数据类"""

    def test_success_result(self):
        """测试成功结果"""
        result = GenerationResult(
            task_graph=TaskGraph(),
            metadata={"key": "value"},
            success=True,
        )
        
        assert result.success
        assert result.error_message is None
        assert isinstance(result.task_graph, TaskGraph)

    def test_failed_result(self):
        """测试失败结果"""
        result = GenerationResult(
            task_graph=TaskGraph(),
            metadata={"error": "测试错误"},
            success=False,
            error_message="测试错误",
        )
        
        assert not result.success
        assert result.error_message == "测试错误"


class TestGenerationStage:
    """测试 GenerationStage 枚举"""

    def test_stage_values(self):
        """测试阶段值"""
        assert GenerationStage.INTENT_PARSING.value == "intent_parsing"
        assert GenerationStage.TASK_DECOMPOSITION.value == "task_decomposition"
        assert GenerationStage.CHAIN_OPTIMIZATION.value == "chain_optimization"
        assert GenerationStage.TASK_GRAPH_BUILDING.value == "task_graph_building"
        assert GenerationStage.COMPLETED.value == "completed"
        assert GenerationStage.ERROR.value == "error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
