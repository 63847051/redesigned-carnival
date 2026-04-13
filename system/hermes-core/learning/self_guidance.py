"""
自我引导系统 - 动态提示注入

在合适的时机注入引导提示，帮助 Agent 自我反思和改进
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import random


@dataclass
class GuidanceTrigger:
    """引导触发器"""

    name: str
    condition: str
    prompt: str
    priority: int = 0
    cooldown: int = 0


@dataclass
class InjectedGuidance:
    """注入的引导"""

    trigger: str
    prompt: str
    injected_at: datetime
    applied: bool = False


class SelfGuidance:
    """
    自我引导系统

    动态注入提示，引导 Agent 自我反思和改进
    """

    DEFAULT_TRIGGERS = [
        GuidanceTrigger(
            name="repeated_error",
            condition="连续相同错误 >= 3",
            prompt="你似乎在重复同样的错误。让我们暂停一下，思考更好的方法。",
            priority=10,
            cooldown=5,
        ),
        GuidanceTrigger(
            name="low_confidence",
            condition="置信度 < 0.5",
            prompt="你的回答似乎不太确定。考虑寻求更多上下文或确认。",
            priority=5,
            cooldown=3,
        ),
        GuidanceTrigger(
            name="complex_task",
            condition="工具调用 > 8",
            prompt="这是一个复杂任务。考虑将问题分解为更小的步骤。",
            priority=7,
            cooldown=2,
        ),
        GuidanceTrigger(
            name="tool_misuse",
            condition="工具使用失败",
            prompt="工具调用遇到了问题。检查参数是否正确，考虑替代方案。",
            priority=8,
            cooldown=1,
        ),
        GuidanceTrigger(
            name="success_pattern",
            condition="连续成功 >= 5",
            prompt="你做得很好！记住这个成功的模式，它可能在将来有帮助。",
            priority=3,
            cooldown=10,
        ),
    ]

    def __init__(self):
        self.triggers = {t.name: t for t in self.DEFAULT_TRIGGERS}
        self._cooldown_counter: Dict[str, int] = {}
        self._guidance_history: List[InjectedGuidance] = []

    def register_trigger(self, trigger: GuidanceTrigger) -> None:
        """注册新的触发器"""
        self.triggers[trigger.name] = trigger

    def evaluate_triggers(self, context: Dict[str, Any]) -> List[str]:
        """
        评估所有触发器

        返回应该注入的引导列表
        """
        active_guides = []

        for name, trigger in self.triggers.items():
            if self._cooldown_counter.get(name, 0) > 0:
                self._cooldown_counter[name] -= 1
                continue

            if self._check_condition(trigger.condition, context):
                active_guides.append(trigger.prompt)
                self._cooldown_counter[name] = trigger.cooldown

                self._guidance_history.append(
                    InjectedGuidance(
                        trigger=name, prompt=trigger.prompt, injected_at=datetime.now()
                    )
                )

        return active_guides

    def _check_condition(self, condition: str, context: Dict) -> bool:
        """检查条件是否满足"""
        try:
            if "连续相同错误" in condition:
                threshold = int(condition.split(">=")[-1].strip())
                return context.get("consecutive_errors", 0) >= threshold

            if "置信度" in condition:
                threshold = float(condition.split("<")[1].strip())
                return context.get("confidence", 1.0) < threshold

            if "工具调用" in condition:
                threshold = int(condition.split(">")[1].strip())
                return context.get("tool_call_count", 0) > threshold

            if "工具使用失败" in condition:
                return context.get("tool_failed", False)

            if "连续成功" in condition:
                threshold = int(condition.split(">=")[1].strip())
                return context.get("consecutive_success", 0) >= threshold

            return False
        except Exception:
            return False

    def inject_guidance(
        self, prompts: List[str], existing_prompts: List[str]
    ) -> List[str]:
        """
        注入引导到现有提示列表

        确保不重复，避免冲突
        """
        result = list(existing_prompts)

        for prompt in prompts:
            if prompt not in result:
                result.append(prompt)

        return result

    def generate_context_summary(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """生成上下文摘要，用于触发器评估"""
        return {
            "consecutive_errors": stats.get("consecutive_errors", 0),
            "consecutive_success": stats.get("consecutive_success", 0),
            "tool_call_count": stats.get("tool_call_count", 0),
            "confidence": stats.get("confidence", 1.0),
            "tool_failed": stats.get("tool_failed", False),
            "last_error": stats.get("last_error"),
        }

    def get_guidance_history(self, limit: int = 10) -> List[Dict]:
        """获取引导历史"""
        return [
            {
                "trigger": g.trigger,
                "prompt": g.prompt,
                "injected_at": g.injected_at.isoformat(),
                "applied": g.applied,
            }
            for g in self._guidance_history[-limit:]
        ]

    def clear_cooldowns(self) -> None:
        """清除所有冷却计数器"""
        self._cooldown_counter.clear()


_guidance_instance: Optional[SelfGuidance] = None


def get_self_guidance() -> SelfGuidance:
    """获取全局自我引导实例"""
    global _guidance_instance
    if _guidance_instance is None:
        _guidance_instance = SelfGuidance()
    return _guidance_instance


def should_inject_guidance(context: Dict[str, Any]) -> List[str]:
    """便捷函数：判断是否需要注入引导"""
    guidance = get_self_guidance()
    context_summary = guidance.generate_context_summary(context)
    return guidance.evaluate_triggers(context_summary)
