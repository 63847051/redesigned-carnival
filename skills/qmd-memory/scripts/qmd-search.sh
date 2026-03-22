#!/bin/bash
# QMD Memory Search - 快速记忆检索工具
# 使用方法: qmd-search "搜索关键词"

set -e

# 检查参数
if [ $# -eq 0 ]; then
    echo "❌ 错误: 请提供搜索关键词"
    echo ""
    echo "使用方法:"
    echo "  qmd-search \"关键词\"        # 全文搜索"
    echo "  qmd-search \"自然语言问题\"  # 智能搜索"
    echo ""
    echo "示例:"
    echo "  qmd-search \"蓝色光标\""
    echo "  qmd-search \"幸运小行星的工作风格\""
    exit 1
fi

QUERY="$*"
COLLECTION="memory"

echo "🔍 搜索: \"$QUERY\""
echo ""

# 优先使用全文搜索（快速可靠）
echo "📄 使用全文搜索（BM25）"
echo ""

# 使用 search 命令（不触发编译）
qmd search "$COLLECTION" "$QUERY" 2>/dev/null || {
    echo "❌ 搜索失败"
    echo ""
    echo "提示:"
    echo "  - 检查查询关键词"
    echo "  - 确认 collection 存在: qmd collection list"
    exit 1
}

echo ""
echo "✅ 搜索完成"
