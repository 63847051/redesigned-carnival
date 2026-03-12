#!/bin/bash
# 扩展 Hook 系统测试
# 测试所有 8 个 Hook + 路由系统 + 信号分析

echo "🧪 扩展 Hook 系统测试"
echo "====================="
echo ""

HOOKS_DIR="/root/.openclaw/workspace/scripts/hooks"
LEARNING_DIR="/root/.openclaw/workspace/.learnings"

# 清理旧日志
rm -rf "$LEARNING_DIR/hooks/"
rm -rf "$LEARNING_DIR/signals/"
rm -rf "$LEARNING_DIR/errors/"
rm -rf "$LEARNING_DIR/success/"
mkdir -p "$LEARNING_DIR/hooks"

# 测试 1: Session Start Hook
echo "📋 测试 1: Session Start Hook"
"$HOOKS_DIR/session-start.sh"
echo ""

# 测试 2: User Prompt Hook
echo "📋 测试 2: User Prompt Hook"
"$HOOKS_DIR/user-prompt.sh" "测试输入"
echo ""

# 测试 3: PreToolUse Hook（成功案例）
echo "📋 测试 3: PreToolUse Hook（成功）"
"$HOOKS_DIR/pre-tool-use.sh" "exec" "ls -la"
echo ""

# 测试 4: PostToolUse Hook（成功）
echo "📋 测试 4: PostToolUse Hook（成功）"
"$HOOKS_DIR/post-tool-use.sh" "exec" "ls -la" "0"
echo ""

# 测试 5: Success Hook
echo "📋 测试 5: Success Hook"
"$HOOKS_DIR/success.sh" "exec" "ls -la"
echo ""

# 测试 6: PreToolUse Hook（失败案例）
echo "📋 测试 6: PreToolUse Hook（失败）"
"$HOOKS_DIR/pre-tool-use.sh" "exec" "invalid-command"
echo ""

# 测试 7: PostToolUse Hook（失败）
echo "📋 测试 7: PostToolUse Hook（失败）"
"$HOOKS_DIR/post-tool-use.sh" "exec" "invalid-command" "127"
echo ""

# 测试 8: Error Hook
echo "📋 测试 8: Error Hook"
"$HOOKS_DIR/error.sh" "exec" "invalid-command" "127"
echo ""

# 测试 9: Session End Hook
echo "📋 测试 9: Session End Hook"
"$HOOKS_DIR/session-end.sh"
echo ""

# 测试 10: 信号捕获
echo "📋 测试 10: 学习信号捕获"
source /root/.openclaw/workspace/scripts/analyze-signals.sh
capture_signal "exec" "ls -la" "0"
capture_signal "exec" "invalid-command" "127"
echo ""

# 测试 11: 信号分析
echo "📋 测试 11: 学习信号分析"
analyze_today
echo ""

echo "✅ 所有测试完成！"
echo ""
echo "📊 日志位置:"
echo "  - Hooks: $LEARNING_DIR/hooks/"
echo "  - Signals: $LEARNING_DIR/signals/"
echo "  - Errors: $LEARNING_DIR/errors/"
echo "  - Success: $LEARNING_DIR/success/"
echo ""
echo "📋 今日日志:"
ls -lh "$LEARNING_DIR/hooks/" 2>/dev/null | tail -5
