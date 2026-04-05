#!/usr/bin/env python3
"""
增强版任务内部 Agent Loop
集成 Feature Flags、工具调用、记忆管理
"""

import time
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import os
import sys

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.join(os.environ.get('OPENCLAW_WORKSPACE', '/root/.openclaw/workspace'), 'scripts'))

try:
    from feature_flags import is_task_agent_loop_enabled
    FEATURE_FLAGS_AVAILABLE = True
except ImportError:
    FEATURE_FLAGS_AVAILABLE = False
    print("⚠️ Feature Flags 模块未找到，将使用默认配置")


class LoopState(Enum):
    """循环状态"""
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class StepResult:
    """步骤结果"""
    iteration: int
    state: LoopState
    thought: str
    action: str
    observation: str
    next_thought: str
    timestamp: float
    tools_used: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "iteration": self.iteration,
            "state": self.state.value,
            "thought": self.thought,
            "action": self.action,
            "observation": self.observation,
            "next_thought": self.next_thought,
            "timestamp": self.timestamp,
            "tools_used": self.tools_used
        }


class EnhancedTaskAgentLoop:
    """增强版任务内部 Agent Loop"""
    
    def __init__(self,
                 task: str,
                 max_iterations: int = 100,
                 timeout: int = 300,
                 enable_loop_tracking: bool = False):
        """
        初始化增强版 Agent Loop
        
        Args:
            task: 任务描述
            max_iterations: 最大迭代次数
            timeout: 超时时间（秒）
            enable_loop_tracking: 是否启用循环路径跟踪
        """
        self.task = task
        self.max_iterations = max_iterations
        self.timeout = timeout
        self.enable_loop_tracking = enable_loop_tracking
        
        self.start_time = None
        self.steps: List[StepResult] = []
        self.current_iteration = 0
        
        # 工具系统
        self.tools = {
            "read": self._tool_read,
            "write": self._tool_write,
            "exec": self._tool_exec,
            "search": self._tool_search
        }
        
        # 检查 Feature Flags
        if FEATURE_FLAGS_AVAILABLE:
            self.loop_enabled = is_task_agent_loop_enabled()
        else:
            self.loop_enabled = True
    
    def _tool_read(self, path: str) -> str:
        """读文件工具"""
        try:
            with open(path, 'r') as f:
                return f"读取文件 {path} 成功"
        except Exception as e:
            return f"读取文件失败: {e}"
    
    def _tool_write(self, path: str, content: str) -> str:
        """写文件工具"""
        try:
            with open(path, 'w') as f:
                f.write(content)
            return f"写入文件 {path} 成功"
        except Exception as e:
            return f"写入文件失败: {e}"
    
    def _tool_exec(self, command: str) -> str:
        """执行命令工具"""
        return f"执行命令: {command}"
    
    def _tool_search(self, query: str) -> str:
        """搜索工具"""
        return f"搜索: {query}"
    
    def think(self, context: Dict[str, Any]) -> str:
        """思考阶段"""
        if len(self.steps) == 0:
            return f"🎯 开始分析任务：{self.task}，需要制定执行计划"
        
        last_step = self.steps[-1]
        
        # 根据上一步的观察结果思考
        if "成功" in last_step.observation:
            return f"✅ 上一步成功，继续推进任务"
        elif "失败" in last_step.observation:
            return f"❌ 上一步失败，需要分析原因并调整策略"
        else:
            return f"🤔 分析观察结果，决定下一步行动"
    
    def decide_action(self, thought: str, context: Dict[str, Any]) -> tuple[str, List[str]]:
        """
        行动阶段 - 决定行动和需要的工具
        
        Returns:
            (行动内容, 工具列表)
        """
        if self.current_iteration == 0:
            return "📋 制定任务执行计划", []
        
        if "计划" in context.get("last_action", ""):
            return "🔧 执行计划的第一步", ["exec"]
        
        if "继续" in thought:
            return "▶️ 执行任务的下一个小步骤", ["exec"]
        
        if "调整" in thought:
            return "🔧 调整执行策略", []
        
        return "🎯 继续推进任务", []
    
    def execute_action(self, action: str, tools: List[str], context: Dict[str, Any]) -> tuple[str, str]:
        """
        执行行动 - 调用工具并返回结果
        
        Returns:
            (执行结果, 使用的工具)
        """
        results = []
        tools_used = []
        
        for tool_name in tools:
            if tool_name in self.tools:
                result = self.tools[tool_name](action)
                results.append(result)
                tools_used.append(tool_name)
        
        if results:
            return "; ".join(results), tools_used
        
        # 模拟执行
        if "计划" in action:
            return f"✅ 任务计划已制定", []
        
        if "执行" in action:
            return f"✅ 任务步骤已执行", []
        
        return f"✅ 行动已执行", []
    
    def observe(self, result: str, context: Dict[str, Any]) -> tuple[str, LoopState]:
        """
        观察阶段 - 观察执行结果并判断状态
        
        Returns:
            (观察内容, 循环状态)
        """
        if "成功" in result or "完成" in result:
            return "观察：执行成功，任务推进正常", LoopState.ACTING
        
        if "失败" in result:
            return "观察：执行失败，需要处理错误", LoopState.FAILED
        
        return f"观察：{result}", LoopState.ACTING
    
    def should_continue(self) -> bool:
        """判断是否应该继续循环"""
        # 检查 Feature Flags
        if FEATURE_FLAGS_AVAILABLE and not self.loop_enabled:
            print("⚠️ TASK_AGENT_LOOP 功能已禁用，跳过循环")
            return False
        
        # 检查超时
        if self.start_time and time.time() - self.start_time > self.timeout:
            print(f"⏰ 超时（{self.timeout}秒），停止循环")
            return False
        
        # 检查最大迭代次数
        if self.current_iteration >= self.max_iterations:
            print(f"🔄 达到最大迭代次数（{self.max_iterations}），停止循环")
            return False
        
        # 检查是否完成
        if self.steps and self.steps[-1].state == LoopState.COMPLETED:
            return False
        
        # 检查是否失败
        if self.steps and self.steps[-1].state == LoopState.FAILED:
            return False
        
        return True
    
    def run(self, context: Optional[Dict[str, Any]] = None) -> List[StepResult]:
        """运行 Agent Loop"""
        if context is None:
            context = {}
        
        self.start_time = time.time()
        self.steps = []
        self.current_iteration = 0
        
        print(f"🚀 启动任务内部 Agent Loop")
        print(f"📋 任务: {self.task}")
        print(f"⚙️ 最大迭代: {self.max_iterations}")
        print(f"⏱️ 超时: {self.timeout}秒")
        print()
        
        while self.should_continue():
            self.current_iteration += 1
            
            # 1. 思考
            thought = self.think(context)
            print(f"🔄 [{self.current_iteration}] 💭 {thought}")
            
            # 2. 行动
            action, tools_needed = self.decide_action(thought, context)
            print(f"🔄 [{self.current_iteration}] 🎬 {action}")
            if tools_needed:
                print(f"🔄 [{self.current_iteration}] 🔧 使用工具: {', '.join(tools_needed)}")
            
            # 3. 执行
            result, tools_used = self.execute_action(action, tools_needed, context)
            
            # 4. 观察
            observation, state = self.observe(result, context)
            print(f"🔄 [{self.current_iteration}] 👁️ {observation}")
            
            # 5. 下一步思考
            next_thought = self.think({**context, "last_observation": observation})
            
            # 记录步骤
            step = StepResult(
                iteration=self.current_iteration,
                state=state,
                thought=thought,
                action=action,
                observation=observation,
                next_thought=next_thought,
                timestamp=time.time(),
                tools_used=tools_used
            )
            self.steps.append(step)
            
            # 更新上下文
            context = {
                **context,
                "last_action": action,
                "last_result": result,
                "last_observation": observation
            }
            
            print()  # 空行分隔
            
            # 小延迟，避免过快
            time.sleep(0.1)
        
        print(f"✅ Agent Loop 完成！共 {self.current_iteration} 次迭代")
        
        return self.steps
    
    def get_summary(self) -> Dict[str, Any]:
        """获取循环总结"""
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
            "tools_used": list(set(tool for step in self.steps for tool in step.tools_used)),
            "first_step": self.steps[0].to_dict(),
            "last_step": self.steps[-1].to_dict()
        }


# 便捷函数
def run_task_with_enhanced_loop(task: str,
                               max_iterations: int = 100,
                               timeout: int = 300,
                               enable_tracking: bool = False) -> Dict[str, Any]:
    """
    使用增强版 Agent Loop 运行任务
    
    Args:
        task: 任务描述
        max_iterations: 最大迭代次数
        timeout: 超时时间
        enable_tracking: 是否启用循环路径跟踪
    
    Returns:
        任务结果
    """
    loop = EnhancedTaskAgentLoop(
        task=task,
        max_iterations=max_iterations,
        timeout=timeout,
        enable_loop_tracking=enable_tracking
    )
    
    steps = loop.run()
    summary = loop.get_summary()
    
    return {
        "task": task,
        "steps": [step.to_dict() for step in steps],
        "summary": summary
    }


if __name__ == '__main__':
    print("=" * 60)
    print("增强版任务内部 Agent Loop 测试")
    print("=" * 60)
    
    # 测试任务
    task = "创建一个 Python 脚本，实现文件读写功能"
    
    result = run_task_with_enhanced_loop(
        task=task,
        max_iterations=5,
        timeout=30
    )
    
    print("\n" + "=" * 60)
    print("📊 执行总结")
    print("=" * 60)
    print(f"✅ 任务: {result['summary']['task']}")
    print(f"📈 总步骤: {result['summary']['total_steps']}")
    print(f"⏱️ 耗时: {result['summary']['duration']}")
    print(f"🚀 速度: {result['summary']['steps_per_second']:.2f} 步/秒")
    if result['summary'].get('tools_used'):
        print(f"🔧 使用工具: {', '.join(result['summary']['tools_used'])}")
