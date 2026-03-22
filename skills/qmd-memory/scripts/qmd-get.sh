#!/bin/bash
# QMD Memory Get - 快速查看记忆文件
# 使用方法: qmd-get <file>[:line]

set -e

# 检查参数
if [ $# -eq 0 ]; then
    echo "❌ 错误: 请提供文件路径"
    echo ""
    echo "使用方法:"
    echo "  qmd-get <file>              # 查看完整文件"
    echo "  qmd-get <file>:<line>       # 从指定行开始查看"
    echo ""
    echo "示例:"
    echo "  qmd-get memory/long-term/people/lucky-asteroid.md"
    echo "  qmd-get memory/long-term/people/lucky-asteroid.md:10"
    exit 1
fi

FILE_PATH="$1"

echo "📖 查看文件: $FILE_PATH"
echo ""

# 使用 qmd get 命令
qmd get "$FILE_PATH" 2>/dev/null || {
    echo "❌ 错误: 无法读取文件"
    echo ""
    echo "提示:"
    echo "  - 检查文件路径是否正确"
    echo "  - 使用 qmd-search 搜索文件"
    exit 1
}

echo ""
echo "✅ 读取完成"
