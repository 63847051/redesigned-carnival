#!/bin/bash
# 时间戳计算辅助脚本
# 用途：准确计算日期对应的毫秒时间戳，避免手动计算错误
# 创建时间：2026-03-06
# 原因：防止重复犯日期时间戳计算错误

show_usage() {
    echo "📅 时间戳计算辅助工具"
    echo ""
    echo "用法："
    echo "  $0 <年份> <月份> <日期>"
    echo ""
    echo "示例："
    echo "  $0 2026 3 6       # 计算 2026年3月6日 00:00:00 的时间戳"
    echo "  $0 2024 3 6       # 计算 2024年3月6日 00:00:00 的时间戳"
    echo ""
    echo "输出格式："
    echo "  - 日期：YYYY-MM-DD"
    echo "  - 时间戳（毫秒）：13位数字"
    echo "  - 验证：显示时间戳对应的日期"
    echo ""
}

if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_usage
    exit 0
fi

if [ $# -ne 3 ]; then
    echo "❌ 错误：需要3个参数（年 月 日）"
    echo ""
    show_usage
    exit 1
fi

YEAR=$1
MONTH=$2
DAY=$3

# 验证参数格式
if ! [[ "$YEAR" =~ ^[0-9]{4}$ ]] || ! [[ "$MONTH" =~ ^[0-9]{1,2}$ ]] || ! [[ "$DAY" =~ ^[0-9]{1,2}$ ]]; then
    echo "❌ 错误：参数格式不正确"
    echo "   年份：4位数字（如：2026）"
    echo "   月份：1-2位数字（如：3 或 03）"
    echo "   日期：1-2位数字（如：6 或 06）"
    exit 1
fi

# 构造日期字符串（确保两位数格式）
DATE_STRING=$(printf "%04d-%02d-%02d 00:00:00" $YEAR $MONTH $DAY)

# 计算时间戳（毫秒）
TIMESTAMP_MS=$(date -d "$DATE_STRING" +%s)000
TIMESTAMP_S=$(date -d "$DATE_STRING" +%s)

# 验证时间戳
VERIFY_DATE=$(date -d @$TIMESTAMP_S +%Y-%m-%d)

# 显示结果
echo "✅ 时间戳计算完成"
echo ""
echo "📅 输入日期：$DATE_STRING"
echo "⏱️  时间戳（毫秒）：$TIMESTAMP_MS"
echo "⏱️  时间戳（秒）：$TIMESTAMP_S"
echo "🔍 验证日期：$VERIFY_DATE"
echo ""

# 验证一致性
if [ "$VERIFY_DATE" = "$(printf "%04d-%02d-%02d" $YEAR $MONTH $DAY)" ]; then
    echo "✅ 验证通过：时间戳正确"
    echo ""
    echo "📋 复制使用："
    echo "   毫秒时间戳：$TIMESTAMP_MS"
else
    echo "❌ 验证失败：时间戳不匹配"
    exit 1
fi
