#!/usr/bin/env python3
"""
配置加载器
负责加载和管理系统配置
"""

import yaml
import os
from pathlib import Path


class ConfigLoader:
    """配置加载器"""

    def __init__(self, config_path=None):
        """
        初始化配置加载器

        Args:
            config_path: 配置文件路径，默认为 system-config.yaml
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "system-config.yaml"

        self.config_path = Path(config_path)
        self._config = None
        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件格式错误: {e}")

    def reload(self):
        """重新加载配置文件"""
        self._load_config()

    @property
    def config(self):
        """获取完整配置"""
        return self._config

    def get(self, key, default=None):
        """
        获取配置项

        Args:
            key: 配置键，支持点号分隔的路径，如 "agents.leader.model"
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

        return value if value is not None else default

    def get_agent_config(self, agent_type):
        """
        获取 Agent 配置

        Args:
            agent_type: Agent 类型，如 "leader", "tech", "log"

        Returns:
            dict: Agent 配置
        """
        return self.get(f'agents.{agent_type}', {})

    def get_workflow_config(self):
        """获取工作流程配置"""
        return self.get('workflow', {})

    def get_quality_config(self):
        """获取质量控制配置"""
        return self.get('quality', {})

    def get_performance_config(self):
        """获取性能配置"""
        return self.get('performance', {})

    def get_display_config(self):
        """获取显示配置"""
        return self.get('display', {})

    def is_debate_enabled(self):
        """是否启用辩论机制"""
        return self.get('workflow.enable_debate', False)

    def is_progress_display_enabled(self):
        """是否启用进度显示"""
        return self.get('workflow.enable_progress_display', True)

    def is_layered_decision_enabled(self):
        """是否启用分层决策"""
        return self.get('workflow.enable_layered_decision', False)

    def is_review_required(self):
        """是否需要质量审查"""
        return self.get('quality.require_review', False)

    def is_parallel_enabled(self):
        """是否启用并行执行"""
        return self.get('performance.enable_parallel', False)


# 全局配置加载器实例
_config_loader = None


def get_config_loader():
    """获取全局配置加载器实例"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader


def load_config():
    """快捷方法：加载配置"""
    return get_config_loader().config


def get_agent_config(agent_type):
    """快捷方法：获取 Agent 配置"""
    return get_config_loader().get_agent_config(agent_type)


# 测试代码
if __name__ == "__main__":
    # 测试配置加载
    loader = get_config_loader()

    print("✅ 配置文件加载成功！\n")

    print("📋 完整配置：")
    print(yaml.dump(loader.config, allow_unicode=True))

    print("\n🤖 Agent 配置：")
    for agent_type in ['leader', 'tech', 'log', 'design', 'challenger', 'review']:
        config = loader.get_agent_config(agent_type)
        print(f"  {agent_type}: {config.get('model')} - {config.get('role')}")

    print("\n⚙️  工作流程配置：")
    print(f"  启用辩论: {loader.is_debate_enabled()}")
    print(f"  启用进度显示: {loader.is_progress_display_enabled()}")
    print(f"  启用分层决策: {loader.is_layered_decision_enabled()}")
