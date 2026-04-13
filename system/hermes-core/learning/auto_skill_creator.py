"""
技能自动创建系统

触发条件：
- 5+ 工具调用
- 错误克服
- 用户纠正

决策逻辑：
- 分析任务复杂度
- 提取可复用的模式
- 生成技能文档
"""

import json
import re
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from core.snapshot_store import get_atomic_writer
from core.fuzzy_patch import calculate_similarity


@dataclass
class TaskContext:
    """任务上下文"""

    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    user_corrections: List[str] = field(default_factory=list)
    success: bool = False
    duration: float = 0.0


@dataclass
class SkillTemplate:
    """技能模板"""

    name: str
    description: str
    trigger_patterns: List[str]
    content: str
    examples: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


class AutoSkillCreator:
    """
    技能自动创建器

    分析任务上下文，自动决策是否创建新技能
    """

    TOOL_CALL_THRESHOLD = 5
    ERROR_THRESHOLD = 1
    CORRECTION_THRESHOLD = 1

    def __init__(self, skills_dir: str = None):
        self.skills_dir = (
            Path(skills_dir) if skills_dir else Path.home() / ".hermes" / "skills"
        )
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.atomic_writer = get_atomic_writer()

    def analyze_context(self, context: TaskContext) -> Dict[str, Any]:
        """
        分析任务上下文

        返回分析结果和创建建议
        """
        analysis = {
            "should_create": False,
            "confidence": 0.0,
            "reasons": [],
            "skill_name": None,
            "skill_description": None,
            "trigger_patterns": [],
        }

        tool_call_count = len(context.tool_calls)
        error_count = len(context.errors)
        correction_count = len(context.user_corrections)

        score = 0

        if tool_call_count >= self.TOOL_CALL_THRESHOLD:
            score += 0.4
            analysis["reasons"].append(f"工具调用数量达标: {tool_call_count}")

        if error_count >= self.ERROR_THRESHOLD:
            score += 0.3
            analysis["reasons"].append(f"错误克服: {error_count} 个错误")

        if correction_count >= self.CORRECTION_THRESHOLD:
            score += 0.3
            analysis["reasons"].append(f"用户纠正: {correction_count} 次")

        analysis["confidence"] = min(score, 1.0)
        analysis["should_create"] = score >= 0.6 and context.success

        if analysis["should_create"]:
            skill_info = self._extract_skill_info(context)
            analysis["skill_name"] = skill_info["name"]
            analysis["skill_description"] = skill_info["description"]
            analysis["trigger_patterns"] = skill_info["trigger_patterns"]

        return analysis

    def _extract_skill_info(self, context: TaskContext) -> Dict[str, Any]:
        """从上下文提取技能信息"""
        tool_names = [tc.get("name", "unknown") for tc in context.tool_calls]
        unique_tools = list(set(tool_names))

        name_parts = []
        if unique_tools:
            name_parts.append(unique_tools[0].replace("_", " ").title()[:20])

        if context.errors:
            name_parts.append("ErrorHandling")

        skill_name = "".join(name_parts) if name_parts else "AutoSkill"

        description = f"自动创建的技能，处理 {len(context.tool_calls)} 个工具调用"
        if context.errors:
            description += f"，克服 {len(context.errors)} 个错误"
        if context.user_corrections:
            description += f"，包含 {len(context.user_corrections)} 次用户纠正"

        trigger_patterns = self._generate_trigger_patterns(context)

        return {
            "name": skill_name,
            "description": description,
            "trigger_patterns": trigger_patterns,
        }

    def _generate_trigger_patterns(self, context: TaskContext) -> List[str]:
        """生成触发模式"""
        patterns = []

        tool_names = [tc.get("name", "") for tc in context.tool_calls]
        for tool in set(tool_names):
            if tool:
                patterns.append(f"使用 {tool}")

        for error in context.errors:
            error_type = self._extract_error_type(error)
            if error_type:
                patterns.append(f"处理 {error_type} 错误")

        return patterns[:5]

    def _extract_error_type(self, error: str) -> Optional[str]:
        """提取错误类型"""
        error_lower = error.lower()

        if "file" in error_lower or "not found" in error_lower:
            return "文件"
        elif "permission" in error_lower or "denied" in error_lower:
            return "权限"
        elif "timeout" in error_lower:
            return "超时"
        elif "network" in error_lower or "connection" in error_lower:
            return "网络"

        return None

    def create_skill(self, context: TaskContext, force: bool = False) -> Optional[str]:
        """
        创建新技能

        返回技能文件路径，失败返回 None
        """
        analysis = self.analyze_context(context)

        if not force and not analysis["should_create"]:
            return None

        if not analysis["skill_name"]:
            analysis["skill_name"] = (
                f"AutoSkill_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

        skill_content = self._generate_skill_content(context, analysis)

        filename = f"{analysis['skill_name']}.md"

        try:
            filepath = self.atomic_writer.write_text(
                f"skills/{filename}", skill_content
            )
            return str(filepath)
        except Exception:
            return None

    def _generate_skill_content(self, context: TaskContext, analysis: Dict) -> str:
        """生成技能文档内容"""
        lines = [
            f"# {analysis['skill_name']}",
            "",
            f"**描述**: {analysis['skill_description']}",
            "",
            f"**创建时间**: {datetime.now().isoformat()}",
            "",
            "## 触发条件",
            "",
        ]

        for pattern in analysis["trigger_patterns"]:
            lines.append(f"- {pattern}")

        lines.extend(["", "## 工具调用序列", ""])

        for i, tc in enumerate(context.tool_calls, 1):
            tool_name = tc.get("name", "unknown")
            args = tc.get("args", {})
            lines.append(f"{i}. **{tool_name}**")
            if args:
                args_str = json.dumps(args, ensure_ascii=False)[:100]
                lines.append(f"   - 参数: {args_str}")

        if context.errors:
            lines.extend(["", "## 错误处理", ""])
            for error in context.errors:
                lines.append(f"- {error}")

        if context.user_corrections:
            lines.extend(["", "## 用户纠正", ""])
            for correction in context.user_corrections:
                lines.append(f"- {correction}")

        lines.extend(["", "## 使用示例", ""])

        for i, example in enumerate(analysis.get("trigger_patterns", [])[:3], 1):
            lines.append(f"{i}. {example}")

        return "\n".join(lines)

    def should_create_skill(
        self,
        tool_calls: int,
        errors: int = 0,
        corrections: int = 0,
        success: bool = True,
    ) -> bool:
        """快速检查是否应该创建技能"""
        context = TaskContext(
            tool_calls=[{"name": f"tool_{i}"} for i in range(tool_calls)],
            errors=["error"] * errors,
            user_corrections=["correction"] * corrections,
            success=success,
        )
        return self.analyze_context(context)["should_create"]


def create_skill_from_task(
    tool_calls: List[Dict], errors: List[str] = None, corrections: List[str] = None
) -> Optional[str]:
    """便捷函数：从任务创建技能"""
    creator = AutoSkillCreator()

    context = TaskContext(
        tool_calls=tool_calls,
        errors=errors or [],
        user_corrections=corrections or [],
        success=True,
    )

    return creator.create_skill(context)
