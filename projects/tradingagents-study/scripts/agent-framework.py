#!/usr/bin/env python3
"""
统一 Agent 框架
整合所有功能到一个统一的框架中
"""

import sys
import time
from pathlib import Path
from typing import Dict, Optional, List

# 添加路径
scripts_dir = Path(__file__).parent
agents_dir = Path(__file__).parent.parent / "agents"
sys.path.insert(0, str(scripts_dir))
sys.path.insert(0, str(agents_dir))

import config_loader
import progress_tracker
import agent_registry
from layered_decision import LayeredDecisionSystem
from debate_manager import DebateManager
from challenger_agent import ChallengerAgent


class AgentFramework:
    """
    统一 Agent 框架
    整合配置系统、进度跟踪、Agent注册、辩论机制、分层决策
    """

    def __init__(self, verbose: bool = True):
        """
        初始化 Agent 框架

        Args:
            verbose: 是否显示详细信息
        """
        self.verbose = verbose

        # 加载配置
        self.config = config_loader.get_config_loader()

        # 创建进度跟踪器
        self.tracker = progress_tracker.ProgressTracker(verbose=verbose)

        # 创建分层决策系统
        self.layered_system = LayeredDecisionSystem(verbose=verbose)

        # 创建辩论管理器（延迟初始化）
        self.debate_manager: Optional[DebateManager] = None

        # 获取 Agent 注册表
        self.registry = agent_registry.get_registry()

        # 统计信息
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "debated_tasks": 0,
            "layered_decisions": 0
        }

    def execute_task(self, task: str, mode: str = "auto") -> Dict:
        """
        执行任务

        Args:
            task: 任务描述
            mode: 执行模式
                - "auto": 自动选择最佳模式
                - "simple": 简单模式（直接执行）
                - "debate": 辩论模式（带辩论）
                - "layered": 分层模式（5层决策）

        Returns:
            dict: 执行结果
        """
        print(f"\n{'='*70}")
        print(f"🚀 Agent 框架启动")
        print(f"{'='*70}\n")

        self.stats["total_tasks"] += 1

        # 自动选择模式
        if mode == "auto":
            mode = self._select_mode(task)

        print(f"📋 执行模式: {mode}\n")
        print(f"📝 任务: {task}\n")

        try:
            # 根据模式执行
            if mode == "layered":
                result = self._execute_layered(task)
            elif mode == "debate":
                result = self._execute_debate(task)
            else:
                result = self._execute_simple(task)

            self.stats["completed_tasks"] += 1
            print(f"\n✅ 任务执行完成！\n")

        except Exception as e:
            self.stats["failed_tasks"] += 1
            print(f"\n❌ 任务执行失败: {e}\n")
            result = {"error": str(e)}

        # 显示摘要
        self._print_summary()

        return result

    def _select_mode(self, task: str) -> str:
        """
        自动选择执行模式

        Args:
            task: 任务描述

        Returns:
            str: 执行模式
        """
        # 检查配置
        if self.config.is_layered_decision_enabled():
            return "layered"
        elif self.config.is_debate_enabled():
            return "debate"
        else:
            return "simple"

    def _execute_simple(self, task: str) -> Dict:
        """
        简单模式执行

        Args:
            task: 任务描述

        Returns:
            dict: 执行结果
        """
        print("🎯 使用简单模式执行\n")

        # 分析任务类型
        task_type = self._analyze_task_type(task)

        # 创建模拟 Agent
        agent = self._create_agent(task_type)

        # 执行任务
        self.tracker.start(agent["name"], f"正在执行: {task}")
        time.sleep(1)
        self.tracker.update(agent["name"], "running", f"正在执行: {task}", 50)
        time.sleep(1)
        self.tracker.complete(agent["name"], "执行完成")

        return {
            "mode": "simple",
            "task": task,
            "agent": agent["name"],
            "result": f"✅ {agent['name']} 完成了任务: {task}"
        }

    def _execute_debate(self, task: str) -> Dict:
        """
        辩论模式执行

        Args:
            task: 任务描述

        Returns:
            dict: 执行结果
        """
        print("🎤 使用辩论模式执行\n")

        # 分析任务类型
        task_type = self._analyze_task_type(task)

        # 创建 Agent
        defender = self._create_agent(task_type)
        challenger = ChallengerAgent("挑战者")

        # 提出方案
        self.tracker.start(defender["name"], "正在设计方案...")
        proposal = f"方案：{task}\n\n技术路线：使用成熟技术栈\n实施步骤：分阶段推进"
        self.tracker.complete(defender["name"], "方案提出完成")

        # 辩论
        self.tracker.start(challenger.name, "正在分析方案...")

        if self.debate_manager is None:
            max_rounds = self.config.get("workflow.max_debate_rounds", 2)
            self.debate_manager = DebateManager(max_rounds=max_rounds, verbose=self.verbose)

        debate_result = self.debate_manager.debate(proposal, MockDefenderAgent(defender["name"]), challenger)

        self.tracker.complete(challenger.name, "辩论完成")

        self.stats["debated_tasks"] += 1

        return {
            "mode": "debate",
            "task": task,
            "debate_quality": debate_result["debate_quality"],
            "recommendation": debate_result["recommendation"],
            "result": f"✅ 辩论完成，质量：{debate_result['debate_quality']}"
        }

    def _execute_layered(self, task: str) -> Dict:
        """
        分层模式执行

        Args:
            task: 任务描述

        Returns:
            dict: 执行结果
        """
        print("🎯 使用分层决策模式执行\n")

        # 使用分层决策系统
        result = self.layered_system.process(task)

        self.stats["layered_decisions"] += 1

        return {
            "mode": "layered",
            "task": task,
            "decision": result.get("action"),
            "reasoning": result.get("reasoning"),
            "result": f"✅ 分层决策完成：{result.get('action')}"
        }

    def _analyze_task_type(self, task: str) -> str:
        """分析任务类型"""
        task_lower = task.lower()

        if "代码" in task_lower or "开发" in task_lower:
            return "tech"
        elif "设计" in task_lower or "图纸" in task_lower:
            return "design"
        elif "日志" in task_lower or "记录" in task_lower:
            return "log"
        else:
            return "tech"  # 默认

    def _create_agent(self, agent_type: str) -> Dict:
        """创建 Agent"""
        agent_config = self.config.get_agent_config(agent_type)

        if not agent_config:
            agent_config = {
                "name": "Agent",
                "role": "通用 Agent",
                "model": "glm-4.7"
            }

        return {
            "type": agent_type,
            "name": agent_config.get("role", "Agent"),
            "config": agent_config
        }

    def _print_summary(self):
        """打印执行摘要"""
        print(f"\n{'='*70}")
        print(f"📊 执行摘要")
        print(f"{'='*70}\n")

        summary = self.tracker.get_summary()

        print(f"总 Agent 数: {summary['total_agents']}")
        print(f"完成: {summary['complete_agents']}")
        print(f"错误: {summary['error_agents']}")
        print(f"成功率: {summary['success_rate']*100:.1f}%")
        print(f"总耗时: {self.tracker._format_time(summary['elapsed_time'])}")

        print(f"\n框架统计:")
        print(f"总任务数: {self.stats['total_tasks']}")
        print(f"完成任务: {self.stats['completed_tasks']}")
        print(f"失败任务: {self.stats['failed_tasks']}")
        print(f"辩论任务: {self.stats['debated_tasks']}")
        print(f"分层决策: {self.stats['layered_decisions']}")

        print(f"\n{'='*70}\n")

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats.copy()

    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "debated_tasks": 0,
            "layered_decisions": 0
        }


# 辅助类
class MockDefenderAgent:
    """模拟防守 Agent"""

    def __init__(self, name: str):
        self.name = name

    def respond(self, challenge: Dict) -> str:
        """回应质疑"""
        return f"""
感谢挑战者的质疑，我的回应如下：

关于风险：我已经评估了所有风险，并准备了缓解措施
关于问题：我会确保充分测试和验证
关于担忧：我们有足够的技术储备

具体措施：
- 增加单元测试覆盖率到 90%
- 进行性能基准测试
- 制定详细的实施计划
        """


# 测试代码
if __name__ == "__main__":
    print("🧪 测试统一 Agent 框架\n")

    framework = AgentFramework(verbose=True)

    # 测试 1: 简单模式
    print("="*70)
    print("测试 1: 简单模式")
    print("="*70)
    framework.execute_task("编写一个 Python 脚本", mode="simple")

    # 测试 2: 分层模式
    print("\n" + "="*70)
    print("测试 2: 分层决策模式")
    print("="*70)
    framework.execute_task("开发新的数据处理模块", mode="layered")

    # 测试 3: 辩论模式
    print("\n" + "="*70)
    print("测试 3: 辩论模式")
    print("="*70)
    framework.execute_task("设计新的用户界面", mode="debate")

    # 显示统计
    print("\n" + "="*70)
    print("框架统计")
    print("="*70)
    stats = framework.get_stats()
    print(f"总任务数: {stats['total_tasks']}")
    print(f"完成任务: {stats['completed_tasks']}")
    print(f"辩论任务: {stats['debated_tasks']}")
    print(f"分层决策: {stats['layered_decisions']}")
