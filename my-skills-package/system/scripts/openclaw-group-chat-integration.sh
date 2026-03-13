#!/bin/bash
# OpenClaw 群聊集成脚本
# 将并行任务系统集成到 OpenClaw 消息处理流程
#
# 版本: v1.0
# 创建时间: 2026-03-12

set -e

WORKSPACE="/root/.openclaw/workspace"
MENTION_HANDLER="$WORKSPACE/scripts/group-chat-mention-handler.sh"
OPENCLAW_CONFIG="/root/.openclaw/openclaw.json"

# ============================================================================
# 配置检查
# ============================================================================

check_openclaw_config() {
    echo "🔍 检查 OpenClaw 配置..."
    
    if [[ ! -f "$OPENCLAW_CONFIG" ]]; then
        echo "❌ OpenClaw 配置文件不存在: $OPENCLAW_CONFIG"
        return 1
    fi
    
    echo "✅ OpenClaw 配置文件存在"
    
    # 检查 feishu 配置
    if python3 -c "import json; config=json.load(open('$OPENCLAW_CONFIG')); print('feishu' in config)" 2>/dev/null | grep -q True; then
        echo "✅ Feishu 配置存在"
    else
        echo "⚠️ 未检测到 Feishu 配置"
    fi
}

# ============================================================================
# 集成配置
# ============================================================================

setup_mention_integration() {
    echo "🔧 设置群聊 @ 提及集成..."
    
    # 创建集成配置文件
    local integration_config="$WORKSPACE/scripts/group-chat-integration-config.json"
    cat > "$integration_config" <<EOF
{
  "integration": {
    "name": "multi-agent-parallel-system",
    "version": "1.0",
    "enabled": true,
    "handler": "$MENTION_HANDLER",
    "triggers": {
      "mentions": ["@大领导", "@设计", "@技术", "@小蓝"],
      "chatTypes": ["group"]
    },
    "agents": {
      "orchestrator": {
        "name": "大领导",
        "triggers": ["@大领导"],
        "model": "glmcode/glm-4.7"
      },
      "design-expert": {
        "name": "设计专家",
        "triggers": ["@设计"],
        "model": "glmcode/glm-4.7"
      },
      "tech-expert": {
        "name": "技术专家",
        "triggers": ["@技术"],
        "model": "openrouter/gpt-oss-120b"
      },
      "xiaolan": {
        "name": "小蓝",
        "triggers": ["@小蓝"],
        "model": "glmcode/glm-4.5-air"
      }
    }
  }
}
EOF

    echo "✅ 集成配置已创建: $integration_config"
    echo "📋 配置内容:"
    cat "$integration_config"
}

# ============================================================================
# 测试脚本
# ============================================================================

create_test_script() {
    echo "🧪 创建测试脚本..."
    
    local test_script="$WORKSPACE/scripts/test-parallel-system.sh"
    cat > "$test_script" <<'EOF'
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
EOF

    chmod +x "$test_script"
    echo "✅ 测试脚本已创建: $test_script"
}

# ============================================================================
# 主函数
# ============================================================================

main() {
    echo "=================================================="
    echo "🚀 OpenClaw 群聊集成 - Phase 2"
    echo "=================================================="
    echo ""
    
    # Step 1: 检查 OpenClaw 配置
    check_openclaw_config
    echo ""
    
    # Step 2: 设置集成配置
    setup_mention_integration
    echo ""
    
    # Step 3: 创建测试脚本
    create_test_script
    echo ""
    
    echo "=================================================="
    echo "✅ Phase 2 配置完成！"
    echo "=================================================="
    echo ""
    echo "📋 已创建:"
    echo "  - 集成配置文件"
    echo "  - 测试脚本"
    echo ""
    echo "🚀 下一步: 运行测试"
    echo "  bash $WORKSPACE/scripts/test-parallel-system.sh"
    echo ""
}

# ============================================================================
# 脚本入口
# ============================================================================

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
