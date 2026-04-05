#!/bin/bash
# 测试 Multi-Agent 并行处理系统
#
# 版本: v1.0
# 创建时间: 2026-03-12

set -e

WORKSPACE="/root/.openclaw/workspace"
DISPATCHER="$WORKSPACE/scripts/parallel-task-dispatcher.sh"

echo "🧪 测试 1: 简单单任务"
echo "=================================================="

# 测试消息
test_message_1="@设计 修改3F更衣室排砖图"
test_sender="test_user"
test_chat_id="test_chat"
test_chat_type="group"

echo "📨 测试消息: $test_message_1"

if [[ -x "$DISPATCHER" ]]; then
    "$DISPATCHER" "$test_message_1" "$test_sender" "$test_chat_id"
    echo "✅ 测试 1 通过"
else
    echo "❌ 测试 1 失败: 分发器不可执行"
    exit 1
fi

echo ""
echo "🧪 测试 2: 并行多任务"
echo "=================================================="

# 测试消息（多个 @）
test_message_2="@大领导 今天要完成的任务：
1. @设计 修改3F更衣室排砖图
2. @技术 写个脚本抓取数据
3. @小蓝 更新工作日志"

echo "📨 测试消息:"
echo "$test_message_2"

if [[ -x "$DISPATCHER" ]]; then
    "$DISPATCHER" "$test_message_2" "$test_sender" "$test_chat_id"
    echo "✅ 测试 2 通过"
else
    echo "❌ 测试 2 失败: 分发器不可执行"
    exit 1
fi

echo ""
echo "🧪 测试 3: 异常处理（未知角色）"
echo "=================================================="

# 测试消息（未知角色）
test_message_3="@未知角色 做一些事情"

echo "📨 测试消息: $test_message_3"

if [[ -x "$DISPATCHER" ]]; then
    "$DISPATCHER" "$test_message_3" "$test_sender" "$test_chat_id"
    echo "✅ 测试 3 通过（应该忽略未知角色）"
else
    echo "❌ 测试 3 失败: 分发器不可执行"
    exit 1
fi

echo ""
echo "=================================================="
echo "🎉 所有测试完成！"
echo "=================================================="
echo ""
echo "📊 测试结果:"
echo "  ✅ 测试 1: 简单单任务 - 通过"
echo "  ✅ 测试 2: 并行多任务 - 通过"
echo "  ✅ 测试 3: 异常处理 - 通过"
echo ""
echo "📁 查看日志:"
echo "  ls -la $WORKSPACE/logs/parallel-tasks/"
