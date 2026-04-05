#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推理式检索系统 - 集成版
- 集成 QMD 搜索
- 优化 LLM 提示词
- 集成到主系统
"""

import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"

# 集成 QMD 搜索
QMD_SEARCH_CMD = "qmd search memory"


class ReasoningRetriever:
    """推理式检索器 - 集成版"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 缓存 5 分钟
    
    def retrieve(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        推理式检索（集成版）
        
        Args:
            query: 查询内容
            top_k: 召回数量
        
        Returns:
            最相关的 3 条结果
        """
        print(f"\n🔍 推理式检索: {query}")
        
        # Step 1: QMD 快速搜索（召回）
        print("   Step 1: QMD 召回...")
        qmd_results = self._qmd_search(query, top_k)
        
        if not qmd_results:
            print("   ⚠️ QMD 无结果，使用规则检索")
            return self._rule_based_retrieve(query)
        
        # Step 2: LLM 推理筛选（精排）
        print("   Step 2: LLM 推理筛选...")
        llm_results = self._llm_reasoning(query, qmd_results)
        
        # Step 3: 合并排序
        print("   Step 3: 合并排序...")
        final_results = self._merge_and_rank(qmd_results, llm_results)
        
        return final_results[:3]  # 返回前 3 条
    
    def _qmd_search(self, query: str, top_k: int) -> List[Dict]:
        """QMD 向量搜索"""
        try:
            # 搜索结果格式：
            # qmd://memory/file.md: #1a2b3c # score
            # qmd://memory/another.md: #1a2b3c # score
            
            result = subprocess.run(
                ["qmd", "search", "memory", query],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return []
            
            lines = result.stdout.strip().split("\n")
            results = []
            
            for line in lines:
                if line.strip():
                    # 解析：qmd://memory/file.md: #score
                    if "qmd://" in line:
                        # 提取文件路径
                        match = re.search(r'qmd://(.+?)#(\d+)', line)
                        if match:
                            file_path = match.group(1)
                            score = float(match.group(2))
                            
                            results.append({
                                "path": file_path,
                                "score": score,
                                "source": "qmd"
                            })
            
            # 按分数排序
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return results[:top_k]
            
        except Exception as e:
            print(f"   ⚠️ QMD 搜索失败: {e}")
            return []
    
    def _llm_reasoning(self, query: str, qmd_results: List[Dict]) -> List[Dict]:
        """LLM 推理筛选"""
        if not qmd_results:
            return []
        
        # 准备上下文
        context = []
        for i, result in enumerate(qmd_results[:5], 1):
            path = result["path"]
            score = result["score"]
            
            # 提取文件名和日期
            if "/" in path:
                filename = path.split("/")[-1]
                parent = path.split("/")[-2] if len(path.split("/")) > 1 else ""
                date_str = self._extract_date_from_path(path)
            else:
                filename = path
                parent = ""
                date_str = ""
            
            context.append(f"{i}. {filename}")
            context.append(f"   位置: {parent}")
            context.append(f"   相关性: {score}")
            if date_str:
                context.append(f"   日期: {date_str}")
            context.append("")
        
        # 准备提示词
        prompt = f"""你是一个专业的信息检索专家，擅长从搜索结果中筛选最相关的内容。

用户查询: {query}

搜索结果（共 {len(qmd_results)} 条）：
{chr(10).join(context)}

筛选标准：
1. **语义相关性**：内容与查询的语义相关程度
2. **上下文相关性**：内容对解决用户问题是否有帮助
3. **时间衰减**：优先最近的信息
4. **层级相关性**：L1（关键点）> L2（结构化）> L0（原始数据）

请返回最相关的 3 条，每行一条，格式：
- 文件路径: 相关理由

注意：
- 只返回最相关的 3 条
- 不要重复相同的文件
- 优先选择 L1（关键点）和 L2（结构化）层级的节点
"""
        
        # 调用 LLM
        try:
            import subprocess
            
            request = {
                "model": "glmcode/glm-4.5-air",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的信息检索专家。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 800,
                "temperature": 0.3
            }
            
            result = subprocess.run(
                ["curl", "-s", "-X", "POST",
                 "-H", "Content-Type: application/json",
                 "-d", json.dumps(request),
                 "https://open.bigmodel.cn/api/anthropic/messages"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"   ⚠️ LLM 调用失败: {result.stderr}")
                return []
            
            response = json.loads(result.stdout)
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 解析 LLM 返回
            results = self._parse_llm_results(content)
            
            return results
            
        except Exception as e:
            print(f"   ⚠️ LLM 推理失败: {e}")
            return []
    
    def _extract_date_from_path(self, path: str) -> str:
        """从路径中提取日期"""
        # 支持多种格式：
        # memory/2026-03-29.md → 2026-03-29
        # memory/key-points/2026-03.md → 2026-03
        # memory/structured/... → N/A
        
        # 从路径中提取日期
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', path)
        if date_match:
            return date_match.group(1)
        
        # 从文件名中提取
        filename = path.split("/")[-1]
        if filename.startswith("2026-"):
            return filename[:10]
        
        return ""
    
    def _parse_llm_results(self, llm_output: str) -> List[Dict]:
        """解析 LLM 返回"""
        results = []
        lines = llm_output.split("\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 解析：- 文件路径: 相关理由
            if "- " in line:
                parts = line.split("-", 1)
                if len(parts) >= 2:
                    file_path = parts[0].strip()
                    reason = parts[1].strip()
                    results.append({
                        "path": file_path,
                        "reason": reason,
                        "source": "llm",
                        "score": 0.9
                    })
        
        return results
    
    def _rule_based_retrieve(self, query: str) -> List[Dict]:
        """规则回退（当 LLM 不可用时）"""
        results = []
        query_lower = query.lower()
        
        # 搜索记忆文件
        memory_files = list(MEMORY_DIR.glob("*.md"))
        
        for file in memory_files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                    
                    # 关键词匹配
                    score = content.count(query_lower)
                    
                    if score > 0:
                        results.append({
                            "path": str(file),
                            "score": score,
                            "source": "rule",
                            "reason": f"关键词匹配: {score} 次"
                        })
            except Exception:
                pass
        
        # 按分数排序
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:3]
    
    def _merge_and_rank(self, qmd_results: List[Dict], llm_results: List[Dict]) -> List[Dict]:
        """合并和排序结果"""
        # 合并结果
        all_results = []
        
        # 添加 QMD 结果（权重 0.5）
        for result in qmd_results:
            all_results.append({
                "path": result["path"],
                "score": result["score"] * 0.5,
                "source": "qmd",
                "reason": "向量相似度"
            })
        
        # 添加 LLM 结果（权重 0.9）
        for result in llm_results:
            all_results.append({
                "path": result["path"],
                "score": result["score"] * 0.9,
                "source": "llm",
                "reason": result.get("reason", "语义相关")
            })
        
        # 按分数排序
        all_results.sort(key=lambda x: x["score"], reverse=True)
        
        # 去重（相同路径只保留一个）
        seen = set()
        unique_results = []
        for result in all_results:
            if result["path"] not in seen:
                unique_results.append(result)
                seen.add(result["path"])
        
        return unique_results
    
    def generate_report(self, query: str, results: List[Dict]) -> str:
        """生成检索报告"""
        report = []
        report.append("="*60)
        report.append(f"🔍 推理式检索报告: {query}")
        report.append("="*60)
        
        if not results:
            report.append("\n⏳ 未找到相关内容")
        else:
            for i, result in enumerate(results, 1):
                source_icon = "🧠" if result["source"] == "llm" else "📊"
                score_icon = "🌟" if result["score"] >= 0.7 else "👍"
                
                report.append(f"\n{i}. {source_icon} {score_icon} {result['path']}")
                
                if result.get("reason"):
                    report.append(f"   理由: {result['reason']}")
                
                # 提取文件名
                if "/" in result["path"]:
                    filename = result["path"].split("/")[-1]
                    parent = result["path"].split("/")[-2] if len(result["path"].split("/")) > 1 else ""
                    report.append(f"   文件: {filename}")
                    if parent:
                        report.append(f"   位置: {parent}")
        
        report.append(f"\n{'='*60}")
        
        return "\n".join(report)


# ============================================================================
# 主流程
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="推理式检索系统（集成版）")
    parser.add_argument("--query", help="搜索查询")
    parser.add_argument("--test", action="store_true", help="测试示例")
    parser.add_argument("--report", action="store_true", help="显示测试报告")
    
    args = parser.parse_args()
    
    retriever = ReasoningRetriever()
    
    if args.test:
        # 测试示例
        print("="*60)
        print("🧪 推理式检索测试（集成版）")
        print("="*60)
        
        # 测试 1: 语义匹配
        print("\n测试 1: 语义匹配")
        results1 = retriever.retrieve("记忆系统优化")
        print(retriever.generate_report("记忆系统优化", results1))
        
        # 测试 2: 隐含关系
        print("\n测试 2: 隐含关系")
        results2 = retriever.retrieve("昨天的问题")
        print(retriever.generate_report("昨天的问题", results2))
        
        # 测试 3: 跨层关联
        print("\n测试 3: 跨层关联")
        results3 =<arg_value> retriever.retrieve("Token 使用情况")
        print(retriever.generate_report("Token 使用情况", results3))
        
        print("\n" + "="*60)
        print("✅ 测试完成")
        print("="*60)
    
    elif args.query:
        # 实际检索
        results = retriever.retrieve(args.query)
        print(retriever.generate_report(args.query, results))
    
    else:
        print("用法:")
        print("  python3 reasoning-retriever.py --test  # 测试示例")
        print("  python3 reasoning-retriever.py --query \"你的查询\"")
        print("\n说明:")
        print("  --test: 运行测试示例")
        print("  --query: 搜索指定内容")
