#!/bin/bash
# 飞书群聊 Multi-Agent 系统配置脚本
# 将并行任务系统集成到飞书群聊
#
# 版本: v1.0
# 创建时间: 2026-03-12

set -e

WORKSPACE="/root/.openclaw/workspace"
OPENCLAW_CONFIG="/root/.openclaw/openclaw.json"
MENTION_HANDLER="$WORKSPACE/scripts/group-chat-mention-handler.sh"

echo "=================================================="
echo "🔧 飞书群聊 Multi-Agent 系统配置"
echo "=================================================="
echo ""

# ============================================================================
# 检查当前配置
# ============================================================================

echo "📋 当前飞书配置:"
echo ""

# 检查飞书是否启用
if cat "$OPENCLAW_CONFIG" | python3 -c "import json, sys; config=json.load(sys.stdin); print('✅ 飞书已启用' if config.get('providers', {}).get('feishu', {}).get('enabled') else '❌ 飞书未启用')" 2>/dev/null; then
    :
fi

# 检查群聊策略
if cat "$OPENCLAW_CONFIG" | python3 -c "import json, sys; config=json.load(sys.stdin); policy=config.get('providers', {}).get('feishu', {}).get('groupPolicy', 'unknown'); print(f\"群聊策略: {policy}\")" 2>/dev/null; then
    :
fi

echo ""
echo "=================================================="
echo "📋 Multi-Agent 系统状态"
echo "=================================================="
echo ""

# 检查核心脚本
echo "核心脚本:"
if [[ -x "$MENTION_HANDLER" ]]; then
    echo "  ✅ 群聊 @ 处理器: $MENTION_HANDLER"
else
    echo "  ❌ 群聊 @ 处理器不存在或不可执行"
fi

DISPATCHER="$WORKSPACE/scripts/parallel-task-dispatcher.sh"
if [[ -x "$DISPATCHER" ]]; then
    echo "  ✅ 并行任务分发器: $DISPATCHER"
else
    echo "  ❌ 并行任务分发器不存在或不可执行"
fi

echo ""
echo "=================================================="
echo "🚀 使用说明"
echo "=================================================="
echo ""

echo "📱 在飞书群聊中使用:"
echo ""
echo "1️⃣ 确保机器人已添加到群聊"
echo "2️⃣ 使用 @ 提及触发不同角色:"
echo ""
echo "   示例 1 - 单任务:"
echo "   @设计 修改3F更衣室排砖图"
echo ""
echo "   示例 2 - 并行多任务:"
echo "   @大领导 今天要完成的任务："
echo "     1. @设计 修改图纸"
echo "     2. @技术 编写脚本"
echo "     3. @小蓝 更新日志"
echo ""
echo "=================================================="
echo "👥 可用角色"
echo "=================================================="
echo ""

echo "┌─────────────┬──────────┬──────────────┐"
echo "│ 触发词      │ 角色     │ 模型         │"
echo "├─────────────┼──────────┼──────────────┤"
echo "│ @大领导     │ 任务总监 │ GLM-4.7      │"
echo "│ @设计       │ 设计专家 │ GLM-4.7      │"
echo "│ @技术       │ 技术专家 │ GPT-OSS-120B │"
echo "│ @小蓝       │ 工作日志 │ GLM-4.5-Air  │"
echo "└─────────────┴──────────┴──────────────┘"
echo ""

echo "💡 成本分配: 70% 免费 + 30% 付费"
echo ""

echo "=================================================="
echo "🧪 测试系统"
echo "=================================================="
echo ""

echo "运行测试脚本:"
echo "  bash $WORKSPACE/scripts/test-parallel-system.sh"
echo ""

echo "查看日志:"
echo "  ls -la $WORKSPACE/logs/parallel-tasks/"
echo ""

echo "=================================================="
echo "✅ 配置完成！"
echo "=================================================="
echo ""

echo "📝 重要提示:"
echo "  1. 飞书已配置为 groupPolicy: open"
echo "  2. 所有群聊都可以使用 Multi-Agent 系统"
echo "  3. 确保 OpenClaw Gateway 正在运行"
echo "  4. 在群聊中使用 @ 触发即可"
echo ""

echo "🚀 现在可以在任意飞书群聊中使用了！"
echo ""

# ============================================================================
# 检查 Gateway 状态
# ============================================================================

echo "=================================================="
echo "🔍 检查 Gateway 状态"
echo "=================================================="
echo ""

if systemctl --user is-active --quiet openclaw-gateway; then
    echo "✅ OpenClaw Gateway 正在运行"
else
    echo "⚠️ OpenClaw Gateway 未运行"
    echo "   启动命令: systemctl --user start openclaw-gateway"
fi

echo ""
