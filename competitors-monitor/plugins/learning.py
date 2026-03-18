#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习助手系统插件
知识图谱学习、进度追踪、智能复习提醒
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any


class KnowledgeGraph:
    """简单知识图谱"""

    def __init__(self):
        self.topics = {}
        self.dependencies = {}

    def build_from_config(self, subjects: List[Dict]) -> Dict:
        """从配置构建知识图谱"""
        graph = {"nodes": [], "edges": []}

        for subject in subjects:
            subject_name = subject.get("name")

            for topic in subject.get("topics", []):
                topic_name = topic.get("name")

                graph["nodes"].append(
                    {
                        "id": f"{subject_name}_{topic_name}",
                        "label": topic_name,
                        "subject": subject_name,
                        "priority": topic.get("priority", 3),
                        "mastery": topic.get("mastery", 0.0),
                    }
                )

        return graph


class SpacedRepetition:
    """间隔重复算法 (简化版 SM-2)"""

    def __init__(self, config: Dict):
        self.intervals = config.get("spaced_repetition", {}).get(
            "review_intervals_days", [1, 3, 7, 14, 30]
        )
        self.ease_factor_default = config.get("spaced_repetition", {}).get(
            "ease_factor_default", 2.5
        )
        self.review_file = "data/learning_review.json"

    def calculate_next_review(self, topic: str, quality: int) -> Dict:
        """计算下次复习时间"""
        review_data = self._load_review_data()

        if topic not in review_data:
            review_data[topic] = {
                "ease_factor": self.ease_factor_default,
                "interval_index": 0,
                "last_review": None,
            }

        data = review_data[topic]

        if quality >= 3:
            if data["interval_index"] < len(self.intervals) - 1:
                data["interval_index"] += 1
        else:
            data["interval_index"] = 0

        interval = self.intervals[data["interval_index"]]
        next_review = datetime.now() + timedelta(days=interval)

        data["last_review"] = datetime.now().isoformat()
        data["next_review"] = next_review.isoformat()

        self._save_review_data(review_data)

        return {
            "next_review_date": next_review.strftime("%Y-%m-%d"),
            "interval_days": interval,
            "ease_factor": data["ease_factor"],
        }

    def get_due_reviews(self) -> List[Dict]:
        """获取今日待复习内容"""
        review_data = self._load_review_data()
        due = []

        for topic, data in review_data.items():
            next_review = data.get("next_review")
            if next_review:
                review_date = datetime.fromisoformat(next_review)
                if review_date <= datetime.now():
                    due.append(
                        {
                            "topic": topic,
                            "days_overdue": (datetime.now() - review_date).days,
                        }
                    )

        return due

    def _load_review_data(self) -> Dict:
        """加载复习数据"""
        if os.path.exists(self.review_file):
            with open(self.review_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_review_data(self, data: Dict):
        """保存复习数据"""
        os.makedirs("data", exist_ok=True)
        with open(self.review_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


class LearningAssistant:
    """学习助手"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.kg = KnowledgeGraph()
        self.sr = SpacedRepetition(config)

    def generate_daily_plan(self) -> Dict:
        """生成每日学习计划"""
        subjects = self.config.get("subjects", [])
        user_profile = self.config.get("user_profile", {})
        daily_limit = self.config.get("check_rules", {}).get(
            "daily_new_topics_limit", 3
        )

        plan = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "new_topics": [],
            "review_topics": [],
            "total_time_minutes": user_profile.get("daily_study_time_minutes", 60),
        }

        all_topics = []
        for subject in subjects:
            for topic in subject.get("topics", []):
                if topic.get("mastery", 0) < 0.8:
                    all_topics.append(
                        {
                            "subject": subject.get("name"),
                            "name": topic.get("name"),
                            "priority": topic.get("priority", 3),
                            "mastery": topic.get("mastery", 0),
                        }
                    )

        all_topics.sort(key=lambda x: (x["priority"], -x["mastery"]))

        plan["new_topics"] = all_topics[:daily_limit]

        due_reviews = self.sr.get_due_reviews()
        plan["review_topics"] = due_reviews

        return plan

    def generate_knowledge_graph(self) -> Dict:
        """生成知识图谱"""
        subjects = self.config.get("subjects", [])
        return self.kg.build_from_config(subjects)

    def analyze_progress(self) -> List[Dict[str, Any]]:
        """分析学习进度"""
        alerts = []

        subjects = self.config.get("subjects", [])
        total_mastery = 0
        topic_count = 0

        for subject in subjects:
            for topic in subject.get("topics", []):
                mastery = topic.get("mastery", 0)
                total_mastery += mastery
                topic_count += 1

                if mastery < 0.3:
                    alerts.append(
                        {
                            "type": "low_mastery",
                            "severity": "warning",
                            "subject": subject.get("name"),
                            "topic": topic.get("name"),
                            "mastery": mastery,
                            "message": f"{topic.get('name')} 掌握度较低 ({mastery * 100:.0f}%)",
                        }
                    )

        avg_mastery = total_mastery / topic_count if topic_count > 0 else 0

        if avg_mastery >= 0.8:
            alerts.append(
                {
                    "type": "goal_achieved",
                    "severity": "info",
                    "message": f"整体学习进度良好! 平均掌握度: {avg_mastery * 100:.0f}%",
                }
            )

        due_reviews = self.sr.get_due_reviews()
        if due_reviews and self.config.get("check_rules", {}).get(
            "alert_on_overdue_review"
        ):
            alerts.append(
                {
                    "type": "review_due",
                    "severity": "info",
                    "count": len(due_reviews),
                    "message": f"今日有 {len(due_reviews)} 项待复习内容",
                }
            )

        return alerts

    def generate_report(self, plan: Dict, alerts: List[Dict]) -> str:
        """生成学习报告"""
        report = "## 📚 学习助手报告\n\n"

        report += f"**日期**: {plan.get('date')}\n"
        report += f"**学习时长**: {plan.get('total_time_minutes')} 分钟\n\n"

        report += "### 📖 今日学习计划\n\n"

        if plan.get("new_topics"):
            report += "**新内容**:\n\n"
            for topic in plan["new_topics"]:
                mastery_pct = topic["mastery"] * 100
                report += f"- {topic['subject']} - {topic['name']} (当前: {mastery_pct:.0f}%)\n"
            report += "\n"

        if plan.get("review_topics"):
            report += "**复习内容**:\n\n"
            for topic in plan["review_topics"]:
                report += f"- {topic['topic']}\n"
            report += "\n"

        if alerts:
            report += "### 📊 进度分析\n\n"
            for alert in alerts:
                emoji = "🎉" if alert["type"] == "goal_achieved" else "📝"
                report += f"{emoji} {alert['message']}\n"

        return report


def run_assistant():
    """运行学习助手"""
    import sys

    config_path = "config/learning.json"

    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    assistant = LearningAssistant(config)
    plan = assistant.generate_daily_plan()
    alerts = assistant.analyze_progress()

    print(
        f"今日学习计划: {len(plan.get('new_topics', []))} 个新主题, {len(plan.get('review_topics', []))} 个复习"
    )
    print(f"进度分析: {len(alerts)} 条")

    report = assistant.generate_report(plan, alerts)
    print("\n" + report)

    graph = assistant.generate_knowledge_graph()
    print(f"知识图谱: {len(graph['nodes'])} 个节点")

    return plan, alerts


if __name__ == "__main__":
    run_assistant()
