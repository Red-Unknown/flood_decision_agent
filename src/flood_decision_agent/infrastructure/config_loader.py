"""配置加载器 - 支持 YAML 和 JSON 格式"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml


class ConfigLoader:
    """配置加载器
    
    支持 YAML 和 JSON 格式的配置文件加载
    支持环境变量覆盖
    支持配置合并
    """
    
    def __init__(self, config_dir: Optional[Union[str, Path]] = None):
        """初始化配置加载器
        
        Args:
            config_dir: 配置目录路径，默认为项目根目录下的 configs/
        """
        if config_dir is None:
            # 从当前文件向上查找项目根目录
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent.parent.parent
            config_dir = project_root / "configs"
        
        self.config_dir = Path(config_dir)
        self._cache: Dict[str, Any] = {}
    
    def load(
        self,
        name: str,
        env: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """加载配置文件
        
        Args:
            name: 配置名称（如 'app', 'mcp/servers'）
            env: 环境名称（如 'development', 'production'）
            use_cache: 是否使用缓存
            
        Returns:
            配置字典
        """
        cache_key = f"{name}:{env}"
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        # 加载默认配置
        config = self._load_file(name)
        
        # 加载环境特定配置并合并
        if env:
            env_config = self._load_file(name, env)
            config = self._merge(config, env_config)
        
        # 应用环境变量覆盖
        config = self._apply_env_overrides(config, name)
        
        if use_cache:
            self._cache[cache_key] = config
        
        return config
    
    def _load_file(self, name: str, env: Optional[str] = None) -> Dict[str, Any]:
        """加载单个配置文件
        
        优先尝试 YAML 格式，然后尝试 JSON 格式
        """
        # 构建文件路径
        if env:
            file_path = self.config_dir / name / f"{env}.yaml"
            if not file_path.exists():
                file_path = self.config_dir / name / f"{env}.yml"
            if not file_path.exists():
                file_path = self.config_dir / name / f"{env}.json"
        else:
            file_path = self.config_dir / name / "default.yaml"
            if not file_path.exists():
                file_path = self.config_dir / name / "default.yml"
            if not file_path.exists():
                file_path = self.config_dir / name / "default.json"
        
        if not file_path.exists():
            return {}
        
        # 读取文件内容
        content = file_path.read_text(encoding='utf-8')
        
        # 根据文件扩展名解析
        if file_path.suffix in ['.yaml', '.yml']:
            return yaml.safe_load(content) or {}
        elif file_path.suffix == '.json':
            return json.loads(content)
        else:
            raise ValueError(f"不支持的配置文件格式: {file_path.suffix}")
    
    def _merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """递归合并两个字典
        
        override 中的值会覆盖 base 中的值
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _apply_env_overrides(self, config: Dict[str, Any], prefix: str) -> Dict[str, Any]:
        """应用环境变量覆盖
        
        环境变量格式: FLOOD_AGENT_<PREFIX>__<KEY>=value
        例如: FLOOD_AGENT_APP__DEBUG=true
        """
        env_prefix = f"FLOOD_AGENT_{prefix.upper().replace('/', '_')}__"
        
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                # 提取配置键路径
                config_key = key[len(env_prefix):].lower()
                keys = config_key.split('__')
                
                # 递归设置配置值
                current = config
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                
                # 尝试解析值类型
                current[keys[-1]] = self._parse_value(value)
        
        return config
    
    def _parse_value(self, value: str) -> Any:
        """解析字符串值为合适的类型"""
        # 尝试布尔值
        if value.lower() in ('true', 'yes', '1'):
            return True
        if value.lower() in ('false', 'no', '0'):
            return False
        
        # 尝试整数
        try:
            return int(value)
        except ValueError:
            pass
        
        # 尝试浮点数
        try:
            return float(value)
        except ValueError:
            pass
        
        # 尝试 JSON 数组/对象
        if value.startswith('[') or value.startswith('{'):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        
        # 返回字符串
        return value
    
    def clear_cache(self):
        """清除配置缓存"""
        self._cache.clear()
    
    def get(
        self,
        key: str,
        default: Any = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Any:
        """获取配置项
        
        Args:
            key: 配置键，支持点号分隔的路径（如 'llm.temperature'）
            default: 默认值
            config: 配置字典，默认为 None（使用已加载的配置）
            
        Returns:
            配置值
        """
        if config is None:
            raise ValueError("必须提供 config 参数")
        
        keys = key.split('.')
        current = config
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current


# 全局配置加载器实例
_config_loader: Optional[ConfigLoader] = None


def get_config_loader() -> ConfigLoader:
    """获取全局配置加载器实例"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader


def load_config(
    name: str,
    env: Optional[str] = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """便捷函数：加载配置
    
    Args:
        name: 配置名称
        env: 环境名称
        use_cache: 是否使用缓存
        
    Returns:
        配置字典
    """
    return get_config_loader().load(name, env, use_cache)


def get_config(
    key: str,
    default: Any = None,
    config: Optional[Dict[str, Any]] = None
) -> Any:
    """便捷函数：获取配置项
    
    Args:
        key: 配置键
        default: 默认值
        config: 配置字典
        
    Returns:
        配置值
    """
    return get_config_loader().get(key, default, config)
