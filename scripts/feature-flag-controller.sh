#!/bin/bash
# Feature Flag 控制系统 v1.0
# 基于 Claude Code Compaction 设计：安全发布 + 快速回滚 + A/B 测试

set -e

# =============================================================================
# ⚙️ 配置
# =============================================================================

FLAG_DIR="/root/.openclaw/workspace/.feature-flags"
STATE_FILE="$FLAG_DIR/feature-flags.json"
LOG_FILE="/root/.openclaw/workspace/logs/feature-flags.log"

# =============================================================================
# 📊 状态管理
# =============================================================================

init_state() {
    mkdir -p "$FLAG_DIR"
    mkdir -p "$(dirname "$LOG_FILE")"

    if [ ! -f "$STATE_FILE" ]; then
        cat > "$STATE_FILE" << EOF
{
  "version": 1,
  "last_updated": "$(date -Iseconds)",
  "flags": {}
}
EOF
    fi
}

# =============================================================================
# 🚩 Feature Flag 操作
# =============================================================================

create_flag() {
    local flag_name=$1
    local description=$2
    local enabled=${3:-false}

    echo "🚩 创建 Feature Flag: $flag_name"

    # 检查是否已存在
    if flag_exists "$flag_name"; then
        echo "⚠️ Flag 已存在: $flag_name"
        return 1
    fi

    # 添加到配置
    local temp_file=$(mktemp)
    jq ".flags.\"$flag_name\" = {
        \"description\": \"$description\",
        \"enabled\": $enabled,
        \"created_at\": \"$(date -Iseconds)\",
        \"updated_at\": \"$(date -Iseconds)\",
        \"version\": 1
    }" "$STATE_FILE" > "$temp_file"
    mv "$temp_file" "$STATE_FILE"

    update_timestamp

    echo "✅ Flag 已创建: $flag_name (enabled: $enabled)"
}

enable_flag() {
    local flag_name=$1

    echo "✅ 启用 Feature Flag: $flag_name"

    if ! flag_exists "$flag_name"; then
        echo "❌ Flag 不存在: $flag_name"
        return 1
    fi

    local temp_file=$(mktemp)
    jq ".flags.\"$flag_name\".enabled = true | \
        .flags.\"$flag_name\".updated_at = \"$(date -Iseconds)\" | \
        .flags.\"$flag_name\".version += 1" "$STATE_FILE" > "$temp_file"
    mv "$temp_file" "$STATE_FILE"

    update_timestamp

    echo "✅ Flag 已启用: $flag_name"
    log_action "enable" "$flag_name"
}

disable_flag() {
    local flag_name=$1

    echo "❌ 禁用 Feature Flag: $flag_name"

    if ! flag_exists "$flag_name"; then
        echo "❌ Flag 不存在: $flag_name"
        return 1
    fi

    local temp_file=$(mktemp)
    jq ".flags.\"$flag_name\".enabled = false | \
        .flags.\"$flag_name\".updated_at = \"$(date -Iseconds)\" | \
        .flags.\"$flag_name\".version += 1" "$STATE_FILE" > "$temp_file"
    mv "$temp_file" "$STATE_FILE"

    update_timestamp

    echo "❌ Flag 已禁用: $flag_name"
    log_action "disable" "$flag_name"
}

delete_flag() {
    local flag_name=$1

    echo "🗑️ 删除 Feature Flag: $flag_name"

    if ! flag_exists "$flag_name"; then
        echo "❌ Flag 不存在: $flag_name"
        return 1
    fi

    local temp_file=$(mktemp)
    jq "del(.flags.\"$flag_name\")" "$STATE_FILE" > "$temp_file"
    mv "$temp_file" "$STATE_FILE"

    update_timestamp

    echo "✅ Flag 已删除: $flag_name"
    log_action "delete" "$flag_name"
}

# =============================================================================
# 🔍 查询操作
# =============================================================================

flag_exists() {
    local flag_name=$1
    jq -e ".flags.\"$flag_name\"" "$STATE_FILE" >/dev/null 2>&1
}

is_flag_enabled() {
    local flag_name=$1

    if ! flag_exists "$flag_name"; then
        echo "false"
        return 1
    fi

    local enabled=$(jq -r ".flags.\"$flag_name\".enabled" "$STATE_FILE")
    echo "$enabled"
    [ "$enabled" = "true" ]
}

get_flag_info() {
    local flag_name=$1

    if ! flag_exists "$flag_name"; then
        echo "❌ Flag 不存在: $flag_name"
        return 1
    fi

    echo ""
    echo "📋 Flag 信息: $flag_name"
    echo ""

    jq ".flags.\"$flag_name\"" "$STATE_FILE"
}

list_flags() {
    echo ""
    echo "🚩 Feature Flag 列表:"
    echo ""

    local count=$(jq ".flags | length" "$STATE_FILE")

    if [ "$count" = "0" ]; then
        echo "  (无 Flag)"
    else
        jq -r '.flags | to_entries[] | "  \(.key): \(.value.enabled) // \(.value.description)"' "$STATE_FILE" | while read line; do
            local flag_name=$(echo "$line" | cut -d: -f1)
            local enabled=$(echo "$line" | cut -d: -f2 | xargs)
            local description=$(jq -r ".flags.\"$flag_name\".description" "$STATE_FILE")
            local status=""

            if [ "$enabled" = "true" ]; then
                status="✅"
            else
                status="❌"
            fi

            echo "  $status $flag_name"
            echo "     $description"
        done
    fi

    echo ""
    echo "总计: $count 个 Flag"
}

# =============================================================================
# 🎲 A/B 测试支持
# =============================================================================

ab_test_sample() {
    local flag_name=$1
    local user_id=$2
    local percentage=${3:-50}

    # 使用用户 ID 的哈希值进行采样
    local hash=$(echo -n "$user_id" | md5sum | cut -c1-8)
    local value=$((16#$hash % 100))

    if [ $value -lt $percentage ]; then
        echo "true"
    else
        echo "false"
    fi
}

is_flag_enabled_for_user() {
    local flag_name=$1
    local user_id=$2

    if ! flag_exists "$flag_name"; then
        echo "false"
        return 1
    fi

    # 检查是否有 A/B 测试配置
    local ab_test=$(jq -r ".flags.\"$flag_name\".ab_test // \"null\"" "$STATE_FILE")

    if [ "$ab_test" = "null" ]; then
        # 没有 A/B 测试，直接返回 Flag 状态
        is_flag_enabled "$flag_name"
        return $?
    fi

    # 有 A/B 测试，进行采样
    local percentage=$(jq -r ".flags.\"$flag_name\".ab_test.percentage" "$STATE_FILE")
    ab_test_sample "$flag_name" "$user_id" "$percentage"
}

# =============================================================================
# 📝 日志和更新
# =============================================================================

update_timestamp() {
    local temp_file=$(mktemp)
    jq ".last_updated = \"$(date -Iseconds)\"" "$STATE_FILE" > "$temp_file"
    mv "$temp_file" "$STATE_FILE"
}

log_action() {
    local action=$1
    local flag_name=$2
    echo "[$(date -Iseconds)] $action $flag_name" >> "$LOG_FILE"
}

# =============================================================================
# 🧪 测试函数
# =============================================================================

test_feature_flags() {
    echo ""
    echo "🧪 测试 Feature Flag 控制系统..."
    echo ""

    # 初始化
    init_state

    # 创建测试 Flag
    echo "📝 创建测试 Flag..."
    create_flag "test-feature" "测试功能" true

    # 检查状态
    echo ""
    echo "🔍 检查 Flag 状态..."
    if is_flag_enabled "test-feature"; then
        echo "✅ Flag 已启用"
    else
        echo "❌ Flag 未启用"
    fi

    # 禁用 Flag
    echo ""
    echo "❌ 禁用 Flag..."
    disable_flag "test-feature"

    # 再次检查
    echo ""
    echo "🔍 再次检查状态..."
    if is_flag_enabled "test-feature"; then
        echo "✅ Flag 已启用"
    else
        echo "❌ Flag 未启用"
    fi

    # 获取信息
    echo ""
    get_flag_info "test-feature"

    # 删除测试 Flag
    echo ""
    delete_flag "test-feature"

    # 列出所有 Flag
    echo ""
    list_flags
}

# =============================================================================
# 🚀 主流程
# =============================================================================

main() {
    echo "🚩 Feature Flag 控制系统 v1.0"
    echo "⏰ 时间: $(date)"
    echo ""

    case "${1:-test}" in
        test)
            test_feature_flags
            ;;
        create)
            if [ -z "$2" ]; then
                echo "用法: $0 create <flag_name> <description> [enabled]"
                exit 1
            fi
            init_state
            create_flag "$2" "$3" "${4:-false}"
            ;;
        enable)
            if [ -z "$2" ]; then
                echo "用法: $0 enable <flag_name>"
                exit 1
            fi
            init_state
            enable_flag "$2"
            ;;
        disable)
            if [ -z "$2" ]; then
                echo "用法: $0 disable <flag_name>"
                exit 1
            fi
            init_state
            disable_flag "$2"
            ;;
        delete)
            if [ -z "$2" ]; then
                echo "用法: $0 delete <flag_name>"
                exit 1
            fi
            init_state
            delete_flag "$2"
            ;;
        list)
            init_state
            list_flags
            ;;
        show)
            if [ -z "$2" ]; then
                echo "用法: $0 show <flag_name>"
                exit 1
            fi
            init_state
            get_flag_info "$2"
            ;;
        *)
            echo "用法: $0 {test|create|enable|disable|delete|list|show}"
            exit 1
            ;;
    esac
}

# 执行主流程
main "$@"
