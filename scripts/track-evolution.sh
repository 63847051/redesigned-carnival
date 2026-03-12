#!/bin/bash
# 进化追踪脚本

set -e

echo "📊 进化追踪统计"
echo ""

# 错误统计
ERRORS=$(ls -1 .learnings/errors/*.md 2>/dev/null | wc -l)
echo "❌ 错误记录: ${ERRORS} 个"

# 模式统计
PATTERNS=$(ls -1 .learnings/patterns/*.md 2>/dev/null | wc -l)
echo "🧠 提取模式: ${PATTERNS} 个"

# 资产统计
ASSETS=$(ls -1 .evomap/*.md 2>/dev/null | wc -l)
echo "🌟 EvoMap 资产: ${ASSETS} 个"

# 设计模式统计
DESIGN=$(ls -1 .learnings/design-patterns/*.md 2>/dev/null | wc -l)
echo "📐 设计模式: ${DESIGN} 个"

echo ""
echo "✅ 进化追踪完成"
