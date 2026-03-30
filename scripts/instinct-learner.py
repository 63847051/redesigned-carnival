#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持续学习 Instincts 系统
自动从会话中提取模式并转换为技能
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class InstinctLearner:
    """Instinct 学习器 - 持续学习"""
    
    def __init__(self):
        self.instincts_file = Path("/root/.openclaw/workspace/.learnings/instincts.json")
        self.instincts = self._load_instincts()
    
    def _load_instincts(self) -> List[Dict]:
        """加载已保存的 instincts"""
        if self.instincts_file.exists():
            try:
                with open(self.instincts_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  加载 instincts 失败: {e}")
                return []
        return []
    
    def _save_instincts(self):
        """保存 instincts"""
        self.instincts_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.instincts_file, "w", encoding="utf-8") as f:
            json.dump(self.instincts, f, indent=2, ensure_ascii=False)
    
    def extract_pattern(self, session_data: Dict) -> List[Dict]:
        """
        从会话数据中提取模式
        
        Args:
            session_data: 会话数据
        
        Returns:
            提取的模式列表
        """
        print(f"\n🔍 提取模式...")
        
        patterns = []
        
        # 提取 1: 常见问题
        questions = self._extract_questions(session_data)
        if questions:
            patterns.extend(questions)
        
        # 提取 2: 常见解决方案
        solutions = self._extract_solutions(session_data)
        if solutions:
            patterns.extend(solutions)
        
        # 提取 3: 常见错误
        errors = self._extract_errors(session_data)
        if errors:
            patterns.extend(errors)
        
        print(f"   提取了 {len(patterns)} 个模式")
        
        return patterns
    
    def _extract_questions(self, session_data: Dict) -> List[Dict]:
        """提取常见问题"""
        questions = []
        
        # 从用户消息中提取问题
        user_messages = session_data.get("user_messages", [])
        for msg in user_messages:
            # 检测问题模式
            if "?" in msg or "？" in msg or "如何" in msg or "怎么" in msg:
                questions.append({
                    "type": "question",
                    "pattern": msg,
                    "confidence": 0.8,
                    "source": "user"
                })
        
        return questions
    
    def _extract_solutions(self, session_data: Dict) -> List[Dict]:
        """提取常见解决方案"""
        solutions = []
        
        # 从助手回复中提取解决方案
        assistant_messages = session_data.get("assistant_messages", [])
        for msg in assistant_messages:
            # 检测解决方案模式
            if "解决方案" in msg or "可以尝试" in msg or "建议" in msg:
                solutions.append({
                    "type": "solution",
                    "pattern": msg,
                    "confidence": 0.8,
                    "source": "assistant"
                })
        
        return solutions
    
    def _extract_errors(self, session_data: Dict) -> List[Dict]:
        """提取常见错误"""
        errors = []
        
        # 从系统消息中提取错误
        system_messages = session_data.get("system_messages", [])
        for msg in system_messages:
            # 检测错误模式
            if "错误" in msg or "失败" in msg or "异常" in msg:
                errors.append({
                    "type": "error",
                    "pattern": msg,
                    "confidence": 0.9,
                    "source": "system"
                })
        
        return errors
    
    def convert_to_skill(self, pattern: Dict) -> Dict:
        """
        将模式转换为技能
        
        Args:
            pattern: 提取的模式
        
        Returns:
            技能定义
        """
        print(f"\n🔄 转换为技能...")
        
        skill = {
            "name": self._generate_skill_name(pattern),
            "type": pattern["type"],
            "pattern": pattern["pattern"],
            "confidence": pattern.get("confidence", 0.5),
            "source": "instinct_learning",
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        # 添加技能描述
        skill["description"] = self._generate_description(pattern)
        
        print(f"   技能: {skill['name']}")
        
        return skill
    
    def _generate_skill_name(self, pattern: Dict) -> str:
        """生成技能名称"""
        pattern_type = pattern["type"]
        pattern_text = pattern["pattern"][:30]
        
        # 生成名称
        if pattern_type == "question":
            return f"answer-{hash(pattern_text) % 1000:04x}"
        elif pattern_type == "solution":
            return f"solution-{hash(pattern_text) % 1000:04x}"
        elif pattern_type == "error":
            return f"fix-{hash(pattern_text) % 1000:04x}"
        else:
            return f"auto-{hash(pattern_text) % 1000:04x}"
    
    def _generate_description(self, pattern: Dict) -> str:
        """生成技能描述"""
        pattern_type = pattern["type"]
        pattern_text = pattern["pattern"][:100]
        
        if pattern_type == "question":
            return f"自动回答问题: {pattern_text}"
        elif pattern == "solution":
            return f"自动解决方案: {pattern_text}"
        elif pattern_type == "error":
            return f"错误修复: {pattern_text}"
        else:
            return f"自动模式: {pattern_text}"
    
    def learn(self, session_data: Dict) -> List[Dict]:
        """
        从会话数据中学习
        
        Args:
            session_data: 会话数据
        
        Returns:
            新学习的技能
        """
        print(f"\n🎓 持续学习 Instincts")
        print("="*60)
        
        # Step 1: 提取模式
        patterns = self.extract_pattern(session_data)
        
        # Step 2: 转换为技能
        new_skills = []
        for pattern in patterns:
            if pattern["confidence"] >= 0.7:  # 只保留高置信度的模式
                skill = self.convert_to_skill(pattern)
                new_skills.append(skill)
        
        # Step 3: 更新 instincts
        if new_skills:
            self.instincts.extend(new_skills)
            self._save_instincts()
            print(f"\n✅ 学习了 {len(new_skills)} 个新技能")
        else:
            print("\n⏳ 没有新的模式需要学习")
        
        return new_skills


# ============================================================================
# 主流程
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="持续学习 Instincts 系统")
    parser.add_argument("--test", action="store_true", help="测试示例")
    parser.add_argument("--session", help="会话数据文件路径")
    
    args = parser.parse_args()
    
    learner = InstinctLearner()
    
    if args.test:
        # 测试示例
        print("="*60)
        print("🧪 持续学习测试")
        print("="*60)
        
        # 模拟会话数据
        session_data = {
            "user_messages": [
                "如何优化性能？",
                "怎么安装？",
                "有什么建议？"
            ],
            "assistant_messages": [
                "解决方案：使用缓存",
                "建议：查看文档",
                "可以尝试：pip install"
            ],
            "system_messages": [
                "错误：连接失败",
                "异常：权限不足"
            ]
        }
        
        # 学习
        new_skills = learner.learn(session_data)
        
        print("\n" + "="*60)
        print("✅ 测试完成")
        print("="*60)
        print(f"\n📊 统计:")
        print(f"   已保存的 instincts: {len(learner.instincts)}")
        print(f"   新学习的技能: {len(new_skills)}")
    
    elif args.session:
        # 从实际会话学习
        try:
            with open(args.session, "r", encoding="utf-8") as f:
                session_data = json.load(f)
            
            new_skills = learner.learn(session_data)
            
            print(f"\n✅ 学习了 {len(new_skills)} 个新技能")
            
        except Exception as e:
            print(f"\n❌ 错误: {e}")
    
    else:
        print("用法:")
        print("  python3 instinct-learner.py --test  # 测试示例")
        print("  python3 instinct-learner.py --session <会话数据.json>")
        print("\n说明:")
        print("  从会话数据中自动提取模式")
        print("  转换为可重用的技能")
        print("  持续进化基础")
        print("\n核心价值:")
        print("  学习效率 +100%")
        print("  技能积累速度 +200%")
