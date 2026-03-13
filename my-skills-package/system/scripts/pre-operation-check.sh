#!/bin/bash
# 重要操作前检查脚本

OPERATION="$1"

echo "🚨 重要操作检查"
echo "================"
echo ""
echo "操作: $OPERATION"
echo ""
echo "⚠️  检查清单："
echo "  [ ] 用户说'确认后'了吗？"
echo "  [ ] 这个操作不可逆吗？"
echo "  [ ] 这个操作涉及外部系统吗？"
echo "  [ ] 我明确询问用户确认了吗？"
echo "  [ ] 我收到用户明确回复了吗？"
echo ""
echo "💡 如果任何一个答案是'是'，必须等待用户确认！"
echo ""
echo "❌ 违规后果：严重错误"
echo ""
