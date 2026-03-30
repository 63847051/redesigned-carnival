#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆系统同步协调器
协调 memory/ 和 .context/ 两个系统
确保数据一致性和协调工作
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class MemorySyncCoordinator:
    """记忆系统同步协调器"""
    
    def __init__(self, workspace: str = "/root/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.memory_dir = self.workspace / "memory"
        self.context_dir = self.workspace / ".context"
        self.context_index = self.context_dir / "index.json"
        
        # 确保目录存在
        self.memory_dir.mkdir(parents=True, exist_ok=True)
    
    def sync_to_memory(self, force: bool = False) -> str:
        """
        同步 .context/ 到 memory/
        
        Args:
            force: 强制同步（即使没有新数据）
        
        Returns:
            同步报告
        """
        print("\n🔄 同步 .context/ → memory/")
        print("="*60)
        
        # 读取上下文索引
        if not self.context_index.exists():
            return "❌ 上下文索引不存在，无需同步"
        
        with open(self.context_index, "r", encoding="utf-8") as f:
            context_index = json.load(f)
        
        # 检查是否有新数据
        total_items = sum(len(v) for v in context_index.values() if isinstance(v, dict))
        
        if total_items == 0 and not force:
            return "⚠️  没有新数据，无需同步"
        
        # 生成今日记忆文件
        today = datetime.now().strftime("%Y-%m-%d")
        memory_file = self.memory_dir / f"{today}.md"
        
        # 构建同步内容
        sync_content = self._build_sync_content(context_index)
        
        # 检查文件是否存在
        if memory_file.exists():
            # 追加模式
            with open(memory_file, "r", encoding="utf-8") as f:
                existing_content = f.read()
            
            # 检查是否已同步
            if "# 🔄 上下文同步" in existing_content and not force:
                return "⚠️  今日已同步，使用 --force 强制同步"
            
            # 追加
            with open(memory_file, "a", encoding="utf-8") as f:
                f.write("\n\n")
                f.write(sync_content)
            
            action = "追加"
        else:
            # 新建
            with open(memory_file, "w", encoding="utf-8") as f:
                f.write(sync_content)
            
            action = "创建"
        
        # 统计
        stats = self._get_stats(context_index)
        
        print(f"✅ {action}文件: {memory_file.name}")
        print(f"📊 统计:")
        print(f"   - 记忆: {stats['memory_count']}")
        print(f"   - 资源: {stats['resources_count']}")
        print(f"   - 技能: {stats['skills_count']}")
        print("="*60)
        
        return f"✅ 同步完成: {memory_file.name}"
    
    def _build_sync_content(self, context_index: Dict) -> str:
        """构建同步内容"""
        lines = []
        lines.append("# 🔄 上下文同步")
        lines.append(f"**同步时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 记忆
        if "memory" in context_index and context_index["memory"]:
            lines.append("## 📝 记忆")
            lines.append("")
            
            for key, info in context_index["memory"].items():
                file_path = self.workspace / info["path"]
                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    lines.append(f"### {key}")
                    lines.append(content)
                    lines.append("")
        
        # 资源
        if "resources" in context_index and context_index["resources"]:
            lines.append("## 📚 资源")
            lines.append("")
            
            for key, info in context_index["resources"].items():
                file_path = self.workspace / info["path"]
                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    lines.append(f"### {key}")
                    lines.append(content)
                    lines.append("")
        
        # 技能
        if "skills" in context_index and context_index["skills"]:
            lines.append("## 🛠️ 技能")
            lines.append("")
            
            for key, info in context_index["skills"].items():
                file_path = self.workspace / info["path"]
                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    lines.append(f"### {key}")
                    lines.append(content)
                    lines.append("")
        
        return "\n".join(lines)
    
    def _get_stats(self, context_index: Dict) -> Dict:
        """获取统计信息"""
        return {
            "memory_count": len(context_index.get("memory", {})),
            "resources_count": len(context_index.get("resources", {})),
            "skills_count": len(context_index.get("skills", {}))
        }
    
    def load_from_memory(self, date: str = None) -> Dict:
        """
        从 memory/ 加载到 .context/
        
        Args:
            date: 日期（YYYY-MM-DD），默认今天
        
        Returns:
            加载报告
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        memory_file = self.memory_dir / f"{date}.md"
        
        if not memory_file.exists():
            return {"status": "error", "message": f"记忆文件不存在: {date}.md"}
        
        print(f"\n🔄 从 memory/ 加载: {date}.md")
        print("="*60)
        
        # 读取记忆文件
        with open(memory_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 简单解析（实际需要更复杂的解析）
        # 这里只是示例
        
        print(f"✅ 已加载: {memory_file.name}")
        print("="*60)
        
        return {"status": "success", "message": f"已加载: {date}.md"}
    
    def check_consistency(self) -> Dict:
        """
        检查两个系统的一致性
        
        Returns:
            一致性报告
        """
        print("\n🔍 检查一致性")
        print("="*60)
        
        issues = []
        
        # 检查 1: 上下文索引
        if not self.context_index.exists():
            issues.append({
                "type": "missing_index",
                "severity": "high",
                "message": "上下文索引不存在"
            })
        
        # 检查 2: 记忆目录
        if not self.memory_dir.exists():
            issues.append({
                "type": "missing_memory_dir",
                "severity": "high",
                "message": "记忆目录不存在"
            })
        
        # 检查 3: 今日记忆文件
        today = datetime.now().strftime("%Y-%m-%d")
        today_memory = self.memory_dir / f"{today}.md"
        
        if today_memory.exists():
            with open(today_memory, "r", encoding="utf-8") as f:
                content = f.read()
            
            if "# 🔄 上下文同步" not in content:
                issues.append({
                    "type": "not_synced",
                    "severity": "medium",
                    "message": "今日记忆未同步"
                })
        
        if issues:
            print(f"⚠️  发现 {len(issues)} 个问题:")
            for issue in issues:
                print(f"   - [{issue['severity'].upper()}] {issue['message']}")
        else:
            print("✅ 系统一致，无问题")
        
        print("="*60)
        
        return {
            "status": "consistent" if not issues else "inconsistent",
            "issues": issues
        }
    
    def auto_sync(self) -> str:
        """
        自动同步（推荐每天执行）
        
        Returns:
            同步报告
        """
        print("\n🤖 自动同步协调")
        print("="*60)
        
        # 1. 检查一致性
        consistency = self.check_consistency()
        
        # 2. 如果需要，执行同步
        if consistency["status"] == "inconsistent":
            result = self.sync_to_memory(force=False)
            print(f"\n{result}")
        else:
            print("\n✅ 系统一致，无需同步")
        
        print("="*60)
        
        return f"✅ 自动同步完成"


# ============================================================================
# 主流程
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="记忆系统同步协调器")
    parser.add_argument("--sync", action="store_true", help="同步到 memory/")
    parser.add_argument("--force", action="store_true", help="强制同步")
    parser.add_argument("--load", nargs="?", const="", metavar="date", help="从 memory/ 加载")
    parser.add_argument("--check", action="store_true", help="检查一致性")
    parser.add_argument("--auto", action="store_true", help="自动同步")
    
    args = parser.parse_args()
    
    coordinator = MemorySyncCoordinator()
    
    if args.sync:
        result = coordinator.sync_to_memory(force=args.force)
        print(result)
    
    elif args.load is not None:
        date = args.load if args.load else None
        result = coordinator.load_from_memory(date)
        print(result.get("message", result))
    
    elif args.check:
        coordinator.check_consistency()
    
    elif args.auto:
        result = coordinator.auto_sync()
        print(result)
    
    else:
        print("用法:")
        print("  python3 memory-sync-coordinator.py --sync  # 同步到 memory/")
        print("  python3 memory-sync-coordinator.py --sync --force  # 强制同步")
        print("  python3 memory-sync-coordinator.py --load [date]  # 从 memory/ 加载")
        print("  python3 memory-sync-coordinator.py --check  # 检查一致性")
        print("  python3 memory-sync-coordinator.py --auto  # 自动同步")
        print("\n核心价值:")
        print("  数据一致性")
        print("  自动协调")
        print("  避免混乱")
