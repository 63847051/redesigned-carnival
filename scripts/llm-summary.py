#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 驱动的记忆摘要生成
使用 GLM-4.5-Air（免费）实现智能摘要
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
MEMORY_KEY_POINTS = MEMORY_DIR / "key-points"
MEMORY_STRUCTURED = MEMORY_DIR / "structured"
MEMORY_FILE = WORKSPACE / "MEMORY.md"
LOG_FILE = MEMORY_DIR / ".llm-summary.log"

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
# LLM 接口（使用 GLM-4.5-Air）
# ============================================================================

def call_llm(prompt: str, max_tokens: int = 1000) -> str:
    """
    调用 GLM-4.5-Air（免费模型）
    """
    try:
        # 检查 API Key
        api_key = os.getenv("GLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            log("未找到 GLM_API_KEY，使用规则提取", "WARNING")
            return _rule_based_extraction(prompt)
        
        # 使用 OpenAI 兼容接口
        from openai import OpenAI
        
        client = OpenAI(
            base_url="https://open.bigmodel.cn/api/anthropic",
            api_key=api_key
        )
        
        log(f"调用 GLM-4.5-Air（prompt: {len(prompt)} 字符）", "DEBUG")
        
        response = client.chat.completions.create(
            model="glmcode/glm-4.5-air",
            messages=[
                {
                    "role": "system",
                    "content": """你是一个专业的文本分析助手，擅长：
1. 提取关键信息（事件、决策、行动项）
2. 分类内容（人物、项目、知识、偏好）
3. 总结提炼（洞察、模式、经验）

请用简洁、准确的方式完成任务。只返回结果，不要有多余的废话。"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=max_tokens,
            temperature=0.3
        )
        
        result = response.choices[0].message.content.strip()
        log(f"GLM-4.5-Air 返回: {len(result)} 字符", "DEBUG")
        return result
        
    except ImportError:
        log("openai 库未安装，使用规则提取", "WARNING")
        return _rule_based_extraction(prompt)
        
    except Exception as e:
        log(f"GLM 调用失败: {e}，使用规则提取", "WARNING")
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
                       "创建" in line or "实施" in line or "优化" in line):
                results.append(line)
        return "\n".join(results[:15]) if results else "无关键点"
    
    # 提取项目相关
    elif "项目" in prompt or "project" in prompt.lower():
        for line in lines:
            if "项目" in line or "任务" in line or "开发" in line or "实施" in line or "优化" in line:
                results.append(line.strip())
        return "\n".join(results[:8]) if results else "无项目相关"
    
    # 提取人物相关
    elif "幸运小行星" in prompt or "用户" in prompt or "people" in prompt.lower():
        for line in lines:
            if "幸运小行星" in line or "用户" in line or "客户" in line:
                results.append(line.strip())
        return "\n".join(results[:8]) if results else "无人物相关"
    
    # 提取知识相关
    elif "知识" in prompt or "学习" in prompt or "knowledge" in prompt.lower():
        for line in lines:
            if "学习" in line or "研究" in line or "分析" in line or "发现" in line or "洞察" in line:
                results.append(line.strip())
        return "\n".join(results[:8]) if results else "无知识相关"
    
    # 提取洞察
    elif "洞察" in prompt or "insight" in prompt.lower():
        for line in lines:
            if "洞察" in line or "发现" in line or "教训" in line or "经验" in line or "核心" in line:
                results.append(line.strip())
        return "\n".join(results[:5]) if results else "无明显洞察"
    
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

要求：
1. 只返回关键点列表，每行一个
2. 关键点应该包括：重要事件、决策、行动项
3. 简洁明了，不超过20字每条

格式：
- 关键点1
- 关键点2
..."""
        key_points = call_llm(prompt, max_tokens=800)

        return {
            "date": date,
            "key_points": key_points,
            "source_file": str(daily_file)
        }

    except Exception as e:
        log(f"处理失败: {e}", "ERROR")
        return None

# ============================================================================
# 主流程（与原版保持一致）
# ============================================================================

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

# 其他函数与原版保持一致...

if __name__ == "__main__":
    import argparse
    from datetime import timedelta

    parser = argparse.ArgumentParser(description="LLM 驱动的记忆摘要生成")
    parser.add_argument("--date", help="指定日期 (YYYY-MM-DD)")
    parser.add_argument("--test-llm", action="store_true", help="测试 LLM 连接")

    args = parser.parse_args()

    if args.test_llm:
        # 测试 LLM
        log("测试 GLM-4.5-Air 连接...", "INFO")
        test_prompt = "请简单介绍一下你自己"
        result = call_llm(test_prompt, max_tokens=200)
        log(f"LLM 返回: {result}", "INFO")
    else:
        # 处理 L0 → L1
        process_l0_to_l1(args.date)
