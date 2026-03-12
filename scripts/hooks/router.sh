#!/bin/bash
# Hook Router: 统一 Hook 路由系统
# 功能: 根据事件类型路由到相应的 Hook

HOOKS_DIR="/root/.openclaw/workspace/scripts/hooks"
LOG_DIR="/root/.openclaw/workspace/.learnings/hooks"

# 确保日志目录存在
mkdir -p "$LOG_DIR"

# Hook 路由函数
route_hook() {
    local event_type="$1"
    shift
    local args="$@"

    case "$event_type" in
        "session_start")
            "$HOOKS_DIR/session-start.sh"
            ;;
        "user_prompt")
            "$HOOKS_DIR/user-prompt.sh" "$args"
            ;;
        "pre_tool_use")
            "$HOOKS_DIR/pre-tool-use.sh" "$args"
            ;;
        "post_tool_use")
            "$HOOKS_DIR/post-tool-use.sh" "$args"
            ;;
        "error")
            "$HOOKS_DIR/error.sh" "$args"
            ;;
        "success")
            "$HOOKS_DIR/success.sh" "$args"
            ;;
        "session_end")
            "$HOOKS_DIR/session-end.sh"
            ;;
        *)
            echo "未知事件类型: $event_type"
            return 1
            ;;
    esac
}

# 导出函数供外部使用
export -f route_hook
