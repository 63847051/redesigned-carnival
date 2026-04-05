#!/usr/bin/env python3
"""
进度跟踪器
实时显示 Agent 执行进度
"""

import time
from datetime import datetime
from typing import Dict, Optional


class ProgressTracker:
    """进度跟踪器"""

    def __init__(self, verbose=True):
        """
        初始化进度跟踪器

        Args:
            verbose: 是否显示详细信息
        """
        self.agent_status: Dict[str, dict] = {}
        self.start_time = time.time()
        self.verbose = verbose

    def update(self, agent_id: str, status: str, message: str, progress: int = 0):
        """
        更新 Agent 状态

        Args:
            agent_id: Agent ID
            status: 状态 (running, complete, error, waiting)
            message: 状态消息
            progress: 进度百分比 (0-100)
        """
        self.agent_status[agent_id] = {
            "status": status,
            "message": message,
            "progress": progress,
            "timestamp": time.time()
        }

        if self.verbose:
            self.display()

    def display(self):
        """显示进度面板"""
        print("\n" + "="*70)
        print("📊 任务执行进度")
        print("="*70)

        if not self.agent_status:
            print("⏳ 暂无 Agent 运行")
        else:
            for agent_id, info in self.agent_status.items():
                icon = {
                    "running": "🔄",
                    "complete": "✅",
                    "error": "❌",
                    "waiting": "⏳"
                }.get(info["status"], "❓")

                progress_bar = self._make_progress_bar(info.get("progress", 0))
                status_text = info["message"]

                print(f"{icon} {agent_id:25s} {status_text:35s}")

                if info["status"] == "running" and info.get("progress", 0) > 0:
                    print(f"   {progress_bar} {info.get('progress', 0)}%")

        elapsed = time.time() - self.start_time
        print(f"\n⏱️  已用时间: {self._format_time(elapsed)}")
        print("="*70 + "\n")

    def start(self, agent_id: str, message: str = ""):
        """标记 Agent 开始运行"""
        self.update(agent_id, "running", message or "开始执行...", 0)

    def complete(self, agent_id: str, message: str = "执行完成"):
        """标记 Agent 完成"""
        self.update(agent_id, "complete", message, 100)

    def error(self, agent_id: str, message: str = "执行出错"):
        """标记 Agent 出错"""
        self.update(agent_id, "error", message, 0)

    def waiting(self, agent_id: str, message: str = "等待中"):
        """标记 Agent 等待"""
        self.update(agent_id, "waiting", message, 0)

    def get_status(self, agent_id: str) -> Optional[dict]:
        """获取 Agent 状态"""
        return self.agent_status.get(agent_id)

    def get_all_status(self) -> Dict[str, dict]:
        """获取所有 Agent 状态"""
        return self.agent_status.copy()

    def is_complete(self, agent_id: str) -> bool:
        """检查 Agent 是否完成"""
        status = self.agent_status.get(agent_id, {}).get("status")
        return status == "complete"

    def is_running(self, agent_id: str) -> bool:
        """检查 Agent 是否正在运行"""
        status = self.agent_status.get(agent_id, {}).get("status")
        return status == "running"

    def has_error(self, agent_id: str) -> bool:
        """检查 Agent 是否出错"""
        status = self.agent_status.get(agent_id, {}).get("status")
        return status == "error"

    def reset(self):
        """重置进度跟踪器"""
        self.agent_status = {}
        self.start_time = time.time()

    def _make_progress_bar(self, progress: int, width: int = 30) -> str:
        """
        生成进度条

        Args:
            progress: 进度百分比 (0-100)
            width: 进度条宽度

        Returns:
            str: 进度条字符串
        """
        filled = int(width * progress / 100)
        bar = "█" * filled + "░" * (width - filled)
        return bar

    def _format_time(self, seconds: float) -> str:
        """
        格式化时间

        Args:
            seconds: 秒数

        Returns:
            str: 格式化的时间字符串
        """
        minutes, seconds = divmod(int(seconds), 60)
        if minutes > 0:
            return f"{minutes}分{seconds}秒"
        else:
            return f"{seconds}秒"

    def get_summary(self) -> dict:
        """
        获取执行摘要

        Returns:
            dict: 执行摘要
        """
        total_agents = len(self.agent_status)
        complete_agents = sum(1 for s in self.agent_status.values() if s["status"] == "complete")
        error_agents = sum(1 for s in self.agent_status.values() if s["status"] == "error")
        running_agents = sum(1 for s in self.agent_status.values() if s["status"] == "running")

        elapsed = time.time() - self.start_time

        return {
            "total_agents": total_agents,
            "complete_agents": complete_agents,
            "error_agents": error_agents,
            "running_agents": running_agents,
            "elapsed_time": elapsed,
            "success_rate": complete_agents / total_agents if total_agents > 0 else 0
        }


# 测试代码
if __name__ == "__main__":
    print("🧪 测试进度跟踪器\n")

    tracker = ProgressTracker()

    # 模拟任务执行
    print("1. 开始执行任务...\n")
    tracker.start("小新", "正在编写代码...")

    time.sleep(1)
    tracker.update("小新", "running", "正在编写代码...", 30)

    time.sleep(1)
    tracker.update("小新", "running", "正在编写代码...", 60)

    time.sleep(1)
    tracker.complete("小新", "代码编写完成")

    # 多个 Agent
    print("2. 多个 Agent 并行执行...\n")
    tracker.reset()

    tracker.start("小新", "正在编写代码...")
    tracker.start("小蓝", "正在记录日志...")
    tracker.waiting("设计专家", "等待小新完成...")

    time.sleep(1)
    tracker.update("小新", "running", "正在编写代码...", 50)
    tracker.update("小蓝", "running", "正在记录日志...", 80)

    time.sleep(1)
    tracker.complete("小新", "代码编写完成")
    tracker.complete("小蓝", "日志记录完成")

    time.sleep(1)
    tracker.start("设计专家", "正在设计方案...")

    time.sleep(1)
    tracker.complete("设计专家", "方案设计完成")

    # 模拟错误
    print("3. 模拟错误情况...\n")
    tracker.reset()

    tracker.start("小新", "正在执行任务...")
    time.sleep(1)
    tracker.error("小新", "执行出错：缺少依赖")

    # 显示摘要
    print("\n📊 执行摘要:")
    summary = tracker.get_summary()
    print(f"  总 Agent 数: {summary['total_agents']}")
    print(f"  完成: {summary['complete_agents']}")
    print(f"  运行中: {summary['running_agents']}")
    print(f"  错误: {summary['error_agents']}")
    print(f"  成功率: {summary['success_rate']*100:.1f}%")
    print(f"  总耗时: {tracker._format_time(summary['elapsed_time'])}")
