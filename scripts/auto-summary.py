#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动摘要生成系统
- L0 → L1: 每日对话 → 关键点
- L1 → L2: 月度关键点 → 结构化知识
- L2 → L3: 分类知识 → 长期洞察
"""

import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
MEMORY_KEY_POINTS = MEMORY_DIR / "key-points"
MEMORY_STRUCTURED = MEMORY_DIR / "structured"
MEMORY_FILE = WORKSPACE / "MEMORY.md"
LOG_FILE = MEMORY_DIR / ".auto-summary.log"

# 分类目录
CATEGORIES = ["people", "projects", "knowledge", "preferences"]

# 颜色输出
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    RED = '\033[0;31m'
    NC = '\033[0m'

def log(message: str, level: str = "INFO"):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}"
    print(log_line)

    # 写入日志文件
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except Exception as e:
        print(f"写入日志失败: {e}")

# ============================================================================
# LLM 接口（使用 GLM-4.5-Air 免费模型）
# ============================================================================

def call_llm(prompt: str, max_tokens: int = 500) -> str:
    """
    调用 LLM（使用 GLM-4.5-Air 免费模型）
    """
    try:
        # 尝试使用 OpenAI 兼容接口
        from openai import OpenAI
        
        # 检查 API Key
        api_key = os.getenv("GLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            # 回退到规则提取
            return _rule_based_extraction(prompt)
        
        client = OpenAI(
            base_url="https://open.bigmodel.cn/api/anthropic",
            api_key=api_key
        )
        
        response = client.chat.completions.create(
            model="glmcode/glm-4.5-air",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的文本分析助手，擅长提取关键信息、分类和总结。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=max_tokens,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except ImportError:
        # openai 库未安装，回退到规则提取
        log("openai 库未安装，使用规则提取", "WARNING")
        return _rule_based_extraction(prompt)
        
    except Exception as e:
        # API 调用失败，回退到规则提取
        log(f"LLM 调用失败: {e}，使用规则提取", "WARNING")
        return _rule_based_extraction(prompt)

def _rule_based_extraction(prompt: str) -> str:
    """
    基于规则的提取（回退方案）
    """
    lines = prompt.split("\n")
    results = []
    
    # 提取关键点
    if "关键点" in prompt or "key points" in prompt.lower():
        for line in lines:
            line = line.strip()
            if line and (line.startswith("##") or line.startswith("✅") or 
                       line.startswith("❌") or "完成" in line or "实现" in line or
                       "创建" in line or "实施" in line):
                results.append(line)
        return "\n".join(results[:10]) if results else "无关键点"
    
    # 提取项目相关
    elif "项目" in prompt or "project" in prompt.lower():
        for line in lines:
            if "项目" in line or "任务" in line or "开发" in line or "实施" in line:
                results.append(line.strip())
        return "\n".join(results[:5]) if results else "无项目相关"
    
    # 提取人物相关
    elif "幸运小行星" in prompt or "用户" in prompt or "people" in prompt.lower():
        for line in lines:
            if "幸运小行星" in line or "用户" in line or "客户" in line:
                results.append(line.strip())
        return "\n".join(results[:5]) if results else "无人物相关"
    
    # 提取知识相关
    elif "知识" in prompt or "学习" in prompt or "knowledge" in prompt.lower():
        for line in lines:
            if "学习" in line or "研究" in line or "分析" in line or "发现" in line:
                results.append(line.strip())
        return "\n".join(results[:5]) if results else "无知识相关"
    
    # 提取洞察
    elif "洞察" in prompt or "insight" in prompt.lower():
        for line in lines:
            if "洞察" in line or "发现" in line or "教训" in line or "经验" in line:
                results.append(line.strip())
        return "\n".join(results[:3]) if results else "无明显洞察"
    
    return "无法提取"

# ============================================================================
# L0 → L1: 每日对话 → 关键点
# ============================================================================

def extract_key_points_from_daily(daily_file: Path) -> Dict:
    """从每日对话中提取关键点"""
    log(f"处理 L0 → L1: {daily_file.name}", "INFO")

    try:
        # 读取文件
        with open(daily_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取日期
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', daily_file.name)
        date = date_match.group(1) if date_match else daily_file.stem

        # 使用 LLM 提取关键点
        prompt = f"""请从以下对话中提取关键点（不超过10条）：

{content}

只返回关键点列表，每行一个。"""
        key_points = call_llm(prompt, max_tokens=500)

        return {
            "date": date,
            "key_points": key_points,
            "source_file": str(daily_file)
        }

    except Exception as e:
        log(f"处理失败: {e}", "ERROR")
        return None

def process_l0_to_l1(target_date: Optional[str] = None):
    """处理 L0 → L1"""
    log("开始处理 L0 → L1: 每日对话 → 关键点", "INFO")

    # 确定目标日期
    if target_date:
        daily_files = [MEMORY_DIR / f"{target_date}.md"]
    else:
        # 处理昨天的文件
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        daily_files = [MEMORY_DIR / f"{yesterday}.md"]

    # 处理每个文件
    for daily_file in daily_files:
        if not daily_file.exists():
            log(f"文件不存在: {daily_file}", "WARNING")
            continue

        result = extract_key_points_from_daily(daily_file)
        if result:
            # 保存到 L1
            month = result["date"][:7]  # "2026-03"
            month_file = MEMORY_KEY_POINTS / f"{month}.md"

            # 追加到月度文件
            with open(month_file, "a", encoding="utf-8") as f:
                f.write(f"\n## {result['date']}\n\n")
                f.write(f"{result['key_points']}\n")

            log(f"✓ L0 → L1 完成: {result['date']}", "INFO")

# ============================================================================
# L1 → L2: 月度关键点 → 结构化知识
# ============================================================================

def categorize_monthly_key_points(month_file: Path) -> Dict[str, List[str]]:
    """将月度关键点分类到结构化知识"""
    log(f"处理 L1 → L2: {month_file.name}", "INFO")

    try:
        # 读取月度关键点
        with open(month_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取月份
        month_match = re.search(r'(\d{4}-\d{2})', month_file.name)
        month = month_match.group(1) if month_match else month_file.stem

        # 按日期分割
        days = content.split("## ")[1:]  # 跳过标题

        categorized = {cat: [] for cat in CATEGORIES}

        # 分类每一天的关键点
        for day_content in days:
            lines = day_content.split("\n")
            date = lines[0].strip() if lines else ""

            # 使用 LLM 分类
            for category in CATEGORIES:
                prompt = f"""从以下关键点中提取{category}相关的内容：

{day_content}

只返回相关内容，每行一个。"""
                extracted = call_llm(prompt, max_tokens=300)

                if extracted and extracted != f"无{category}相关":
                    categorized[category].append(f"\n## {date}\n{extracted}")

        return categorized

    except Exception as e:
        log(f"分类失败: {e}", "ERROR")
        return {cat: [] for cat in CATEGORIES}

def process_l1_to_l2(target_month: Optional[str] = None):
    """处理 L1 → L2"""
    log("开始处理 L1 → L2: 月度关键点 → 结构化知识", "INFO")

    # 确定目标月份
    if target_month:
        month_files = [MEMORY_KEY_POINTS / f"{target_month}.md"]
    else:
        # 处理所有月份文件
        month_files = list(MEMORY_KEY_POINTS.glob("*.md"))

    # 处理每个月份
    for month_file in month_files:
        categorized = categorize_monthly_key_points(month_file)

        # 保存到 L2
        month_match = re.search(r'(\d{4}-\d{2})', month_file.name)
        month = month_match.group(1) if month_match else month_file.stem

        for category, contents in categorized.items():
            if contents:
                category_dir = MEMORY_STRUCTURED / category
                category_file = category_dir / f"{month}.md"

                with open(category_file, "w", encoding="utf-8") as f:
                    f.write(f"# {month} {category.capitalize()}\n")
                    f.write("".join(contents))

                log(f"✓ L1 → L2 完成: {category}/{month}", "INFO")

# ============================================================================
# L2 → L3: 分类知识 → 长期洞察
# ============================================================================

def extract_insights_from_l2() -> Dict[str, str]:
    """从 L2 结构化知识中提取长期洞察"""
    log("开始处理 L2 → L3: 分类知识 → 长期洞察", "INFO")

    insights = {}

    # 处理每个分类
    for category in CATEGORIES:
        category_dir = MEMORY_STRUCTURED / category

        if not category_dir.exists():
            continue

        # 读取该分类的所有文件
        all_content = []
        for file in sorted(category_dir.glob("*.md")):
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                all_content.append(f"## {file.name}\n{content}")

        combined_content = "\n".join(all_content)

        # 使用 LLM 提取洞察
        if combined_content:
            prompt = f"""从以下{category}相关的内容中提取3-5个最重要的洞察或模式：

{combined_content}

只返回洞察列表，每行一个。"""
            extracted_insights = call_llm(prompt, max_tokens=300)

            if extracted_insights and extracted_insights != "无明显洞察":
                insights[category] = extracted_insights
                log(f"✓ 提取洞察: {category}", "INFO")

    return insights

def process_l2_to_l3():
    """处理 L2 → L3"""
    log("开始处理 L2 → L3: 分类知识 → 长期洞察", "INFO")

    insights = extract_insights_from_l2()

    if insights:
        # 追加到 MEMORY.md
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n## 长期洞察（自动生成）\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for category, content in insights.items():
                f.write(f"### {category.capitalize()}\n")
                f.write(f"{content}\n\n")

        log("✓ L2 → L3 完成: 长期洞察", "INFO")
    else:
        log("无新洞察需要添加", "WARNING")

# ============================================================================
# 主流程
# ============================================================================

def main():
    """主流程"""
    log("="*50, "INFO")
    log("自动摘要生成系统", "INFO")
    log("="*50, "INFO")

    # L0 → L1
    process_l0_to_l1()

    # L1 → L2
    process_l1_to_l2()

    # L2 → L3
    process_l2_to_l3()

    log("="*50, "INFO")
    log("✓ 自动摘要生成完成", "INFO")
    log("="*50, "INFO")

# ============================================================================
# CLI 接口
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="自动摘要生成系统")
    parser.add_argument("--date", help="指定日期 (YYYY-MM-DD)")
    parser.add_argument("--month", help="指定月份 (YYYY-MM)")
    parser.add_argument("--layer", choices=["l1", "l2", "l3", "all"], default="all",
                       help="处理的层级: l1(L0→L1), l2(L1→L2), l3(L2→L3), all(全部)")

    args = parser.parse_args()

    if args.layer in ["l1", "all"]:
        process_l0_to_l1(args.date)

    if args.layer in ["l2", "all"]:
        process_l1_to_l2(args.month)

    if args.layer in ["l3", "all"]:
        process_l2_to_l3()
