#!/usr/bin/env python3
"""
挑战者 Agent
专门负责质疑和挑战方案，发现潜在问题
"""

from typing import Dict, List, Optional
import json


class ChallengerAgent:
    """挑战者 Agent - 质疑方案的专业 Agent"""

    def __init__(self, name: str = "挑战者", model: Optional[str] = None):
        """
        初始化挑战者 Agent

        Args:
            name: Agent 名称
            model: 使用的模型（暂时为占位符）
        """
        self.name = name
        self.model = model
        self.debate_history = []

    def challenge(self, proposal: str) -> Dict:
        """
        对方案提出质疑

        Args:
            proposal: 原始方案

        Returns:
            dict: {
                "risks": ["风险点1", "风险点2"],
                "alternatives": ["替代方案1", "替代方案2"],
                "questions": ["问题1", "问题2"],
                "concerns": ["担忧1", "担忧2"]
            }
        """
        print(f"\n🔍 {self.name} 正在分析方案...\n")

        # 模拟分析过程
        challenges = self._analyze_proposal(proposal)

        # 记录到历史
        self.debate_history.append({
            "type": "challenge",
            "content": challenges
        })

        return challenges

    def respond_to_defense(self, defense: str, original_challenge: Dict) -> Dict:
        """
        对防守方的回应进行反驳

        Args:
            defense: 防守方的回应
            original_challenge: 原始的质疑

        Returns:
            dict: 反驳意见
        """
        print(f"\n⚔️  {self.name} 正在准备反驳...\n")

        # 模拟反驳过程
        counter = self._prepare_counter(defense, original_challenge)

        # 记录到历史
        self.debate_history.append({
            "type": "counter",
            "content": counter
        })

        return counter

    def _analyze_proposal(self, proposal: str) -> Dict:
        """
        分析方案并生成质疑

        Args:
            proposal: 方案内容

        Returns:
            dict: 质疑内容
        """
        # 这里是模拟实现，实际应该调用 LLM
        challenges = {
            "risks": self._identify_risks(proposal),
            "alternatives": self._propose_alternatives(proposal),
            "questions": self._ask_questions(proposal),
            "concerns": self._express_concerns(proposal)
        }

        return challenges

    def _prepare_counter(self, defense: str, original_challenge: Dict) -> Dict:
        """
        准备反驳

        Args:
            defense: 防守回应
            original_challenge: 原始质疑

        Returns:
            dict: 反驳内容
        """
        # 模拟反驳实现
        counter = {
            "unresolved_issues": [],
            "additional_concerns": [],
            "satisfaction_level": 0.0
        }

        # 检查防守是否充分
        if "性能" in defense:
            counter["unresolved_issues"].append("性能优化方案不够具体")

        if "测试" in defense:
            counter["unresolved_issues"].append("测试覆盖率未明确说明")

        # 添加额外担忧
        counter["additional_concerns"].append("实施时间可能偏紧")
        counter["additional_concerns"].append("资源分配需要进一步明确")

        # 计算满意度
        counter["satisfaction_level"] = 0.6  # 60% 满意

        return counter

    def _identify_risks(self, proposal: str) -> List[str]:
        """识别潜在风险"""
        # 模拟风险识别
        risks = [
            "实施复杂度较高，可能影响进度",
            "需要额外的测试和验证",
            "可能与现有系统存在兼容性问题",
            "维护成本可能增加"
        ]
        return risks

    def _propose_alternatives(self, proposal: str) -> List[str]:
        """提出替代方案"""
        # 模拟替代方案
        alternatives = [
            "采用渐进式实施策略，分阶段推进",
            "优先考虑使用成熟的第三方库",
            "简化部分功能，优先保证核心功能",
            "增加代码审查和自动化测试"
        ]
        return alternatives

    def _ask_questions(self, proposal: str) -> List[str]:
        """提出关键问题"""
        # 模拟问题
        questions = [
            "如何确保新方案与现有系统的兼容性？",
            "性能优化的具体指标是什么？",
            "测试策略和覆盖率如何保证？",
            "实施过程中如何控制风险？"
        ]
        return questions

    def _express_concerns(self, proposal: str) -> List[str]:
        """表达主要担忧"""
        # 模拟担忧
        concerns = [
            "担心实施时间不够充分",
            "担心团队技术储备是否足够",
            "担心维护成本过高",
            "担心用户体验可能受影响"
        ]
        return concerns

    def get_debate_summary(self) -> Dict:
        """
        获取辩论摘要

        Returns:
            dict: 辩论摘要
        """
        return {
            "total_rounds": len([h for h in self.debate_history if h["type"] == "challenge"]),
            "key_issues": self._extract_key_issues(),
            "resolved": self._check_resolved(),
            "recommendation": self._make_recommendation()
        }

    def _extract_key_issues(self) -> List[str]:
        """提取关键问题"""
        issues = []
        for history in self.debate_history:
            if history["type"] == "challenge":
                issues.extend(history["content"].get("questions", []))
        return list(set(issues))

    def _check_resolved(self) -> bool:
        """检查问题是否已解决"""
        # 模拟检查
        return len(self.debate_history) >= 2

    def _make_recommendation(self) -> str:
        """生成建议"""
        # 模拟建议
        if len(self.debate_history) >= 2:
            return "方案基本可行，但建议解决上述关键问题后再实施。"
        else:
            return "需要进一步讨论和验证。"

    def reset(self):
        """重置辩论历史"""
        self.debate_history = []


# 测试代码
if __name__ == "__main__":
    print("🧪 测试挑战者 Agent\n")

    challenger = ChallengerAgent()

    # 测试 1: 质疑方案
    print("="*70)
    print("测试 1: 质疑方案")
    print("="*70)

    proposal = """
    方案：使用 Python 开发一个新的数据处理模块
    1. 使用 Pandas 进行数据处理
    2. 使用 NumPy 进行数值计算
    3. 添加单元测试
    4. 编写文档
    """

    challenge = challenger.challenge(proposal)

    print("\n📋 质疑内容：")
    print("-"*70)
    print(f"\n⚠️  潜在风险：")
    for risk in challenge["risks"]:
        print(f"  • {risk}")

    print(f"\n💡 替代方案：")
    for alt in challenge["alternatives"]:
        print(f"  • {alt}")

    print(f"\n❓ 关键问题：")
    for question in challenge["questions"]:
        print(f"  • {question}")

    print(f"\n😟 主要担忧：")
    for concern in challenge["concerns"]:
        print(f"  • {concern}")

    # 测试 2: 反驳
    print("\n" + "="*70)
    print("测试 2: 反驳防守")
    print("="*70)

    defense = """
    防守回应：
    1. 会充分测试性能和兼容性
    2. 使用成熟的第三方库
    3. 编写完整的单元测试
    """

    counter = challenger.respond_to_defense(defense, challenge)

    print("\n⚔️  反驳内容：")
    print("-"*70)
    print(f"\n❌ 未解决的问题：")
    for issue in counter["unresolved_issues"]:
        print(f"  • {issue}")

    print(f"\n😟 额外担忧：")
    for concern in counter["additional_concerns"]:
        print(f"  • {concern}")

    print(f"\n📊 满意度：{counter['satisfaction_level']*100:.0f}%")

    # 测试 3: 辩论摘要
    print("\n" + "="*70)
    print("测试 3: 辩论摘要")
    print("="*70)

    summary = challenger.get_debate_summary()
    print(f"\n📝 辩论摘要：")
    print(f"  总轮数：{summary['total_rounds']}")
    print(f"  关键问题：{len(summary['key_issues'])} 个")
    print(f"  已解决：{summary['resolved']}")
    print(f"  建议：{summary['recommendation']}")
