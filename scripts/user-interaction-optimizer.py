#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户交互优化系统
- 智能确认机制
- 进度反馈
- 友好错误提示
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
LOG_FILE = WORKSPACE / ".user-interaction.log"

# 颜色输出
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    RED = '\033[0;31m'
    NC = '\033[0m'

def log(message: str, level: str = "INFO"):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}"
    print(log_line)
    
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except Exception as e:
        print(f"写入日志失败: {e}")

# ============================================================================
# 风险评估
# ============================================================================

def assess_risk(task_description: str) -> Tuple[str, str]:
    """
    评估任务风险等级
    返回: (风险等级, 原因)
    """
    task_lower = task_description.lower()
    
    # 低风险: 常规任务，不修改系统
    low_risk_keywords = [
        # 信息查询
        r"查询|搜索|查找|读取|获取|分析|总结|统计",
        # 简单创建
        r"写个|创建|生成.*脚本|代码|文章|内容",
        # 简单设计
        r"设计.*图|平面图|海报|文案",
        # 测试
        r"测试|验证|检查",
    ]
    
    for pattern in low_risk_keywords:
        if re.search(pattern, task_lower):
            return ("low", "常规任务，无系统修改风险")
    
    # 中风险: 涉及配置修改
    medium_risk_keywords = [
        # 配置相关
        r"配置|修改|更改|设置|调整|优化",
        # 部署相关
        r"部署|发布|上线|推送|git push",
        # 数据相关
        r"数据|备份|恢复|迁移",
    ]
    
    for pattern in medium_risk_keywords:
        if re.search(pattern, task_lower):
        return ("medium", "涉及系统或数据修改，需要确认")
    
    # 高风险: 删除、破坏性操作
    high_risk_keywords = [
        # 删除相关
        r"删除|移除|卸载|清理|清除|撤销",
        # 停止相关
        r"停止|关闭|禁用|禁",
        # 重置相关
        r"重置|恢复出厂|清空|格式化",
    ]
    
    for pattern in high_risk_keywords:
        if re.search(pattern, task_lower):
        return ("high", "破坏性操作，必须详细确认")
    
    # 默认中等风险
    return ("medium", "未识别的任务，建议确认")

# ============================================================================
# 智能确认
# ============================================================================

EXPLICIT_CONFIRMATIONS = {
    "确认", "确认执行", "开始实施", "执行", "开始做", "好的，执行吧"
}

def has_explicit_confirmation(context: list) -> bool:
    """检查是否有明确确认"""
    recent_messages = context[-5:]  # 最近 5 条消息
    
    for msg in recent_messages:
        content = msg.get("content", "")
        for confirmation in EXPLICIT_CONFIRMATIONS:
            if confirmation in content:
                return True
    
    return False

# ============================================================================
# 主流程
# ============================================================================

def analyze_task(task_description: str) -> Tuple[str, str]:
    """分析任务类型和风险"""
    task_lower = task_description.lower()
    
    # 识别任务类型
    if re.search(r"写个|创建|生成.*脚本|代码", task_lower):
        task_type = "tech"
    elif re.search(r"日志|记录|工作|任务|进度", task_lower):
        task_type = "log"
    elif re.search(r"设计|图|平面图|海报", task_lower):
        task_type = "design"
    else:
        task_type = "general"
    
    # 评估风险
    risk, reason = assess_risk(task_description)
    
    return task_type, risk

def should_confirm(task_description: str, task_type: str, risk: str) -> Tuple[bool, str]:
    """判断是否需要确认"""
    
    # 低风险: 不确认
    if risk == "low":
        return False, "低风险，直接执行"
    
    # 中风险: 检查是否有明确确认
    if risk == "medium":
        # TODO: 检查对话历史中的确认
        # return True if not has_explicit_confirmation() else False
        return True, "中风险，需要确认"
    
    # 高风险: 总是确认
    if risk == "high":
        return True, "高风险，必须详细确认"
    
    return True, "未识别，建议确认"

# ============================================================================
# 测试
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="用户交互优化系统")
    parser.add_argument("--test-risk", action="store_true", help="测试风险评估")
    parser.add_argument("--task", help="测试任务描述")
    
    args = parser.parse_args()
    
    if args.test_risk:
        # 测试风险评估
        if args.task:
            task_type, risk, reason = analyze_task(args.task)
            print(f"任务: {args.task}")
            print(f"类型: {task_type}")
            print(f"风险: {risk}")
            print(f"原因: {reason}")
        else:
            # 测试不同类型的任务
            test_tasks = [
                "写个 Python 脚本",
                "配置系统设置",
                "删除所有文件",
                "查询今天的天气",
                "优化性能",
            ]
            
            print("="*60)
            print("风险评估测试")
            print("="*60)
            
            for task in test_tasks:
                task_type, risk, reason = analyze_task(task)
                status = "✅" if risk == "low" else "⚠️" if risk == "medium" else "🔴"
                print(f"{status} {task}")
                print(f"   类型: {task_type}")
                print(f"   风险: {risk}")
                print(f"   原因: {reason}")
                print()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="用户交互优化系统")
    parser.add_argument("--test-risk", action="store_true", help="测试风险评估")
    parser.add_argument("--task", help="测试任务描述")
    
    args = parser.parse_args()
    
    print("="*60)
    print("用户交互优化系统")
    print("="*60)
    
    if args.test_risk:
        if args.task:
            # 测试单个任务
            task_type, risk, reason = analyze_task(args.task)
            print(f"任务: {args.task}")
            print(f"类型: {task_type}")
            print(f"风险: {risk}")
            print(f"原因: {reason}")
        else:
            # 测试不同类型的任务
            test_tasks = [
                "写个 Python 脚本",
                "配置系统设置",
                "删除所有文件",
                "查询今天的天气",
                "优化性能",
            ]
            
            print("\n风险评估测试:")
            print("-"*60)
            
            for task in test_tasks:
                task_type, risk, reason = analyze_task(task)
                status = "✅" if risk == "low" else "⚠️" if risk == "medium" else "🔴"
                print(f"{status} {task}")
                print(f"   类型: {task_type}")
                print(f"   风险: {risk}")
                print(f"   原因: {reason}")
                print()
    
    print("="*60)
    print("✅ 系统已准备就绪")
    print("="*60)
