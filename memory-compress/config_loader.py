"""
配置加载器
加载和验证配置文件
"""

import json
import os
from typing import Dict, Optional


DEFAULT_CONFIG = {
    # 触发条件
    "preserve_recent": 10,        # 保留最近 10 条消息
    "max_tokens": 2000,           # 超过 2000 tokens 触发压缩
    "min_messages": 20,           # 最少 20 条消息才压缩

    # 提取规则
    "todo_keywords": ["todo", "next", "pending", "remaining", "待办", "计划"],
    "decision_keywords": ["决定", "选择", "采用", "方案"],
    "link_patterns": [r'https?://[^\s]+'],

    # 摘要格式
    "summary_format": "markdown",  # markdown | json | xml
    "include_timeline": True,      # 是否包含时间线
    "max_timeline_items": 10,      # 时间线最多显示 10 条
}


def load_config(config_path: Optional[str] = None) -> Dict:
    """
    加载配置文件

    参数:
        config_path: 配置文件路径（JSON 格式）

    返回:
        配置字典
    """
    # 如果没有指定路径，使用默认路径
    if config_path is None:
        # 尝试多个可能的配置文件位置
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "config.json"),
            os.path.join(os.path.dirname(__file__), "..", "config", "memory-compress.json"),
            "/root/.openclaw/workspace/memory-compress/config.json",
        ]

        for path in possible_paths:
            if os.path.exists(path):
                config_path = path
                break

    # 如果配置文件不存在，使用默认配置
    if config_path is None or not os.path.exists(config_path):
        return DEFAULT_CONFIG.copy()

    # 加载配置文件
    with open(config_path, "r", encoding="utf-8") as f:
        user_config = json.load(f)

    # 合并默认配置和用户配置
    config = DEFAULT_CONFIG.copy()
    config.update(user_config)

    return config


def validate_config(config: Dict) -> tuple[bool, list[str]]:
    """
    验证配置

    参数:
        config: 配置字典

    返回:
        (是否有效, 错误列表)
    """
    errors = []

    # 验证触发条件
    if "preserve_recent" not in config:
        errors.append("缺少 preserve_recent 配置")
    elif not isinstance(config["preserve_recent"], int) or config["preserve_recent"] < 0:
        errors.append("preserve_recent 必须是非负整数")

    if "max_tokens" not in config:
        errors.append("缺少 max_tokens 配置")
    elif not isinstance(config["max_tokens"], int) or config["max_tokens"] <= 0:
        errors.append("max_tokens 必须是正整数")

    if "min_messages" not in config:
        errors.append("缺少 min_messages 配置")
    elif not isinstance(config["min_messages"], int) or config["min_messages"] < 0:
        errors.append("min_messages 必须是非负整数")

    # 验证逻辑一致性
    if config.get("preserve_recent", 0) >= config.get("min_messages", 0):
        errors.append(f"preserve_recent ({config.get('preserve_recent')}) 必须 < min_messages ({config.get('min_messages')})")

    # 验证摘要格式
    if "summary_format" in config:
        valid_formats = ["markdown", "json", "xml"]
        if config["summary_format"] not in valid_formats:
            errors.append(f"summary_format 必须是 {valid_formats} 之一")

    # 验证时间线配置
    if "include_timeline" in config:
        if not isinstance(config["include_timeline"], bool):
            errors.append("include_timeline 必须是布尔值")

    if "max_timeline_items" in config:
        if not isinstance(config["max_timeline_items"], int) or config["max_timeline_items"] <= 0:
            errors.append("max_timeline_items 必须是正整数")

    return len(errors) == 0, errors


def save_config(config: Dict, config_path: Optional[str] = None) -> None:
    """
    保存配置文件

    参数:
        config: 配置字典
        config_path: 配置文件路径（可选）
    """
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "config.json")

    # 验证配置
    is_valid, errors = validate_config(config)
    if not is_valid:
        raise ValueError(f"配置无效: {errors}")

    # 保存配置
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def print_config(config: Dict) -> None:
    """
    打印配置（用于调试）

    参数:
        config: 配置字典
    """
    print("=" * 60)
    print("配置信息")
    print("=" * 60)
    print(f"preserve_recent: {config.get('preserve_recent')}")
    print(f"max_tokens: {config.get('max_tokens')}")
    print(f"min_messages: {config.get('min_messages')}")
    print(f"summary_format: {config.get('summary_format')}")
    print(f"include_timeline: {config.get('include_timeline')}")
    print(f"max_timeline_items: {config.get('max_timeline_items')}")
    print("=" * 60)


# 测试
if __name__ == "__main__":
    # 测试 1: 加载默认配置
    print("=== 测试 1: 加载默认配置 ===")
    config = load_config()
    print_config(config)

    # 测试 2: 验证配置
    print("\n=== 测试 2: 验证配置 ===")
    is_valid, errors = validate_config(config)
    print(f"配置有效: {is_valid}")
    if errors:
        print(f"错误: {errors}")
    assert is_valid

    # 测试 3: 无效配置
    print("\n=== 测试 3: 无效配置 ===")
    invalid_config = {
        "preserve_recent": -1,  # 无效值
        "max_tokens": 0,        # 无效值
    }
    is_valid, errors = validate_config(invalid_config)
    print(f"配置有效: {is_valid}")
    print(f"错误: {errors}")
    assert not is_valid
    assert len(errors) > 0

    # 测试 4: 保存配置
    print("\n=== 测试 4: 保存配置 ===")
    test_config = {
        "preserve_recent": 5,
        "max_tokens": 1500,
        "min_messages": 15,
        "summary_format": "markdown",
        "include_timeline": True,
        "max_timeline_items": 5
    }
    test_path = "/tmp/test-config.json"
    save_config(test_config, test_path)
    print(f"✅ 配置已保存到: {test_path}")

    # 验证保存的配置（只验证用户配置的字段）
    loaded_config = load_config(test_path)
    for key, value in test_config.items():
        assert loaded_config[key] == value
    print("✅ 配置加载验证通过")

    # 清理
    os.remove(test_path)

    print("\n✅ 所有测试通过！")
