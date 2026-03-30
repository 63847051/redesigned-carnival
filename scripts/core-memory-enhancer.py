#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoreMemoryEnhancer - 核心记忆系统增强器
增强现有 memory/ 系统，不创建独立系统
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timedelta


class CoreMemoryEnhancer:
    """核心记忆系统增强器"""
    
    def __init__(self, workspace: str = "/root/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.memory_dir = self.workspace / "memory"
        self.memory_md = self.workspace / "MEMORY.md"
        
        # 检索轨迹记录
        self.trajectory_file = self.workspace / ".learnings" / "retrieval-trajectories.jsonl"
        self.trajectory_file.parent.mkdir(parents=True, exist_ok=True)
    
    def save_memory(self, content: str, category: str = "general"):
        """
        保存到核心 memory/ 系统
        
        Args:
            content: 记忆内容
            category: 分类（general, work, learning, etc.）
        """
        today = datetime.now().strftime("%Y-%m-%d")
        memory_file = self.memory_dir / f"{today}.md"
        
        # 追加到今日记忆
        with open(memory_file, "a", encoding="utf-8") as f:
            f.write(f"\n\n## {category.upper()}\n\n")
            f.write(f"**时间**: {datetime.now().strftime('%H:%M:%S')}\n\n")
            f.write(content)
        
        return f"✅ 已保存到 {today}.md"
    
    def load_memory_enhanced(self, token_budget: int = 4000) -> str:
        """
        增强的记忆加载（分层加载）
        
        Args:
            token_budget: Token 预算
        
        Returns:
            加载的内容
        """
        print(f"\n🔄 智能加载核心 memory/（预算: {token_budget} tokens）")
        print("="*60)
        
        # L0: MEMORY.md（核心）
        l0_content = ""
        if self.memory_md.exists():
            l0_content = self.memory_md.read_text(encoding="utf-8")
        l0_tokens = len(l0_content.split())
        
        print(f"L0 (MEMORY.md): {l0_tokens} tokens ✅")
        
        remaining = token_budget - l0_tokens
        
        if remaining <= 0:
            print("⚠️  Token 预算不足，仅加载 MEMORY.md")
            return l0_content
        
        # L1: 最近 7 天
        l1_content = self._load_recent_days(days=7)
        l1_tokens = len(l1_content.split())
        
        if l1_tokens <= remaining:
            print(f"L1 (最近 7 天): {l1_tokens} tokens ✅")
            remaining -= l1_tokens
            loaded_content = l0_content + "\n\n" + l1_content
        else:
            # 截断
            l1_truncated = self._truncate_content(l1_content, remaining)
            print(f"L1 (最近 7 天): {len(l1_truncated.split())} tokens ⚠️ (截断)")
            loaded_content = l0_content + "\n\n" + l1_truncated
            remaining = 0
        
        if remaining <= 0:
            print("⚠️  Token 预算不足，L2 未加载")
            return loaded_content
        
        # L2: 更早的记忆（按需）
        l2_content = self._load_earlier_days(remaining)
        l2_tokens = len(l2_content.split())
        
        if l2_tokens > 0:
            print(f"L2 (更早记忆): {l2_tokens} tokens ✅")
            loaded_content += "\n\n" + l2_content
        
        print("="*60)
        print(f"✅ 总计: {len(loaded_content.split())} tokens")
        
        return loaded_content
    
    def _load_recent_days(self, days: int = 7) -> str:
        """加载最近 N 天的记忆"""
        content_parts = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            memory_file = self.memory_dir / f"{date}.md"
            
            if memory_file.exists():
                with open(memory_file, "r", encoding="utf-8") as f:
                    content_parts.append(f.read())
        
        return "\n\n".join(content_parts)
    
    def _load_earlier_days(self, max_tokens: int) -> str:
        """加载更早的记忆（按需）"""
        # 获取所有记忆文件
        memory_files = sorted(self.memory_dir.glob("*.md"), reverse=True)
        
        # 跳过最近 7 天
        recent_files = set()
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            recent_files.add(f"{date}.md")
        
        # 加载更早的文件
        content_parts = []
        total_tokens = 0
        
        for file_path in memory_files:
            if file_path.name in recent_files:
                continue
            
            content = file_path.read_text(encoding="utf-8")
            tokens = len(content.split())
            
            if total_tokens + tokens > max_tokens:
                break
            
            content_parts.append(content)
            total_tokens += tokens
        
        return "\n\n".join(content_parts)
    
    def _truncate_content(self, content: str, max_tokens: int) -> str:
        """截断内容"""
        words = content.split()
        return " ".join(words[:max_tokens])
    
    def search_memory(self, query: str) -> List[Dict]:
        """
        在核心 memory/ 中搜索
        
        Args:
            query: 查询内容
        
        Returns:
            搜索结果
        """
        print(f"\n🔍 搜索核心 memory/: {query}")
        print("-"*60)
        
        results = []
        
        # 搜索 MEMORY.md
        if self.memory_md.exists():
            content = self.memory_md.read_text(encoding="utf-8")
            if query.lower() in content.lower():
                results.append({
                    "source": "MEMORY.md",
                    "path": "MEMORY.md",
                    "score": 0.95,
                    "reason": "核心记忆匹配"
                })
        
        # 搜索每日记忆
        memory_files = sorted(self.memory_dir.glob("*.md"), reverse=True)
        
        for file_path in memory_files:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if query.lower() in content.lower():
                results.append({
                    "source": file_path.name,
                    "path": str(file_path.relative_to(self.workspace)),
                    "score": 0.85,
                    "reason": "每日记忆匹配"
                })
        
        # 记录检索轨迹
        self._record_trajectory(query, results)
        
        print(f"✅ 找到 {len(results)} 个结果")
        
        return results
    
    def _record_trajectory(self, query: str, results: List[Dict]):
        """记录检索轨迹"""
        trajectory = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "source": "core-memory/",
            "total_results": len(results),
            "results": results
        }
        
        with open(self.trajectory_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(trajectory) + "\n")


# ============================================================================
# 主流程
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="核心记忆系统增强器")
    parser.add_argument("--save", nargs=1, metavar="content", help="保存记忆")
    parser.add_argument("--load", type=int, default=4000, metavar="budget", help="加载记忆")
    parser.add_argument("--search", nargs=1, metavar="query", help="搜索记忆")
    
    args = parser.parse_args()
    
    enhancer = CoreMemoryEnhancer()
    
    if args.save:
        content = args.save[0]
        result = enhancer.save_memory(content)
        print(result)
    
    elif args.load:
        content = enhancer.load_memory_enhanced(args.load)
        print("\n加载的内容:")
        print(content[:500] + "..." if len(content) > 500 else content)
    
    elif args.search:
        query = args.search[0]
        results = enhancer.search_memory(query)
        print("\n结果:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['source']}")
            print(f"   路径: {result['path']}")
            print(f"   分数: {result['score']:.2f}")
    
    else:
        print("用法:")
        print("  python3 core-memory-enhancer.py --save content  # 保存记忆")
        print("  python3 core-memory-enhancer.py --load 4000  # 加载记忆")
        print("  python3 core-memory-enhancer.py --search query  # 搜索记忆")
        print("\n核心价值:")
        print("  增强核心系统")
        print("  不创建独立系统")
        print("  统一使用 memory/")
