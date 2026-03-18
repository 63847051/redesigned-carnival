#!/bin/bash
# opencode 调用检查脚本

echo "🔍 检查 opencode 调用方式..."

# 检查是否有错误的调用
if grep -r "sessions_spawn.*opencode.*minimax" ~/.openclaw/workspace/ 2>/dev/null; then
    echo "❌ 检测到错误的 opencode 调用！"
    echo ""
    echo "正确方式:"
    echo "  opencode -m opencode/minimax-m2.5-free run \"任务\""
    echo ""
    echo "错误方式（不要使用）:"
    echo "  sessions_spawn(runtime=\"subagent\", model=\"opencode/minimax-m2.5-free\")"
    echo ""
    echo "参考: .learnings/errors/opencode-subagent-error-20260318.md"
fi

echo "✅ 检查完成"
