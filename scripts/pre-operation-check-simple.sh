#!/bin/bash
# pre-operation-check.sh - 操作前检查脚本
# Token 成本: ~100 tokens (输出)
# 用途: 重要操作前的强制检查

OPERATION_NAME="$1"

echo "🔍 操作前检查: $OPERATION_NAME"
echo "================"

# 检查清单（5项）
echo ""
echo "请检查以下 5 项："
echo ""
echo "1. ✅ 或 ❌ 用户明确说了确认词吗？"
echo "   (确认词: 确认、确认执行、开始实施、执行)"
echo ""
echo "2. ✅ 或 ❌ 我明确询问用户确认了吗？"
echo ""
echo "3. ✅ 或 ❌ 我收到了用户的明确回复吗？"
echo ""
echo "4. ✅ 或 ❌ 这个操作是用户要求的吗？"
echo ""
echo "5. ✅ 或 ❌ 我理解正确了吗？"
echo ""
echo "================"
echo ""
echo "⚠️ 如果全部是 ✅，可以继续执行"
echo "⚠️ 如果有任何 ❌，立即停止，询问确认"
echo ""
echo "等待手动确认..."
