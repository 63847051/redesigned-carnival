#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能问答系统 - Karpathy 风格
结合 QMD + LLM Q&A
"""

import subprocess
import json
from pathlib import Path

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
COMPILED_DIR = WORKSPACE / "knowledge-compiled"
KNOWLEDGE_FILE = COMPILED_DIR / "knowledge.json"
QMD_SEARCH_CMD = "qmd search memory"


class KarpathyQA:
    """Karpathy 风格的 Q&A 系统"""
    
    def __init__(self):
        self.knowledge = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict:
        """加载编译后的知识"""
        if KNOWLEDGE_FILE.exists():
            with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        return {'compiled': [], 'index': {}, 'stats': {}}
    
    def ask(self, question: str) -> str:
        """
        提问问题
        
        Args:
            question: 用户问题
        
        Returns:
            回答
        """
        print(f"\n🤔 问题: {question}")
        
        # Step 1: QMD 快速召回
        print("   Step 1: QMD 召回...")
        qmd_results = self._qmd_search(question, top_k=5)
        
        # Step 2: 加载相关文档内容
        print("   Step 2: 加载文档...")
        context = self._load_context(qmd_results)
        
        # Step 3: LLM 综合回答
        print("   Step 3: LLM 综合...")
        answer = self._llm_answer(question, context)
        
        return answer
    
    def _qmd_search(self, query: str, top_k: int = 5) -> List[str]:
        """QMD 搜索"""
        results = []
        
        try:
            cmd = f"{QMD_SEARCH_CMD} {query}"
            output = subprocess.check_output(
                cmd, shell=True, text=True, stderr=subprocess.DEVNULL
            )
            
            for line in output.strip().split('\n')[:top_k]:
                if 'qmd://' in line:
                    path = line.split('://')[1].split(':')[0]
                    results.append(path)
        except Exception as e:
            print(f"   ⚠️ QMD 搜索失败: {e}")
        
        return results
    
    def _load_context(self, paths: List[str]) -> str:
        """加载文档上下文"""
        context_parts = []
        
        for path in paths[:3]:  # 只加载前 3 个
            fullpath = WORKSPACE / path
            if fullpath.exists():
                try:
                    content = fullpath.read_text(encoding='utf-8', errors='ignore')
                    # 只取前 500 字符
                    context_parts.append(f"\n--- {path} ---\n")
                    context_parts.append(content[:500])
                except Exception as e:
                    context_parts.append(f"\n--- {path} (读取失败: {e}) ---\n")
        
        return "\n".join(context_parts)
    
    def _llm_answer(self, question: str, context: str) -> str:
        """LLM 综合回答"""
        
        prompt = f"""你是一个知识助手。根据以下上下文回答用户问题。

用户问题: {question}

上下文:
{context}

要求:
1. 基于上下文回答
2. 如果上下文中没有答案，诚实说明
3. 回答要简洁准确
4. 可以引用来源文档

现在回答:"""
        
        try:
            result = subprocess.run(
                ['sessions_spawn', '-runtime', 'subagent', '-model', 'glmcode/glm-4.5-air'],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            answer = result.stdout.strip()
            return answer
            
        except Exception as e:
            return f"⚠️ 回答生成失败: {e}"


def main():
    """主函数"""
    qa = KarpathyQA()
    
    print("🤖 Karpathy 风格智能问答")
    print("=" * 60)
    print("")
    
    # 示例问题
    questions = [
        "如何部署系统？",
        "什么是三重防护机制？",
        "OpenCode CLI 怎么用？"
    ]
    
    for q in questions:
        print("\n" + "="*60)
        answer = qa.ask(q)
        print(f"\n💬 回答:\n{answer}")


if __name__ == "__main__":
    main()
