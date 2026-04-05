#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 排序器 - 使用智谱 AI 重新排序检索结果
"""

import subprocess
import json
from typing import List, Dict

# 配置
LLM_MODEL = "glmcode/glm-4.7"
MAX_TOKENS = 500

class LLMReranker:
    """LLM 重新排序器"""
    
    def rerank(self, query: str, results: List[Dict]) -> List[Dict]:
        """
        使用 LLM 重新排序结果
        
        Args:
            query: 用户查询
            results: 检索结果列表
        
        Returns:
            重新排序后的结果
        """
        if not results:
            return results
        
        print(f"   🤖 LLM 排序中...")
        
        # 构建排序提示词
        prompt = self._build_prompt(query, results)
        
        # 调用 LLM
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
    
    def _build_prompt(self, query: str, results: List[Dict]) -> str:
        """构建排序提示词"""
        
        # 构建候选列表
        candidates_text = ""
        for i, r in enumerate(results):
            path = r.get('path', 'unknown')
            candidates_text += f"\n[{i}] {path}"
        
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
        """调用智谱 AI"""
        
        # 使用 sessions_spawn 调用 LLM
        cmd = [
            'sessions_spawn',
            '-runtime', 'subagent',
            '-model', LLM_MODEL,
            '-mode', 'run',
            'python3', '-c',
            f'import sys; print("{prompt}")'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 解析输出
            output = result.stdout.strip()
            
            # 提取数字
            indices = []
            for part in output.split(','):
                part = part.strip()
                if part.isdigit():
                    indices.append(int(part))
            
            return indices
            
        except Exception as e:
            print(f"   ⚠️ LLM 调用失败: {e}")
            # 返回原始顺序
            return list(range(len(self.candidates)))


# 测试
if __name__ == "__main__":
    reranker = LLMReranker()
    
    # 模拟结果
    query = "如何部署系统？"
    results = [
        {'path': 'memory/2026-04-05.md', 'score': 0.9},
        {'path': 'memory/2026-03-25.md', 'score': 0.8},
        {'path': 'docs/DEPLOYMENT.md', 'score': 0.7},
    ]
    
    ranked = reranker.rerank(query, results)
    
    print("\n排序结果:")
    for i, r in enumerate(ranked, 1):
        print(f"  {i}. {r['path']} (score: {r['score']})")
