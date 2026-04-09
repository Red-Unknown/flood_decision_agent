"""默认值配置模块。

定义洪水决策系统中各类参数的默认值，包括糙率系数、降雨径流参数、河道断面参数等。
"""

from typing import Dict, Any


class DefaultValueConfig:
    """默认值配置类，提供各类水文水利参数的默认值查询。"""

    # 糙率系数默认值表 (Manning's roughness coefficient)
    # 按土壤类型、植被覆盖、河道状况分类
    ROUGHNESS_COEFFICIENTS: Dict[str, Dict[str, Dict[str, float]]] = {
        "土壤类型": {
            "黏土": {"裸土": 0.030, "草地": 0.040, "灌木": 0.050, "森林": 0.080},
            "壤土": {"裸土": 0.025, "草地": 0.035, "灌木": 0.045, "森林": 0.070},
            "砂土": {"裸土": 0.020, "草地": 0.030, "灌木": 0.040, "森林": 0.060},
            "砾石": {"裸土": 0.035, "草地": 0.045, "灌木": 0.055, "森林": 0.090},
        },
        "河道状况": {
            "清洁顺直": {"无植被": 0.025, "少量植被": 0.030, "中等植被": 0.035, "茂密植被": 0.045},
            "清洁弯曲": {"无植被": 0.030, "少量植被": 0.035, "中等植被": 0.040, "茂密植被": 0.050},
            "有浅滩深潭": {"无植被": 0.035, "少量植被": 0.040, "中等植被": 0.050, "茂密植被": 0.070},
            "多石块杂草": {"无植被": 0.040, "少量植被": 0.050, "中等植被": 0.060, "茂密植被": 0.080},
            "山区急流": {"无植被": 0.050, "少量植被": 0.060, "中等植被": 0.080, "茂密植被": 0.120},
        },
        "人工渠道": {
            "混凝土": {"光滑": 0.012, "普通": 0.015, "粗糙": 0.018},
            "砌石": {"光滑": 0.020, "普通": 0.025, "粗糙": 0.030},
            "土渠": {"密实": 0.020, "普通": 0.025, "疏松": 0.030},
        },
    }

    # 降雨径流参数默认值
    RUNOFF_PARAMETERS: Dict[str, Any] = {
        "径流系数": {
            "商业区": {"中心": 0.85, "周边": 0.70},
            "住宅区": {"独栋": 0.40, "多栋": 0.60, "公寓": 0.75},
            "工业区": {"轻工业": 0.65, "重工业": 0.80},
            "公园绿地": {"草坪": 0.15, "林地": 0.10},
            "农田": {"旱地": 0.30, "水田": 0.25, "果园": 0.20},
            "裸地": {"平坦": 0.25, "起伏": 0.35, "陡峭": 0.50},
        },
        "初损值_mm": {
            "沙土": 15.0,
            "壤土": 25.0,
            "黏土": 35.0,
            "岩石": 5.0,
        },
        "平均入渗率_mm_h": {
            "沙土": 25.0,
            "壤土": 12.0,
            "黏土": 5.0,
            "岩石": 1.0,
        },
        "汇流时间系数": {
            "山区": 0.6,
            "丘陵": 0.8,
            "平原": 1.0,
        },
    }

    # 河道断面参数经验值
    CHANNEL_PARAMETERS: Dict[str, Any] = {
        "边坡系数": {
            "土渠": {"缓坡": 2.0, "中坡": 1.5, "陡坡": 1.0},
            "砌石": {"缓坡": 1.5, "中坡": 1.0, "陡坡": 0.5},
            "混凝土": {"缓坡": 1.0, "中坡": 0.5, "陡坡": 0.0},
        },
        "底宽_米": {
            "小型河道": {"最小": 2.0, "典型": 5.0, "最大": 10.0},
            "中型河道": {"最小": 10.0, "典型": 20.0, "最大": 50.0},
            "大型河道": {"最小": 50.0, "典型": 100.0, "最大": 300.0},
        },
        "水深_米": {
            "小型河道": {"枯水": 0.5, "常水": 1.5, "洪水": 3.0},
            "中型河道": {"枯水": 1.5, "常水": 3.0, "洪水": 6.0},
            "大型河道": {"枯水": 3.0, "常水": 6.0, "洪水": 12.0},
        },
        "水面比降": {
            "平原": 0.0005,
            "丘陵": 0.002,
            "山区": 0.01,
            "急流": 0.05,
        },
    }

    # 流域特征参数
    BASIN_PARAMETERS: Dict[str, Any] = {
        "形状系数": {
            "狭长型": 0.3,
            "羽状型": 0.5,
            "扇形": 0.7,
            "圆形": 1.0,
        },
        "河道坡度": {
            "平原": 0.001,
            "丘陵": 0.005,
            "山区": 0.02,
            "高山": 0.05,
        },
        "滞时系数": {
            "小流域(<10km2)": 0.5,
            "中流域(10-100km2)": 1.0,
            "大流域(100-1000km2)": 2.0,
            "特大流域(>1000km2)": 4.0,
        },
    }

    # 洪水计算参数
    FLOOD_PARAMETERS: Dict[str, Any] = {
        "洪峰流量系数": {
            "暴雨洪水": 0.8,
            "融雪洪水": 0.4,
            "混合洪水": 0.6,
        },
        "洪量系数": {
            "暴雨洪水": 0.7,
            "融雪洪水": 0.5,
            "混合洪水": 0.6,
        },
        "涨水历时_小时": {
            "小流域": 2.0,
            "中流域": 6.0,
            "大流域": 12.0,
        },
        "退水历时_小时": {
            "小流域": 8.0,
            "中流域": 24.0,
            "大流域": 72.0,
        },
    }

    # 土壤水文参数
    SOIL_HYDROLOGY: Dict[str, Any] = {
        "田间持水量_mm": {
            "沙土": 80.0,
            "壤土": 150.0,
            "黏土": 250.0,
        },
        "凋萎系数_mm": {
            "沙土": 20.0,
            "壤土": 60.0,
            "黏土": 120.0,
        },
        "饱和导水率_mm_h": {
            "沙土": 100.0,
            "壤土": 20.0,
            "黏土": 5.0,
        },
    }

    @classmethod
    def get_roughness(
        cls,
        soil_type: str = None,
        vegetation: str = None,
        condition: str = None,
        channel_type: str = None,
    ) -> float:
        """获取糙率系数。

        Args:
            soil_type: 土壤类型
            vegetation: 植被覆盖类型
            condition: 河道状况
            channel_type: 人工渠道类型

        Returns:
            糙率系数值，未找到时返回 None
        """
        if channel_type:
            # 人工渠道糙率
            data = cls.ROUGHNESS_COEFFICIENTS.get("人工渠道", {})
            channel_data = data.get(channel_type, {})
            return channel_data.get(vegetation) if vegetation else None
        elif condition:
            # 按河道状况查询
            data = cls.ROUGHNESS_COEFFICIENTS.get("河道状况", {})
            condition_data = data.get(condition, {})
            return condition_data.get(vegetation) if vegetation else None
        elif soil_type and vegetation:
            # 按土壤类型查询
            data = cls.ROUGHNESS_COEFFICIENTS.get("土壤类型", {})
            soil_data = data.get(soil_type, {})
            return soil_data.get(vegetation)
        return None

    @classmethod
    def get_runoff_coefficient(cls, land_use: str, sub_type: str = None) -> float:
        """获取径流系数。

        Args:
            land_use: 土地利用类型
            sub_type: 子类型

        Returns:
            径流系数值
        """
        data = cls.RUNOFF_PARAMETERS.get("径流系数", {})
        land_data = data.get(land_use, {})
        if sub_type:
            return land_data.get(sub_type)
        # 返回该类型的平均值
        if land_data:
            return sum(land_data.values()) / len(land_data)
        return None

    @classmethod
    def get_channel_parameter(cls, param_name: str, channel_size: str = None) -> Any:
        """获取河道断面参数。

        Args:
            param_name: 参数名称
            channel_size: 河道规模

        Returns:
            参数值
        """
        data = cls.CHANNEL_PARAMETERS.get(param_name, {})
        if channel_size and isinstance(data, dict):
            return data.get(channel_size)
        return data

    @classmethod
    def get_all_roughness_options(cls) -> Dict[str, list]:
        """获取所有糙率系数查询选项。

        Returns:
            包含所有选项的字典
        """
        return {
            "土壤类型": list(cls.ROUGHNESS_COEFFICIENTS["土壤类型"].keys()),
            "植被覆盖": ["裸土", "草地", "灌木", "森林"],
            "河道状况": list(cls.ROUGHNESS_COEFFICIENTS["河道状况"].keys()),
            "人工渠道": list(cls.ROUGHNESS_COEFFICIENTS["人工渠道"].keys()),
        }

    @classmethod
    def get_parameter_categories(cls) -> Dict[str, list]:
        """获取所有参数类别。

        Returns:
            参数类别字典
        """
        return {
            "糙率系数": ["土壤类型", "河道状况", "人工渠道"],
            "降雨径流": ["径流系数", "初损值", "平均入渗率", "汇流时间系数"],
            "河道断面": ["边坡系数", "底宽", "水深", "水面比降"],
            "流域特征": ["形状系数", "河道坡度", "滞时系数"],
            "洪水计算": ["洪峰流量系数", "洪量系数", "涨水历时", "退水历时"],
            "土壤水文": ["田间持水量", "凋萎系数", "饱和导水率"],
        }
