#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目标跟踪系统 - 设定目标、跟踪进度、验证成果
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
GOALS_FILE = WORKSPACE / ".learnings" / "goals.json"
PROGRESS_FILE = WORKSPACE / ".learnings" / "progress.json"


class GoalTrackingSystem:
    """目标跟踪系统"""
    
    def __init__(self):
        self.goals = self._load_goals()
        self.progress = self._load_progress()
    
    def _load_goals(self) -> List[Dict]:
        """加载目标"""
        if GOALS_FILE.exists():
            try:
                with open(GOALS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        
        # 默认目标
        return [
            {
                "id": "goal-001",
                "name": "Token 节省 70%",
                "description": "通过记忆分层架构，减少 Token 使用",
                "target": 70,
                "unit": "%",
                "current": 70,
                "status": "achieved",  # pending, in_progress, achieved
                "achieved_date": "2026-03-29"
            },
            {
                "id": "goal-002",
                "name": "自动化率 100%",
                "description": "通过后台任务调度器，实现完全自动化",
                "target": 100,
                "unit": "%",
                "current": 100,
                "status": "achieved",
                "achieved_date": "2026-03-29"
            },
            {
                "id": "goal-003",
                "name": "用户满意度 80%",
                "description": "通过用户交互优化，提升用户满意度",
                "target": 80,
                "unit": "%",
                "current": 70,
                "status": "in_progress",
                "start_date": "2026-03-29"
            },
            {
                "id": "goal-004",
                "name": "准确率 95%",
                "description": "通过 LLM 驱动，提升记忆检索准确率",
                "target": 95,
                "unit": "%",
                "current": 90,
                "status": "in_progress",
                "start_date": "2026-03-29"
            },
            {
                "id": "goal-005",
                "name": "响应速度 < 2秒",
                "description": "通过性能优化，提升响应速度",
                "target": 2,
                "unit": "秒",
                "current": 3.5,
                "status": "in_progress",
                "start_date": "2026-03-29"
            },
            {
                "id": "goal-006",
                "name": "错误恢复率 90%",
                "description": "通过错误处理优化，提升错误恢复率",
                "target": 90,
                "unit": "%",
                "current": 90,
                "status": "achieved",
                "achieved_date": "2026-03-29"
            },
            {
                "id": "goal-007",
                "name": "对话轮次 -30%",
                "description": "通过智能确认，减少对话轮次",
                "target": -30,
                "unit": "%",
                "current": -30,
                "status": "achieved",
                "achieved_date": "2026-03-29"
            }
        ]
    
    def _load_progress(self) -> List[Dict]:
        """加载进度记录"""
        if PROGRESS_FILE.exists():
            try:
                with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        
        return []
    
    def update_goal_progress(self, goal_id: str, current_value: float, note: str = ""):
        """更新目标进度"""
        for goal in self.goals:
            if goal["id"] == goal_id:
                goal["current"] = current_value
                
                # 更新状态
                if goal["target"] > 0:
                    if current_value >= goal["target"]:
                        goal["status"] = "achieved"
                        goal["achieved_date"] = datetime.now().isoformat()
                else:
                    if current_value <= goal["target"]:
                        goal["status"] = "achieved"
                        goal["achieved_date"] = datetime.now().isoformat()
                
                # 记录进度
                self.progress.append({
                    "goal_id": goal_id,
                    "timestamp": datetime.now().isoformat(),
                    "current_value": current_value,
                    "note": note
                })
                
                self._save()
                return True
        
        return False
    
    def _save(self):
        """保存目标和进度"""
        GOALS_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(GOALS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.goals, f, indent=2, ensure_ascii=False)
        
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)
    
    def get_status(self) -> Dict:
        """获取目标状态"""
        total = len(self.goals)
        achieved = len([g for g in self.goals if g["status"] == "achieved"])
        in_progress = len([g for g in self.goals if g["status"] == "in_progress"])
        pending = len([g for g in self.goals if g["status"] == "pending"])
        
        return {
            "total": total,
            "achieved": achieved,
            "in_progress": in_progress,
            "pending": pending,
            "completion_rate": round(achieved / total * 100, 1) if total > 0 else 0
        }
    
    def generate_report(self) -> str:
        """生成目标报告"""
        status = self.get_status()
        
        report = []
        report.append("="*60)
        report.append("🎯 目标跟踪报告")
        report.append("="*60)
        
        report.append(f"\n📊 总体进度: {status['completion_rate']}%")
        report.append(f"   ✅ 已完成: {status['achieved']}/{status['total']}")
        report.append(f"   🔄 进行中: {status['in_progress']}/{status['total']}")
        report.append(f"   ⏳ 未开始: {status['pending']}/{status['total']}")
        
        report.append(f"\n{'='*60}")
        report.append("📋 目标详情")
        report.append("="*60)
        
        for i, goal in enumerate(self.goals, 1):
            status_icon = "✅" if goal["status"] == "achieved" else "🔄" if goal["status"] == "in_progress" else "⏳"
            progress_pct = 0
            if goal["target"] > 0:
                progress_pct = min(100, (goal["current"] / goal["target"]) * 100)
            else:
                progress_pct = min(100, (goal["current"] / goal["target"]) * 100) if goal["target"] != 0 else 100
            
            report.append(f"\n{i}. {status_icon} {goal['name']}")
            report.append(f"   目标: {goal['target']}{goal['unit']}")
            report.append(f"   当前: {goal['current']}{goal['unit']}")
            report.append(f"   进度: {progress_pct:.1f}%")
            report.append(f"   状态: {goal['status']}")
            
            if goal.get("achieved_date"):
                report.append(f"   完成日期: {goal['achieved_date'][:10]}")
        
        report.append(f"\n{'='*60}")
        report.append("📈 进度历史")
        report.append("="*60)
        
        if self.progress:
            for i, record in enumerate(self.progress[-5:], 1):
                goal = next((g for g in self.goals if g["id"] == record["goal_id"]), None)
                if goal:
                    report.append(f"\n{i}. {record['timestamp'][:19]}")
                    report.append(f"   {goal['name']}: {record['current_value']}{goal['unit']}")
                    if record.get("note"):
                        report.append(f"   备注: {record['note']}")
        
        report.append(f"\n{'='*60}")
        
        return "\n".join(report)


# ============================================================================
# 主流程
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="目标跟踪系统")
    parser.add_argument("--update", help="更新目标进度: goal_id value")
    parser.add_argument("--note", help="备注说明", default="")
    parser.add_argument("--status", action="store_true", help="查看目标状态")
    
    args = parser.parse_args()
    
    system = GoalTrackingSystem()
    
    if args.status:
        # 显示目标状态
        print(system.generate_report())
    
    elif args.update:
        # 更新目标进度
        parts = args.update.split()
        if len(parts) >= 2:
            goal_id = parts[0]
            value = float(parts[1])
            note = " ".join(parts[2:])
            
            if system.update_goal_progress(goal_id, value, note):
                print(f"✅ 目标 {goal_id} 已更新为 {value}")
                print(system.generate_report())
            else:
                print(f"❌ 未找到目标: {goal_id}")
        else:
            print("用法: python3 goal-tracking.py --update goal_id value [note]")
    
    else:
        # 默认显示状态
        print(system.generate_report())
