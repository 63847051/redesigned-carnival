#!/usr/bin/env python3
"""
Auto-Learning Guidance System

Provides self-directed learning capabilities for the agent:
1. Skill Creation Triggers - When to create new skills from successful approaches
2. Skill Improvement Triggers - When to improve existing skills after usage
3. Self-Prompt Injection - Guidance to inject into system prompts

This system analyzes tool usage patterns to autonomously decide when
to create or improve skills, following Hermes-agent's approach.
"""

import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class TriggerType(Enum):
    SKILL_CREATE = "skill_create"
    SKILL_IMPROVE = "skill_improve"
    NONE = "none"


@dataclass
class LearningMetrics:
    tool_call_count: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    skill_usage_count: int = 0
    consecutive_failures: int = 0
    last_task_timestamp: float = field(default_factory=time.time)
    tool_sequence: List[str] = field(default_factory=list)

    def add_tool_call(self, tool_name: str, success: bool = True) -> None:
        self.tool_call_count += 1
        self.tool_sequence.append(tool_name)
        if len(self.tool_sequence) > 50:
            self.tool_sequence = self.tool_sequence[-50:]

        if success:
            self.successful_tasks += 1
            self.consecutive_failures = 0
        else:
            self.failed_tasks += 1
            self.consecutive_failures += 1

        self.last_task_timestamp = time.time()

    def get_tool_sequence_string(self) -> str:
        return " → ".join(self.tool_sequence[-10:])


@dataclass
class SkillDecision:
    trigger_type: TriggerType
    skill_name: Optional[str] = None
    reason: str = ""
    confidence: float = 0.0
    suggested_improvements: List[str] = field(default_factory=list)
    suggested_content: Optional[str] = None


class AutoLearningConfig:
    SKILL_CREATE_THRESHOLD = 5
    SKILL_IMPROVE_USAGE_THRESHOLD = 3
    CONSECUTIVE_FAILURE_THRESHOLD = 3
    TOOL_DIVERSITY_THRESHOLD = 3
    TIME_WINDOW_SECONDS = 300


config = AutoLearningConfig()


def should_create_skill(metrics: LearningMetrics) -> Tuple[bool, str, float]:
    """
    Determine if a skill should be created based on current metrics.

    Triggers for skill creation:
    1. 5+ tool calls in a session (complex task)
    2. 3+ unique tools used (reusable pattern)
    3. 3+ consecutive failures (needs documentation)

    Returns: (should_create, reason, confidence)
    """
    if metrics.tool_call_count < config.SKILL_CREATE_THRESHOLD:
        return False, "", 0.0

    unique_tools = len(set(metrics.tool_sequence))
    if unique_tools < config.TOOL_DIVERSITY_THRESHOLD:
        return False, "", 0.0

    time_elapsed = time.time() - metrics.last_task_timestamp
    if time_elapsed > config.TIME_WINDOW_SECONDS:
        return False, "Task too spread out", 0.0

    confidence = min(1.0, metrics.tool_call_count / 10.0) * 0.5 + unique_tools / 10.0

    reason = (
        f"Complex task detected: {metrics.tool_call_count} tool calls, "
        f"{unique_tools} unique tools. "
        f"Sequence: {metrics.get_tool_sequence_string()}"
    )

    return True, reason, confidence


def should_improve_skill(
    skill_name: str, metrics: LearningMetrics, failure_context: Optional[str] = None
) -> Tuple[bool, str, List[str]]:
    """
    Determine if a skill should be improved based on usage patterns.

    Triggers for skill improvement:
    1. Skill used 3+ times (enough usage data)
    2. Consecutive failures with skill (bug/chasm)
    3. User requests specific improvements

    Returns: (should_improve, reason, suggested_improvements_list)
    """
    if metrics.skill_usage_count < config.SKILL_IMPROVE_USAGE_THRESHOLD:
        return False, "", []

    if metrics.consecutive_failures >= config.CONSECUTIVE_FAILURE_THRESHOLD:
        reason = f"Skill '{skill_name}' failing {metrics.consecutive_failures} times consecutively"
        suggestions = ["Review error handling", "Add common edge cases"]
        return True, reason, suggestions

    if failure_context:
        if (
            "not found" in failure_context.lower()
            or "missing" in failure_context.lower()
        ):
            return (
                True,
                f"Skill '{skill_name}' missing functionality",
                ["Add missing capability"],
            )
        elif (
            "wrong" in failure_context.lower() or "incorrect" in failure_context.lower()
        ):
            return (
                True,
                f"Skill '{skill_name}' producing incorrect results",
                ["Review logic", "Add validation"],
            )

    reason = f"Skill '{skill_name}' used {metrics.skill_usage_count} times"
    return True, reason, ["Consider adding examples", "Add edge case handling"]


def analyze_task_complexity(tool_calls: List[Dict], task_success: bool) -> Dict:
    """
    Analyze a completed task to determine learning value.

    Args:
        tool_calls: List of {tool_name, result, success} dicts
        task_success: Whether the overall task succeeded

    Returns:
        Analysis dict with metrics and suggestions
    """
    metrics = LearningMetrics()

    for call in tool_calls:
        tool_name = call.get("tool_name", "unknown")
        success = call.get("success", task_success)
        metrics.add_tool_call(tool_name, success)

    unique_tools = len(set(metrics.tool_sequence))
    call_count = len(tool_calls)

    analysis = {
        "call_count": call_count,
        "unique_tools": unique_tools,
        "success": task_success,
        "tool_sequence": metrics.tool_sequence.copy(),
        "should_create_skill": False,
        "skill_create_reason": "",
        "skill_create_confidence": 0.0,
    }

    if call_count >= config.SKILL_CREATE_THRESHOLD:
        should, reason, conf = should_create_skill(metrics)
        analysis["should_create_skill"] = should
        analysis["skill_create_reason"] = reason
        analysis["skill_create_confidence"] = conf

    return analysis


def generate_skill_content(
    task_description: str, tool_sequence: List[str], successful_approach: str
) -> str:
    """
    Generate SKILL.md content from successful task execution.

    Args:
        task_description: What the task accomplished
        tool_sequence: Steps taken (tools used)
        successful_approach: How the task was solved

    Returns:
        Formatted SKILL.md content
    """
    tool_steps = "\n".join([f"{i + 1}. {tool}" for i, tool in enumerate(tool_sequence)])

    content = f"""---
name: {task_description.lower().replace(" ", "-")[:64]}
description: {task_description[:200]}
version: 1.0.0
created: {time.strftime("%Y-%m-%d")}
---

# {task_description}

## When to Use

Use this skill when you need to: {task_description}

## Steps

{tool_steps}

## Approach

{successful_approach}

## Notes

- This skill was auto-generated from successful task execution
- Consider adding edge case handling for production use
"""
    return content


def generate_improvement_patch(
    skill_content: str, issue_description: str, improvement_suggestion: str
) -> Optional[Tuple[str, str]]:
    """
    Generate a patch for improving existing skill content.

    Args:
        skill_content: Current SKILL.md content
        issue_description: What's wrong
        improvement_suggestion: How to fix

    Returns:
        (old_string, new_string) for fuzzy patch, or None if no clear patch
    """
    if "edge case" in issue_description.lower():
        old_section = "## Notes\n\n- "
        new_section = (
            "## Notes\n\n- Consider adding edge case handling for production use\n- "
        )
        return (old_section, new_section)

    if "error handling" in issue_description.lower():
        if "## Notes" in skill_content:
            return ("## Notes\n\n- ", "## Notes\n- Add error handling guidance\n- ")

    return None


def get_self_prompt_guidance() -> str:
    """
    Get the self-prompt guidance text to inject into system prompts.

    This tells the agent to consider skill creation/improvement autonomously.
    """
    return """
## Auto-Learning Guidance

You have the ability to create and improve skills autonomously:

### Skill Creation
After completing a complex task (5+ tool calls, 3+ unique tools), consider creating a skill
if the approach is reusable. A skill captures:
- When to use this approach
- Step-by-step process
- Key decisions and tradeoffs

### Skill Improvement
When using a skill and encountering issues (failures, missing functionality),
consider improving the skill to help future iterations.

### Decision Framework
- Create skill if: Complex task + reusable pattern + high value
- Improve skill if: Repeated failures + clear improvement + low effort
- Defer if: Task too specific + low reuse potential

You can create skills using skill_manager_tool or request skill creation assistance.
"""


def inject_auto_learning_prompt(
    base_prompt: str, metrics: Optional[LearningMetrics] = None
) -> str:
    """
    Inject auto-learning guidance into a system prompt.

    Args:
        base_prompt: The existing system prompt
        metrics: Optional current session metrics

    Returns:
        Prompt with guidance appended
    """
    guidance = get_self_prompt_guidance()

    if metrics and metrics.tool_call_count >= config.SKILL_CREATE_THRESHOLD:
        should, reason, conf = should_create_skill(metrics)
        if should:
            guidance += f"\n\n**Current Opportunity**: {reason}\n"
            guidance += f"Consider creating a skill to capture this approach."

    return f"{base_prompt}\n\n{guidance}"


def evaluate_skill_usage_for_improvement(
    skill_name: str,
    usage_count: int,
    failure_count: int,
    last_error: Optional[str] = None,
) -> Optional[SkillDecision]:
    """
    Evaluate if a skill should be improved.

    Args:
        skill_name: Name of the skill
        usage_count: Times skill has been used
        failure_count: Times skill has failed
        last_error: Most recent error message

    Returns:
        SkillDecision if improvement warranted, None otherwise
    """
    if usage_count < config.SKILL_IMPROVE_USAGE_THRESHOLD:
        return None

    if failure_count >= config.CONSECUTIVE_FAILURE_THRESHOLD:
        return SkillDecision(
            trigger_type=TriggerType.SKILL_IMPROVE,
            skill_name=skill_name,
            reason=f"Skill failing {failure_count}/{usage_count} times",
            confidence=min(1.0, failure_count / usage_count),
            suggested_improvements=["Add error handling", "Review edge cases"],
        )

    if last_error and (
        "not found" in last_error.lower() or "missing" in last_error.lower()
    ):
        return SkillDecision(
            trigger_type=TriggerType.SKILL_IMPROVE,
            skill_name=skill_name,
            reason=f"Skill missing functionality: {last_error}",
            confidence=0.8,
            suggested_improvements=["Add missing capability", "Document requirements"],
        )

    return None


def format_decision_for_display(decision: SkillDecision) -> str:
    """
    Format a skill decision for display to the agent/user.
    """
    if decision.trigger_type == TriggerType.NONE:
        return "No action needed"

    lines = [
        f"**{decision.trigger_type.value}**: {decision.skill_name or 'new skill'}",
        f"Reason: {decision.reason}",
        f"Confidence: {decision.confidence:.0%}",
    ]

    if decision.suggested_improvements:
        lines.append("Suggestions:")
        for imp in decision.suggested_improvements:
            lines.append(f"  - {imp}")

    return "\n".join(lines)


if __name__ == "__main__":
    print("Auto-Learning Guidance System")
    print("=" * 50)

    print("\n1. Testing skill creation detection:")
    metrics = LearningMetrics()
    for tool in ["read", "grep", "edit", "write", "glob"]:
        metrics.add_tool_call(tool)

    should, reason, conf = should_create_skill(metrics)
    print(f"  Should create: {should}")
    print(f"  Reason: {reason}")
    print(f"  Confidence: {conf:.0%}")

    print("\n2. Testing skill improvement detection:")
    metrics2 = LearningMetrics()
    metrics2.skill_usage_count = 5
    metrics2.consecutive_failures = 3

    decision = evaluate_skill_usage_for_improvement(
        "test-skill",
        metrics2.skill_usage_count,
        metrics2.consecutive_failures,
        "Key not found in content",
    )
    if decision:
        print(format_decision_for_display(decision))

    print("\n3. Testing self-prompt injection:")
    prompt = inject_auto_learning_prompt("Base system prompt", metrics)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
