#!/bin/bash
# 安全的 Git 推送脚本

echo "🚨 Git 推送 - 安全检查"
echo "======================"
echo ""

# 执行操作前检查
bash /root/.openclaw/workspace/scripts/pre-operation-check.sh "git push"

echo ""
echo "⚠️  是否已获得用户明确确认？"
echo "  - 用户说'确认'或'可以'了吗？"
echo "  - 用户明确回复了吗？"
echo ""
echo "如果答案是'是'，执行："
echo "  git push $@"
echo ""
echo "如果答案是'否'，立即停止！"
