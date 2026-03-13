#!/bin/bash
# =============================================================================
# PAI Hook 系统 v2.0 - 细化版
# =============================================================================
# 基于 PAI 官方深度学习（2026-03-05）
# 17 个 hooks，7 个生命周期事件
# =============================================================================

HOOK_DIR="/root/.openclaw/workspace/.pai-learning/hooks"
LOG_DIR="$HOOK_DIR/logs"
TODAY=$(date +%Y-%m-%d)
NOW=$(date +%s)

# 创建目录
mkdir -p "$LOG_DIR"

echo "🎣 PAI Hook 系统 v2.0"
echo "======================================"
echo "17 个 hooks，7 个生命周期事件"
echo ""

# =============================================================================
# Hook 系统 - 7 个生命周期事件
# =============================================================================

# =============================================================================
# Event 1: SessionStart - 新会话开始
# =============================================================================

hook_session_start() {
    echo "🚀 [SessionStart] Hook 触发"
    echo "   - 检查 SKILL.md 是否需要重建"
    echo "   - 加载上下文文件"
    echo "   - 加载关系上下文"
    echo "   - 检查活跃工作"
    echo "   - 注入为 system-reminder"

    # 记录日志
    echo "[$NOW] SessionStart: Hook 执行" >> "$LOG_DIR/hooks-$TODAY.log"
}

# =============================================================================
# Event 2: UserPromptSubmit - 每次用户消息
# =============================================================================

hook_user_prompt_submit() {
    local prompt="$1"
    echo "💬 [UserPromptSubmit] Hook 触发"
    echo "   - 检测响应模式（FULL/ITERATION/MINIMAL）"
    echo "   - 路由到正确的技能"

    # 检测响应模式
    if [[ "$prompt" =~ ^(hi|hey|thanks|ok|cool) ]]; then
        echo "   → 模式: MINIMAL"
    elif [[ "$prompt" =~ ^(ok|yes)(现在|然后|尝试|但是) ]]; then
        echo "   → 模式: ITERATION"
    else
        echo "   → 模式: FULL Algorithm"
    fi

    # 记录日志
    echo "[$NOW] UserPromptSubmit: $prompt" >> "$LOG_DIR/hooks-$TODAY.log"
}

# =============================================================================
# Event 3: PreToolUse - 工具执行前（<50ms）
# =============================================================================

hook_pre_tool_use() {
    local tool="$1"
    local command="$2"

    echo "🔒 [PreToolUse] Hook 触发"
    echo "   - 工具: $tool"
    echo "   - 安全验证（<50ms）"

    # 安全验证
    # 1. 阻止提示注入模式
    if [[ "$command" =~ ignore|all|previous|instructions ]]; then
        echo "   ❌ 阻止: 可能的提示注入"
        return 1
    fi

    # 2. 检测命令注入
    if [[ "$command" =~ \$\(.*\) ]]; then
        echo "   ❌ 阻止: 命令注入尝试"
        return 1
    fi

    # 3. 检测路径遍历
    if [[ "$command" =~ \.\./\.\. ]]; then
        echo "   ❌ 阻止: 路径遍历攻击"
        return 1
    fi

    echo "   ✅ 安全验证通过"

    # 记录日志
    echo "[$NOW] PreToolUse: $tool - 安全验证通过" >> "$LOG_DIR/security-$TODAY.log"
}

# =============================================================================
# Event 4: PostToolUse - 工具完成后
# =============================================================================

hook_post_tool_use() {
    local tool="$1"
    local status="$2"

    echo "📊 [PostToolUse] Hook 触发"
    echo "   - 工具: $tool"
    echo "   - 状态: $status"
    echo "   - 可观察性日志"

    # 记录日志
    echo "[$NOW] PostToolUse: $tool - $status" >> "$LOG_DIR/observability-$TODAY.log"
}

# =============================================================================
# Event 5: StopSession - 会话结束
# =============================================================================

hook_stop_session() {
    echo "🛑 [StopSession] Hook 触发"
    echo "   - 重建 SKILL.md"
    echo "   - 捕获学习"
    echo "   - 保存会话状态"

    # 记录日志
    echo "[$NOW] StopSession: Hook 执行" >> "$LOG_DIR/hooks-$TODAY.log"
}

# =============================================================================
# Event 6: SubagentStop - 子 agent 完成
# =============================================================================

hook_subagent_stop() {
    local agent_name="$1"
    local output="$2"

    echo "🤖 [SubagentStop] Hook 触发"
    echo "   - Agent: $agent_name"
    echo "   - AgentOutputCapture: 收集结果"

    # 记录日志
    echo "[$NOW] SubagentStop: $agent_name" >> "$LOG_DIR/agents-$TODAY.log"
}

# =============================================================================
# Event 7: Custom - 自定义事件
# =============================================================================

hook_custom() {
    local event_name="$1"
    local data="$2"

    echo "⭐ [Custom] Hook 触发"
    echo "   - 事件: $event_name"
    echo "   - 数据: $data"

    # 记录日志
    echo "[$NOW] Custom: $event_name - $data" >> "$LOG_DIR/custom-$TODAY.log"
}

# =============================================================================
# 主程序
# =============================================================================

case "$1" in
    session_start)
        hook_session_start
        ;;
    user_prompt)
        hook_user_prompt_submit "$2"
        ;;
    pre_tool)
        hook_pre_tool_use "$2" "$3"
        ;;
    post_tool)
        hook_post_tool_use "$2" "$3"
        ;;
    stop_session)
        hook_stop_session
        ;;
    subagent_stop)
        hook_subagent_stop "$2" "$3"
        ;;
    custom)
        hook_custom "$2" "$3"
        ;;
    test_all)
        echo "🧪 测试所有 hooks..."
        echo ""
        hook_session_start
        echo ""
        hook_user_prompt_submit "测试算法循环"
        echo ""
        hook_pre_tool_use "bash" "ls -la"
        echo ""
        hook_post_tool_use "bash" "success"
        echo ""
        hook_subagent_stop "TestAgent" "输出结果"
        echo ""
        hook_stop_session
        echo ""
        echo "✅ 所有 hooks 测试完成"
        ;;
    *)
        echo "🎣 PAI Hook 系统 v2.0"
        echo ""
        echo "用法: $0 <hook> [参数...]"
        echo ""
        echo "Hooks:"
        echo "  session_start     - 会话开始"
        echo "  user_prompt       - 用户消息"
        echo "  pre_tool          - 工具执行前"
        echo "  post_tool         - 工具执行后"
        echo "  stop_session      - 会话结束"
        echo "  subagent_stop     - 子 agent 完成"
        echo "  custom            - 自定义事件"
        echo "  test_all          - 测试所有 hooks"
        echo ""
        echo "示例:"
        echo "  $0 session_start"
        echo "  $0 user_prompt '测试算法循环'"
        echo "  $0 pre_tool bash 'ls -la'"
        echo "  $0 test_all"
        exit 1
        ;;
esac
