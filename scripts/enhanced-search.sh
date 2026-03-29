#!/bin/bash
# 增强版集成搜索 - 包含预处理层
# 使用方法: bash scripts/enhanced-search.sh "查询内容"

set -e

QUERY="$*"

if [ -z "$QUERY" ]; then
    echo "❌ 错误: 请提供搜索查询"
    echo ""
    echo "使用方法:"
    echo "  bash scripts/enhanced-search.sh \"查询内容\""
    echo ""
    echo "示例:"
    echo "  bash scripts/enhanced-search.sh \"昨天的问题\""
    exit 1
fi

echo "🔍 增强搜索: \"$QUERY\""
echo ""

# Step 1: 查询预处理
echo "Step 1: 查询预处理..."
PREPROCESS_RESULT=$(python3 /root/.openclaw/workspace/scripts/query-preprocessor.py --query "$QUERY")

# 提取扩展查询
EXPANDED_QUERIES=$(echo "$PREPROCESS_RESULT" | grep "扩展查询:" -A 10 | grep "^[0-9]" | awk '{print $2}' | head -3)

echo "   原始查询: $QUERY"
echo "   扩展查询: $EXPANDED_QUERIES"

# Step 2: 执行搜索
echo ""
echo "Step 2: 执行搜索..."

ALL_RESULTS=""

for subquery in $QUERY $EXPANDED_QUERIES; do
    if [ -n "$subquery" ]; then
        echo "   搜索: \"$subquery\""
        RESULT=$(qmd search memory "$subquery" 2>&1 | grep "qmd://" | head -3)
        
        if [ -n "$RESULT" ]; then
            echo "   ✅ 找到结果"
            ALL_RESULTS="$ALL_RESULTS
$RESULT"
        else
            echo "   ❌ 未找到"
        fi
    fi
done

# Step 3: 显示结果
echo ""
echo "📊 搜索结果："
echo "=================================="

if [ -n "$ALL_RESULTS" ]; then
    echo "$ALL_RESULTS" | grep "qmd://" | sort -u
else
    echo "未找到相关结果"
fi

echo ""
echo "✅ 搜索完成"
echo ""
echo "💡 提示:"
echo "  - 查询预处理: python3 scripts/query-preprocessor.py --query \"$QUERY\""
echo "  - 同义词扩展: python3 scripts/synonym-expander.py --query \"$QUERY\""
echo "  - 推理式检索: python3 scripts/reasoning-retriever.py --query \"$QUERY\""
