#!/usr/bin/env python3
# -*-- coding: utf-8 -*-
"""
第一性原理引擎 - 提升内容质量，减少空话和套话
"""

import re
from typing import Dict, List


class FirstPrinciplesEngine:
    """第一性原理引擎"""
    
    def decompose(self, problem: str) -> Dict:
        """
        第一性原理分解
        
        Args:
            problem: 问题描述
        
        Returns:
            分解结果
        """
        print(f"\n🔬 第一性原理分解: {problem}")
        
        # 1. 本质是什么？
        essence = self._find_essence(problem)
        
        # 2. 底层逻辑是什么？
        logic = self._find_underlying_logic(problem)
        
        # 3. 最小可行方案是什么？
        mvp = self._find_mvp_solution(problem)
        
        return {
            "problem": problem,
            "essence": essence,
            "underlying_logic": logic,
            "mvp_solution": mvp
        }
    
    def _find_essence(self, problem: str) -> str:
        """找到本质"""
        # 移除修饰词，提取核心
        words = problem.split()
        
        # 识别核心关键词
        essence_keywords = []
        for word in words:
            # 跳过修饰词
            if word in ["的", "一个", "这个", "那个", "如何", "怎么"]:
                continue
            essence_keywords.append(word)
        
        essence = " ".join(essence_keywords) if essence_keywords else problem
        
        # 如果是技术问题，提取核心概念
        if "系统" in problem or "优化" in problem:
            # 提取核心对象
            match = re.search(r'(优化|改进|升级)(.+?)(系统|功能)', problem)
            if match:
                essence = match.group(2).strip()
        
        return essence
    
    def _find_underlying_logic(self, problem: str) -> str:
        """找到底层逻辑"""
        # 常见的底层逻辑
        logic_patterns = {
            "性能": "性能 = 时间 × 复杂度",
            "准确率": "准确率 = 信息量 × 处理能力",
            "效率": "效率 = 输出 / 输入",
            "成本": "成本 = 资源消耗 × 时间",
            "体验": "体验 = 响应速度 + 结果质量"
        }
        
        for key, logic in logic_patterns.items():
            if key in problem:
                return logic
        
        # 默认逻辑
        return "效果 = 质量 × 效率"
    
    def _find_mvp_solution(self, problem: str) -> str:
        """找到最小可行方案"""
        # 分析问题类型
        if "创建" in problem or "开发" in problem:
            return "先写文档，再写代码"
        elif "优化" in problem or "改进" in problem:
            return "测量 → 分析 → 优化 → 验证"
        elif "学习" in problem or "理解" in problem:
            return "拆解 → 关联 → 实践 → 总结"
        else:
            return "明确目标 → 拆解问题 → 逐一解决"
    
    def apply_first_principles(self, content: str, context: Dict = None) -> str:
        """
        应用第一性原理，生成高质量内容
        
        Args:
            content: 原始内容
            context: 上下文信息
        
        Returns:
            优化后的内容
        """
        print("\n🧠 应用第一性原理...")
        
        # 1. 去除空话和套话
        content = self._remove_cliches(content)
        
        # 2. 聚焦核心逻辑
        content = self._focus_on_logic(content)
        
        # 3. 简化表达
        content = self._simplify_expression(content)
        
        # 4. 添加数据支撑
        content = self._add_data_support(content)
        
        return content
    
    def _remove_cliches(self, content: str) -> str:
        """去除空话和套话"""
        # 常见套话模式
        cliches = [
            r"总的来说，.*?就是.*",
            r"值得注意的是.*?（.*?）",
            r"我们需要.*?注意.*?",
            r".*?是.*?的重要.*?",
            r".*?不仅.*?而且.*?",
            r"一方面.*?另一方面.*?"
        ]
        
        lines = content.split("\n")
        filtered_lines = []
        
        for line in lines:
            # 跳过空话行
            is_cliche = False
            for pattern in cliches:
                if re.search(pattern, line):
                    is_cliche = True
                    break
            
            if not is_cliche:
                filtered_lines.append(line)
        
        return "\n".join(filtered_lines)
    
    def _focus_on_logic(self, content: str) -> str:
        """聚焦核心逻辑"""
        # 提取核心论点和论据
        lines = content.split("\n")
        
        core_lines = []
        for line in lines:
            line = line.strip()
            # 跳过空行
            if not line:
                continue
            
            # 聚焦有逻辑的行
            if any(keyword in line for keyword in ["因为", "所以", "由于", "导致", "原因是", "结果是"]):
                core_lines.append(line)
            # 保留关键数据
            elif re.search(r'\d+[%\$]', line):
                core_lines.append(line)
            # 保留列表和标题
            elif line.startswith('#') or line.startswith('-') or line.startswith('*'):
                core_lines.append(line)
        
        return "\n".join(core_lines)
    
    def _simplify_expression(self, content: str) -> str:
        """简化表达"""
        # 去除冗余的修饰词
        content = re.sub(r'非常|极其|特别|相当', '', content)
        content = re.sub(r'十分|极其|非常', '', content)
        content = re.sub(r'很多|大量|不少', '', content)
        
        return content
    
    def _add_data_support(self, content: str) -> str:
        """添加数据支撑"""
        # 如果内容中有断言但没有数据，添加数据占位符
        if re.search(r'(提升|改善|优化|降低)', content):
            if not re.search(r'\d+[%\$]', content):
                # 提示添加数据
                content += "\n\n💡 数据支撑：[需要添加具体数据]"
        
        return content
    
    def analyze_content_quality(self, content: str) -> Dict:
        """分析内容质量"""
        print("\n📊 分析内容质量...")
        
        # 检查空话比例
        lines = content.split("\n")
        empty_lines = len([l for l in lines if not l.strip()])
        total_lines = len(lines)
        
        empty_ratio = empty_lines / total_lines if total_lines > 0 else 0
        
        # 检查逻辑密度
        logic_keywords = ["因为", "所以", "由于", "导致", "原因是", "结果是"]
        logic_count = sum(1 for line in lines if any(kw in line for kw in logic_keywords))
        logic_density = logic_count / total_lines if total_lines > 0 else 0
        
        # 检查数据密度
        data_count = sum(1 for line in lines if re.search(r'\d+[\$%]', line))
        data_density = data_count / total_lines if total_lines > 0 else 0
        
        # 综合评分
        quality_score = (1 - empty_ratio) * 0.4 + logic_density * 0.4 + data_density * 0.2
        
        return {
            "empty_ratio": round(empty_ratio * 100, 1),
            "logic_density": round(logic_density * 100, 1),
            "data_density": round(data_density * 100, 1),
            "quality_score": round(quality_score * 100, 1),
            "suggestions": self._generate_suggestions(empty_ratio, logic_density, data_density)
        }
    
    def _generate_suggestions(self, empty_ratio: float, logic_density: float, data_density: float) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if empty_ratio > 30:
            suggestions.append(f"空话过多（{empty_ratio:.1f}%），建议去除")
        
        if logic_density < 20:
            suggestions.append(f"逻辑密度低（{logic_density:.1f}%），建议增加因果分析")
        
        if data_density < 10:
            suggestions.append(f"数据密度低（{data_density:.1f}%），建议添加具体数据")
        
        if not suggestions:
            suggestions.append("内容质量良好")
        
        return suggestions


# ============================================================================
# 主流程
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="第一性原理引擎")
    parser.add_argument("--decompose", help="问题分解")
    parser.add_argument("--apply", help="应用第一性原理到内容")
    parser.add_argument("--analyze", help="分析内容质量", action="store_true")
    
    args = parser.parse_args()
    
    engine = FirstPrinciplesEngine()
    
    if args.decompose:
        # 问题分解
        result = engine.decompose(args.decompose)
        
        print(f"\n📊 分解结果:")
        print(f"本质: {result['essence']}")
        print(f"底层逻辑: {result['underlying_logic']}")
        print(f"MVP: {result['mvp_solution']}")
    
    elif args.analyze:
        # 分析内容质量
        # 从文件读取或使用示例内容
        sample_content = """
这是一篇关于系统优化的文章。

总的来说，我们需要特别注意系统的性能问题。值得注意的是，性能优化是非常重要的。

系统性能的提升可以通过多种方式实现。一方面，我们可以优化代码；另一方面，我们可以优化架构。

用户最关心的是响应速度。响应速度提升了30%，用户满意度也会提升。
"""
        
        result = engine.analyze_content_quality(sample_content)
        
        print(f"\n📊 内容质量分析:")
        print(f"空话比例: {result['empty_ratio']}%")
        print(f"逻辑密度: {result['logic_density']}%")
        print(f"数据密度: {result['data_density']}%")
        print(f"综合评分: {result['quality_score']}/100")
        
        print(f"\n💡 改进建议:")
        for i, suggestion in enumerate(result['suggestions'], 1):
            print(f"{i}. {suggestion}")
    
    else:
        print("用法:")
        print("  python3 first-principles-engine.py --decompose \"优化系统性能\"")
        print("  python3 first-principles-engine.py --analyze < content.txt")
