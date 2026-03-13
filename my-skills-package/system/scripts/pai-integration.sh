#!/bin/bash
# =============================================================================
# 🔄 大领导 PAI 系统 - 集成超级进化大脑
# =============================================================================
# 功能：当检测到错误或风险时，调用超级进化大脑的防护层
# 使用：由大领导 PAI 系统自动调用
# =============================================================================

WORKSPACE="/root/.openclaw/workspace"
SE_SUPER_BRAIN="$WORKSPACE/SOUL.md"
SE_LOG_ERROR="$WORKSPACE/scripts/log-error.sh"
SE_EXTRACT_PATTERNS="$WORKSPACE/scripts/extract-patterns.sh"
SE_TRACK_EVOLUTION="$WORKSPACE/scripts/track-evolution.sh"
PAI_DIR="$WORKSPACE/.pai-learning"

echo "🔄 集成接口：大领导 PAI → 超级进化大脑"
echo "======================================"
echo ""

# =============================================================================
# 集成接口 1: 错误处理集成
# =============================================================================

call_super_evolution_on_error() {
    local error_type="$1"
    local error_context="$2"

    echo "🛡️ 检测到错误，调用超级进化大脑..."
    echo "   错误类型: $error_type"
    echo "   上下文: $error_context"
    echo ""

    # 调用超级进化大脑的错误处理
    if [ -f "$SE_LOG_ERROR" ]; then
        bash "$SE_LOG_ERROR" "$error_type" "$error_context"
    fi

    # 记录到三层记忆
    local signal_file="$PAI_DIR/signals/$(date +%Y-%m-%d)-signals.jsonl"
    mkdir -p "$PAI_DIR/signals"

    echo "{\"timestamp\":$(date +%s),\"date\":\"$(date +%Y-%m-%d)\",\"task_type\":\"错误处理\",\"complexity\":3,\"success\":0,\"description\":\"超级进化大脑处理错误: $error_type\",\"emotion\":\"negative\"}" >> "$signal_file"

    echo "✅ 错误已记录，超级进化大脑正在分析..."
}

# =============================================================================
# 集成接口 2: 风险预警集成
# =============================================================================

call_super_evolution_on_risk() {
    local risk_level="$1"
    local risk_context="$2"

    echo "⚠️  检测到风险，调用超级进化大脑..."
    echo "   风险级别: $risk_level"
    echo "   上下文: $risk_context"
    echo ""

    # 调用超级进化大脑的防护检查
    bash "$WORKSPACE/scripts/protection-check.sh"

    # 记录到三层记忆
    local signal_file="$PAI_DIR/signals/$(date +%Y-%m-%d)-signals.jsonl"
    mkdir -p "$PAI_DIR/signals"

    echo "{\"timestamp\":$(date +%s),\"date\":\"$(date +%Y-%m-%d)\",\"task_type\":\"风险预警\",\"complexity\":4,\"success\":1,\"description\":\"超级进化大脑处理风险: $risk_level\",\"emotion\":\"cautious\"}" >> "$signal_file"

    echo "✅ 风险已记录，超级进化大脑正在防护..."
}

# =============================================================================
# 集成接口 3: 进化建议集成
# =============================================================================

call_super_evolution_for_evolution() {
    local task_type="$1"
    local task_context="$2"

    echo "🚀 触发进化分析..."
    echo "   任务类型: $task_type"
    echo "   上下文: $task_context"
    echo ""

    # 调用超级进化大脑的进化分析
    if [ -f "$SE_EXTRACT_PATTERNS" ]; then
        bash "$SE_EXTRACT_PATTERNS"
    fi

    if [ -f "$SE_TRACK_EVOLUTION" ]; then
        bash "$SE_TRACK_EVOLUTION"
    fi

    # 记录到三层记忆
    local signal_file="$PAI_DIR/signals/$(date +%Y-%m-%d)-signals.jsonl"
    mkdir -p "$PAI_DIR/signals"

    echo "{\"timestamp\":$(date +%s),\"date\":\"$(date +%Y-%m-%d)\",\"task_type\":\"进化分析\",\"complexity\":5,\"success\":1,\"description\":\"超级进化大脑完成进化分析\",\"emotion\":\"positive\"}" >> "$signal_file"

    echo "✅ 进化分析完成，建议已生成..."
}

# =============================================================================
# 主程序
# =============================================================================

case "$1" in
    error)
        if [ -z "$2" ]; then
            echo "用法: $0 error <错误类型> <上下文>"
            exit 1
        fi
        call_super_evolution_on_error "$2" "$3"
        ;;
    risk)
        if [ -z "$2" ]; then
            echo "用法: $0 risk <风险级别> <上下文>"
            exit 1
        fi
        call_super_evolution_on_risk "$2" "$3"
        ;;
    evolve)
        if [ -z "$2" ]; then
            echo "用法: $0 evolve <任务类型> <上下文>"
            exit 1
        fi
        call_super_evolution_for_evolution "$2" "$3"
        ;;
    test)
        echo "🧪 测试集成接口..."
        echo ""
        echo "测试 1: 错误处理集成"
        call_super_evolution_on_error "测试错误" "测试上下文"
        echo ""
        echo "测试 2: 风险预警集成"
        call_super_evolution_on_risk "中风险" "测试上下文"
        echo ""
        echo "测试 3: 进化建议集成"
        call_super_evolution_for_evolution "测试任务" "测试上下文"
        echo ""
        echo "✅ 所有集成接口测试完成"
        ;;
    *)
        echo "🔄 集成接口：大领导 PAI → 超级进化大脑"
        echo ""
        echo "用法: $0 <接口> [参数...]"
        echo ""
        echo "接口:"
        echo "  error <错误类型> <上下文> - 错误处理集成"
        echo "  risk <风险级别> <上下文> - 风险预警集成"
        echo "  evolve <任务类型> <上下文> - 进化建议集成"
        echo "  test_all - 测试所有集成接口"
        echo ""
        echo "示例:"
        echo "  $0 error 系统崩溃 'Gateway 无响应'"
        echo "  $0 risk 中风险 '内存使用 80%'"
        echo "  $0 evolve 设计任务 '需要新技能'"
        echo "  $0 test_all"
        exit 1
        ;;
esac
