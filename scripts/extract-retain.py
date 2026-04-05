#!/usr/bin/env python3
"""
Retain 自动提取脚本 - Auto Extract Retain Entries
功能: 从对话内容中自动提取 W/B/O 条目
作者: 大领导 🎯
创建: 2026-04-02
"""

import re
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple

# =============================================================================
# 配置
# =============================================================================

MEMORY_DIR = Path("/root/.openclaw/workspace/memory")
TODAY_LOG = MEMORY_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"

# Retain 条目模式
PATTERNS = {
    "W": [
        r"(?:不支持|不支持用|必须使用|不能用|需要用|不能用|限制)",
        r"(?:API|接口|平台|系统|配置)\s*(?:不支持|不支持用|必须|要求)",
        r"(?:服务器|IP|地址|路径|端口)\s*[是为]\s*[0-9a-zA-Z\.:/]+",
        r"(?:版本|v\.?)\s*[0-9]+\.[0-9]+",
    ],
    "B": [
        r"(?:完成|创建|更新|删除|添加)\s*(?:了|脚本|文档|文件|工具)",
        r"(?:Step\s*\d+|任务)\s*(?:完成|进行中|暂停)",
        r"(?:安装|部署|配置)\s*(?:成功|完成)",
        r"(?:测试|验证)\s*(?:通过|成功|失败)",
    ],
    "O": [
        r"(?:认为|建议|觉得)\s*(?:应该|最好|需要)",
        r"(?:更好|更优|推荐)\s*(?:的方案|的方法|的方式)",
        r"(?:原则|策略|方向)\s*(?:是|应该是)",
    ]
}

# 关键词权重
KEYWORD_WEIGHTS = {
    # W 关键词
    "不支持": 0.9, "不支持用": 0.9, "必须使用": 0.9, "不能用": 0.9,
    "API": 0.7, "接口": 0.7, "平台": 0.6,
    # B 关键词
    "完成": 0.8, "创建": 0.8, "更新": 0.7, "测试": 0.7,
    "任务": 0.6, "脚本": 0.6, "文档": 0.6,
    # O 关键词
    "认为": 0.7, "建议": 0.8, "觉得": 0.6,
    "更好": 0.7, "推荐": 0.8,
}

# 域名映射
DOMAIN_MAPPING = {
    "API": "API",
    "接口": "API",
    "飞书": "飞书API",
    "记忆": "记忆系统",
    "日志": "日志管理",
    "脚本": "工具脚本",
    "文档": "文档编写",
    "系统": "系统配置",
    "代码": "代码开发",
    "项目": "项目管理",
}

# =============================================================================
# 工具函数
# =============================================================================

def log_info(message: str):
    print(f"[INFO] {message}", file=sys.stderr)

def log_success(message: str):
    print(f"[✓] {message}", file=sys.stderr)

def log_warning(message: str):
    print(f"[!] {message}", file=sys.stderr)

def log_error(message: str):
    print(f"[✗] {message}", file=sys.stderr)

# =============================================================================
# 提取函数
# =============================================================================

def extract_domain(text: str) -> str:
    """从文本中提取域（领域）"""
    for keyword, domain in DOMAIN_MAPPING.items():
        if keyword in text:
            return domain

    # 默认域
    if "API" in text or "接口" in text:
        return "API"
    elif "系统" in text:
        return "系统"
    elif "脚本" in text or "工具" in text:
        return "工具"
    else:
        return "通用"

def extract_confidence(text: str, entry_type: str) -> float:
    """提取信心度（仅 O 类型）"""
    if entry_type != "O":
        return None

    # 高信心度指标
    if any(word in text for word in ["确定", "肯定", "一定", "必须"]):
        return 0.9
    elif any(word in text for word in ["应该", "建议", "推荐"]):
        return 0.8
    elif any(word in text for word in ["可能", "也许", "或许"]):
        return 0.6
    else:
        return 0.7  # 默认

def classify_entry(text: str) -> Tuple[str, float]:
    """分类条目类型并计算权重"""
    scores = {"W": 0.0, "B": 0.0, "O": 0.0}

    # 基于关键词计算分数
    for keyword, weight in KEYWORD_WEIGHTS.items():
        if keyword in text:
            # 确定关键词属于哪一类
            if keyword in ["不支持", "不支持用", "必须使用", "不能用", "API", "接口", "平台"]:
                scores["W"] += weight
            elif keyword in ["完成", "创建", "更新", "测试", "任务", "脚本", "文档"]:
                scores["B"] += weight
            elif keyword in ["认为", "建议", "觉得", "更好", "推荐"]:
                scores["O"] += weight

    # 基于模式匹配
    for entry_type, patterns in PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                scores[entry_type] += 0.5

    # 返回得分最高的类型
    max_type = max(scores, key=scores.get)
    max_score = scores[max_type]

    if max_score == 0:
        return None, 0.0

    return max_type, max_score

def extract_entries_from_text(text: str) -> List[Dict]:
    """从文本中提取 Retain 条目"""
    entries = []

    # 分割为句子
    sentences = re.split(r'[。！？\n]', text)

    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 5:  # 跳过太短的句子
            continue

        # 分类
        entry_type, score = classify_entry(sentence)

        if entry_type is None or score < 0.5:
            continue

        # 提取域
        domain = extract_domain(sentence)

        # 提取信心度
        confidence = extract_confidence(sentence, entry_type)

        entries.append({
            "type": entry_type,
            "domain": domain,
            "content": sentence,
            "confidence": confidence,
            "score": score,
        })

    return entries

def deduplicate_entries(entries: List[Dict]) -> List[Dict]:
    """去重相似的条目"""
    unique_entries = []

    for entry in entries:
        is_duplicate = False

        for existing in unique_entries:
            # 检查类型和域是否相同
            if entry["type"] == existing["type"] and entry["domain"] == existing["domain"]:
                # 检查内容相似度
                content_words = set(entry["content"])
                existing_words = set(existing["content"])

                overlap = len(content_words & existing_words)
                min_len = min(len(content_words), len(existing_words))

                if overlap / min_len > 0.6:  # 60% 相似度
                    is_duplicate = True
                    # 保留得分更高的
                    if entry["score"] > existing["score"]:
                        unique_entries.remove(existing)
                        unique_entries.append(entry)
                    break

        if not is_duplicate:
            unique_entries.append(entry)

    return unique_entries

def format_retain_entry(entry: Dict) -> str:
    """格式化 Retain 条目"""
    entry_type = entry["type"]
    domain = entry["domain"]
    content = entry["content"]
    confidence = entry["confidence"]

    if entry_type == "O" and confidence is not None:
        return f"- {entry_type}(c={confidence}) @{domain}: {content}"
    else:
        return f"- {entry_type} @{domain}: {content}"

def categorize_entries(entries: List[Dict]) -> Dict[str, List[Dict]]:
    """按类型分类条目"""
    categorized = {"W": [], "B": [], "O": []}

    for entry in entries:
        entry_type = entry["type"]
        categorized[entry_type].append(entry)

    return categorized

# =============================================================================
# 主流程
# =============================================================================

def extract_retain_from_conversation(conversation_text: str) -> str:
    """从对话中提取 Retain 条目"""
    # 提取条目
    entries = extract_entries_from_text(conversation_text)

    if not entries:
        log_warning("未找到可提取的 Retain 条目")
        return ""

    # 去重
    entries = deduplicate_entries(entries)

    # 分类
    categorized = categorize_entries(entries)

    # 生成 Retain 段落
    retain_lines = []
    retain_lines.append("## 🧠 Retain - 结构化记忆提取\n")
    retain_lines.append("### 世界知识 (W) - World Facts\n")
    retain_lines.append("_客观的、持久的事实性知识_\n")

    for entry in categorized["W"]:
        retain_lines.append(format_retain_entry(entry))

    retain_lines.append("\n### 行为记录 (B) - Behavior\n")
    retain_lines.append("_Agent 执行的具体行动和项目进展_\n")

    for entry in categorized["B"]:
        retain_lines.append(format_retain_entry(entry))

    retain_lines.append("\n### 观点偏好 (O) - Opinions\n")
    retain_lines.append("_带主观判断的观点、偏好、趋势观察_\n")

    for entry in categorized["O"]:
        retain_lines.append(format_retain_entry(entry))

    return "\n".join(retain_lines)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        log_error("用法: python3 extract-retain.py <对话文本文件或内容>")
        sys.exit(1)

    # 读取输入
    input_arg = sys.argv[1]

    if input_arg == "-":
        # 从标准输入读取
        conversation_text = sys.stdin.read()
    else:
        # 尝试判断是文件还是文本
        try:
            # 如果输入较短且看起来像文件路径，尝试作为文件读取
            if len(input_arg) < 256 and '\n' not in input_arg:
                input_path = Path(input_arg)
                if input_path.exists() and input_path.is_file():
                    with open(input_arg, 'r', encoding='utf-8') as f:
                        conversation_text = f.read()
                else:
                    # 不是文件，直接作为文本
                    conversation_text = input_arg
            else:
                # 输入较长或包含换行，直接作为文本
                conversation_text = input_arg
        except (OSError, ValueError):
            # 出错时直接作为文本
            conversation_text = input_arg

    # 提取 Retain
    retain_text = extract_retain_from_conversation(conversation_text)

    if not retain_text:
        log_warning("未提取到 Retain 条目")
        sys.exit(0)

    # 输出
    print(retain_text)

    # 统计
    entries = extract_entries_from_text(conversation_text)
    entries = deduplicate_entries(entries)
    categorized = categorize_entries(entries)

    log_success(f"提取完成: W={len(categorized['W'])}, B={len(categorized['B'])}, O={len(categorized['O'])}")

if __name__ == "__main__":
    main()
