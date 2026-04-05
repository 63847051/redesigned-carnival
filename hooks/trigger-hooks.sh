#!/bin/bash
###############################################################################
# 手动触发 Hooks
###############################################################################

echo "🔧 手动触发 Hooks"
echo ""

# 触发 SessionStart
echo "## 🚀 触发 SessionStart Hook"
bash /root/.openclaw/workspace/hooks/session-start.sh
echo ""

# 触发 SessionEnd
echo "## 🏁 触发 SessionEnd Hook"
bash /root/.openclaw/workspace/hooks/session-end.sh
echo ""

echo "✅ Hooks 触发完成"
