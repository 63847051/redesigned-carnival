#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
混合检索系统 - pageindex-rag 风格
结合 QMD 快速召回 + LLM 推理排序
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"

# QMD 搜索命令
QMD_SEARCH_CMD = "qmd search memory"

# LLM 配置（使用智谱 AI）
LLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"


class HybridRetriever:
    """混合检索器 - pageindex-rag 风格"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 缓存 5 分钟
    
    def retrieve(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        混合检索（快速召回 + LLM 排序）
        
        Args:
            query: 查询内容
            top_k: 初始召回数量
        
        Returns:
            最相关的 3 条结果
        """
        print(f"\n🔍 混合检索: {query}")
        
        # Step 1: 快速召回（QMD）
        print("   Step 1: 快速召回...")
        initial_results = self._quick_recall(query, top_k)
        
        if not initial_results:
            print("   ⚠️ 无结果")
            return []
        
        print(f"   召回 {len(initial_results)} 条")
        
        # Step 2: LLM 推理排序
        print("   Step 2: LLM 推理排序...")
        ranked_results = self._llm_rerank(query, initial_results)
        
        # Step 3: 返回 Top 3
        top_results = ranked_results[:3]
        
        print(f"   ✅ 返回 Top {len(top_results)}")
        return top_results
    
    def _quick_recall(self, query: str, top_k: int) -> List[Dict]:
        """快速召回（QMD + 文件名匹配）"""
        results = []
        
        # 方法 1: QMD 搜索
        try:
            cmd = f"{QMD_SEARCH_CMD} {query}"
            output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
            
            # 解析 QMD 输出（格式：qmd://path:line #hash）
            for line in output.strip().split('\n')[:top_k]:
                if 'qmd://' in line:
                    # 提取文件路径
                    path = line.split('://')[1].split(':')[0]
                    results.append({
                        'path': path,
                        'score': 1.0,
                        'method': 'qmd'
                    })
        except Exception as e:
            print(f"   ⚠️ QMD 搜索失败: {e}")
        
        # 方法 2: 文件名匹配（补充）
        if len(results) < top_k:
            query_lower = query.lower()
            for md_file in MEMORY_DIR.glob("*.md"):
                if query_lower in md_file.name.lower():
                    results.append({
                        'path': str(md_file),
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
        
        return unique_results[:top_k]
    
    def _llm_rerank(self, query: str, results: List[Dict]) -> List[Dict]:
        """LLM 推理排序（pageindex-rag 风格）"""
        if not results:
            return results
        
        # 构建排序提示词
        prompt = self._build_rerank_prompt(query, results)
        
        # 调用 LLM
        try:
            ranked_indices = self._call_llm(prompt)
            
            # 重新排序
            ranked_results = []
            for idx in ranked_indices:
                if 0 <= idx < len(results):
                    ranked_results.append(results[idx])
            
            # 添加未排序的结果
            for i, r in enumerate(results):
                if i not in ranked_indices:
                    ranked_results.append(r)
            
            return ranked_results
            
        except Exception as e:
            print(f"   ⚠️ LLM 排序失败: {e}")
            return results
    
    def _build_rerank_prompt(self, query: str, results: List[Dict]) -> str:
        """构建排序提示词"""
        # 构建候选列表
        candidates_text = ""
        for i, r in enumerate(results):
            candidates_text += f"\n[{i}] {r['path']}"
        
        prompt = f"""你是一个智能检索助手。请根据用户查询，对以下候选文档进行排序。

用户查询: {query}

候选文档:{candidates_text}

任务:
1. 分析每个文档与查询的相关性
2. 按相关性从高到低排序
3. 只返回排序后的索引号，用逗号分隔

示例格式: 3,1,5,2,4

现在开始排序:"""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> List[int]:
        """调用 LLM（智谱 AI）"""
        # 使用 sessions_spawn 调用 LLM
        
        try:
            # 保存当前提示词到临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                prompt_file = f.name
            
            # 调用 sessions_spawn
            cmd = [
                'sessions_spawn',
                '-runtime', 'subagent',
                '-model', 'glmcode/glm-4.7',
                '-mode', 'run',
                'bash', '-c', f'cat {prompt_file} | head -1'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # 清理临时文件
            import os
            os.unlink(prompt_file)
            
            # 简化版本：返回原始顺序
            # TODO: 实现 LLM 排序
            return list(range(10))  # 临时返回前10个索引
            
        except Exception as e:
            print(f"   ⚠️ LLM 调用失败: {e}")
            return list(range(len(self.candidates)))


def main():
    """测试混合检索"""
    retriever = HybridRetriever()
    
    # 测试查询
    queries = [
        "如何部署系统？",
        "什么是三重防护机制？",
        "OpenCode CLI 怎么用？"
    ]
    
    for query in queries:
        print("\n" + "="*60)
        results = retriever.retrieve(query, top_k=10)
        
        print(f"\n📊 Top 结果:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r['path']}")


if __name__ == "__main__":
    main()
