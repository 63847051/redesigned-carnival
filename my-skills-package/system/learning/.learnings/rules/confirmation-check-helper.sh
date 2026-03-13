#!/bin/bash
# 确认检查助手
# 在执行任何重要操作前，强制进行确认检查
#
# 用途: 防止 RULE-001 违规
# 版本: v1.0
# 创建时间: 2026-03-12

# ============================================================================
# 确认词白名单（只有这些才是真正的确认）
# ============================================================================

CONFIRMATION_WORDS=(
    "确认"
    "确认执行"
    "开始实施"
    "执行"
    "好的，执行吧"
    "开始做"
    "同意"
    "可以，执行"
)

# 模糊词（这些绝对不是确认）
AMBIGUOUS_WORDS=(
    "继续"
    "方案"
    "可以吗"
    "行不行"
    "怎么做"
    "怎么弄"
)

# ============================================================================
# 检查函数
# ============================================================================

# 检查是否是确认词
is_confirmation() {
    local user_input="$1"
    local word

    for word in "${CONFIRMATION_WORDS[@]}"; do
        if [[ "$user_input" == *"$word"* ]]; then
            echo "true"
            return 0
        fi
    done

    echo "false"
    return 1
}

# 检查是否是模糊词
is_ambiguous() {
    local user_input="$1"
    local word

    for word in "${AMBIGUOUS_WORDS[@]}"; do
        if [[ "$user_input" == *"$word"* ]]; then
            echo "true"
            return 0
        fi
    done

    echo "false"
    return 1
}

# 确认检查（主要函数）
confirmation_check() {
    local user_message="$1"
    local operation_description="$2"

    echo "=================================================="
    echo "🔒 确认检查（RULE-001）"
    echo "=================================================="
    echo ""
    echo "用户消息: $user_message"
    echo "计划操作: $operation_description"
    echo ""

    # 检查 1: 是否是确认词
    if [[ "$(is_confirmation "$user_message")" == "true" ]]; then
        echo "✅ 检查 1: 是明确的确认词"
    else
        echo "❌ 检查 1: 不是明确的确认词"
        echo ""
        echo "⚠️ 必须停止操作，询问用户确认"
        return 1
    fi

    # 检查 2: 是否是模糊词
    if [[ "$(is_ambiguous "$user_message")" == "true" ]]; then
        echo "❌ 检查 2: 检测到模糊词"
        echo ""
        echo "⚠️ 必须停止操作，询问用户确认"
        return 1
    else
        echo "✅ 检查 2: 不是模糊词"
    fi

    echo ""
    echo "=================================================="
    echo "✅ 所有检查通过，可以执行操作"
    echo "=================================================="
    echo ""

    return 0
}

# ============================================================================
# 使用示例
# ============================================================================

# 示例 1: 检查确认
# if confirmation_check "确认执行" "创建脚本"; then
#     echo "可以执行"
# else
#     echo "不能执行"
# fi

# 示例 2: 检查模糊词
# if confirmation_check "继续完成" "创建脚本"; then
#     echo "可以执行"
# else
#     echo "不能执行，需要明确确认"
# fi

# ============================================================================
# 导出函数供其他脚本使用
# ============================================================================

export -f is_confirmation
export -f is_ambiguous
export -f confirmation_check
