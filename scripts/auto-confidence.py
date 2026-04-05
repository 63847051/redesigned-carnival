#!/usr/bin/env python3
"""
自动置信度计算器 - Auto Confidence Calculator
功能: 基于历史对话自动计算 Retain 条目的置信度
作者: 大领导 🎯
创建: 2026-04-02
"""

import sys
import re
import json
import time
from pathlib import Path
from collections import Counter
from typing import List, Dict, Tuple

# =============================================================================
# 配置
# =============================================================================

MEMORY_DIR = Path("/root/.openclaw/workspace/memory")
MIN_CONFIDENCE = 0.5
MAX_CONFIDENCE = 1.0
OCCURRENCE_THRESHOLD = 3  # 出现 3 次以上 → 0.9 置信度

# =============================================================================
# 工具函数
# =============================================================================

def log_info(message: str):
    print(f"[INFO] {message}")

def log_success(message: str):
    print(f"[✓] {message}")

# =============================================================================
# 置信度计算
# =============================================================================

def calculate_confidence_from_history(statement: str, history_files: List[Path]) -> float:
    """基于历史对话计算置信度"""

    # 1. 检查出现频率
    occurrences = count_statement_occurrences(statement, history_files)

    if occurrences >= OCCURRENCE_THRESHOLD:
        return 0.9

    # 2. 检查是否有证据支持
    if has_supporting_evidence(statement, history_files):
        return 0.8

    # 3. 检查表述确定性
    certainty_score = check_certainty_keywords(statement)

    if certainty_score >= 0.8:
        return 0.8
    elif certainty_score >= 0.6:
        return 0.7
    else:
        return 0.6

def count_statement_occurrences(statement: str, history_files: List[Path]) -> int:
    """统计陈述在历史中出现的次数"""

    # 提取关键词
    keywords = extract_keywords(statement)

    if not keywords:
        return 0

    # 在历史文件中搜索
    count = 0
    for history_file in history_files:
        try:
            content = history_file.read_text(encoding='utf-8')
            for keyword in keywords:
                count += content.lower().count(keyword.lower())
        except Exception:
            continue

    return count

def has_supporting_evidence(statement: str, history_files: List[Path]) -> bool:
    """检查是否有证据支持"""

    evidence_keywords = [
        "测试通过", "验证成功", "实验证明", "数据显示",
        "实测", "实际运行", "生产环境", "上线后"
    ]

    for history_file in history_files:
        try:
            content = history_file.read_text(encoding='utf-8')
            for keyword in evidence_keywords:
                if keyword in content and any(kw in content for kw in extract_keywords(statement)):
                    return True
        except Exception:
            continue

    return False

def check_certainty_keywords(statement: str) -> float:
    """检查表述的确定性关键词"""

    high_certainty = ["确定", "肯定", "一定", "必须", "必然", "无疑"]
    medium_certainty = ["应该", "建议", "推荐", "通常", "一般", "基本"]
    low_certainty = ["可能", "也许", "或许", "大概", "估计", "应该"]

    statement_lower = statement.lower()

    for keyword in high_certainty:
        if keyword in statement_lower:
            return 0.9

    for keyword in medium_certainty:
        if keyword in statement_lower:
            return 0.7

    for keyword in low_certainty:
        if keyword in statement_lower:
            return 0.5

    return 0.7  # 默认中等

def extract_keywords(statement: str) -> List[str]:
    """从陈述中提取关键词"""

    # 移除常见的停用词
    stopwords = {"的", "了", "是", "在", "有", "和", "与", "或", "但", "而"}

    # 分词（简单实现，按空格和标点分割）
    words = re.findall(r'[\w]+', statement)

    # 过滤停用词和短词
    keywords = [w for w in words if len(w) > 1 and w not in stopwords]

    return keywords

# =============================================================================
# 主流程
# =============================================================================

def analyze_retain_confidence(retain_entries: List[Dict], history_files: List[Path]) -> List[Dict]:
    """分析 Retain 条目的置信度"""

    results = []

    for entry in retain_entries:
        if entry["type"] != "O":
            # 非 O 类型条目，置信度为 None
            results.append(entry)
            continue

        # 计算置信度
        confidence = calculate_confidence_from_history(entry["content"], history_files)

        # 更新置信度
        entry["confidence"] = confidence
        results.append(entry)

    return results

def get_recent_history(days: int = 30) -> List[Path]:
    """获取最近的历史日志"""

    history_files = []

    for log_file in MEMORY_DIR.glob("*.md"):
        # 跳过非日志文件
        if log_file.name in ["health-status.md", "cleanup-report.md", "audit-report.md"]:
            continue

        # 检查文件年龄
        mtime = log_file.stat().st_mtime
        import time
        age_days = (time.time() - mtime) / 86400

        if age_days <= days:
            history_files.append(log_file)

    return sorted(history_files, key=lambda x: x.stat().st_mtime, reverse=True)

def main():
    """主函数"""

    import sys

    if len(sys.argv) < 2:
        print("用法: python3 auto-confidence.py <Retain JSON 文件或内容>")
        sys.exit(1)

    # 读取 Retain 条目
    if input_arg == "-":
        retain_json = sys.stdin.read()
    elif Path(input_arg).exists():
        with open(input_arg, 'r', encoding='utf-8') as f:
            retain_json = f.read()
    else:
        retain_json = input_arg

    try:
        retain_entries = json.loads(retain_json)
    except json.JSONDecodeError:
        print("错误：无法解析 JSON")
        sys.exit(1)

    # 获取历史文件
    history_files = get_recent_history(days=30)

    log_info(f"分析 {len(retain_entries)} 个条目，使用 {len(history_files)} 个历史文件")

    # 分析置信度
    results = analyze_retain_confidence(retain_entries, history_files)

    # 输出结果
    print(json.dumps(results, indent=2, ensure_ascii=False))

    # 统计
    o_entries = [e for e in results if e["type"] == "O"]
    if o_entries:
        avg_confidence = sum(e["confidence"] for e in o_entries) / len(o_entries)
        log_success(f"平均置信度: {avg_confidence:.2f}")

if __name__ == "__main__":
    main()
