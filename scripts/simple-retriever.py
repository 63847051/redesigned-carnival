#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版混合检索 - 无 LLM 排序
专注于 QMD 快速召回
"""

import subprocess
from pathlib import Path
from typing import List, Dict

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
QMD_SEARCH_CMD = "qmd search memory"


class SimpleRetriever:
    """简化检索器 - QMD + 文件名匹配"""
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        简化检索
        
        Args:
            query: 查询内容
            top_k: 返回数量
        
        Returns:
            相关文档列表
        """
        print(f"\n🔍 检索: {query}")
        
        results = []
        
        # 方法 1: QMD 搜索
        try:
            cmd = f"{QMD_SEARCH_CMD} {query}"
            output = subprocess.check_output(
                cmd, 
                shell=True, 
                text=True, 
                stderr=subprocess.DEVNULL
            )
            
            # 解析 QMD 输出
            for line in output.strip().split('\n')[:top_k]:
                if 'qmd://' in line:
                    # 提取文件路径
                    try:
                        path = line.split('://')[1].split(':')[0]
                        results.append({
                            'path': path,
                            'score': 1.0,
                            'method': 'qmd'
                        })
                    except IndexError:
                        continue
        except Exception as e:
            print(f"   ⚠️ QMD 搜索失败: {e}")
        
        # 方法 2: 文件名匹配（补充）
        if len(results) < top_k:
            query_lower = query.lower()
            for md_file in MEMORY_DIR.glob("*.md"):
                if query_lower in md_file.name.lower():
                    results.append({
                        'path': str(md_file.relative_to(WORKSPACE)),
                        'score': 0.8,
                        'method': 'filename'
                    })
        
        # 去重
        seen = set()
        unique_results = []
        for r in results:
            if r['path'] not in seen:
                seen.add(r['path'])
                unique_results.append(r)
        
        # 按分数排序
        unique_results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"   ✅ 找到 {len(unique_results)} 条结果")
        
        return unique_results[:top_k]


def main():
    """测试简化检索"""
    retriever = SimpleRetriever()
    
    # 测试查询
    queries = [
        "如何部署系统？",
        "三重防护机制",
        "OpenCode CLI"
    ]
    
    for query in queries:
        print("\n" + "="*60)
        results = retriever.retrieve(query, top_k=5)
        
        print(f"\n📊 Top 结果:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r['path']} ({r['method']})")
        
        # 显示第一个文件的内容片段
        if results:
            first_file = WORKSPACE / results[0]['path']
            if first_file.exists():
                print(f"\n📄 内容预览 ({first_file.name}):")
                try:
                    content = first_file.read_text(encoding='utf-8')
                    lines = content.split('\n')
                    # 显示前 3 行
                    for line in lines[:3]:
                        print(f"   {line}")
                    print("   ...")
                except Exception as e:
                    print(f"   ⚠️ 无法读取: {e}")


if __name__ == "__main__":
    main()
