"""
技能自动改进系统

自动决策何时对技能进行 patch：
- 使用技能时发现不足
- 上下文不完全匹配
- 执行失败或结果不理想

Fuzzy matching 用于找到最佳匹配并建议改进
"""

import json
import re
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from core.fuzzy_patch import (
    FuzzyPatcher,
    calculate_similarity,
    find_closest_match,
    PatchResult,
)
from core.snapshot_store import get_atomic_writer


@dataclass
class UsageContext:
    """技能使用上下文"""

    skill_name: str
    user_request: str
    execution_result: str
    success: bool
    error: Optional[str] = None
    partial_match: bool = False
    missing_context: List[str] = field(default_factory=list)


@dataclass
class ImprovementSuggestion:
    """改进建议"""

    skill_name: str
    patch_content: str
    confidence: float
    reason: str
    priority: str


class AutoSkillImprover:
    """
    技能自动改进器

    监控技能使用，决策是否进行改进
    """

    CONFIDENCE_THRESHOLD = 0.6
    PARTIAL_MATCH_THRESHOLD = 0.5
    ERROR_THRESHOLD = 1

    def __init__(self, skills_dir: str = None):
        self.skills_dir = (
            Path(skills_dir) if skills_dir else Path.home() / ".hermes" / "skills"
        )
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.patcher = FuzzyPatcher()
        self.atomic_writer = get_atomic_writer()

        self._usage_history: Dict[str, List[UsageContext]] = {}
        self._improvements: Dict[str, List[Dict]] = {}

    def analyze_usage(self, context: UsageContext) -> ImprovementSuggestion:
        """
        分析技能使用情况

        返回改进建议（如果有）
        """
        if context.skill_name not in self._usage_history:
            self._usage_history[context.skill_name] = []

        self._usage_history[context.skill_name].append(context)

        if not context.success:
            return self._analyze_failure(context)

        if context.partial_match:
            return self._analyze_partial_match(context)

        if context.missing_context:
            return self._analyze_missing_context(context)

        return None

    def _analyze_failure(self, context: UsageContext) -> ImprovementSuggestion:
        """分析执行失败"""
        skill_path = self.skills_dir / f"{context.skill_name}.md"

        if not skill_path.exists():
            return ImprovementSuggestion(
                skill_name=context.skill_name,
                patch_content="",
                confidence=0.0,
                reason="技能文件不存在",
                priority="high",
            )

        original = skill_path.read_text()

        error_type = self._classify_error(context.error or "")

        patch_content = self._generate_error_handling_patch(original, error_type)

        return ImprovementSuggestion(
            skill_name=context.skill_name,
            patch_content=patch_content,
            confidence=0.8,
            reason=f"执行失败，需要添加 {error_type} 错误处理",
            priority="high",
        )

    def _analyze_partial_match(self, context: UsageContext) -> ImprovementSuggestion:
        """分析部分匹配"""
        skill_path = self.skills_dir / f"{context.skill_name}.md"

        if not skill_path.exists():
            return None

        original = skill_path.read_text()

        patch_content = self._generate_context_extension_patch(
            original, context.user_request, context.missing_context
        )

        return ImprovementSuggestion(
            skill_name=context.skill_name,
            patch_content=patch_content,
            confidence=0.7,
            reason=f"上下文不完全匹配，缺少: {', '.join(context.missing_context[:2])}",
            priority="medium",
        )

    def _analyze_missing_context(self, context: UsageContext) -> ImprovementSuggestion:
        """分析缺失上下文"""
        skill_path = self.skills_dir / f"{context.skill_name}.md"

        if not skill_path.exists():
            return None

        original = skill_path.read_text()

        patch_content = self._generate_context_extension_patch(
            original, context.user_request, context.missing_context
        )

        return ImprovementSuggestion(
            skill_name=context.skill_name,
            patch_content=patch_content,
            confidence=0.6,
            reason=f"缺少上下文: {', '.join(context.missing_context[:2])}",
            priority="medium",
        )

    def _classify_error(self, error: str) -> str:
        """分类错误类型"""
        error_lower = error.lower()

        if "file" in error_lower or "not found" in error_lower:
            return "文件"
        elif "permission" in error_lower or "denied" in error_lower:
            return "权限"
        elif "timeout" in error_lower:
            return "超时"
        elif "network" in error_lower or "connection" in error_lower:
            return "网络"
        elif "syntax" in error_lower or "parse" in error_lower:
            return "语法"
        elif "import" in error_lower or "module" in error_lower:
            return "导入"

        return "未知"

    def _generate_error_handling_patch(self, original: str, error_type: str) -> str:
        """生成错误处理补丁"""
        error_handling = f"""
### 错误处理 - {error_type} 类型

**常见错误**:
- 描述这类错误的特征

**处理方法**:
1. 检测错误特征
2. 尝试替代方案
3. 返回友好错误信息

**示例代码**:
```python
try:
    # 原操作
    pass
except {error_type}Error as e:
    # 错误处理
    pass
```
"""

        if "## 错误处理" in original:
            return ""

        return error_handling

    def _generate_context_extension_patch(
        self, original: str, user_request: str, missing: List[str]
    ) -> str:
        """生成上下文扩展补丁"""
        context_extension = f"""
### 扩展上下文

**触发场景**:
- {user_request[:100]}

**需要补充**:
{chr(10).join(f"- {m}" for m in missing[:3])}
"""

        return context_extension

    def apply_improvement(
        self, suggestion: ImprovementSuggestion, auto_apply: bool = False
    ) -> bool:
        """
        应用改进建议

        如果 auto_apply 为 True，自动应用；否则返回建议供用户确认
        """
        skill_path = self.skills_dir / f"{suggestion.skill_name}.md"

        if not skill_path.exists():
            return False

        try:
            original = skill_path.read_text()

            result = self.patcher.apply_patch(
                original, original + "\n" + suggestion.patch_content
            )

            if result.success:
                self.atomic_writer.write_text(
                    f"skills/{suggestion.skill_name}.md", result.patched
                )

                if suggestion.skill_name not in self._improvements:
                    self._improvements[suggestion.skill_name] = []

                self._improvements[suggestion.skill_name].append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "reason": suggestion.reason,
                        "confidence": suggestion.confidence,
                    }
                )

                return True

            return False
        except Exception:
            return False

    def get_usage_stats(self, skill_name: str) -> Dict[str, Any]:
        """获取技能使用统计"""
        history = self._usage_history.get(skill_name, [])

        total = len(history)
        success = sum(1 for h in history if h.success)
        failure = total - success

        return {
            "total_uses": total,
            "success": success,
            "failure": failure,
            "success_rate": success / total if total > 0 else 0.0,
            "improvements": len(self._improvements.get(skill_name, [])),
        }

    def suggest_skills_for_improvement(self) -> List[Tuple[str, float]]:
        """建议需要改进的技能"""
        suggestions = []

        for skill_name, history in self._usage_history.items():
            if not history:
                continue

            failure_count = sum(1 for h in history if not h.success)
            partial_count = sum(1 for h in history if h.partial_match)

            failure_rate = failure_count / len(history)

            if failure_rate > 0.3 or partial_count > 2:
                suggestions.append((skill_name, failure_rate))

        return sorted(suggestions, key=lambda x: x[1], reverse=True)


def improve_skill(
    skill_name: str, result: str, success: bool, error: str = None
) -> Optional[str]:
    """便捷函数：改进技能"""
    improver = AutoSkillImprover()

    context = UsageContext(
        skill_name=skill_name,
        user_request="",
        execution_result=result,
        success=success,
        error=error,
    )

    suggestion = improver.analyze_usage(context)

    if suggestion and suggestion.confidence > 0.7:
        improver.apply_improvement(suggestion, auto_apply=True)
        return suggestion.reason

    return None
