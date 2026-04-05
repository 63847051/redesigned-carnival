#!/usr/bin/env python3
"""
任务内部 Agent Loop 实现
参考 Claude Code 的 Agent Loop 机制

核心原理：
- 不是"一步到位"，而是"循环推进"
- 思考 → 行动 → 观察 → 再思考
- 每次循环推进一步，建立在上一步反馈上
"""

import time
import json
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum


class LoopState(Enum):
    """循环状态"""
    THINKING = "thinking"      # 思考
    ACTING = "acting"          # 行动
    OBSERVING = "observing"    # 观察
    COMPLETED = "completed"    # 完成
    FAILED = "failed"          # 失败


@dataclass
class StepResult:
    """步骤结果"""
    state: LoopState
    thought: str              # 思考内容
    action: str               # 行动内容
    observation: str          # 观察结果
    next_thought: str         # 下一步思考
    timestamp: float          # 时间戳
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "state": self.state.value,
            "thought": self.thought,
            "action": self.action,
            "observation": self.observation,
            "next_thought": self.next_thought,
            "timestamp": self.timestamp
        }


class TaskAgentLoop:
    """任务内部 Agent Loop"""
    
    def __init__(self, 
                 task: str,
                 max_iterations: int = 100,
                 timeout: int = 300):
        """
        初始化 Agent Loop
        
        Args:
            task: 任务描述
            max_iterations: 最大迭代次数
            timeout: 超时时间（秒）
        """
        self.task = task
        self.max_iterations = max_iterations
        self.timeout = timeout
        self.start_time = None
        self.steps: List[StepResult] = []
        self.current_state = None
        
    def think(self, context: Dict[str, Any]) -> str:
        """
        思考阶段 - 分析当前状态，决定下一步
        
        Args:
            context: 当前上下文
        
        Returns:
            思考内容
        """
        # 这里可以集成 AI 模型进行思考
        # 简化版本：基于规则思考
        
        if not self.steps:
            # 第一步：分析任务
            return f"分析任务：{self.task}，需要分解为具体步骤"
        
        last_step = self.steps[-1]
        
        if last_step.state == LoopState.OBSERVING:
            # 观察后思考：根据观察结果决定下一步
            if "成功" in last_step.observation:
                return "上一步成功，继续下一步"
            elif "失败" in last_step.observation:
                return "上一步失败，需要调整策略"
            else:
                return "观察结果不明确，需要更多信息"
        
        return "继续推进任务"
    
    def decide_action(self, thought: str, context: Dict[str, Any]) -> str:
        """
        行动阶段 - 根据思考决定具体行动
        
        Args:
            thought: 思考内容
            context: 当前上下文
        
        Returns:
            行动内容
        """
        if not self.steps:
            # 第一步：分解任务
            return f"分解任务：{self.task}"
        
        last_step = self.steps[-1]
        
        if "继续" in thought:
            # 继续下一步
            return f"执行任务的下一个小步骤"
        
        if "调整" in thought:
            # 调整策略
            return f"调整任务执行策略"
        
        return "执行任务"
    
    def execute_action(self, action: str, context: Dict[str, Any]) -> str:
        """
        执行行动 - 执行具体行动
        
        Args:
            action: 行动内容
            context: 当前上下文
        
        Returns:
            观察结果
        """
        # 这里可以集成具体的工具执行
        # 简化版本：模拟执行
        
        if "分解" in action:
            return f"任务已分解为多个步骤"
        
        if "执行" in action:
            return f"步骤执行成功"
        
        if "调整" in action:
            return f"策略已调整"
        
        return f"行动已执行"
    
    def observe(self, result: str, context: Dict[str, Any]) -> str:
        """
        观察阶段 - 观察行动结果
        
        Args:
            result: 执行结果
            context: 当前上下文
        
        Returns:
            观察内容
        """
        # 观察结果，判断是否成功
        if "成功" in result:
            return "观察到：执行成功"
        
        if "失败" in result:
            return "观察到：执行失败"
        
        return f"观察到：{result}"
    
    def should_continue(self) -> bool:
        """
        判断是否应该继续循环
        
        Returns:
            是否继续
        """
        # 检查超时
        if self.start_time and time.time() - self.start_time > self.timeout:
            return False
        
        # 检查最大迭代次数
        if len(self.steps) >= self.max_iterations:
            return False
        
        # 检查是否完成
        if self.steps and self.steps[-1].state == LoopState.COMPLETED:
            return False
        
        # 检查是否失败
        if self.steps and self.steps[-1].state == LoopState.FAILED:
            return False
        
        return True
    
    def run(self, context: Optional[Dict[str, Any]] = None) -> List[StepResult]:
        """
        运行 Agent Loop
        
        Args:
            context: 初始上下文
        
        Returns:
            所有步骤的结果列表
        """
        if context is None:
            context = {}
        
        self.start_time = time.time()
        self.steps = []
        
        while self.should_continue():
            # 1. 思考
            thought = self.think(context)
            
            # 2. 行动
            action = self.decide_action(thought, context)
            
            # 3. 执行
            result = self.execute_action(action, context)
            
            # 4. 观察
            observation = self.observe(result, context)
            
            # 5. 下一步思考
            next_thought = self.think({**context, "last_observation": observation})
            
            # 记录步骤
            step = StepResult(
                state=LoopState.THINKING,
                thought=thought,
                action=action,
                observation=observation,
                next_thought=next_thought,
                timestamp=time.time()
            )
            self.steps.append(step)
            
            # 更新上下文
            context = {
                **context,
                "last_step": step.to_dict()
            }
            
            # 检查是否完成
            if "完成" in observation or "成功" in result:
                break
        
        return self.steps
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取循环总结
        
        Returns:
            总结信息
        """
        if not self.steps:
            return {
                "task": self.task,
                "status": "no_steps",
                "total_steps": 0,
                "duration": 0
            }
        
        duration = time.time() - self.start_time if self.start_time else 0
        
        return {
            "task": self.task,
            "status": "completed",
            "total_steps": len(self.steps),
            "duration": f"{duration:.2f}s",
            "steps_per_second": len(self.steps) / duration if duration > 0 else 0,
            "first_step": self.steps[0].to_dict(),
            "last_step": self.steps[-1].to_dict()
        }


# 便捷函数
def run_task_with_loop(task: str, 
                      max_iterations: int = 100,
                      timeout: int = 300) -> Dict[str, Any]:
    """
    使用 Agent Loop 运行任务
    
    Args:
        task: 任务描述
        max_iterations: 最大迭代次数
        timeout: 超时时间
    
    Returns:
        任务结果
    """
    loop = TaskAgentLoop(
        task=task,
        max_iterations=max_iterations,
        timeout=timeout
    )
    
    steps = loop.run()
    summary = loop.get_summary()
    
    return {
        "task": task,
        "steps": [step.to_dict() for step in steps],
        "summary": summary
    }


# 测试代码
if __name__ == '__main__':
    print("=" * 60)
    print("任务内部 Agent Loop 测试")
    print("=" * 60)
    
    # 测试任务
    task = "创建一个 Python 脚本，读取文件并统计行数"
    
    print(f"\n📋 任务: {task}")
    print("\n🔄 开始执行 Agent Loop...\n")
    
    # 运行任务
    result = run_task_with_loop(task, max_iterations=10)
    
    # 显示结果
    print(f"✅ 任务完成！")
    print(f"\n📊 统计信息:")
    print(f"  总步骤: {result['summary']['total_steps']}")
    print(f"  耗时: {result['summary']['duration']}")
    print(f"  速度: {result['summary']['steps_per_second']:.2f} 步/秒")
    
    print(f"\n📝 执行步骤:")
    for i, step in enumerate(result['steps'], 1):
        print(f"\n  步骤 {i}:")
        print(f"    💭 思考: {step['thought']}")
        print(f"    🎬 行动: {step['action']}")
        print(f"    👁️ 观察: {step['observation']}")
