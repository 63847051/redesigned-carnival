#!/bin/bash
# OpenCode 免费模型包装脚本
# 作者: 大领导系统 v5.15
# 日期: 2026-03-16
#
# 用法: ./opencode-free.sh "你的任务"
#
# 支持的免费模型:
#   - opencode/minimax-m2.5-free (默认)
#   - opencode/mimo-v2-flash-free
#   - opencode/nemotron-3-super-free

TASK="$1"
MODEL="${2:-opencode/minimax-m2.5-free}"

# 检查 opencode 是否安装
if ! command -v opencode &> /dev/null; then
    echo "❌ 错误: OpenCode CLI 未安装"
    echo ""
    echo "安装命令:"
    echo "  curl -fsSL https://opencode.ai/install | bash"
    exit 1
fi

# 检查任务参数
if [ -z "$TASK" ]; then
    echo "❌ 错误: 缺少任务参数"
    echo ""
    echo "用法:"
    echo "  $0 \"你的任务\" [模型]"
    echo ""
    echo "示例:"
    echo "  $0 \"写一个 Python 脚本\""
    echo "  $0 \"解释这段代码\" opencode/mimo-v2-flash-free"
    exit 1
fi

# 创建临时工作目录
WORK_DIR=$(mktemp -d)
cd "$WORK_DIR"

# 执行任务
echo "🤖 OpenCode 免费模型"
echo "📍 模型: $MODEL"
echo "📝 任务: $TASK"
echo ""

# 使用 opencode 执行任务（设置 60 秒超时）
timeout 60 opencode -m "$MODEL" run "$TASK" 2>&1 || echo "⚠️ 任务执行超时或失败"

# 清理临时目录
cd /
rm -rf "$WORK_DIR"
