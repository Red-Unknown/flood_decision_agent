"""
智能解析引擎模块

使用LLM进行水利数据的智能提取和解析
"""

import json
import re
from typing import Any, Dict, List, Optional, Type, Union
from dataclasses import dataclass, field

from .schema import (
    HydraulicDataSchema,
    DataType,
    FieldDefinition,
    get_schema,
    list_available_schemas
)

from flood_decision_agent.agents.prompts import BasePrompts, AgentRole


@dataclass
class ParsedDataResult:
    """解析结果类"""
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    schema_type: str = ""
    raw_input: str = ""
    confidence: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "data": self.data,
            "schema_type": self.schema_type,
            "raw_input": self.raw_input,
            "confidence": self.confidence,
            "errors": self.errors,
            "warnings": self.warnings,
            "extraction_metadata": self.extraction_metadata
        }
    
    def is_valid(self) -> bool:
        """检查结果是否有效"""
        return self.success and len(self.errors) == 0


class IntelligentParserEngine:
    """
    智能解析引擎
    
    使用LLM从非结构化文本中提取结构化水利数据
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        """
        初始化解析引擎
        
        Args:
            llm_client: LLM客户端实例，用于调用语言模型
        """
        self._llm_client = llm_client
        self._extraction_history: List[Dict[str, Any]] = []
    
    def parse(
        self,
        raw_input: str,
        schema_type: str,
        confidence_threshold: float = 0.6
    ) -> ParsedDataResult:
        """
        解析原始输入数据
        
        Args:
            raw_input: 原始输入文本
            schema_type: Schema类型名称
            confidence_threshold: 置信度阈值
            
        Returns:
            ParsedDataResult: 解析结果
        """
        # 获取Schema
        schema = get_schema(schema_type)
        if not schema:
            return ParsedDataResult(
                success=False,
                schema_type=schema_type,
                raw_input=raw_input,
                errors=[f"未知的Schema类型: {schema_type}. 可用类型: {list_available_schemas()}"]
            )
        
        # 构建提取提示
        prompt_data = self._build_extraction_prompt(schema, raw_input)
        
        # 使用LLM提取数据
        try:
            extracted_data = self._extract_from_llm(prompt_data)
        except Exception as e:
            return ParsedDataResult(
                success=False,
                schema_type=schema_type,
                raw_input=raw_input,
                errors=[f"LLM提取失败: {str(e)}"]
            )
        
        # 后处理提取的数据
        processed_data = self._post_process_data(extracted_data, schema)
        
        # 计算置信度
        confidence = self._calculate_confidence(processed_data, schema, raw_input)
        
        # 收集警告
        warnings = self._collect_warnings(processed_data, schema)
        
        # 检查置信度
        if confidence < confidence_threshold:
            warnings.append(f"置信度 {confidence:.2f} 低于阈值 {confidence_threshold}")
        
        result = ParsedDataResult(
            success=True,
            data=processed_data,
            schema_type=schema_type,
            raw_input=raw_input,
            confidence=confidence,
            warnings=warnings,
            extraction_metadata={
                "prompt_length": len(prompt_data.get("prompt", "")),
                "raw_response": extracted_data.get("_raw_response", ""),
                "fields_extracted": len(processed_data)
            }
        )
        
        # 记录历史
        self._extraction_history.append(result.to_dict())
        
        return result
    
    def _build_extraction_prompt(
        self,
        schema: HydraulicDataSchema,
        raw_input: str
    ) -> Dict[str, str]:
        """
        构建数据提取提示词
        
        Args:
            schema: 数据Schema
            raw_input: 原始输入文本
            
        Returns:
            包含 system_prompt 和 prompt 的字典
        """
        metadata = schema.metadata
        fields = schema.fields
        
        # 构建字段描述
        field_descriptions = []
        for field_def in fields:
            req_mark = "[必填]" if field_def.required else "[可选]"
            range_str = ""
            if field_def.min_value is not None and field_def.max_value is not None:
                range_str = f"，范围: {field_def.min_value}~{field_def.max_value}"
            elif field_def.min_value is not None:
                range_str = f"，最小值: {field_def.min_value}"
            elif field_def.max_value is not None:
                range_str = f"，最大值: {field_def.max_value}"
            
            unit_str = f"，单位: {field_def.unit}" if field_def.unit else ""
            example_str = ""
            if field_def.examples:
                example_str = f"，示例: {field_def.examples[0]}"
            
            field_descriptions.append(
                f"- {field_def.name} {req_mark}: {field_def.description}"
                f"{range_str}{unit_str}{example_str}"
            )
        
        system_prompt = BasePrompts.get_system_prompt(AgentRole.DATA_EXTRACTOR)
        
        prompt = f"""请从以下文本中提取结构化的{metadata.description}。

## 数据Schema

数据类型: {metadata.name}
说明: {metadata.description}

## 字段定义

{chr(10).join(field_descriptions)}

## 原始文本

```
{raw_input}
```

## 提取要求

1. 仔细阅读原始文本，提取所有与字段定义相关的信息
2. 对于数值字段，只返回数值，不要包含单位
3. 如果文本中缺少某些字段的信息，使用null表示
4. 确保数值在有效范围内
5. 返回严格的JSON格式，不要添加任何解释说明

## 输出格式

请以JSON格式返回提取结果，格式如下：
{{
{chr(10).join([f'    "{f.name}": <值或null>' for f in fields])}
}}

请只返回JSON，不要添加任何其他内容。"""
        
        return {
            "system_prompt": system_prompt,
            "prompt": prompt
        }
    
    def _extract_from_llm(self, prompt_data: Dict[str, str]) -> Dict[str, Any]:
        """
        使用LLM提取数据
        
        Args:
            prompt_data: 包含 system_prompt 和 prompt 的字典
            
        Returns:
            提取的数据字典
        """
        prompt = prompt_data.get("prompt", "")
        
        if self._llm_client is None:
            # 模拟LLM响应（用于测试）
            return self._simulate_extraction(prompt)
        
        # 调用LLM客户端
        try:
            response = self._llm_client.complete(prompt)
            raw_response = response if isinstance(response, str) else response.get("text", "")
            
            # 解析JSON响应
            data = self._parse_json_response(raw_response)
            data["_raw_response"] = raw_response
            return data
        except Exception as e:
            raise RuntimeError(f"LLM调用失败: {str(e)}")
    
    def _simulate_extraction(self, prompt: str) -> Dict[str, Any]:
        """
        模拟数据提取（用于测试）
        
        Args:
            prompt: 提示词
            
        Returns:
            模拟的提取结果
        """
        # 从提示中提取原始文本
        raw_match = re.search(r'## 原始文本\n\n```\n(.*?)\n```', prompt, re.DOTALL)
        raw_text = raw_match.group(1) if raw_match else ""
        
        # 简单的模式匹配提取
        result = {}
        
        # 河道断面数据提取模式
        if "河道断面" in prompt or "river_cross_section" in prompt:
            result = self._extract_river_cross_section(raw_text)
        # 糙率系数数据提取模式
        elif "糙率" in prompt or "roughness" in prompt:
            result = self._extract_roughness(raw_text)
        # 降雨径流数据提取模式
        elif "降雨" in prompt or "rainfall" in prompt:
            result = self._extract_rainfall_runoff(raw_text)
        
        result["_raw_response"] = json.dumps(result, ensure_ascii=False)
        return result
    
    def _extract_river_cross_section(self, text: str) -> Dict[str, Any]:
        """提取河道断面数据"""
        result = {}
        
        # 断面名称
        name_match = re.search(r'断面[：:]\s*([^\n，。]+)', text)
        result["section_name"] = name_match.group(1).strip() if name_match else None
        
        # 高程
        elevation_match = re.search(r'高程[：:]\s*(\d+\.?\d*)\s*米', text)
        result["elevation"] = float(elevation_match.group(1)) if elevation_match else None
        
        # 宽度
        width_match = re.search(r'宽度[：:]\s*(\d+\.?\d*)\s*米', text)
        result["width"] = float(width_match.group(1)) if width_match else None
        
        # 边坡
        slope_match = re.search(r'边坡[：:]\s*(\d+\.?\d*)', text)
        if slope_match:
            result["left_slope"] = float(slope_match.group(1))
            result["right_slope"] = float(slope_match.group(1))
        else:
            left_slope_match = re.search(r'左岸.*?边坡[：:]\s*(\d+\.?\d*)', text)
            result["left_slope"] = float(left_slope_match.group(1)) if left_slope_match else None
            right_slope_match = re.search(r'右岸.*?边坡[：:]\s*(\d+\.?\d*)', text)
            result["right_slope"] = float(right_slope_match.group(1)) if right_slope_match else None
        
        # 水位
        water_level_match = re.search(r'水位[：:]\s*(\d+\.?\d*)\s*米', text)
        result["water_level"] = float(water_level_match.group(1)) if water_level_match else None
        
        # 糙率
        roughness_match = re.search(r'糙率[：:]\s*(0\.\d+)', text)
        result["roughness"] = float(roughness_match.group(1)) if roughness_match else None
        
        # 位置
        location_match = re.search(r'位置[：:]\s*([^\n，。]+)', text)
        result["location"] = location_match.group(1).strip() if location_match else None
        
        return result
    
    def _extract_roughness(self, text: str) -> Dict[str, Any]:
        """提取糙率系数数据"""
        result = {}
        
        # 断面编号
        section_match = re.search(r'断面[编号]*[：:]\s*([^\n，。]+)', text)
        result["section_id"] = section_match.group(1).strip() if section_match else None
        
        # 主槽糙率
        main_n_match = re.search(r'主槽.*?糙率[：:]\s*(0\.\d+)', text)
        result["main_channel_n"] = float(main_n_match.group(1)) if main_n_match else None
        
        # 左岸糙率
        left_n_match = re.search(r'左岸.*?糙率[：:]\s*(0\.\d+)', text)
        result["left_bank_n"] = float(left_n_match.group(1)) if left_n_match else None
        
        # 右岸糙率
        right_n_match = re.search(r'右岸.*?糙率[：:]\s*(0\.\d+)', text)
        result["right_bank_n"] = float(right_n_match.group(1)) if right_n_match else None
        
        # 植被类型
        vegetation_match = re.search(r'植被[：:]\s*([^\n，。]+)', text)
        result["vegetation_type"] = vegetation_match.group(1).strip() if vegetation_match else None
        
        # 河床质
        bed_match = re.search(r'河床质[：:]\s*([^\n，。]+)', text)
        result["bed_material"] = bed_match.group(1).strip() if bed_match else None
        
        return result
    
    def _extract_rainfall_runoff(self, text: str) -> Dict[str, Any]:
        """提取降雨径流数据"""
        result = {}
        
        # 事件编号
        event_match = re.search(r'事件[编号]*[：:]\s*([^\n，。]+)', text)
        result["event_id"] = event_match.group(1).strip() if event_match else None
        
        # 降雨历时
        duration_match = re.search(r'历时[：:]\s*(\d+\.?\d*)\s*小时', text)
        result["rainfall_duration"] = float(duration_match.group(1)) if duration_match else None
        
        # 降雨总量
        total_match = re.search(r'总量[：:]\s*(\d+\.?\d*)\s*毫米', text)
        result["total_rainfall"] = float(total_match.group(1)) if total_match else None
        
        # 峰值雨强
        peak_match = re.search(r'峰值.*?雨强[：:]\s*(\d+\.?\d*)\s*毫米', text)
        result["peak_intensity"] = float(peak_match.group(1)) if peak_match else None
        
        # 流域面积
        area_match = re.search(r'流域面积[：:]\s*(\d+\.?\d*)\s*平方公里', text)
        result["catchment_area"] = float(area_match.group(1)) if area_match else None
        
        # 径流系数
        runoff_match = re.search(r'径流系数[：:]\s*(0\.\d+)', text)
        result["runoff_coefficient"] = float(runoff_match.group(1)) if runoff_match else None
        
        # 洪峰流量
        flow_match = re.search(r'洪峰流量[：:]\s*(\d+\.?\d*)\s*立方米', text)
        result["peak_flow"] = float(flow_match.group(1)) if flow_match else None
        
        # 重现期
        return_match = re.search(r'(\d+)\s*年一遇', text)
        result["return_period"] = int(return_match.group(1)) if return_match else None
        
        return result
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        解析LLM的JSON响应
        
        Args:
            response: LLM响应文本
            
        Returns:
            解析后的字典
        """
        # 尝试直接解析
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # 尝试提取JSON代码块
        json_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
        matches = re.findall(json_pattern, response, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue
        
        # 尝试提取花括号内容
        brace_pattern = r'\{[\s\S]*\}'
        brace_match = re.search(brace_pattern, response)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # 返回空字典
        return {}
    
    def _post_process_data(
        self,
        data: Dict[str, Any],
        schema: HydraulicDataSchema
    ) -> Dict[str, Any]:
        """
        后处理提取的数据
        
        Args:
            data: 提取的原始数据
            schema: 数据Schema
            
        Returns:
            处理后的数据
        """
        result = {}
        
        for field_def in schema.fields:
            value = data.get(field_def.name)
            
            # 跳过None值
            if value is None:
                continue
            
            # 类型转换
            try:
                if field_def.data_type == DataType.FLOAT:
                    value = float(value)
                elif field_def.data_type == DataType.INTEGER:
                    value = int(float(value))
                elif field_def.data_type == DataType.STRING:
                    value = str(value)
                elif field_def.data_type == DataType.BOOLEAN:
                    value = bool(value)
            except (ValueError, TypeError):
                continue
            
            result[field_def.name] = value
        
        return result
    
    def _calculate_confidence(
        self,
        data: Dict[str, Any],
        schema: HydraulicDataSchema,
        raw_input: str
    ) -> float:
        """
        计算提取结果的置信度
        
        Args:
            data: 提取的数据
            schema: 数据Schema
            raw_input: 原始输入
            
        Returns:
            置信度分数 (0.0-1.0)
        """
        if not data:
            return 0.0
        
        required_fields = schema.get_required_fields()
        if not required_fields:
            return 0.5
        
        # 计算必填字段的填充率
        filled_required = sum(1 for f in required_fields if f.name in data and data[f.name] is not None)
        required_ratio = filled_required / len(required_fields)
        
        # 计算所有字段的填充率
        all_fields = schema.fields
        filled_all = sum(1 for f in all_fields if f.name in data and data[f.name] is not None)
        all_ratio = filled_all / len(all_fields) if all_fields else 0
        
        # 综合置信度（必填字段权重更高）
        confidence = required_ratio * 0.7 + all_ratio * 0.3
        
        return min(1.0, max(0.0, confidence))
    
    def _collect_warnings(
        self,
        data: Dict[str, Any],
        schema: HydraulicDataSchema
    ) -> List[str]:
        """
        收集数据警告
        
        Args:
            data: 提取的数据
            schema: 数据Schema
            
        Returns:
            警告列表
        """
        warnings = []
        
        # 检查必填字段缺失
        for field_def in schema.get_required_fields():
            if field_def.name not in data or data[field_def.name] is None:
                warnings.append(f"必填字段缺失: {field_def.name} ({field_def.description})")
        
        # 检查数值范围
        for field_name, value in data.items():
            field_def = schema.get_field(field_name)
            if field_def and field_def.data_type in (DataType.FLOAT, DataType.INTEGER):
                if value is not None:
                    if field_def.min_value is not None and value < field_def.min_value:
                        warnings.append(f"字段 {field_name} 的值 {value} 小于最小值 {field_def.min_value}")
                    if field_def.max_value is not None and value > field_def.max_value:
                        warnings.append(f"字段 {field_name} 的值 {value} 大于最大值 {field_def.max_value}")
        
        return warnings
    
    def get_extraction_history(self) -> List[Dict[str, Any]]:
        """获取提取历史记录"""
        return self._extraction_history.copy()
    
    def clear_history(self) -> None:
        """清除提取历史"""
        self._extraction_history.clear()
