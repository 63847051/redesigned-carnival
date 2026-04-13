"""
Fuzzy Patch 算法 - 自动技能改进

支持：
- 空白符规范化
- 缩进差异容忍
- 转义序列处理
- 智能 diff 生成
"""

import re
import difflib
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class PatchResult:
    """补丁结果"""

    success: bool
    original: str
    patched: str
    diff: str
    confidence: float


class FuzzyPatcher:
    """
    Fuzzy Patch 引擎

    提供智能的代码差异计算和修补功能
    """

    def __init__(self, normalize_whitespace: bool = True):
        self.normalize_whitespace = normalize_whitespace

    def normalize(self, text: str) -> str:
        """
        规范化空白符

        - 统一换行符为 \n
        - 压缩连续空白符
        - 去除行尾空格
        - 统一缩进为4空格
        """
        if not self.normalize_whitespace:
            return text

        lines = text.split("\n")
        normalized = []

        for line in lines:
            line = line.rstrip()
            line = re.sub(r"[ \t]+", " ", line)
            normalized.append(line)

        while normalized and not normalized[-1]:
            normalized.pop()

        while normalized and not normalized[0]:
            normalized.pop(0)

        return "\n".join(normalized)

    def compute_diff(
        self,
        original: str,
        patched: str,
        fromfile: str = "original",
        tofile: str = "patched",
    ) -> str:
        """计算统一格式 diff"""
        original_lines = original.splitlines(keepends=True)
        patched_lines = patched.splitlines(keepends=True)

        diff = difflib.unified_diff(
            original_lines, patched_lines, fromfile=fromfile, tofile=tofile, lineterm=""
        )

        return "".join(diff)

    def apply_patch(self, original: str, patch: str) -> PatchResult:
        """
        应用补丁到原始文本

        使用模糊匹配处理缩进和空白符差异
        """
        try:
            patched_lines = original.splitlines()
            patch_lines = patch.splitlines()

            result_lines = []
            i = 0
            j = 0

            while i < len(patched_lines) and j < len(patch_lines):
                orig_line = patched_lines[i].rstrip()
                patch_line = patch_lines[j].rstrip()

                if orig_line == patch_line:
                    result_lines.append(patched_lines[i])
                    i += 1
                    j += 1
                else:
                    if patch_line.startswith("+"):
                        result_lines.append(patch_line[1:])
                        j += 1
                    elif patch_line.startswith("-"):
                        i += 1
                        j += 1
                    else:
                        similarity = difflib.SequenceMatcher(
                            None, orig_line, patch_line
                        ).ratio()

                        if similarity > 0.8:
                            result_lines.append(patched_lines[i])
                            i += 1
                            j += 1
                        else:
                            result_lines.append(patched_lines[i])
                            i += 1

            while i < len(patched_lines):
                result_lines.append(patched_lines[i])
                i += 1

            while j < len(patch_lines):
                if patch_lines[j].startswith("+"):
                    result_lines.append(patch_lines[j][1:])
                j += 1

            patched = "\n".join(result_lines)
            diff = self.compute_diff(original, patched)

            return PatchResult(
                success=True,
                original=original,
                patched=patched,
                diff=diff,
                confidence=0.95,
            )
        except Exception as e:
            return PatchResult(
                success=False,
                original=original,
                patched=original,
                diff="",
                confidence=0.0,
            )

    def smart_merge(self, base: str, theirs: str, ours: str) -> str:
        """
        智能三方合并

        处理：base -> theirs/ours 的变更
        """
        base_lines = base.splitlines()
        theirs_lines = theirs.splitlines()
        ours_lines = ours.splitlines()

        result = []
        i = 0

        while i < len(base_lines):
            if i < len(theirs_lines) and base_lines[i] != theirs_lines[i]:
                if i < len(ours_lines) and base_lines[i] != ours_lines[i]:
                    result.append(ours_lines[i])
                else:
                    result.append(theirs_lines[i])
            else:
                result.append(base_lines[i])
            i += 1

        while i < len(theirs_lines):
            result.append(theirs_lines[i])
            i += 1

        return "\n".join(result)

    def suggest_improvements(self, original: str, usage_context: str) -> List[str]:
        """
        基于使用场景建议改进

        返回建议改进列表
        """
        suggestions = []

        lines = original.splitlines()

        if len(lines) < 3:
            suggestions.append("技能代码过短，考虑添加更多细节")

        if not original.strip():
            suggestions.append("技能内容为空")

        if "TODO" in original or "FIXME" in original:
            suggestions.append("存在未完成的代码标记")

        if len(original) > 5000:
            suggestions.append("技能代码过长，考虑拆分为多个技能")

        return suggestions

    def generate_patch(self, original: str, target: str) -> str:
        """生成补丁文件内容"""
        return self.compute_diff(original, target)

    def parse_patch(self, patch: str) -> List[Tuple[str, str]]:
        """
        解析补丁文件

        返回: [(原始行, 新行), ...]
        """
        changes = []
        lines = patch.splitlines()

        current_old = []
        current_new = []
        in_hunk = False

        for line in lines:
            if line.startswith("@@"):
                if in_hunk:
                    if current_old or current_new:
                        changes.append(("\n".join(current_old), "\n".join(current_new)))
                    current_old = []
                    current_new = []
                in_hunk = True
            elif line.startswith("-") and not line.startswith("--"):
                current_old.append(line[1:])
            elif line.startswith("+") and not line.startswith("++"):
                current_new.append(line[1:])
            elif line.startswith(" "):
                current_old.append(line[1:])
                current_new.append(line[1:])

        if current_old or current_new:
            changes.append(("\n".join(current_old), "\n".join(current_new)))

        return changes


def fuzzy_match(pattern: str, text: str, threshold: float = 0.8) -> bool:
    """
    模糊匹配

    检查文本是否匹配模式（允许空白符和缩进差异）
    """
    normalized_pattern = re.sub(r"\s+", "", pattern)
    normalized_text = re.sub(r"\s+", "", text)

    ratio = difflib.SequenceMatcher(None, normalized_pattern, normalized_text).ratio()
    return ratio >= threshold


def calculate_similarity(a: str, b: str) -> float:
    """计算两个文本的相似度"""
    norm_a = re.sub(r"\s+", "", a)
    norm_b = re.sub(r"\s+", "", b)
    return difflib.SequenceMatcher(None, norm_a, norm_b).ratio()


def find_closest_match(
    target: str, candidates: List[str]
) -> Tuple[Optional[str], float]:
    """
    在候选列表中找到最接近的匹配

    返回: (最匹配的字符串, 相似度)
    """
    if not candidates:
        return None, 0.0

    best_match = None
    best_score = 0.0

    for candidate in candidates:
        score = calculate_similarity(target, candidate)
        if score > best_score:
            best_score = score
            best_match = candidate

    return best_match, best_score
