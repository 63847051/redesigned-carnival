#!/bin/bash
# 集成搜索系统 - QMD + 推理式检索
# 使用方法: bash scripts/integrated-search.sh "查询内容"

set -e

QUERY="$*"

if [ -z "$QUERY" ]; then
    echo "❌ 错误: 请提供搜索查询"
    echo ""
    echo "使用方法:"
    echo "  bash scripts/integrated-search.sh \"查询内容\""
    echo ""
    echo "示例:"
    echo "  bash scripts/integrated-search.sh \"记忆系统优化\""
    exit 1
fi

echo "🔍 集成搜索: \"$QUERY\""
echo ""

# Step 1: QMD 快速搜索
echo "Step 1: QMD 向量搜索..."
QMD_RESULTS=$(qmd search memory "$QUERY" 2>&1 | head -20)
QMD_COUNT=$(echo "$QMD_RESULTS" | grep -c "qmd://" || echo "0")

echo "   找到 $QMD_COUNT 条结果"

# Step 2: 推理式检索（可选）
if [ "$QMD_COUNT" -gt 0 ]; then
    echo ""
    echo "Step 2: 推理式检索（可选）..."
    echo "   提示: 使用 python3 scripts/reasoning-retriever.py --query \"$QUERY\""
fi

# Step 3: 显示结果
echo ""
echo "📊 搜索结果："
echo "=================================="
echo "$QMD_RESULTS"
echo ""
echo "✅ 搜索完成"
echo ""
echo "💡 提示:"
echo "  - 使用推理式检索: python3 scripts/reasoning-retriever.py --query \"$QUERY\""
echo "  - 查看文件: qmd-get memory/<file-path>"
