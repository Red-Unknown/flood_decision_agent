"""经验公式计算模块。

提供水文水利计算中常用的经验公式。
"""

import math
from typing import Optional, Dict, Any


class EmpiricalFormulaCalculator:
    """经验公式计算器。"""

    @staticmethod
    def calculate_roughness(
        soil_type: str = None,
        vegetation: str = None,
        condition: str = None,
        channel_type: str = None,
    ) -> Optional[float]:
        """根据条件计算糙率系数。

        基于《水文手册》和工程经验公式。

        Args:
            soil_type: 土壤类型 (黏土/壤土/砂土/砾石)
            vegetation: 植被覆盖 (裸土/草地/灌木/森林)
            condition: 河道状况 (清洁顺直/清洁弯曲/有浅滩深潭/多石块杂草/山区急流)
            channel_type: 人工渠道类型 (混凝土/砌石/土渠)

        Returns:
            糙率系数值，无法计算时返回 None
        """
        from .config import DefaultValueConfig

        # 优先使用配置表中的精确值
        roughness = DefaultValueConfig.get_roughness(
            soil_type=soil_type,
            vegetation=vegetation,
            condition=condition,
            channel_type=channel_type,
        )

        if roughness is not None:
            return roughness

        # 使用经验公式估算
        base_roughness = 0.025

        # 土壤类型调整
        soil_factors = {
            "黏土": 1.2,
            "壤土": 1.0,
            "砂土": 0.8,
            "砾石": 1.4,
        }

        # 植被覆盖调整
        vegetation_factors = {
            "裸土": 1.0,
            "草地": 1.3,
            "灌木": 1.6,
            "森林": 2.2,
        }

        # 河道状况调整
        condition_factors = {
            "清洁顺直": 1.0,
            "清洁弯曲": 1.2,
            "有浅滩深潭": 1.4,
            "多石块杂草": 1.6,
            "山区急流": 2.0,
        }

        factor = 1.0
        if soil_type:
            factor *= soil_factors.get(soil_type, 1.0)
        if vegetation:
            factor *= vegetation_factors.get(vegetation, 1.0)
        if condition:
            factor *= condition_factors.get(condition, 1.0)

        return base_roughness * factor

    @staticmethod
    def calculate_flood_peak(
        rainfall_duration: float,
        total_rainfall: float,
        basin_area: float,
        runoff_coefficient: float = 0.7,
        concentration_time: float = None,
    ) -> Optional[float]:
        """使用推理公式计算洪峰流量。

        公式: Q = 0.278 * α * H * A / t
        其中:
        - Q: 洪峰流量 (m³/s)
        - α: 径流系数
        - H: 降雨量 (mm)
        - A: 流域面积 (km²)
        - t: 汇流时间 (h)

        Args:
            rainfall_duration: 降雨历时 (小时)
            total_rainfall: 降雨总量 (mm)
            basin_area: 流域面积 (km²)
            runoff_coefficient: 径流系数 (默认0.7)
            concentration_time: 汇流时间 (小时)，不指定则使用降雨历时

        Returns:
            洪峰流量 (m³/s)，计算失败返回 None
        """
        if not all([rainfall_duration > 0, total_rainfall > 0, basin_area > 0]):
            return None

        t = concentration_time if concentration_time else rainfall_duration

        # 推理公式
        q = 0.278 * runoff_coefficient * total_rainfall * basin_area / t

        return round(q, 2)

    @staticmethod
    def calculate_runoff_coefficient(
        land_use: str,
        soil_type: str,
        slope: float = None,
    ) -> Optional[float]:
        """计算径流系数。

        基于土地利用类型和土壤类型的综合计算。

        Args:
            land_use: 土地利用类型
            soil_type: 土壤类型
            slope: 坡度 (可选)

        Returns:
            径流系数 (0-1)，计算失败返回 None
        """
        from .config import DefaultValueConfig

        # 基础径流系数
        base_coefficient = DefaultValueConfig.get_runoff_coefficient(land_use)

        if base_coefficient is None:
            # 默认值
            land_use_coefficients = {
                "商业区": 0.75,
                "住宅区": 0.50,
                "工业区": 0.70,
                "公园绿地": 0.15,
                "农田": 0.25,
                "裸地": 0.35,
            }
            base_coefficient = land_use_coefficients.get(land_use, 0.50)

        # 土壤类型调整
        soil_adjustments = {
            "沙土": -0.10,
            "壤土": 0.0,
            "黏土": 0.10,
            "岩石": 0.15,
        }

        adjustment = soil_adjustments.get(soil_type, 0.0)

        # 坡度调整
        if slope:
            if slope < 0.05:
                adjustment -= 0.05
            elif slope > 0.20:
                adjustment += 0.10

        coefficient = base_coefficient + adjustment

        # 限制在合理范围内
        return max(0.05, min(0.95, coefficient))

    @staticmethod
    def calculate_concentration_time(
        basin_length: float,
        slope: float,
        coefficient: float = 0.5,
        method: str = "kirpich",
    ) -> Optional[float]:
        """计算汇流时间。

        Args:
            basin_length: 流域长度 (km)
            slope: 河道坡度 (m/m)
            coefficient: 经验系数
            method: 计算方法 (kirpich/kerby/faa)

        Returns:
            汇流时间 (小时)，计算失败返回 None
        """
        if not all([basin_length > 0, slope > 0]):
            return None

        if method == "kirpich":
            # Kirpich公式: tc = 0.0195 * L^0.77 * S^-0.385
            tc = 0.0195 * (basin_length * 1000) ** 0.77 * (slope * 100) ** (-0.385)
        elif method == "kerby":
            # Kerby公式: tc = 0.83 * (L * N / S^0.5)^0.467
            n = coefficient  # 粗糙系数
            tc = 0.83 * (basin_length * n / math.sqrt(slope)) ** 0.467
        elif method == "faa":
            # FAA公式简化版
            tc = 0.5 * (basin_length / (slope ** 0.5)) ** 0.6
        else:
            return None

        # 转换为小时
        tc_hours = tc / 60.0

        return round(tc_hours, 2)

    @staticmethod
    def calculate_channel_velocity(
        hydraulic_radius: float,
        slope: float,
        roughness: float,
    ) -> Optional[float]:
        """使用曼宁公式计算流速。

        公式: V = (1/n) * R^(2/3) * S^(1/2)

        Args:
            hydraulic_radius: 水力半径 (m)
            slope: 水面比降 (m/m)
            roughness: 糙率系数

        Returns:
            流速 (m/s)，计算失败返回 None
        """
        if not all([hydraulic_radius > 0, slope > 0, roughness > 0]):
            return None

        velocity = (1.0 / roughness) * (hydraulic_radius ** (2.0 / 3.0)) * (slope ** 0.5)

        return round(velocity, 3)

    @staticmethod
    def calculate_flood_volume(
        peak_flow: float,
        duration: float,
        shape_factor: float = 0.8,
    ) -> Optional[float]:
        """计算洪水总量。

        使用简化三角形/梯形法估算。

        Args:
            peak_flow: 洪峰流量 (m³/s)
            duration: 洪水历时 (小时)
            shape_factor: 形状系数 (三角形=0.5, 梯形=0.8)

        Returns:
            洪水总量 (万m³)，计算失败返回 None
        """
        if not all([peak_flow > 0, duration > 0]):
            return None

        # 转换为秒
        duration_seconds = duration * 3600

        # 三角形/梯形面积公式
        volume_m3 = shape_factor * peak_flow * duration_seconds

        # 转换为万m³
        volume_10k = volume_m3 / 10000

        return round(volume_10k, 2)


# 便捷函数

def calculate_roughness(
    soil_type: str = None,
    vegetation: str = None,
    condition: str = None,
    channel_type: str = None,
) -> Optional[float]:
    """计算糙率系数的便捷函数。"""
    return EmpiricalFormulaCalculator.calculate_roughness(
        soil_type, vegetation, condition, channel_type
    )


def calculate_flood_peak(
    rainfall_duration: float,
    total_rainfall: float,
    basin_area: float,
    **kwargs,
) -> Optional[float]:
    """计算洪峰流量的便捷函数。"""
    return EmpiricalFormulaCalculator.calculate_flood_peak(
        rainfall_duration, total_rainfall, basin_area, **kwargs
    )


def calculate_runoff_coefficient(
    land_use: str,
    soil_type: str,
    slope: float = None,
) -> Optional[float]:
    """计算径流系数的便捷函数。"""
    return EmpiricalFormulaCalculator.calculate_runoff_coefficient(
        land_use, soil_type, slope
    )
