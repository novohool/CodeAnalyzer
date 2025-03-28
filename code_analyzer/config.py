"""Configuration module for code analyzer."""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    """LLM configuration settings."""
    api_key: str
    base_url: str
    model: str
    max_tokens: int
    temperature: float
    stream: bool
    timeout: int
    prompt_template: str
    retry_count: int
    retry_delay: int
    batch_size: int
    concurrent_requests: int
    error_handling: Dict[str, Any]

    def validate(self):
        """Validate LLM configuration."""
        if not self.api_key or not self.base_url:
            raise ValueError("api_key and base_url are required for LLM config")

@dataclass
class AnalyzerConfig:
    """Analyzer configuration settings."""
    output_dir: str
    code_extensions: Dict[str, list]
    excluded_dirs: list
    max_file_size: int
    file_patterns: Dict[str, list]

    def validate(self):
        """Validate analyzer configuration."""
        if not self.output_dir:
            raise ValueError("output_dir is required for analyzer config")

@dataclass
class RouteAnalysisConfig:
    """Route analysis configuration settings."""
    client: Dict[str, Any]
    server: Dict[str, Any]

@dataclass
class MetricsConfig:
    """Code metrics configuration settings."""
    complexity_threshold: int
    max_function_length: int
    max_class_length: int
    max_file_length: int
    metrics_to_collect: list

@dataclass
class ReportingConfig:
    """Reporting configuration settings."""
    output_formats: list
    include_timestamps: bool
    include_file_stats: bool
    include_complexity_analysis: bool
    include_dependency_analysis: bool
    include_test_coverage: bool
    custom_templates: Dict[str, str]

class Config:
    """Main configuration class for the code analyzer.
    
    This class handles loading, saving, and updating configuration settings
    for the code analyzer application. It supports both custom and default
    configuration files.
    
    Attributes:
        config_path (str): Path to the configuration file
        llm (LLMConfig): LLM-related configuration
        analyzer (AnalyzerConfig): Code analysis configuration
        route_analysis (RouteAnalysisConfig): Route analysis configuration
        metrics (MetricsConfig): Code metrics configuration
        reporting (ReportingConfig): Reporting configuration
    """
    
    DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config.json"

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration from file or use defaults.
        
        Args:
            config_path: Path to the configuration file. If None, uses default config.json
        """
        self.config_path = config_path or str(self.DEFAULT_CONFIG_PATH)
        self._load_config()
        
    def _load_config(self):
        """Load configuration from file."""
        config_dict = {}
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
        except FileNotFoundError:
            logger.warning(f"配置文件 {self.config_path} 不存在，使用默认配置")
            config_dict = self._get_default_config()
        except json.JSONDecodeError:
            logger.error(f"配置文件 {self.config_path} 格式错误，使用默认配置")
            config_dict = self._get_default_config()
            
        try:
            self.llm = LLMConfig(**config_dict.get('llm', {}))
            self.analyzer = AnalyzerConfig(**config_dict.get('analyzer', {}))
            self.route_analysis = RouteAnalysisConfig(**config_dict.get('route_analysis', {}))
            self.metrics = MetricsConfig(**config_dict.get('metrics', {}))
            self.reporting = ReportingConfig(**config_dict.get('reporting', {}))
            
            # 验证配置
            self.llm.validate()
            self.analyzer.validate()
        except (TypeError, ValueError) as e:
            logger.error(f"配置错误: {str(e)}")
            raise ValueError(f"配置加载失败: {str(e)}")
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration from config.json."""
        try:
            with open(self.DEFAULT_CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"无法加载默认配置文件: {e}")
            raise
        
    def save(self, output_path: Optional[str] = None):
        """Save current configuration to file.
        
        Args:
            output_path: Optional path to save config, defaults to self.config_path
        """
        config_dict = {
            'llm': asdict(self.llm),
            'analyzer': asdict(self.analyzer),
            'route_analysis': asdict(self.route_analysis),
            'metrics': asdict(self.metrics),
            'reporting': asdict(self.reporting)
        }
        
        save_path = output_path or self.config_path
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=4, ensure_ascii=False)
            logger.info(f"配置已保存至 {save_path}")
        except IOError as e:
            logger.error(f"保存配置文件时出错: {e}")
            raise
            
    def update(self, config_dict: Dict[str, Any]):
        """Update configuration with new values."""
        for section, values in config_dict.items():
            if not hasattr(self, section):
                raise ValueError(f"未知的配置部分: {section}")
                
            section_config = getattr(self, section)
            for key, value in values.items():
                if not hasattr(section_config, key):
                    raise ValueError(f"未知的配置字段: {section}.{key}")
                setattr(section_config, key, value)
        self.save()
        logger.info("配置已更新")
