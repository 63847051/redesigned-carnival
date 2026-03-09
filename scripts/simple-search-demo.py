#!/usr/bin/env python3
"""
简化版搜索演示
使用关键词匹配，无需下载大模型
"""

import os
import re
from pathlib import Path

MEMORY_DIR = Path("/root/.openclaw/workspace/memory")

def simple_search(query, top_k=5):
    """简单关键词搜索"""
    results = []
    query_lower = query.lower()

    # 遍历所有 .md 文件
    for md_file in MEMORY_DIR.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 计算匹配度
            content_lower = content.lower()
            matches = content_lower.count(query_lower)

            if matches > 0:
                relative_path = md_file.relative_to(MEMORY_DIR)
                results.append({
                    'path': str(relative_path),
                    'matches': matches,
                    'full_path': str(md_file)
                })
        except Exception as e:
            print(f"⚠️  读取文件失败 {md_file}: {e}")

    # 按匹配次数排序
    results.sort(key=lambda x: x['matches'], reverse=True)

    return results[:top_k]

def display_results(query, results):
    """显示搜索结果"""
    print(f"\n🔍 查询: {query}")
    print(f"📊 找到 {len(results)} 个结果\n")

    if not results:
        print("❌ 没有找到匹配的结果")
        return

    for i, result in enumerate(results, 1):
        print(f"--- [排名 {i}] ---")
        print(f"📄 文件: {result['path']}")
        print(f"🎯 匹配次数: {result['matches']}")

        # 读取文件片段
        try:
            with open(result['full_path'], 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 查找包含查询的行
            for j, line in enumerate(lines):
                if query.lower() in line.lower():
                    # 显示上下文（前后各 1 行）
                    start = max(0, j - 1)
                    end = min(len(lines), j + 2)
                    context = ''.join(lines[start:end]).strip()
                    print(f"📝 上下文: {context[:200]}...")
                    break
        except:
            pass

        print()

def main():
    import argparse

    parser = argparse.ArgumentParser(description='简化版搜索演示')
    parser.add_argument('query', help='搜索查询')
    parser.add_argument('--top-k', '-k', type=int, default=5,
                       help='返回结果数量 (默认: 5)')

    args = parser.parse_args()

    results = simple_search(args.query, args.top_k)
    display_results(args.query, results)

if __name__ == '__main__':
    main()
