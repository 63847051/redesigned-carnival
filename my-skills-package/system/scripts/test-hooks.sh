#!/bin/bash
# 测试 Hook 系统
# 验证所有 Hook 是否正常工作

echo "🧪 测试 Hook 系统"
echo "=================="
echo ""

HOOKS_DIR="/root/.openclaw/workspace/.learnings/hooks"

# 测试 1: Session Start Hook
echo "📋 测试 1: Session Start Hook"
/root/.openclaw/workspace/scripts/hooks/session-start.sh
echo ""

# 测试 2: User Prompt Hook
echo "📋 测试 2: User Prompt Hook"
/root/.claw/workspace/scripts/hooks/user-prompt.sh "测试输入"
echo ""

# 测试 3: Tool Use Hook
echo "📋 测试 3: Tool Use Hook"
/root/.openclaw/workspace/scripts/hooks/tool-use.sh "ls" "ls -la" "0"
echo ""

# 测试 4: Session End Hook
echo "📋 测试 4: Session End Hook"
/root/.openclaw/workspace/scripts/hooks/session-end.sh
echo ""

echo "✅ 所有 Hook 测试完成！"
echo ""
echo "📊 日志位置: $HOOKS_DIR/"
echo "📋 今日日志:"
ls -lh "$HOOKS_DIR/" 2>/dev/null | tail -5
