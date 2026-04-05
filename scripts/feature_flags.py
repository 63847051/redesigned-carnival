#!/usr/bin/env python3
"""
Feature Flags 管理模块
用于检查和管理 OpenClaw 系统的功能开关
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class FeatureFlags:
    """功能开关管理类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化功能开关管理器
        
        Args:
            config_path: 配置文件路径，默认为 workspace/feature-flags.json
        """
        if config_path is None:
            workspace = os.environ.get('OPENCLAW_WORKSPACE', '/root/.openclaw/workspace')
            config_path = os.path.join(workspace, 'feature-flags.json')
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 如果配置文件不存在，返回默认配置
            return {
                'flags': {},
                'groups': {},
                'metadata': {
                    'total_flags': 0,
                    'enabled_count': 0,
                    'disabled_count': 0
                }
            }
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件格式错误: {e}")
    
    def is_enabled(self, flag_name: str, default: bool = False) -> bool:
        """
        检查功能是否启用
        
        Args:
            flag_name: 功能名称
            default: 默认值（如果功能不存在）
        
        Returns:
            功能是否启用
        """
        flag = self.config.get('flags', {}).get(flag_name)
        if flag is None:
            return default
        
        return flag.get('enabled', False)
    
    def get_flag(self, flag_name: str) -> Optional[Dict[str, Any]]:
        """
        获取功能完整信息
        
        Args:
            flag_name: 功能名称
        
        Returns:
            功能信息字典，如果不存在返回 None
        """
        return self.config.get('flags', {}).get(flag_name)
    
    def list_flags(self, enabled_only: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        列出所有功能
        
        Args:
            enabled_only: 是否只列出启用的功能
        
        Returns:
            功能字典
        """
        flags = self.config.get('flags', {})
        
        if enabled_only:
            return {k: v for k, v in flags.items() if v.get('enabled', False)}
        
        return flags
    
    def list_by_group(self, group_name: str) -> Dict[str, Dict[str, Any]]:
        """
        按组列出功能
        
        Args:
            group_name: 组名称 (experimental/stable/optimization)
        
        Returns:
            功能字典
        """
        group = self.config.get('groups', {}).get(group_name, {})
        flag_names = group.get('flags', [])
        
        flags = {}
        for flag_name in flag_names:
            flag = self.get_flag(flag_name)
            if flag:
                flags[flag_name] = flag
        
        return flags
    
    def enable(self, flag_name: str) -> bool:
        """
        启用功能
        
        Args:
            flag_name: 功能名称
        
        Returns:
            是否成功
        """
        flag = self.config.get('flags', {}).get(flag_name)
        if flag is None:
            return False
        
        flag['enabled'] = True
        
        # 更新元数据
        metadata = self.config.get('metadata', {})
        metadata['enabled_count'] = metadata.get('enabled_count', 0) + 1
        metadata['disabled_count'] = metadata.get('disabled_count', 0) - 1
        metadata['last_review'] = str(os.environ.get('TODAY', '2026-04-01'))
        
        return self._save_config()
    
    def disable(self, flag_name: str) -> bool:
        """
        禁用功能
        
        Args:
            flag_name: 功能名称
        
        Returns:
            是否成功
        """
        flag = self.config.get('flags', {}).get(flag_name)
        if flag is None:
            return False
        
        flag['enabled'] = False
        
        # 更新元数据
        metadata = self.config.get('metadata', {})
        metadata['enabled_count'] = metadata.get('enabled_count', 0) - 1
        metadata['disabled_count'] = metadata.get('disabled_count', 0) + 1
        metadata['last_review'] = str(os.environ.get('TODAY', '2026-04-01'))
        
        return self._save_config()
    
    def _save_config(self) -> bool:
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False


# 全局实例
_feature_flags = None

def get_feature_flags() -> FeatureFlags:
    """获取功能开关管理器实例（单例）"""
    global _feature_flags
    if _feature_flags is None:
        _feature_flags = FeatureFlags()
    return _feature_flags


def is_feature_enabled(flag_name: str, default: bool = False) -> bool:
    """
    便捷函数：检查功能是否启用
    
    Args:
        flag_name: 功能名称
        default: 默认值
    
    Returns:
        功能是否启用
    """
    return get_feature_flags().is_enabled(flag_name, default)


# 便捷函数：检查常用功能
def is_task_agent_loop_enabled() -> bool:
    """检查任务内部 Agent Loop 是否启用"""
    return is_feature_enabled('TASK_AGENT_LOOP', default=True)


def is_proactive_mode_enabled() -> bool:
    """检查主动模式是否启用"""
    return is_feature_enabled('PROACTIVE_MODE', default=False)


def is_memory_search_enabled() -> bool:
    """检查记忆搜索是否启用"""
    return is_feature_enabled('MEMORY_SEARCH', default=True)


def is_auto_compression_enabled() -> bool:
    """检查自动压缩是否启用"""
    return is_feature_enabled('AUTO_COMPRESSION', default=True)


if __name__ == '__main__':
    # 测试代码
    ff = get_feature_flags()
    
    print("功能开关测试")
    print("=" * 60)
    
    # 检查几个功能
    test_flags = [
        'TASK_AGENT_LOOP',
        'PROACTIVE_MODE',
        'MEMORY_SEARCH',
        'AUTO_COMPRESSION'
    ]
    
    for flag in test_flags:
        enabled = ff.is_enabled(flag)
        status = "✅ 启用" if enabled else "⚪ 未启用"
        print(f"{status}: {flag}")
    
    print("\n" + "=" * 60)
    print(f"总计: {ff.config['metadata']['enabled_count']} 个功能启用")
    print(f"未启用: {ff.config['metadata']['disabled_count']} 个功能")
