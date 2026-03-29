#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆树重构系统
- 将扁平文件重构为树形结构
- 支持路径追溯
- 支持可视化
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
MEMORY_KEY_POINTS = MEMORY_DIR / "key-points"
MEMORY_STRUCTURED = MEMORY_DIR / "structured"
TREE_FILE = MEMORY_DIR / "memory-tree.json"

# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class MemoryNode:
    """记忆节点"""
    title: str
    content: str = ""
    summary: str = ""
    depth: int = 0
    path: List[str] = field(default_factory=list)
    children: List['MemoryNode'] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def is_leaf(self) -> bool:
        """是否是叶子节点"""
        return len(self.children) == 0

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "depth": self.depth,
            "path": self.path,
            "children": [child.to_dict() for child in self.children],
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryNode':
        """从字典创建"""
        node = cls(
            title=data["title"],
            content=data.get("content", ""),
            summary=data.get("summary", ""),
            depth=data.get("depth", 0),
            path=data.get("path", []),
            metadata=data.get("metadata", {})
        )
        node.children = [cls.from_dict(child) for child in data.get("children", [])]
        return node

# ============================================================================
# 树构建
# ============================================================================

def build_memory_tree() -> MemoryNode:
    """构建记忆树"""
    print("开始构建记忆树...")

    # 创建根节点
    root = MemoryNode(
        title="Root",
        summary="幸运小行星的完整记忆系统",
        depth=0,
        path=["Root"]
    )

    # L3: 长期洞察（MEMORY.md）
    l3_node = MemoryNode(
        title="L3-长期洞察",
        summary="跨时间的长期洞察和模式",
        depth=1,
        path=["Root", "L3-长期洞察"]
    )

    memory_file = WORKSPACE / "MEMORY.md"
    if memory_file.exists():
        with open(memory_file, "r", encoding="utf-8") as f:
            l3_node.content = f.read()
        l3_node.summary = "包含永久规则、用户偏好、项目状态等长期洞察"
        l3_node.metadata["file"] = str(memory_file)
        l3_node.metadata["size"] = memory_file.stat().st_size

    root.children.append(l3_node)

    # L2: 结构化知识
    for category in ["people", "projects", "knowledge", "preferences"]:
        category_dir = MEMORY_STRUCTURED / category

        if not category_dir.exists():
            continue

        category_node = MemoryNode(
            title=f"L2-{category}",
            summary=f"{category} 相关的结构化知识",
            depth=2,
            path=["Root", f"L2-{category}"]
        )

        # 处理该分类的所有文件
        for file in sorted(category_dir.glob("*.md")):
            file_node = MemoryNode(
                title=file.name,
                summary=f"{category} 知识: {file.name}",
                depth=3,
                path=["Root", f"L2-{category}", file.name]
            )

            with open(file, "r", encoding="utf-8") as f:
                file_node.content = f.read()
                # 提取第一行作为摘要
                first_line = file_node.content.split("\n")[0]
                file_node.summary = first_line[:100]

            file_node.metadata["file"] = str(file)
            file_node.metadata["size"] = file.stat().st_size
            file_node.metadata["category"] = category

            category_node.children.append(file_node)

        root.children.append(category_node)

    # L1: 关键点
    if MEMORY_KEY_POINTS.exists():
        for month_file in sorted(MEMORY_KEY_POINTS.glob("*.md")):
            month_node = MemoryNode(
                title=f"L1-{month_file.name}",
                summary=f"月度关键点: {month_file.name}",
                depth=2,
                path=["Root", f"L1-{month_file.name}"]
            )

            with open(month_file, "r", encoding="utf-8") as f:
                month_node.content = f.read()
                month_node.summary = f"包含 {month_file.name} 的所有关键点"

            month_node.metadata["file"] = str(month_file)
            month_node.metadata["size"] = month_file.stat().st_size

            root.children.append(month_node)

    # L0: 原始数据（只添加引用，不加载内容）
    l0_count = len(list(MEMORY_DIR.glob("*.md")))
    l0_node = MemoryNode(
        title="L0-原始数据",
        summary=f"每日对话记录（{l0_count} 个文件）",
        depth=1,
        path=["Root", "L0-原始数据"]
    )
    l0_node.metadata["count"] = l0_count
    l0_node.metadata["location"] = str(MEMORY_DIR)

    root.children.append(l0_node)

    print("✓ 记忆树构建完成")
    return root

# ============================================================================
# 树保存和加载
# ============================================================================

def save_tree(root: MemoryNode, path: Path = None):
    """保存树到 JSON"""
    if path is None:
        path = TREE_FILE

    print(f"保存记忆树到: {path}")

    tree_data = {
        "version": "2.0",
        "created_at": datetime.now().isoformat(),
        "tree": root.to_dict()
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(tree_data, f, ensure_ascii=False, indent=2)

    print(f"✓ 记忆树已保存")

def load_tree(path: Path = None) -> MemoryNode:
    """从 JSON 加载树"""
    if path is None:
        path = TREE_FILE

    print(f"从 {path} 加载记忆树")

    with open(path, "r", encoding="utf-8") as f:
        tree_data = json.load(f)

    root = MemoryNode.from_dict(tree_data["tree"])
    print(f"✓ 记忆树已加载 (版本: {tree_data['version']})")

    return root

# ============================================================================
# 树搜索
# ============================================================================

def search_tree(root: MemoryNode, query: str, max_results: int = 5) -> List[MemoryNode]:
    """在树中搜索"""
    print(f"搜索: {query}")

    results = []

    # 递归搜索
    def search_recursive(node: MemoryNode):
        if len(results) >= max_results:
            return

        # 搜索标题和摘要
        if query.lower() in node.title.lower() or query.lower() in node.summary.lower():
            results.append(node)

        # 递归搜索子节点
        for child in node.children:
            search_recursive(child)

    search_recursive(root)

    print(f"✓ 找到 {len(results)} 个结果")
    return results

# ============================================================================
# 树可视化
# ============================================================================

def visualize_tree(root: MemoryNode, max_depth: int = 3):
    """可视化树结构"""
    print("\n记忆树结构:")
    print("=" * 60)

    def print_node(node: MemoryNode, indent: int = 0):
        if indent > max_depth:
            return

        prefix = "  " * indent + ("└─ " if indent > 0 else "")
        print(f"{prefix}{node.title}")
        if node.summary:
            print(f"{'  ' * (indent + 1)}摘要: {node.summary[:50]}...")

        for child in node.children:
            print_node(child, indent + 1)

    print_node(root)
    print("=" * 60)

# ============================================================================
# 统计信息
# ============================================================================

def get_tree_stats(root: MemoryNode) -> Dict:
    """获取树的统计信息"""
    stats = {
        "total_nodes": 0,
        "max_depth": 0,
        "leaf_nodes": 0,
        "by_depth": {}
    }

    def count_recursive(node: MemoryNode, depth: int = 0):
        stats["total_nodes"] += 1
        stats["max_depth"] = max(stats["max_depth"], depth)

        if depth not in stats["by_depth"]:
            stats["by_depth"][depth] = 0
        stats["by_depth"][depth] += 1

        if node.is_leaf():
            stats["leaf_nodes"] += 1
        else:
            for child in node.children:
                count_recursive(child, depth + 1)

    count_recursive(root)

    return stats

# ============================================================================
# 主流程
# ============================================================================

def main():
    """主流程"""
    import argparse

    parser = argparse.ArgumentParser(description="记忆树重构系统")
    parser.add_argument("action", choices=["build", "load", "search", "visualize", "stats"],
                       help="操作: build(构建), load(加载), search(搜索), visualize(可视化), stats(统计)")
    parser.add_argument("--query", help="搜索关键词")
    parser.add_argument("--max-depth", type=int, default=3, help="最大深度")

    args = parser.parse_args()

    if args.action == "build":
        # 构建树
        root = build_memory_tree()
        save_tree(root)
        visualize_tree(root, args.max_depth)
        stats = get_tree_stats(root)
        print(f"\n统计信息:")
        print(f"  总节点数: {stats['total_nodes']}")
        print(f"  最大深度: {stats['max_depth']}")
        print(f"  叶子节点: {stats['leaf_nodes']}")

    elif args.action == "load":
        # 加载树
        root = load_tree()
        visualize_tree(root, args.max_depth)

    elif args.action == "search":
        # 搜索
        root = load_tree()
        results = search_tree(root, args.query)

        print(f"\n搜索结果:")
        for i, node in enumerate(results, 1):
            print(f"\n{i}. {node.title}")
            print(f"   路径: {' → '.join(node.path)}")
            print(f"   摘要: {node.summary[:100]}...")

    elif args.action == "stats":
        # 统计
        root = load_tree()
        stats = get_tree_stats(root)

        print(f"\n统计信息:")
        print(f"  总节点数: {stats['total_nodes']}")
        print(f"  最大深度: {stats['max_depth']}")
        print(f"  叶子节点: {stats['leaf_nodes']}")
        print(f"\n按深度分布:")
        for depth, count in sorted(stats["by_depth"].items()):
            print(f"  深度 {depth}: {count} 个节点")

    elif args.action == "visualize":
        # 可视化
        root = load_tree()
        visualize_tree(root, args.max_depth)

if __name__ == "__main__":
    main()
