#!/usr/bin/env python3
"""
质量门禁系统 - Phase 3
实现自动化质量检查
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import re


class QualityLevel(Enum):
    """质量等级"""
    EXCELLENT = "excellent"  # 优秀
    GOOD = "good"           # 良好
    ACCEPTABLE = "acceptable"  # 可接受
    POOR = "poor"           # 差，需要修复


class CheckType(Enum):
    """检查类型"""
    SYNTAX = "syntax"           # 语法检查
    SEMANTIC = "semantic"       # 语义检查
    PERFORMANCE = "performance"  # 性能检查
    SECURITY = "security"       # 安全检查
    COMPLETENESS = "completeness"  # 完整性检查


@dataclass
class QualityCheck:
    """质量检查定义"""
    check_id: str
    name: str
    check_type: CheckType
    description: str
    checker: Callable  # 检查函数
    weight: float = 1.0  # 权重
    is_blocking: bool = True  # 是否阻塞（不通过则无法继续）


@dataclass
class CheckResult:
    """检查结果"""
    check_id: str
    passed: bool
    score: float  # 0-100
    message: str
    suggestions: List[str] = None
    execution_time: float = 0.0

    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []


@dataclass
class QualityReport:
    """质量报告"""
    task_id: str
    overall_score: float  # 0-100
    quality_level: QualityLevel
    check_results: List[CheckResult]
    passed: bool
    execution_time: float = 0.0


class QualityGate:
    """质量门禁 - 管理和执行质量检查"""

    def __init__(self, min_score: float = 70.0):
        self.checks: Dict[str, QualityCheck] = {}
        self.min_score = min_score  # 最低通过分数
        self.check_history: List[QualityReport] = []

    def register_check(self, check: QualityCheck):
        """
        注册质量检查

        参数:
            check: 质量检查对象
        """
        self.checks[check.check_id] = check

    def unregister_check(self, check_id: str):
        """
        取消注册质量检查

        参数:
            check_id: 检查 ID
        """
        if check_id in self.checks:
            del self.checks[check_id]

    async def check_quality(
        self,
        task_id: str,
        content: str,
        metadata: Dict = None
    ) -> QualityReport:
        """
        执行质量检查

        参数:
            task_id: 任务 ID
            content: 要检查的内容
            metadata: 额外元数据

        返回:
            质量报告
        """
        import time
        start_time = time.time()

        results = []
        total_weighted_score = 0.0
        total_weight = 0.0

        for check_id, check in self.checks.items():
            try:
                # 执行检查
                result = await check.checker(content, metadata or {})
                result.check_id = check_id
                results.append(result)

                # 计算加权分数
                total_weighted_score += result.score * check.weight
                total_weight += check.weight

            except Exception as e:
                # 检查失败
                results.append(CheckResult(
                    check_id=check_id,
                    passed=False,
                    score=0.0,
                    message=f"检查执行失败: {str(e)}"
                ))

        # 计算总体分数
        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0

        # 确定质量等级
        quality_level = self._determine_quality_level(overall_score)

        # 检查是否通过
        passed = overall_score >= self.min_score

        execution_time = time.time() - start_time

        report = QualityReport(
            task_id=task_id,
            overall_score=overall_score,
            quality_level=quality_level,
            check_results=results,
            passed=passed,
            execution_time=execution_time
        )

        self.check_history.append(report)
        return report

    def _determine_quality_level(self, score: float) -> QualityLevel:
        """根据分数确定质量等级"""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 75:
            return QualityLevel.GOOD
        elif score >= 60:
            return QualityLevel.ACCEPTABLE
        else:
            return QualityLevel.POOR

    def get_check_history(self, task_id: Optional[str] = None) -> List[QualityReport]:
        """
        获取检查历史

        参数:
            task_id: 任务 ID 过滤（可选）

        返回:
            质量报告列表
        """
        if task_id:
            return [r for r in self.check_history if r.task_id == task_id]
        return self.check_history.copy()

    def get_statistics(self) -> Dict:
        """
        获取统计信息

        返回:
            统计数据
        """
        if not self.check_history:
            return {
                "total_checks": 0,
                "pass_rate": 0.0,
                "average_score": 0.0,
                "average_execution_time": 0.0,
            }

        total = len(self.check_history)
        passed = sum(1 for r in self.check_history if r.passed)
        avg_score = sum(r.overall_score for r in self.check_history) / total
        avg_time = sum(r.execution_time for r in self.check_history) / total

        return {
            "total_checks": total,
            "pass_rate": passed / total,
            "average_score": avg_score,
            "average_execution_time": avg_time,
        }


# 内置检查器
class BuiltInCheckers:
    """内置质量检查器"""

    @staticmethod
    async def check_code_syntax(content: str, metadata: Dict) -> CheckResult:
        """检查代码语法"""
        import time
        start = time.time()

        issues = []

        # 检查常见语法错误
        if "```" in content and not content.count("```") % 2 == 0:
            issues.append("代码块标记不匹配")

        # 检查缩进
        lines = content.split("\n")
        for i, line in enumerate(lines[:50], 1):  # 只检查前 50 行
            if line.startswith("\t") and "    " in line:
                issues.append(f"第 {i} 行混用了 Tab 和空格缩进")

        score = max(0, 100 - len(issues) * 10)

        return CheckResult(
            passed=score >= 70,
            score=score,
            message=f"语法检查: {'通过' if score >= 70 else '未通过'}",
            suggestions=issues,
            execution_time=time.time() - start
        )

    @staticmethod
    async def check_completeness(content: str, metadata: Dict) -> CheckResult:
        """检查完整性"""
        import time
        start = time.time()

        missing = []

        # 检查是否有描述
        if len(content.split("\n")) < 3:
            missing.append("内容过短，缺少详细描述")

        # 检查是否有示例（如果是代码）
        if "```" in content and "示例" not in content and "example" not in content.lower():
            missing.append("缺少使用示例")

        # 检查是否有错误处理
        if "def " in content or "function " in content:
            if "try" not in content and "catch" not in content and "except" not in content:
                missing.append("缺少错误处理")

        score = max(0, 100 - len(missing) * 15)

        return CheckResult(
            passed=score >= 70,
            score=score,
            message=f"完整性检查: {'通过' if score >= 70 else '未通过'}",
            suggestions=missing,
            execution_time=time.time() - start
        )

    @staticmethod
    async def check_security(content: str, metadata: Dict) -> CheckResult:
        """检查安全问题"""
        import time
        start = time.time()

        warnings = []

        # 检查敏感信息
        sensitive_patterns = [
            (r'api[_-]?key\s*[:=]\s*["\'][\w-]+["\']', "API Key 硬编码"),
            (r'password\s*[:=]\s*["\'][\w-]+["\']', "密码硬编码"),
            (r'secret\s*[:=]\s*["\'][\w-]+["\']', "密钥硬编码"),
            (r'token\s*[:=]\s*["\'][\w-]+["\']', "Token 硬编码"),
        ]

        for pattern, warning in sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                warnings.append(warning)

        score = max(0, 100 - len(warnings) * 20)

        return CheckResult(
            passed=score >= 70,
            score=score,
            message=f"安全检查: {'通过' if score >= 70 else '未通过'}",
            suggestions=warnings,
            execution_time=time.time() - start
        )


if __name__ == "__main__":
    # 测试质量门禁
    async def test():
        gate = QualityGate(min_score=70.0)

        # 注册检查器
        gate.register_check(QualityCheck(
            "syntax", "语法检查", CheckType.SYNTAX,
            "检查代码语法错误", BuiltInCheckers.check_code_syntax
        ))

        gate.register_check(QualityCheck(
            "completeness", "完整性检查", CheckType.COMPLETENESS,
            "检查内容是否完整", BuiltInCheckers.check_completeness
        ))

        gate.register_check(QualityCheck(
            "security", "安全检查", CheckType.SECURITY,
            "检查安全问题", BuiltInCheckers.check_security
        ))

        # 执行检查
        content = """
```python
def hello():
    print("Hello, World!")
```
这是一个简单的示例函数。
"""

        report = await gate.check_quality("task1", content)

        print(f"总体分数: {report.overall_score:.1f}")
        print(f"质量等级: {report.quality_level.value}")
        print(f"是否通过: {report.passed}")
        print("\n检查结果:")
        for result in report.check_results:
            print(f"  {result.check_id}: {result.score:.1f} - {result.message}")
            if result.suggestions:
                for suggestion in result.suggestions:
                    print(f"    ⚠️  {suggestion}")

    import asyncio
    asyncio.run(test())
