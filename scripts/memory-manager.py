#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MemoryManager - 记忆系统统一管理器
统一入口，协调所有子系统，避免冲突
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class MemoryManager:
    """记忆系统统一管理器"""
    
    def __init__(self, workspace: str = "/root/.openclaw/workspace"):
        self.workspace = Path(workspace)
        
        # 初始化子系统
        self._init_subsystems()
    
    def _init_subsystems(self):
        """初始化所有子系统"""
        print("🔄 初始化记忆系统...")
        print("="*60)
        
        # 1. 文件系统范式
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from filesystem_context import FileSystemContext
        self.filesystem = FileSystemContext(str(self.workspace))
        print("✅ 文件系统范式")
        
        # 2. 分层上下文加载
        from layered_context import LayeredContextLoader
        self.layered = LayeredContextLoader(str(self.workspace))
        print("✅ 分层上下文加载")
        
        # 3. 可视化检索轨迹
        from retrieval_visualizer import RetrievalVisualizer
        self.retriever = RetrievalVisualizer()
        print("✅ 可视化检索轨迹")
        
        # 4. 记忆系统协调器
        from memory_sync_coordinator import MemorySyncCoordinator
        self.coordinator = MemorySyncCoordinator(str(self.workspace))
        print("✅ 记忆系统协调器")
        
        print("="*60)
        print("✅ 记忆系统初始化完成")
    
    def save_memory(self, key: str, content: str, layer: str = "l1", 
                   metadata: Optional[Dict] = None) -> str:
        """
        保存记忆（统一入口）
        
        Args:
            key: 记忆键
            content: 记忆内容
            layer: 分层（l0, l1, l2）
            metadata: 元数据
        
        Returns:
            保存结果
        """
        print(f"\n💾 保存记忆: {key}")
        print("-"*60)
        
        # 1. 保存到文件系统范式
        self.filesystem.add_memory(key, content, metadata)
        
        # 2. 根据分层规则存储
        self.layered.add_to_layer(layer, key, content)
        
        # 3. 记录检索轨迹
        self.retriever.record_retrieval(
            f"save:{key}",
            [{
                "source": "memory",
                "path": f".context/{layer}/{key}.md",
                "score": 1.0,
                "reason": "直接保存"
            }],
            "save"
        )
        
        return f"✅ 记忆已保存: {key} (层: {layer})"
    
    def save_resource(self, key: str, content: str, 
                     metadata: Optional[Dict] = None) -> str:
        """
        保存资源
        
        Args:
            key: 资源键
            content: 资源内容
            metadata: 元数据
        
        Returns:
            保存结果
        """
        print(f"\n💾 保存资源: {key}")
        print("-"*60)
        
        # 1. 保存到文件系统范式
        self.filesystem.add_resource(key, content, metadata)
        
        # 2. 记录检索轨迹
        self.retriever.record_retrieval(
            f"resource:{key}",
            [{
                "source": "resource",
                "path": f".context/resources/{key}.md",
                "score": 1.0,
                "reason": "直接保存"
            }],
            "save"
        )
        
        return f"✅ 资源已保存: {key}"
    
    def save_skill(self, key: str, content: str, 
                  metadata: Optional[Dict] = None) -> str:
        """
        保存技能
        
        Args:
            key: 技能键
            content: 技能内容
            metadata: 元数据
        
        Returns:
            保存结果
        """
        print(f"\n💾 保存技能: {key}")
        print("-"*60)
        
        # 1. 保存到文件系统范式
        self.filesystem.add_skill(key, content, metadata)
        
        # 2. 记录检索轨迹
        self.retriever.record_retrieval(
            f"skill:{key}",
            [{
                "source": "skill",
                "path": f".context/skills/{key}.md",
                "score": 1.0,
                "reason": "直接保存"
            }],
            "save"
        )
        
        return f"✅ 技能已保存: {key}"
    
    def search_memory(self, query: str, method: str = "hybrid") -> List[Dict]:
        """
        检索记忆（统一入口）
        
        Args:
            query: 查询内容
            method: 检索方法（hybrid, semantic, keyword）
        
        Returns:
            检索结果
        """
        print(f"\n🔍 检索记忆: {query}")
        print("-"*60)
        
        # 1. 从文件系统检索
        results = []
        
        # 搜索记忆
        memory_items = self.filesystem.list_context("memory")
        for item in memory_items:
            content = self.filesystem.get_context("memory", item["key"])
            if query.lower() in content.lower():
                results.append({
                    "source": "memory",
                    "key": item["key"],
                    "path": item["path"],
                    "score": 0.9,
                    "reason": "关键词匹配"
                })
        
        # 2. 记录检索轨迹
        self.retriever.record_retrieval(query, results, method)
        
        # 3. 返回结果
        print(f"✅ 找到 {len(results)} 个结果")
        
        return results
    
    def load_context(self, token_budget: int = 4000) -> str:
        """
        加载上下文（统一入口）
        
        Args:
            token_budget: Token 预算
        
        Returns:
            加载的上下文
        """
        print(f"\n🔄 加载上下文（预算: {token_budget} tokens）")
        print("-"*60)
        
        # 使用分层上下文加载
        content = self.layered.load_context(token_budget)
        
        return content
    
    def sync_to_memory(self, force: bool = False) -> str:
        """
        同步到长期存储（统一入口）
        
        Args:
            force: 强制同步
        
        Returns:
            同步结果
        """
        print(f"\n🔄 同步到长期存储")
        print("-"*60)
        
        # 使用记忆系统协调器
        result = self.coordinator.sync_to_memory(force=force)
        
        return result
    
    def check_consistency(self) -> Dict:
        """
        检查一致性（统一入口）
        
        Returns:
            一致性报告
        """
        print(f"\n🔍 检查一致性")
        print("-"*60)
        
        # 使用记忆系统协调器
        result = self.coordinator.check_consistency()
        
        return result
    
    def get_stats(self) -> Dict:
        """
        获取统计信息（统一入口）
        
        Returns:
            统计信息
        """
        print(f"\n📊 系统统计")
        print("="*60)
        
        # 文件系统统计
        fs_stats = self.filesystem.get_stats()
        
        # 分层上下文统计
        layer_stats = self.layered.get_stats()
        
        stats = {
            "filesystem": fs_stats,
            "layered": layer_stats,
            "total_items": fs_stats["total_items"]
        }
        
        print(f"文件系统:")
        print(f"  记忆: {fs_stats['memory_count']}")
        print(f"  资源: {fs_stats['resources_count']}")
        print(f"  技能: {fs_stats['skills_count']}")
        print(f"  总计: {fs_stats['total_items']}")
        
        print(f"\n分层上下文:")
        print(f"  L0 (核心): {layer_stats['l0_count']}")
        print(f"  L1 (相关): {layer_stats['l1_count']}")
        print(f"  L2 (背景): {layer_stats['l2_count']}")
        print(f"  总 Token: {layer_stats['total_tokens']}")
        
        print("="*60)
        
        return stats


# ============================================================================
# 主流程
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="记忆系统统一管理器")
    parser.add_argument("--save-memory", nargs=2, metavar=("key", "content"), help="保存记忆")
    parser.add_argument("--save-resource", nargs=2, metavar=("key", "content"), help="保存资源")
    parser.add_argument("--save-skill", nargs=2, metavar=("key", "content"), help="保存技能")
    parser.add_argument("--search", nargs=1, metavar="query", help="检索记忆")
    parser.add_argument("--load", type=int, default=4000, metavar="budget", help="加载上下文")
    parser.add_argument("--sync", action="store_true", help="同步到长期存储")
    parser.add_argument("--check", action="store_true", help="检查一致性")
    parser.add_argument("--stats", action="store_true", help="查看统计")
    
    args = parser.parse_args()
    
    # 创建管理器
    manager = MemoryManager()
    
    if args.save_memory:
        key, content = args.save_memory
        result = manager.save_memory(key, content)
        print(result)
    
    elif args.save_resource:
        key, content = args.save_resource
        result = manager.save_resource(key, content)
        print(result)
    
    elif args.save_skill:
        key, content = args.save_skill
        result = manager.save_skill(key, content)
        print(result)
    
    elif args.search:
        query = args.search[0]
        results = manager.search_memory(query)
        print("\n结果:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['key']} ({result['source']})")
            print(f"   路径: {result['path']}")
            print(f"   分数: {result['score']:.2f}")
    
    elif args.load:
        content = manager.load_context(args.load)
        print("\n上下文:")
        print(content[:500] + "..." if len(content) > 500 else content)
    
    elif args.sync:
        result = manager.sync_to_memory()
        print(result)
    
    elif args.check:
        manager.check_consistency()
    
    elif args.stats:
        manager.get_stats()
    
    else:
        print("用法:")
        print("  python3 memory-manager.py --save-memory key content  # 保存记忆")
        print("  python3 memory-manager.py --save-resource key content  # 保存资源")
        print("  python3 memory-manager.py --save-skill key content  # 保存技能")
        print("  python3 memory-manager.py --search query  # 检索记忆")
        print("  python3 memory-manager.py --load 4000  # 加载上下文")
        print("  python3 memory-manager.py --sync  # 同步到长期存储")
        print("  python3 memory-manager.py --check  # 检查一致性")
        print("  python3 memory-manager.py --stats  # 查看统计")
        print("\n核心价值:")
        print("  统一入口")
        print("  协调所有子系统")
        print("  避免冲突")
