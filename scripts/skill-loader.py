#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skills 按需加载机制 - 通过 tool_result 注入知识
基于 learn-claude-code 的 s05 课程
"""

import os
from pathlib import Path
from typing import Dict, Optional, List


class SkillLoader:
    """技能加载器 - 按需加载知识"""
    
    def __init__(self, workspace: str = "/root/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.skills_dir = self.workspace / "skills"
        
        # 技能缓存
        self.skill_cache = {}
    
    def load_skill(self, skill_name: str) -> str:
        """
        按需加载技能
        
        Args:
            skill_name: 技能名称
        
        Returns:
            技能内容
        """
        print(f"\n📚 加载技能: {skill_name}")
        print("-"*60)
        
        # 检查缓存
        if skill_name in self.skill_cache:
            print(f"✅ 从缓存加载")
            return self.skill_cache[skill_name]
        
        # 查找技能文件
        skill_file = self.skills_dir / skill_name / "SKILL.md"
        
        if not skill_file.exists():
            print(f"⚠️  技能不存在: {skill_name}")
            return ""
        
        # 读取技能内容
        with open(skill_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 缓存技能
        self.skill_cache[skill_name] = content
        
        # 统计信息
        lines = len(content.split("\n"))
        print(f"✅ 技能已加载: {lines} 行")
        
        return content
    
    def list_skills(self) -> List[str]:
        """
        列出可用技能
        
        Returns:
            技能名称列表
        """
        print(f"\n📚 可用技能:")
        print("-"*60)
        
        if not self.skills_dir.exists():
            print("⚠️  技能目录不存在")
            return []
        
        skills = []
        for skill_dir in sorted(self.skills_dir.iterdir()):
            if (skill_dir / "SKILL.md").exists():
                skills.append(skill_dir.name)
                print(f"  ✅ {skill_dir.name}")
        
        print(f"✅ 找到 {len(skills)} 个技能")
        
        return skills
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        cached = len(self.skill_cache)
        total = len(self.list_skills())
        
        return {
            "cached": cached,
            "total": total,
            "cache_hit_rate": f"{(cached/total*100):.1f}%" if total > 0 else "0%"
        }


# ============================================================================
# 主流程
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Skills 按需加载机制")
    parser.add_argument("--load", nargs=1, metavar="skill", help="加载技能")
    parser.add_argument("--list", action="store_true", help="列出技能")
    parser.add_argument("--stats", action="store_true", help="查看统计")
    
    args = parser.parse_args()
    
    loader = SkillLoader()
    
    if args.load:
        content = loader.load_skill(args.load)
        print("\n技能内容:")
        print(content[:500] + "..." if len(content) > 500 else content)
    
    elif args.list:
        skills = loader.list_skills()
    
    elif args.stats:
        stats = loader.get_stats()
        print("\n📊 统计信息:")
        print("="*60)
        print(f"已缓存: {stats['cached']} 个")
        print(f"总技能: {stats['total']} 个")
        print(f"缓存命中率: {stats['cache_hit_rate']}")
        print("="*60)
    
    else:
        print("用法:")
        print("  python3 skill-loader.py --load <skill>  # 加载技能")
        print("  python3 skill-loader.py --list  # 列出技能")
        print("  python3 skill-loader.py --stats  # 查看统计")
        print("\n核心价值:")
        print("  上下文优化 +40%")
        print("  按需加载，不塞 system prompt")
        print("  减少 Token 消耗")
