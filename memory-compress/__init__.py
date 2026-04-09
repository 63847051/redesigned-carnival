"""
智能记忆压缩系统 v1.0

从消息中智能提取关键信息，生成结构化摘要，保留重要上下文

核心组件：
- TokenEstimator: Token 数量估算
- RuleExtractor: 规则提取器（待办/决策/链接/统计）
- SummaryGenerator: 摘要生成器
- Compactor: 压缩执行器
"""

from .token_estimator import estimate_tokens, estimate_message_tokens, estimate_messages_tokens
from .rule_extractor import extract_todos, extract_decisions, extract_links, extract_stats, extract_tools
from .summary_generator import generate_summary, generate_summary_as_dict
from .compactor import compact_memory, compact_memory_with_validation, should_compact

__version__ = "1.0.0"
__author__ = "大领导 AI"

# 默认配置
DEFAULT_CONFIG = {
    # 触发条件
    "preserve_recent": 10,        # 保留最近 10 条消息
    "max_tokens": 2000,           # 超过 2000 tokens 触发压缩
    "min_messages": 20,           # 最少 20 条消息才压缩

    # 提取规则
    "todo_keywords": ["todo", "next", "pending", "remaining", "待办", "计划"],
    "decision_keywords": ["决定", "选择", "采用", "方案", "规则"],
    "link_patterns": [r'https?://[^\s]+'],

    # 摘要格式
    "summary_format": "markdown",  # markdown | json | xml
    "include_timeline": True,      # 是否包含时间线
    "max_timeline_items": 10,      # 时间线最多显示 10 条
}


def load_config(config_path: str = None) -> dict:
    """
    加载配置文件

    参数:
        config_path: 配置文件路径（JSON 格式）

    返回:
        配置字典
    """
    import json
    import os

    # 如果没有指定路径，使用默认路径
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "memory-compress.json")

    # 如果配置文件不存在，使用默认配置
    if not os.path.exists(config_path):
        return DEFAULT_CONFIG.copy()

    # 加载配置文件
    with open(config_path, "r", encoding="utf-8") as f:
        user_config = json.load(f)

    # 合并默认配置和用户配置
    config = DEFAULT_CONFIG.copy()
    config.update(user_config)

    return config


def compact_messages(messages: list, config: dict = None) -> dict:
    """
    压缩消息列表（对外接口）

    参数:
        messages: 消息列表
        config: 配置字典（可选，默认使用 load_config()）

    返回:
        压缩结果字典
    """
    if config is None:
        config = load_config()

    return compact_memory(messages, config)


# 导出所有公共接口
__all__ = [
    # Token 估算
    "estimate_tokens",
    "estimate_message_tokens",
    "estimate_messages_tokens",

    # 规则提取
    "extract_todos",
    "extract_decisions",
    "extract_links",
    "extract_stats",
    "extract_tools",

    # 摘要生成
    "generate_summary",
    "generate_summary_as_dict",

    # 压缩执行
    "compact_memory",
    "compact_memory_with_validation",
    "should_compact",
    "compact_messages",

    # 配置
    "load_config",
    "DEFAULT_CONFIG",
]
