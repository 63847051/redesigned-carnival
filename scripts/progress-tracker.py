#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进度反馈系统
- 实时进度条
- 任务状态更新
- ETA 估算
"""

import time
import sys
from datetime import datetime, timedelta
from typing import Callable, Optional

class ProgressTracker:
    """进度跟踪器"""
    
    def __init__(self, total_steps: int, task_name: str = "任务"):
        self.total_steps = total_steps
        self.current_step = 0
        self.task_name = task_name
        self.start_time = datetime.now()
        self.last_update = self.start_time
        
    def update(self, step: int, message: str = ""):
        """更新进度"""
        self.current_step = step
        progress = (step / self.total_steps) * 100
        
        # 计算 ETA
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if step > 0:
            avg_time_per_step = elapsed / step
            remaining_steps = self.total_steps - step
            eta_seconds = avg_time_per_step * remaining_steps
            eta = str(timedelta(seconds=int(eta_seconds)))
        else:
            eta = "计算中..."
        
        # 显示进度条
        self._display_progress(progress, message, eta)
    
    def _display_progress(self, progress: float, message: str, eta: str):
        """显示进度条"""
        bar_length = 40
        filled = int(bar_length * progress / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        # 清除当前行
        sys.stdout.write("\r\033[K")
        
        # 显示进度
        output = f"[{bar}] {progress:.1f}% | {self.task_name}"
        if message:
            output += f" | {message}"
        if eta != "计算中...":
            output += f" | ETA: {eta}"
        
        sys.stdout.write(output)
        sys.stdout.flush()
    
    def complete(self, message: str = "完成！"):
        """标记完成"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        elapsed_str = str(timedelta(seconds=int(elapsed)))
        
        sys.stdout.write("\r\033[K")
        print(f"✅ {self.task_name} | {message} | 耗时: {elapsed_str}")


def execute_with_progress(
    task_name: str,
    steps: list,
    step_func: Callable,
    show_progress: bool = True
):
    """
    执行任务并显示进度
    
    Args:
        task_name: 任务名称
        steps: 步骤列表
        step_func: 步骤执行函数
        show_progress: 是否显示进度
    """
    if not show_progress:
        # 不显示进度，直接执行
        for step in steps:
            step_func(step)
        return
    
    # 显示进度
    tracker = ProgressTracker(len(steps), task_name)
    
    for i, step in enumerate(steps):
        # 执行步骤
        result = step_func(step)
        
        # 更新进度
        tracker.update(i + 1, f"正在处理: {step}")
        
        # 避免更新过快
        time.sleep(0.1)
    
    # 完成
    tracker.complete(f"成功完成 {len(steps)} 个步骤")


# ============================================================================
# 测试
# ============================================================================

if __name__ == "__main__":
    def test_step_func(step):
        """测试步骤函数"""
        time.sleep(0.2)  # 模拟耗时操作
        return f"完成: {step}"
    
    # 测试进度条
    print("="*60)
    print("进度反馈系统测试")
    print("="*60)
    
    test_steps = [
        "分析任务",
        "创建方案",
        "实施改进",
        "测试验证",
        "完成总结"
    ]
    
    execute_with_progress(
        task_name="用户交互优化",
        steps=test_steps,
        step_func=test_step_func,
        show_progress=True
    )
    
    print("\n✅ 测试完成！")
