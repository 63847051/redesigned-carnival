#!/bin/bash
# 记忆搜索检查清单
# 确保每次对话前都能找到相关的历史记忆

echo "🔍 记忆搜索检查清单"
echo "===================="
echo ""

# 检查 1: QMD 索引是否最新
echo "📋 检查 1: QMD 索引状态"
if qmd status | grep -q "Indexed:.*0 new"; then
    echo "✅ 索引是最新的"
else
    echo "⚠️  索引需要更新"
    echo "   运行: qmd update"
fi
echo ""

# 检查 2: Embeddings 是否生成
echo "📋 检查 2: Embeddings 状态"
EMBED_COUNT=$(qmd status 2>/dev/null | grep "Embedded:" | awk '{print $2}')
if [ "$EMBED_COUNT" != "0" ]; then
    echo "✅ 已生成 $EMBED_COUNT 个 embeddings"
else
    echo "⚠️  需要生成 embeddings"
    echo "   运行: qmd embed"
fi
echo ""

# 检查 3: 测试搜索功能
echo "📋 检查 3: 搜索功能测试"
echo "   测试搜索 '记忆'..."
if qmd-search "记忆" >/dev/null 2>&1; then
    echo "✅ 搜索功能正常"
else
    echo "❌ 搜索功能异常"
fi
echo ""

# 提示：对话前应该做什么
echo "💡 对话前建议："
echo "   1. 使用 qmd-search 搜索相关历史"
echo "   2. 查看搜索结果"
echo "   3. 根据结果调整回答"
echo ""

# 快速搜索命令
echo "🚀 快速搜索："
echo "   qmd-search \"关键词\""
echo ""
