"""数据获取服务单元测试。

测试数据获取服务的核心功能。
"""

import pytest
from typing import Dict, Any

from flood_decision_agent.application.services.data_acquisition.models import (
    DataRequest,
    DataResponse,
    DataConfidenceLevel,
    DataSource,
)
from flood_decision_agent.application.services.data_acquisition.service import DataAcquisitionService
from flood_decision_agent.application.services.data_acquisition.adapters.text import TextInputAdapter
from flood_decision_agent.application.services.data_acquisition.adapters.table import TableInputAdapter
from flood_decision_agent.application.services.data_acquisition.adapters.detector import InputFormatDetector
from flood_decision_agent.application.services.data_acquisition.parser.schema import (
    RiverCrossSectionSchema,
    RoughnessCoefficientSchema,
)
from flood_decision_agent.application.services.data_acquisition.parser.validator import DataValidator
from flood_decision_agent.application.services.data_acquisition.confidence.rater import ConfidenceRater
from flood_decision_agent.application.services.data_acquisition.defaults.config import DefaultValueConfig
from flood_decision_agent.application.services.data_acquisition.defaults.formulas import (
    EmpiricalFormulaCalculator,
)
from flood_decision_agent.application.services.data_acquisition.defaults.provider import (
    DefaultValueProvider,
    DefaultValueSourceType,
)


class TestDataAcquisitionModels:
    """测试数据模型。"""

    def test_data_request_creation(self):
        """测试数据请求创建。"""
        request = DataRequest(
            data_key="roughness_coefficient",
            description="河道糙率系数",
            required=True,
        )
        assert request.data_key == "roughness_coefficient"
        assert request.description == "河道糙率系数"
        assert request.required is True

    def test_data_response_creation(self):
        """测试数据响应创建。"""
        response = DataResponse(
            value=0.035,
            source=DataSource.STANDARD_LOOKUP,
            confidence=DataConfidenceLevel.REFERENCE,
        )
        assert response.value == 0.035
        assert response.source == DataSource.STANDARD_LOOKUP
        assert response.confidence == DataConfidenceLevel.REFERENCE


class TestInputAdapters:
    """测试输入适配器。"""

    def test_text_adapter(self):
        """测试文本适配器。"""
        adapter = TextInputAdapter()
        input_data = "断面高程85.5米，底宽100米"
        result = adapter.parse(input_data)
        assert isinstance(result, dict)

    def test_table_adapter_csv(self):
        """测试表格适配器CSV解析。"""
        adapter = TableInputAdapter()
        csv_data = "高程,宽度\n85.5,100\n86.0,120"
        result = adapter.parse(csv_data)
        assert isinstance(result, dict)
        assert result["type"] == "table"
        assert len(result["content"]["records"]) == 2

    def test_input_format_detector_text(self):
        """测试格式检测器-文本。"""
        detector = InputFormatDetector()
        result = detector.detect_format("这是自然语言文本")
        assert result == "text"

    def test_input_format_detector_csv(self):
        """测试格式检测器-CSV。"""
        detector = InputFormatDetector()
        csv_data = "a,b,c\n1,2,3"
        result = detector.detect_format(csv_data)
        assert result == "csv"


class TestSchemas:
    """测试数据Schema。"""

    def test_river_cross_section_schema(self):
        """测试河道断面Schema。"""
        schema = RiverCrossSectionSchema()
        assert schema.schema_name == "river_cross_section"
        field_names = [f.name for f in schema.fields]
        assert "elevation" in field_names
        assert "width" in field_names

    def test_roughness_coefficient_schema(self):
        """测试糙率系数Schema。"""
        schema = RoughnessCoefficientSchema()
        assert schema.schema_name == "roughness_coefficient"
        field_names = [f.name for f in schema.fields]
        assert "main_channel_n" in field_names


class TestDataValidator:
    """测试数据验证器。"""

    def test_roughness_range_validation(self):
        """测试糙率范围验证。"""
        validator = DataValidator()
        schema = RoughnessCoefficientSchema()
        
        # 有效值（提供所有必填字段）
        valid_data = {"section_id": "CS-001", "main_channel_n": 0.035}
        result = validator.validate(valid_data, schema)
        assert result.is_valid
        
        # 无效值（超出范围）
        invalid_data = {"section_id": "CS-002", "main_channel_n": 5.0}
        result = validator.validate(invalid_data, schema)
        assert not result.is_valid

    def test_completeness_check(self):
        """测试完整性检查。"""
        validator = DataValidator()
        schema = RiverCrossSectionSchema()
        
        # 缺失必填字段
        incomplete_data = {"elevation": 85.5}
        result = validator._check_completeness(incomplete_data, schema)
        assert len(result) > 0


class TestConfidenceRater:
    """测试可信度评级。"""

    def test_rate_confidence_measured(self):
        """测试实测数据评级。"""
        rater = ConfidenceRater()
        level = rater.rate_confidence(0.035, DataSource.USER_INPUT, {})
        assert level == DataConfidenceLevel.MEASURED

    def test_rate_confidence_formula(self):
        """测试公式计算评级。"""
        rater = ConfidenceRater()
        level = rater.rate_confidence(0.035, DataSource.FORMULA_CALCULATION, {})
        assert level == DataConfidenceLevel.CALCULATED

    def test_get_confidence_score(self):
        """测试可信度分数。"""
        rater = ConfidenceRater()
        assert rater.get_confidence_score(DataConfidenceLevel.MEASURED) == 1.0
        assert rater.get_confidence_score(DataConfidenceLevel.ASSUMED) == 0.2

    def test_should_request_confirmation(self):
        """测试是否需要确认。"""
        rater = ConfidenceRater()
        assert rater.should_request_confirmation(DataConfidenceLevel.ASSUMED) is True
        assert rater.should_request_confirmation(DataConfidenceLevel.MEASURED) is False


class TestDefaultValueConfig:
    """测试默认值配置。"""

    def test_get_roughness_by_soil_type(self):
        """测试按土壤类型获取糙率。"""
        roughness = DefaultValueConfig.get_roughness(
            soil_type="黏土",
            vegetation="草地"
        )
        assert roughness is not None
        assert 0.01 < roughness < 0.1

    def test_get_roughness_by_condition(self):
        """测试按河道状况获取糙率。"""
        roughness = DefaultValueConfig.get_roughness(
            condition="清洁顺直",
            vegetation="无植被"
        )
        assert roughness is not None

    def test_get_runoff_coefficient(self):
        """测试获取径流系数。"""
        coefficient = DefaultValueConfig.get_runoff_coefficient("商业区", "中心")
        assert coefficient is not None
        assert 0 < coefficient < 1

    def test_get_all_roughness_options(self):
        """测试获取所有糙率选项。"""
        options = DefaultValueConfig.get_all_roughness_options()
        assert "土壤类型" in options
        assert "河道状况" in options


class TestEmpiricalFormulas:
    """测试经验公式。"""

    def test_calculate_roughness(self):
        """测试糙率计算。"""
        calculator = EmpiricalFormulaCalculator()
        roughness = calculator.calculate_roughness(
            soil_type="黏土",
            vegetation="草地"
        )
        assert roughness is not None
        assert 0.01 < roughness < 0.1

    def test_calculate_flood_peak(self):
        """测试洪峰流量计算。"""
        calculator = EmpiricalFormulaCalculator()
        peak = calculator.calculate_flood_peak(
            rainfall_duration=6.0,
            total_rainfall=100.0,
            basin_area=50.0,
            runoff_coefficient=0.7,
        )
        assert peak is not None
        assert peak > 0

    def test_calculate_runoff_coefficient(self):
        """测试径流系数计算。"""
        calculator = EmpiricalFormulaCalculator()
        coefficient = calculator.calculate_runoff_coefficient(
            land_use="住宅区",
            soil_type="壤土",
        )
        assert coefficient is not None
        assert 0 < coefficient < 1

    def test_calculate_concentration_time(self):
        """测试汇流时间计算。"""
        calculator = EmpiricalFormulaCalculator()
        time = calculator.calculate_concentration_time(
            basin_length=5.0,
            slope=0.01,
        )
        assert time is not None
        assert time > 0


class TestDefaultValueProvider:
    """测试默认值提供者。"""

    def test_lookup_from_standard(self):
        """测试规范查表。"""
        provider = DefaultValueProvider()
        value = provider.lookup_from_standard(
            "roughness",
            {"soil_type": "黏土", "vegetation": "草地"}
        )
        assert value is not None
        assert value.source_type == DefaultValueSourceType.STANDARD

    def test_calculate_from_formula(self):
        """测试公式计算。"""
        provider = DefaultValueProvider()
        value = provider.calculate_from_formula(
            "roughness",
            {"soil_type": "黏土", "vegetation": "草地"}
        )
        assert value is not None
        assert value.source_type == DefaultValueSourceType.FORMULA

    def test_get_all_suggestions(self):
        """测试获取所有建议。"""
        provider = DefaultValueProvider()
        suggestions = provider.get_all_suggestions(
            "roughness",
            {"soil_type": "黏土", "vegetation": "草地"}
        )
        assert len(suggestions) > 0
        # 按可信度排序
        for i in range(len(suggestions) - 1):
            assert suggestions[i].confidence >= suggestions[i + 1].confidence


class TestDataAcquisitionService:
    """测试数据获取服务。"""

    def test_service_initialization(self):
        """测试服务初始化。"""
        service = DataAcquisitionService()
        assert service is not None

    def test_request_data(self):
        """测试数据请求。"""
        service = DataAcquisitionService()
        request = DataRequest(
            data_key="test_key",
            description="测试数据",
            required=False,
        )
        response = service.request_data(request)
        assert isinstance(response, DataResponse)

    def test_get_statistics(self):
        """测试获取统计信息。"""
        service = DataAcquisitionService()
        stats = service.get_statistics()
        assert isinstance(stats, dict)
        assert "total_records" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
