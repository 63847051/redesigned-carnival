#!/bin/bash
# QMD Memory Multi-Get - 批量查看记忆文件
# 使用方法: qmd-multi <pattern>

set -e

# 检查参数
if [ $# -eq 0 ]; then
    echo "❌ 错误: 请提供文件模式"
    echo ""
    echo "使用方法:"
    echo "  qmd-multi <pattern>          # 批量查看文件"
    echo ""
    echo "示例:"
    echo "  qmd-multi \"memory/**/*.md\""
    echo "  qmd-multi \"memory/long-term/**/*.md\""
    echo "  qmd-multi \"memory/2026-03-*.md\""
    exit 1
fi

PATTERN="$*"

echo "📚 批量查看: $PATTERN"
echo ""

# 使用 qmd multi-get 命令
qmd multi-get "$PATTERN" 2>/dev/null || {
    echo "❌ 错误: 无法批量读取文件"
    echo ""
    echo "提示:"
    echo "  - 检查文件模式是否正确"
    echo "  - 使用 qmd-search 搜索文件"
    exit 1
}

echo ""
echo "✅ 批量读取完成"
