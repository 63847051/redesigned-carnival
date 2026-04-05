#!/usr/bin/env python3
"""
审查 Agent
专门负责审查方案质量，发现问题并提供改进建议
"""

from typing import Dict, List, Optional


class ReviewAgent:
    """质量审查 Agent"""

    def __init__(self, name: str = "审查员", model: Optional[str] = None):
        """
        初始化审查 Agent

        Args:
            name: Agent 名称
            model: 使用的模型（暂时为占位符）
        """
        self.name = name
        self.model = model
        self.review_history = []

    def review(self, proposal: Dict) -> Dict:
        """
        审查方案质量

        Args:
            proposal: 方案内容

        Returns:
            dict: {
                "quality_score": 0-100,
                "issues": ["问题1", "问题2"],
                "suggestions": ["建议1", "建议2"],
                "approved": True/False,
                "review_details": {...}
            }
        """
        print(f"\n🔍 {self.name} 正在审查方案...\n")

        # 审查方案
        review_result = self._perform_review(proposal)

        # 记录到历史
        self.review_history.append({
            "proposal": proposal,
            "review": review_result
        })

        return review_result

    def _perform_review(self, proposal: Dict) -> Dict:
        """
        执行审查

        Args:
            proposal: 方案内容

        Returns:
            dict: 审查结果
        """
        # 评估各个维度
        completeness = self._assess_completeness(proposal)
        feasibility = self._assess_feasibility(proposal)
        quality = self._assess_quality(proposal)
        risks = self._assess_risks(proposal)

        # 计算总分
        quality_score = int((completeness + feasibility + quality) / 3)

        # 发现问题
        issues = self._find_issues(proposal, {
            "completeness": completeness,
            "feasibility": feasibility,
            "quality": quality,
            "risks": risks
        })

        # 提出建议
        suggestions = self._make_suggestions(proposal, issues)

        # 判断是否通过
        approved = self._should_approve(quality_score, issues)

        return {
            "quality_score": quality_score,
            "completeness": completeness,
            "feasibility": feasibility,
            "quality": quality,
            "risks": risks,
            "issues": issues,
            "suggestions": suggestions,
            "approved": approved,
            "review_details": {
                "reviewer": self.name,
                "timestamp": self._get_timestamp(),
                "criteria": ["完整性", "可行性", "质量", "风险"]
            }
        }

    def _assess_completeness(self, proposal: Dict) -> int:
        """评估完整性"""
        score = 100

        # 检查必要元素
        required_elements = ["approach", "steps", "resources", "timeline", "quality_plan"]
        missing_elements = []

        for element in required_elements:
            if not proposal.get(element):
                missing_elements.append(element)
                score -= 15

        # 检查步骤详细程度
        steps = proposal.get("steps", [])
        if len(steps) < 3:
            score -= 10

        return max(0, score)

    def _assess_feasibility(self, proposal: Dict) -> int:
        """评估可行性"""
        score = 85  # 基础分

        timeline = proposal.get("timeline", "")
        if "周" in timeline:
            weeks = int(timeline.split("周")[0].split()[-1])
            if weeks < 2:
                score -= 10  # 时间太紧
            elif weeks > 4:
                score -= 5   # 时间太长

        resources = proposal.get("resources", "")
        if "2名" in resources or "3名" in resources:
            score += 5  # 资源合理

        return min(100, max(0, score))

    def _assess_quality(self, proposal: Dict) -> int:
        """评估质量"""
        score = 80  # 基础分

        quality_plan = proposal.get("quality_plan", "")
        if "测试" in quality_plan:
            score += 10

        if "审查" in quality_plan:
            score += 5

        if "优化" in quality_plan:
            score += 5

        return min(100, score)

    def _assess_risks(self, proposal: Dict) -> str:
        """评估风险"""
        return "中等"  # 简化实现

    def _find_issues(self, proposal: Dict, scores: Dict) -> List[str]:
        """发现问题"""
        issues = []

        # 基于评分发现问题
        if scores["completeness"] < 80:
            issues.append("方案不够完整，缺少关键元素")

        if scores["feasibility"] < 80:
            issues.append("可行性存在疑问，时间或资源可能不足")

        if scores["quality"] < 80:
            issues.append("质量保证措施不够充分")

        # 具体问题检查
        timeline = proposal.get("timeline", "")
        if "1周" in timeline:
            issues.append("时间安排可能偏紧")

        resources = proposal.get("resources", "")
        if "1名" in resources:
            issues.append("资源可能不足")

        return issues

    def _make_suggestions(self, proposal: Dict, issues: List[str]) -> List[str]:
        """提出改进建议"""
        suggestions = []

        # 基于问题提供建议
        if "时间安排可能偏紧" in issues:
            suggestions.append("建议增加缓冲时间，预留应对意外的空间")

        if "资源可能不足" in issues:
            suggestions.append("建议增加人力或优化资源配置")

        if "方案不够完整" in issues:
            suggestions.append("建议完善方案的各个部分，特别是实施细节")

        # 通用建议
        suggestions.append("建议增加风险应对措施")
        suggestions.append("建议制定详细的里程碑检查点")

        return list(set(suggestions))  # 去重

    def _should_approve(self, quality_score: int, issues: List[str]) -> bool:
        """判断是否通过审查"""
        # 质量评分 >= 70 且严重问题 < 3
        critical_issues = [issue for issue in issues if "可能" not in issue]

        return quality_score >= 70 and len(critical_issues) < 3

    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_review_summary(self) -> Dict:
        """获取审查摘要"""
        if not self.review_history:
            return {"total_reviews": 0}

        return {
            "total_reviews": len(self.review_history),
            "average_score": sum(
                r["review"]["quality_score"] for r in self.review_history
            ) / len(self.review_history),
            "approval_rate": sum(
                1 for r in self.review_history if r["review"]["approved"]
            ) / len(self.review_history),
            "common_issues": self._extract_common_issues()
        }

    def _extract_common_issues(self) -> List[str]:
        """提取常见问题"""
        all_issues = []
        for record in self.review_history:
            all_issues.extend(record["review"]["issues"])

        # 统计频率
        from collections import Counter
        issue_counts = Counter(all_issues)

        # 返回最常见的 3 个问题
        return [issue for issue, count in issue_counts.most_common(3)]

    def reset(self):
        """重置审查历史"""
        self.review_history = []


# 测试代码
if __name__ == "__main__":
    print("🧪 测试审查 Agent\n")

    reviewer = ReviewAgent()

    # 测试方案
    proposal = {
        "approach": "渐进式实施 + 迭代优化",
        "steps": [
            "需求分析和设计",
            "核心功能开发",
            "测试和优化",
            "文档编写"
        ],
        "resources": "2名开发 + 1名测试",
        "timeline": "3周",
        "quality_plan": "单元测试 + 代码审查"
    }

    print("="*70)
    print("测试：审查方案")
    print("="*70)

    # 执行审查
    review_result = reviewer.review(proposal)

    # 显示结果
    print("\n📊 审查结果：")
    print("-"*70)
    print(f"\n质量评分: {review_result['quality_score']}/100")
    print(f"  • 完整性: {review_result['completeness']}/100")
    print(f"  • 可行性: {review_result['feasibility']}/100")
    print(f"  • 质量: {review_result['quality']}/100")
    print(f"  • 风险: {review_result['risks']}")

    print(f"\n发现问题 ({len(review_result['issues'])} 个):")
    for issue in review_result['issues']:
        print(f"  • {issue}")

    print(f"\n改进建议 ({len(review_result['suggestions'])} 条):")
    for suggestion in review_result['suggestions']:
        print(f"  • {suggestion}")

    print(f"\n审查结果: {'✅ 通过' if review_result['approved'] else '❌ 不通过'}")

    # 测试摘要
    print("\n" + "="*70)
    print("测试：审查摘要")
    print("="*70)

    summary = reviewer.get_review_summary()
    print(f"\n总审查数: {summary['total_reviews']}")
    print(f"平均评分: {summary['average_score']:.1f}")
    print(f"通过率: {summary['approval_rate']*100:.0f}%")
    if summary.get('common_issues'):
        print(f"\n常见问题:")
        for issue in summary['common_issues']:
            print(f"  • {issue}")
