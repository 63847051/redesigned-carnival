#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询预处理系统 - 隐含关系推理
理解用户意图，转换隐含查询
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List


class QueryPreprocessor:
    """查询预处理器 - LLM 驱动"""
    
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    def preprocess(self, query: str) -> Dict:
        """
        预处理查询
        
        Returns:
            {
                "original": "原始查询",
                "expanded": "扩展查询",
                "filters": {"date": "...", "type": "..."},
                "intent": "意图"
            }
        """
        print(f"\n🔍 预处理查询: {query}")
        
        # Step 1: 识别隐含关系
        print("   Step 1: 识别隐含关系...")
        intent = self._identify_intent(query)
        
        # Step 2: 扩展查询
        print("   Step 2: 扩展查询...")
        expanded = self._expand_query(query, intent)
        
        # Step 3: 提取过滤器
        print("   Step 3: 提取过滤器...")
        filters = self._extract_filters(query, intent)
        
        result = {
            "original": query,
            "expanded": expanded,
            "filters": filters,
            "intent": intent
        }
        
        print(f"   ✅ 预处理完成")
        return result
    
    def _identify_intent(self, query: str) -> str:
        """识别查询意图"""
        query_lower = query.lower()
        
        # 时间相关
        if "昨天" in query or "昨" in query:
            return "temporal.yesterday"
        elif "今天" in query or "今" in query:
            return "temporal.today"
        elif "最近" in query:
            return "temporal.recent"
        
        # 统计相关
        elif "使用情况" in query or "统计" in query:
            return "statistics.usage"
        elif "成本" in query or "费用" in query:
            return "statistics.cost"
        elif "数量" in query:
            return "statistics.count"
        
        # 性能相关
        elif "性能" in query or "优化" in query:
            return "performance.optimization"
        elif "速度" in query or "快" in query:
            return "performance.speed"
        elif "延迟" in query or "慢" in query:
            return "performance.latency"
        
        # 默认
        return "semantic.search"
    
    def _expand_query(self, query: str, intent: str) -> List[str]:
        """扩展查询"""
        expanded = [query]  # 原始查询
        
        # 时间扩展
        if "yesterday" in intent:
            expanded.append(self.yesterday)
            expanded.append(query.replace("昨天", self.yesterday))
        elif "today" in intent:
            expanded.append(self.today)
            expanded.append(query.replace("今天", self.today))
        
        # 同义词扩展
        synonyms = self._get_synonyms(query)
        expanded.extend(synonyms)
        
        return list(set(expanded))  # 去重
    
    def _get_synonyms(self, query: str) -> List[str]:
        """获取同义词"""
        synonyms_map = {
            "性能": ["速度", "效率", "优化", "提升"],
            "Token": ["成本", "费用", "使用量", "API"],
            "记忆": ["Memory", "记忆系统", "存储", "知识"],
            "优化": ["改进", "提升", "改善", "增强"],
            "自动化": ["自动", "脚本", "工具", "批处理"]
        }
        
        synonyms = []
        query_lower = query.lower()
        
        for key, values in synonyms_map.items():
            if key.lower() in query_lower:
                synonyms.extend(values)
        
        return synonyms
    
    def _extract_filters(self, query: str, intent: str) -> Dict:
        """提取过滤器"""
        filters = {}
        
        # 时间过滤器
        if "yesterday" in intent:
            filters["date"] = self.yesterday
        elif "today" in intent:
            filters["date"] = self.today
        elif "recent" in intent:
            filters["date_range"] = "7d"
        
        # 类型过滤器
        if "optimization" in intent:
            filters["type"] = "improvement"
        elif "usage" in intent:
            filters["type"] = "statistics"
        
        return filters
    
    def explain(self, result: Dict) -> str:
        """解释预处理结果"""
        explanation = []
        explanation.append("="*60)
        explanation.append(f"🔍 预处理结果: {result['original']}")
        explanation.append("="*60)
        
        explanation.append(f"\n📊 意图识别:")
        explanation.append(f"   {result['intent']}")
        
        if result['expanded']:
            explanation.append(f"\n📝 扩展查询:")
            for i, q in enumerate(result['expanded'], 1):
                explanation.append(f"   {i}. {q}")
        
        if result['filters']:
            explanation.append(f"\n🔧 过滤器:")
            for key, value in result['filters'].items():
                explanation.append(f"   {key}: {value}")
        
        explanation.append(f"\n{'='*60}")
        
        return "\n".join(explanation)


# ============================================================================
# 主流程
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="查询预处理系统")
    parser.add_argument("--query", help="查询内容")
    parser.add_argument("--test", action="store_true", help="测试示例")
    
    args = parser.parse_args()
    
    preprocessor = QueryPreprocessor()
    
    if args.test:
        # 测试示例
        print("="*60)
        print("🧪 查询预处理测试")
        print("="*60)
        
        # 测试 1: 隐含时间
        print("\n测试 1: 隐含时间")
        result1 = preprocessor.preprocess("昨天的问题")
        print(preprocessor.explain(result1))
        
        # 测试 2: 隐含统计
        print("\n测试 2: 隐含统计")
        result2 = preprocessor.preprocess("Token 使用情况")
        print(preprocessor.explain(result2))
        
        # 测试 3: 隐含性能
        print("\n测试 3: 隐含性能")
        result3 = preprocessor.preprocess("性能提升")
        print(preprocessor.explain(result3))
        
        print("\n" + "="*60)
        print("✅ 测试完成")
    
    elif args.query:
        # 实际预处理
        result = preprocessor.preprocess(args.query)
        print(preprocessor.explain(result))
    
    else:
        print("用法:")
        print("  python3 query-preprocessor.py --test  # 测试示例")
        print("  python3 query-preprocessor.py --query \"你的查询\"")
        print("\n示例:")
        print("  python3 query-preprocessor.py --test")
