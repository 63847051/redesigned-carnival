#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同义词扩展系统 - 提升召回率
"""

import json
from pathlib import Path
from typing import Dict, List


class SynonymExpander:
    """同义词扩展器"""
    
    def __init__(self):
        self.synonyms = self._load_synonyms()
    
    def _load_synonyms(self) -> Dict[str, List[str]]:
        """加载同义词库"""
        return {
            # 记忆相关
            "记忆": ["Memory", "memory", "记忆系统", "存储", "知识", "记录"],
            
            # 性能相关
            "性能": ["速度", "效率", "优化", "提升", "改进", "增强"],
            
            # Token 相关
            "Token": ["token", "成本", "费用", "使用量", "API", "调用"],
            
            # 自动化相关
            "自动化": ["自动", "脚本", "工具", "批处理", "流程"],
            
            # 系统相关
            "系统": ["架构", "框架", "平台", "工具", "方案"],
            
            # 时间相关
            "昨天": ["yesterday", "前天", "之前"],
            "今天": ["today", "当前", "现在"],
            "最近": ["recent", "近期", "latest"],
            
            # 动作相关
            "优化": ["改进", "提升", "改善", "增强", "加速"],
            "分析": ["研究", "检查", "审查", "测试"],
            "创建": ["生成", "新建", "建立", "构建"],
        }
    
    def expand(self, query: str) -> List[str]:
        """扩展查询"""
        expanded = [query]  # 原始查询
        
        # 查找匹配的同义词
        for key, synonyms in self.synonyms.items():
            if key.lower() in query.lower():
                expanded.extend(synonyms)
        
        # 去重
        return list(set(expanded))
    
    def save(self, path: str = None):
        """保存同义词库"""
        if path is None:
            path = "/root/.openclaw/workspace/data/synonyms.json"
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.synonyms, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 同义词库已保存到: {path}")
    
    def load(self, path: str = "/root/.openclaw/workspace/data/synonyms.json"):
        """加载同义词库"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.synonyms = json.load(f)
            print(f"✅ 同义词库已加载: {path}")
        except FileNotFoundError:
            print(f"⚠️  同义词库不存在，使用默认库")


# ============================================================================
# 主流程
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="同义词扩展系统")
    parser.add_argument("--query", help="查询内容")
    parser.add_argument("--save", action="store_true", help="保存同义词库")
    parser.add_argument("--test", action="store_true", help="测试示例")
    
    args = parser.parse_args()
    
    expander = SynonymExpander()
    
    if args.save:
        expander.save()
    
    elif args.test:
        # 测试示例
        print("="*60)
        print("🧪 同义词扩展测试")
        print("="*60)
        
        # 测试 1
        print("\n测试 1: \"性能优化\"")
        result1 = expander.expand("性能优化")
        print(f"   原始: 性能优化")
        print(f"   扩展: {', '.join(result1)}")
        
        # 测试 2
        print("\n测试 2: \"Token 使用\"")
        result2 = expander.expand("Token 使用")
        print(f"   原始: Token 使用")
        print(f"   扩展: {', '.join(result2)}")
        
        # 测试 3
        print("\n测试 3: \"记忆系统\"")
        result3 = expander.expand("记忆系统")
        print(f"   原始: 记忆系统")
        print(f"   扩展: {', '.join(result3)}")
        
        print("\n" + "="*60)
        print("✅ 测试完成")
    
    elif args.query:
        # 实际扩展
        result = expander.expand(args.query)
        print(f"原始: {args.query}")
        print(f"扩展: {', '.join(result)}")
    
    else:
        print("用法:")
        print("  python3 synonym-expander.py --test  # 测试示例")
        print("  python3 synonym-expander.py --query \"你的查询\"")
        print("  python3 synonym-expander.py --save  # 保存同义词库")
