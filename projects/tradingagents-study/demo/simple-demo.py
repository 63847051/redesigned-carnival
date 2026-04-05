#!/usr/bin/env python3
"""
简单演示
展示配置系统、进度跟踪和 Agent 注册的协同工作
"""

import sys
import time
from pathlib import Path

# 直接添加 scripts 目录到路径
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

import config_loader
import progress_tracker
import agent_registry


class SimpleAgent:
    """简单的演示 Agent"""

    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.model = config.get("model", "unknown")

    def execute(self, task, tracker):
        """执行任务"""
        tracker.start(self.name, f"正在执行: {task}")

        # 模拟工作
        for i in range(1, 101, 20):
            time.sleep(0.5)
            tracker.update(self.name, "running", f"正在执行: {task}", i)

        tracker.complete(self.name, f"完成: {task}")
        return f"✅ {self.name} 完成了任务: {task}"


def main():
    """主演示函数"""
    print("\n" + "="*70)
    print("🚀 自主进化系统 v7.0 - 简单演示")
    print("="*70 + "\n")

    # 1. 加载配置
    print("📋 步骤 1: 加载系统配置")
    print("-" * 70)
    config_loader_obj = config_loader.get_config_loader()

    print("✅ 配置加载成功！\n")
    print("已注册的 Agent:")
    for agent_name in ['leader', 'tech', 'log', 'design', 'challenger', 'review']:
        agent_config = config_loader_obj.get_agent_config(agent_name)
        if agent_config:
            print(f"  • {agent_name:15s} {agent_config['model']:30s} - {agent_config['role']}")

    print(f"\n工作流程配置:")
    print(f"  • 启用进度显示: {config_loader_obj.is_progress_display_enabled()}")
    print(f"  • 启用辩论机制: {config_loader_obj.is_debate_enabled()}")
    print(f"  • 启用分层决策: {config_loader_obj.is_layered_decision_enabled()}")

    # 2. 注册 Agent
    print(f"\n📦 步骤 2: 注册 Agent")
    print("-" * 70)
    registry = agent_registry.get_registry()

    # 注册演示 Agent
    for agent_name in ['tech', 'log', 'design']:
        agent_config = config_loader_obj.get_agent_config(agent_name)
        if agent_config:
            registry.register(agent_name, SimpleAgent, agent_config)
            print(f"  ✅ 已注册: {agent_name} - {agent_config['role']}")

    # 3. 创建进度跟踪器
    print(f"\n📊 步骤 3: 初始化进度跟踪器")
    print("-" * 70)
    tracker = progress_tracker.ProgressTracker(verbose=True)
    print("  ✅ 进度跟踪器已就绪")

    # 4. 执行任务
    print(f"\n🎯 步骤 4: 执行任务")
    print("="*70)

    # 任务列表
    tasks = [
        ("tech", "编写 Python 脚本"),
        ("log", "记录工作日志"),
        ("design", "设计平面图")
    ]

    results = []

    for agent_name, task in tasks:
        agent_info = registry.get(agent_name)
        if agent_info:
            agent = agent_info.agent_class(agent_name, agent_info.config)
            result = agent.execute(task, tracker)
            results.append(result)

    # 5. 显示结果
    print(f"\n📝 步骤 5: 执行结果")
    print("-" * 70)
    for result in results:
        print(f"  {result}")

    # 6. 显示摘要
    print(f"\n📊 执行摘要")
    print("-" * 70)
    summary = tracker.get_summary()
    print(f"  总 Agent 数: {summary['total_agents']}")
    print(f"  完成: {summary['complete_agents']}")
    print(f"  错误: {summary['error_agents']}")
    print(f"  成功率: {summary['success_rate']*100:.1f}%")
    print(f"  总耗时: {tracker._format_time(summary['elapsed_time'])}")

    print("\n" + "="*70)
    print("✅ 演示完成！")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
