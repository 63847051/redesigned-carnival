#!/usr/bin/env python3
"""
辩论管理器
主持和管理 Agent 之间的辩论流程
"""

import time
from typing import Dict, Optional
import sys
from pathlib import Path

# 添加 agents 目录到路径
agents_dir = Path(__file__).parent.parent / "agents"
sys.path.insert(0, str(agents_dir))

from challenger_agent import ChallengerAgent


class DebateManager:
    """辩论管理器 - 主持 Agent 之间的辩论"""

    def __init__(self, max_rounds: int = 2, verbose: bool = True):
        """
        初始化辩论管理器

        Args:
            max_rounds: 最大辩论轮数
            verbose: 是否显示详细信息
        """
        self.max_rounds = max_rounds
        self.verbose = verbose
        self.debate_history = []

    def debate(self, proposal: str, defender_agent, challenger_agent: Optional[ChallengerAgent] = None) -> Dict:
        """
        主持辩论流程

        Args:
            proposal: 原始方案
            defender_agent: 防守方 Agent
            challenger_agent: 挑战者 Agent（可选，默认创建新的）

        Returns:
            dict: 辩论结果
        """
        if challenger_agent is None:
            challenger_agent = ChallengerAgent()

        print(f"\n{'='*70}")
        print(f"🎤 开始辩论（最多 {self.max_rounds} 轮）")
        print(f"{'='*70}\n")

        current_proposal = proposal

        for round_num in range(1, self.max_rounds + 1):
            print(f"\n{'='*70}")
            print(f"第 {round_num} 轮辩论")
            print(f"{'='*70}\n")

            # 挑战者提出质疑
            challenge = challenger_agent.challenge(current_proposal)
            self._print_challenge(challenge)

            # 防守方回应
            defense = defender_agent.respond(challenge)
            self._print_defense(defense, defender_agent.name)

            # 记录辩论过程
            round_record = {
                "round": round_num,
                "challenge": challenge,
                "defense": defense
            }
            self.debate_history.append(round_record)

            # 如果不是最后一轮，挑战者可以继续反驳
            if round_num < self.max_rounds:
                print(f"\n{'='*70}")
                print(f"第 {round_num} 轮 - 反驳阶段")
                print(f"{'='*70}\n")

                counter = challenger_agent.respond_to_defense(defense, challenge)
                self._print_counter(counter)

                # 更新 proposal，加入辩论内容
                current_proposal = self._update_proposal(current_proposal, defense, counter)

        # 生成辩论总结
        summary = self._generate_summary(challenger_agent)
        self._print_summary(summary)

        return summary

    def _print_challenge(self, challenge: Dict):
        """打印质疑内容"""
        print("📋 质疑内容：")
        print("-" * 70)

        if challenge.get("risks"):
            print("\n⚠️  潜在风险：")
            for risk in challenge["risks"]:
                print(f"  • {risk}")

        if challenge.get("alternatives"):
            print("\n💡 替代方案：")
            for alt in challenge["alternatives"]:
                print(f"  • {alt}")

        if challenge.get("questions"):
            print("\n❓ 关键问题：")
            for question in challenge["questions"]:
                print(f"  • {question}")

        if challenge.get("concerns"):
            print("\n😟 主要担忧：")
            for concern in challenge["concerns"]:
                print(f"  • {concern}")

        print("-" * 70)

    def _print_defense(self, defense: str, defender_name: str):
        """打印防守内容"""
        print(f"\n🛡️  {defender_name} 的防守回应：")
        print("-" * 70)
        print(defense)
        print("-" * 70)

    def _print_counter(self, counter: Dict):
        """打印反驳内容"""
        print("\n⚔️  反驳意见：")
        print("-" * 70)

        if counter.get("unresolved_issues"):
            print("\n❌ 未解决的问题：")
            for issue in counter["unresolved_issues"]:
                print(f"  • {issue}")

        if counter.get("additional_concerns"):
            print("\n😟 额外担忧：")
            for concern in counter["additional_concerns"]:
                print(f"  • {concern}")

        if counter.get("satisfaction_level") is not None:
            satisfaction = counter["satisfaction_level"] * 100
            print(f"\n📊 满意度：{satisfaction:.0f}%")

        print("-" * 70)

    def _update_proposal(self, proposal: str, defense: str, counter: Dict) -> str:
        """
        更新方案，加入辩论内容

        Args:
            proposal: 原始方案
            defense: 防守回应
            counter: 反驳意见

        Returns:
            str: 更新后的方案
        """
        # 简单实现：拼接内容
        updated = f"""
{proposal}

【辩论补充】
防守方观点：{defense[:100]}...
挑战方反驳：{len(counter.get('unresolved_issues', []))} 个未解决问题
        """
        return updated

    def _generate_summary(self, challenger_agent: ChallengerAgent) -> Dict:
        """
        生成辩论总结

        Args:
            challenger_agent: 挑战者 Agent

        Returns:
            dict: 辩论总结
        """
        # 统计信息
        total_rounds = len(self.debate_history)
        total_questions = sum(
            len(round.get("challenge", {}).get("questions", []))
            for round in self.debate_history
        )
        total_risks = sum(
            len(round.get("challenge", {}).get("risks", []))
            for round in self.debate_history
        )

        # 获取挑战者的总结
        challenger_summary = challenger_agent.get_debate_summary()

        summary = {
            "total_rounds": total_rounds,
            "total_questions": total_questions,
            "total_risks": total_risks,
            "key_issues": challenger_summary["key_issues"],
            "resolved": challenger_summary["resolved"],
            "recommendation": challenger_summary["recommendation"],
            "debate_quality": self._assess_debate_quality()
        }

        return summary

    def _assess_debate_quality(self) -> str:
        """
        评估辩论质量

        Returns:
            str: 质量评级 (excellent, good, fair, poor)
        """
        # 简单实现：根据轮数和问题数量评估
        total_questions = sum(
            len(round.get("challenge", {}).get("questions", []))
            for round in self.debate_history
        )

        if total_questions >= 8:
            return "excellent"
        elif total_questions >= 5:
            return "good"
        elif total_questions >= 3:
            return "fair"
        else:
            return "poor"

    def _print_summary(self, summary: Dict):
        """打印辩论总结"""
        print(f"\n{'='*70}")
        print(f"📊 辩论总结")
        print(f"{'='*70}\n")

        print(f"辩论轮数：{summary['total_rounds']}")
        print(f"总问题数：{summary['total_questions']}")
        print(f"总风险数：{summary['total_risks']}")
        print(f"辩论质量：{summary['debate_quality'].upper()}")
        print(f"\n建议：{summary['recommendation']}")

        print(f"\n{'='*70}\n")

    def get_debate_history(self) -> list:
        """获取辩论历史"""
        return self.debate_history.copy()

    def reset(self):
        """重置辩论历史"""
        self.debate_history = []


# 测试用的防守 Agent
class MockDefenderAgent:
    """模拟防守 Agent（用于测试）"""

    def __init__(self, name: str = "防守方"):
        self.name = name

    def respond(self, challenge: Dict) -> str:
        """回应质疑"""
        defense = f"""
感谢挑战者的质疑，我的回应如下：

1. 关于风险：我已经考虑了这些风险，并准备了相应的缓解措施
2. 关于替代方案：我评估了多个方案，认为当前方案是最优的
3. 关于问题：我会确保充分测试和验证
4. 关于担忧：我们有足够的技术储备和经验

具体措施：
- 增加单元测试覆盖率到 90%
- 进行性能基准测试
- 制定详细的实施计划
- 定期代码审查

请挑战者评估这个回应是否充分。
        """
        return defense


# 测试代码
if __name__ == "__main__":
    print("🧪 测试辩论管理器\n")

    # 创建辩论管理器
    debate_manager = DebateManager(max_rounds=2, verbose=True)

    # 创建防守 Agent
    defender = MockDefenderAgent("小新")

    # 原始方案
    proposal = """
    方案：开发一个新的数据处理模块

    技术栈：
    - Python 3.10+
    - Pandas（数据处理）
    - NumPy（数值计算）
    - Pytest（单元测试）

    实施计划：
    1. 需求分析和设计（1周）
    2. 核心功能开发（2周）
    3. 测试和优化（1周）
    4. 文档编写（3天）

    预期成果：
    - 处理速度提升 50%
    - 代码可维护性提升
    - 完整的测试覆盖
    """

    # 开始辩论
    result = debate_manager.debate(proposal, defender)

    print("\n✅ 辩论完成！")
    print(f"辩论质量：{result['debate_quality']}")
    print(f"建议：{result['recommendation']}")
