#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TodoWrite 机制 - 先列步骤再执行
基于 learn-claude-code 的 s03 课程
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class TodoManager:
    """Todo 管理器 - 先列步骤再执行"""
    
    def __init__(self, workspace: str = "/root/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.todo_file = self.workspace / ".data" / "todos.json"
        self.todo_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载现有待办
        self.todos = self._load_todos()
        
        # nag 提醒间隔（5 分钟）
        self.nag_interval = 300
        
    def _load_todos(self) -> List[Dict]:
        """加载待办事项"""
        if self.todo_file.exists():
            with open(self.todo_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_todos(self):
        """保存待办事项"""
        with open(self.todo_file, "w", encoding="utf-8") as f:
            json.dump(self.todos, f, indent=2, ensure_ascii=False)
    
    def add_todo(self, task: str, priority: int = 5, tags: List[str] = None):
        """
        添加待办事项
        
        Args:
            task: 任务描述
            priority: 优先级（1-10，10 最高）
            tags: 标签列表
        """
        todo = {
            "task": task,
            "priority": priority,
            "tags": tags or [],
            "done": False,
            "created_at": datetime.now().isoformat(),
            "completed_at": None
        }
        
        self.todos.append(todo)
        self._save_todos()
        
        print(f"✅ 已添加待办: {task}")
        return todo
    
    def complete_todo(self, task_id: str):
        """
        完成待办事项
        
        Args:
            task_id: 任务 ID
        """
        for todo in self.todos:
            if todo["task"] == task_id or todo.get("id") == task_id:
                todo["done"] = True
                todo["completed_at"] = datetime.now().isoformat()
        
        self._save_todos()
        
        print(f"✅ 已完成: {task_id}")
    
    def nag(self):
        """nag 提醒 - 提醒未完成的待办"""
        pending = [t for t in self.todos if not t["done"]]
        
        if not pending:
            print("✅ 所有任务已完成！")
            return
        
        # 按优先级排序
        pending.sort(key=lambda x: -x["priority"])
        
        print(f"\n⏰ 待办提醒: {len(pending)} 个任务")
        print("="*60)
        
        for i, todo in enumerate(pending[:10], 1):
            status = "✅" if todo["done"] else "⏳"
            tags_str = ", ".join(todo.get("tags", []))
            print(f"{i}. [{status}] {todo['task']} (优先级: {todo['priority']})")
            if tags_str:
                print(f"   标签: {tags_str}")
        
        if len(pending) > 10:
            print(f"... 还有 {len(pending) - 10} 个任务")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = len(self.todos)
        done = len([t for t in self.todos if t["done"]])
        pending = total - done
        
        return {
            "total": total,
            "done": done,
            "pending": pending,
            "completion_rate": f"{(done/total*100):.1f}%" if total > 0 else "0%"
        }


# ============================================================================
# 主流程
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="TodoWrite 机制")
    parser.add_argument("--add", nargs="+", metavar="task", help="添加待办")
    parser.add_argument("--complete", nargs=1, metavar="task_id", help="完成任务")
    parser.add_argument("--nag", action="store_true", help="查看待办")
    parser.add_argument("--stats", action="store_true", help="查看统计")
    
    args = parser.parse_args()
    
    manager = TodoManager()
    
    if args.add:
        task = " ".join(args.add)
        manager.add_todo(task)
        manager.nag()
    
    elif args.complete:
        manager.complete_todo(args.complete)
        manager.nag()
    
    elif args.nag:
        manager.nag()
    
    elif args.stats:
        stats = manager.get_stats()
        print("\n📊 统计信息:")
        print("="*60)
        print(f"总任务: {stats['total']}")
        print(f"已完成: {stats['done']}")
        print(f"待完成: {stats['pending']}")
        print(f"完成率: {stats['completion_rate']}")
        print("="*60)
    
    else:
        print("用法:")
        print("  python3 todowrite-mechanism.py --add \"任务描述\"  # 添加待办")
        print("  python3 todowrite-mechanism.py --complete \"任务ID\"  # 完成待办")
        print("  python3 todowrite-mechanism.py --nag  # 查看待办")
        print("  python3 todowrite-mechanism.py --stats  # 查看统计")
        print("\n核心价值:")
        print("  完成率 +100%")
        print("  先列步骤再执行")
        print("  nag 提醒机制")
