#!/bin/bash
# 智能搜索 - 多策略搜索
# 使用方法: bash scripts/smart-search.sh "查询内容"

set -e

QUERY="$*"

if [ -z "$QUERY" ]; then
    echo "❌ 错误: 请提供搜索查询"
    echo ""
    echo "使用方法:"
    echo "  bash scripts/smart-search.sh \"查询内容\""
    echo ""
    echo "示例:"
    echo "  bash scripts/smart-search.sh \"昨天的问题\""
    exit 1
fi

echo "🔍 智能搜索: \"$QUERY\""
echo ""

# Step 1: 预处理查询
echo "Step 1: 预处理查询..."
PREPROCESS=$(python3 /root/.openclaw/workspace/scripts/query-preprocessor.py --query "$QUERY")

# 提取日期
DATE=$(echo "$PREPROCESS" | grep "date:" | awk '{print $2}')

if [ -n "$DATE" ]; then
    echo "   检测到日期: $DATE"
    
    # 策略 1: 直接搜索日期文件
    echo ""
    echo "Step 2: 搜索日期文件..."
    if [ -f "/root/.openclaw/workspace/memory/$DATE.md" ]; then
        echo "   ✅ 找到文件: memory/$DATE.md"
        echo ""
        echo "📄 文件内容："
        echo "=================================="
        head -50 /root/.openclaw/workspace/memory/$DATE.md
        echo ""
        echo "=================================="
        echo "✅ 搜索完成"
        exit 0
    else
        echo "   ❌ 文件不存在"
    fi
fi

# 策略 2: QMD 搜索
echo ""
echo "Step 3: QMD 搜索..."
RESULT=$(qmd search memory "$QUERY" 2>&1 | grep "qmd://" | head -5)

if [ -n "$RESULT" ]; then
    echo "   ✅ 找到结果"
    echo ""
    echo "📊 搜索结果："
    echo "=================================="
    echo "$RESULT"
    echo ""
    echo "=================================="
    echo "✅ 搜索完成"
else
    echo "   ❌ 未找到结果"
fi

echo ""
echo "💡 提示:"
echo "  - 如果搜索日期，请使用格式: 2026-03-28"
echo "  - 如果搜索内容，请使用关键词"
echo "  - 查看所有记忆文件: ls memory/"
