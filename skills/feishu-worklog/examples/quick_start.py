#!/usr/bin/env python3
"""
飞书工作日志快速开始示例

演示 3 个常见场景：
1. 记录工作日志
2. 查询任务
3. 获取统计信息
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worklog_assistant import WorklogAssistant
from intent_analyzer import IntentAnalyzer
from bitable_manager import BitableManager

APP_TOKEN = "BISAbNgYXa7Do1sc36YcBChInnS"
TABLE_ID = "tbl5s8TEZ0tKhEm7"

DEMO_TOKEN = "demo_token_placeholder"


def scenario_1_record_worklog():
    """场景 1: 记录工作日志"""
    print("\n" + "=" * 50)
    print("场景 1: 记录工作日志")
    print("=" * 50)

    assistant = WorklogAssistant(APP_TOKEN, TABLE_ID)

    test_inputs = [
        "记录一下：完成了3F会议室平面图设计",
        "添加紧急任务：修复线上bug",
        "新建普通任务：编写技术文档",
    ]

    for user_input in test_inputs:
        print(f"\n>>> {user_input}")
        print("-" * 40)

        analyzer = IntentAnalyzer()
        result = analyzer.analyze(user_input)

        print(f"意图: {result.intent}")
        print(f"内容: {result.content}")
        print(f"项目类型: {result.project_type}")
        print(f"优先级: {result.priority}")
        print(f"状态: {result.status}")
        print(f"可信度: {result.confidence:.2f}")


def scenario_2_query_tasks():
    """场景 2: 查询任务"""
    print("\n" + "=" * 50)
    print("场景 2: 查询任务")
    print("=" * 50)

    assistant = WorklogAssistant(APP_TOKEN, TABLE_ID)

    test_inputs = [
        "查询今天已完成的任务",
        "查看室内设计相关的任务",
        "统计本周的工作情况",
    ]

    for user_input in test_inputs:
        print(f"\n>>> {user_input}")
        print("-" * 40)

        analyzer = IntentAnalyzer()
        result = analyzer.analyze(user_input)

        print(f"意图: {result.intent}")
        print(f"内容: {result.content}")
        print(f"状态: {result.status}")
        print(f"项目类型: {result.project_type}")


def scenario_3_get_statistics():
    """场景 3: 获取统计信息"""
    print("\n" + "=" * 50)
    print("场景 3: 获取统计信息")
    print("=" * 50)

    print("\n>>> 获取整体统计")
    print("-" * 40)
    print("使用 assistant.get_statistics() 可获取:")
    print("  - 总任务数")
    print("  - 已完成任务数")
    print("  - 进行中任务数")
    print("  - 待确认任务数")
    print("  - 完成率")

    print("\n>>> 获取今日摘要")
    print("-" * 40)
    print("使用 assistant.get_today_summary() 可获取:")
    print("  - 今日任务数")
    print("  - 今日完成任务数")
    print("  - 今日进行中任务数")


def demo_intent_analyzer():
    """演示意图分析器"""
    print("\n" + "=" * 50)
    print("意图分析器演示")
    print("=" * 50)

    analyzer = IntentAnalyzer()

    test_cases = [
        "记录一下：完成了3F会议室平面图设计",
        "查询今天完成的任务",
        "更新任务状态为已完成",
        "删除这条记录",
        "紧急任务：完成API开发",
        "普通任务：整理文档",
    ]

    for text in test_cases:
        result = analyzer.analyze(text)
        print(f"\n输入: {text}")
        print(f"  意图: {result.intent}")
        print(f"  内容: {result.content}")
        print(f"  类型: {result.project_type}")
        print(f"  优先级: {result.priority}")
        print(f"  状态: {result.status}")


def demo_bitable_manager():
    """演示 Bitable 管理器"""
    print("\n" + "=" * 50)
    print("Bitable 管理器演示")
    print("=" * 50)

    manager = BitableManager(APP_TOKEN, TABLE_ID)

    print("\n可用方法:")
    print("  - add_record(): 添加记录")
    print("  - query_records(): 查询记录")
    print("  - update_status(): 更新状态")
    print("  - update_record(): 更新记录")
    print("  - delete_record(): 删除记录")
    print("  - get_statistics(): 获取统计")
    print("  - get_today_statistics(): 今日统计")
    print("  - list_fields(): 获取字段列表")


def main():
    """主函数"""
    print("=" * 50)
    print("飞书工作日志智能助手 - 快速开始")
    print("=" * 50)

    print("""
使用方法:
1. 替换 DEMO_TOKEN 为您的飞书 access_token
2. 运行本脚本查看各场景演示

示例:
    from worklog_assistant import WorklogAssistant
    
    assistant = WorklogAssistant(APP_TOKEN, TABLE_ID)
    assistant.set_access_token("your_token")
    result = assistant.process("记录任务：完成开发")
    print(result)
""")

    demo_intent_analyzer()

    demo_bitable_manager()

    print("\n" + "=" * 50)
    print("演示完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()
