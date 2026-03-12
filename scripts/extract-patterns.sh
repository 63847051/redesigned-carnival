#!/bin/bash
# 提取错误模式脚本

set -e

echo "🔍 错误模式分析"
echo ""

cd .learnings/errors/ 2>/dev/null || {
    echo "📁 错误目录不存在，暂无错误记录"
    exit 0
}

# 统计错误类型
echo "📊 错误统计:"
echo "总错误数: $(ls -1 *.md 2>/dev/null | wc -l)"
echo ""

# 提取模式
echo "🔍 错误模式:"
if ls *.md 1> /dev/null 2>&1; then
    for file in *.md; do
        echo "- ${file}"
    done
else
    echo "暂无错误"
fi

echo ""
echo "✅ 模式提取完成"
