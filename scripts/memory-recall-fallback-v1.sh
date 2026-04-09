#!/bin/bash
# 记忆召回降级策略 v1.0
# 基于 Claude Code 设计：多层防御，确保总能找到相关信息

set -e

echo "🔍 记忆召回降级策略 v1.0"
echo "⏰ 时间: $(date)"

# 配置
MEMORY_DIR="/root/.openclaw/workspace/memory"
QUERY="$1"

# =============================================================================
# 🎯 三层降级策略
# =============================================================================

level1_keyword_search() {
    echo ""
    echo "🔍 第一层：keyword 搜索（快速）"
    
    # 使用 tdai_memory_search
    echo "📊 查询: $QUERY"
    
    # 调用记忆搜索
    # 注意：这里需要调用实际的 tdai_memory_search
    # 暂时用 grep 模拟
    grep -r "$QUERY" "$MEMORY_DIR"/*.md 2>/dev/null | head -5
}

level2_conversation_search() {
    echo ""
    echo "🔍 第二层：conversation 搜索（较慢）"
    
    # 使用 tdai_conversation_search
    echo "📊 查询: $QUERY"
    
    # 调用对话搜索
    # 注意：这里需要调用实际的 tdai_conversation_search
    # 暂时用 grep 模拟
    grep -r "$QUERY" "$MEMORY_DIR"/conversations/ 2>/dev/null | head -5
}

level3_full_grep() {
    echo ""
    echo "🔍 第三层：全文 grep（最慢，但最全面）"
    
    echo "📊 查询: $QUERY"
    
    # 全文 grep
    grep -r "$QUERY" "$MEMORY_DIR"/*.md 2>/dev/null
}

# =============================================================================
# 🚀 主流程
# =============================================================================

main() {
    if [ -z "$QUERY" ]; then
        echo "❌ 请提供查询词"
        echo "用法: $0 <查询词>"
        exit 1
    fi
    
    echo ""
    echo "🚀 启动三层降级策略..."
    
    # 第一层：keyword 搜索
    echo "======================================"
    level1_keyword_search
    
    # 检查是否找到结果
    RESULT_COUNT=$(grep -r "$QUERY" "$MEMORY_DIR"/*.md 2>/dev/null | wc -l)
    
    if [ $RESULT_COUNT -gt 0 ]; then
        echo ""
        echo "✅ 第一层找到 $RESULT_COUNT 条结果"
        echo "💡 提示：keyword 搜索是最快的，适用于常用查询"
        exit 0
    fi
    
    # 第二层：conversation 搜索
    echo "======================================"
    level2_conversation_search
    
    # 检查是否找到结果
    RESULT_COUNT=$(grep -r "$QUERY" "$MEMORY_DIR"/conversations/ 2>/dev/null | wc -l)
    
    if [ $RESULT_COUNT -gt 0 ]; then
        echo ""
        echo "✅ 第二层找到 $RESULT_COUNT 条结果"
        echo "💡 提示：conversation 搜索包括完整对话内容"
        exit 0
    fi
    
    # 第三层：全文 grep
    echo "======================================"
    level3_full_grep
    
    # 检查是否找到结果
    RESULT_COUNT=$(grep -r "$QUERY" "$MEMORY_DIR"/*.md 2>/dev/null | wc -l)
    
    if [ $RESULT_COUNT -gt 0 ]; then
        echo ""
        echo "✅ 第三层找到 $RESULT_COUNT 条结果"
        echo "💡 提示：全文 grep 最全面，但最慢"
        exit 0
    fi
    
    echo ""
    echo "❌ 三层都未找到结果"
    echo "💡 提示：尝试调整查询词或扩大搜索范围"
}

# 执行主流程
main "$@"
