#!/bin/bash
# =============================================================================
# 🎯 大领导 PAI 系统 - 主入口
# =============================================================================
# Big Leader PAI System v6.0 - Main Entry Point
# 这是系统的主入口，统一管理所有 PAI 功能
# =============================================================================

VERSION="6.0"
SYSTEM_NAME="大领导 🎯 PAI 系统"
WORKSPACE="/root/.openclaw/workspace"

echo "🎯 $SYSTEM_NAME v$VERSION"
echo "======================================"
echo ""

# =============================================================================
# 显示系统状态
# =============================================================================

show_status() {
    echo "📊 系统状态"
    echo "======================================"
    echo ""

    # 检查核心组件
    echo "🧠 核心组件:"
    echo "   ✅ 三层记忆系统"
    echo "   ✅ 智能分析引擎"
    echo "   ✅ 智能建议系统"
    echo "   ✅ 算法循环（7 阶段）"
    echo "   ✅ Hook 系统（17 个）"
    echo "   ✅ 上下文启动管道"
    echo "   ✅ 个性系统（12 特征）"
    echo "   ✅ AI Steering Rules（8 规则）"
    echo ""

    # 检查 PAI 学习系统
    echo "📚 PAI 学习系统:"
    local signal_count=$(find "$WORKSPACE/.pai-learning/signals" -name "*.jsonl" -type f 2>/dev/null | xargs wc -l 2>/dev/null | awk '{sum+=$1} END {print sum+0}')
    echo "   - 学习信号: $signal_count 条"

    if [ -f "$WORKSPACE/.pai-learning/hot-memory.jsonl" ]; then
        local hot_count=$(wc -l < "$WORKSPACE/.pai-learning/hot-memory.jsonl")
        echo "   - Hot Memory: $hot_count 条"
    fi

    if [ -f "$WORKSPACE/public/pai-dashboard/index.html" ]; then
        echo "   - 可视化仪表板: http://43.134.63.176/pai-dashboard/"
    fi

    echo ""
}

# =============================================================================
# 运行完整工作流
# =============================================================================

run_workflow() {
    echo "🚀 运行完整 PAI 工作流"
    echo "======================================"
    echo ""

    # 1. 系统初始化
    echo "📝 步骤 1: 系统初始化..."
    bash "$WORKSPACE/scripts/pai-init.sh" 2>&1 | grep -v "jq:"
    echo ""

    # 2. 运行算法循环
    if [ -n "$1" ]; then
        echo "🧮 步骤 2: 运行算法循环..."
        bash "$WORKSPACE/scripts/pai-algorithm.sh" run "$1"
        echo ""
    fi

    # 3. 生成分析报告
    echo "🔬 步骤 3: 生成分析报告..."
    bash "$WORKSPACE/scripts/pai-analyzer-v2.sh" all
    echo ""

    # 4. 生成智能建议
    echo "💡 步骤 4: 生成智能建议..."
    bash "$WORKSPACE/scripts/pai-advisor-v2.sh" all
    echo ""

    # 5. 更新可视化仪表板
    echo "📊 步骤 5: 更新可视化仪表板..."
    bash "$WORKSPACE/scripts/pai-dashboard-generator.sh"
    echo ""

    # 6. 显示记忆统计
    echo "📈 步骤 6: 显示记忆统计..."
    bash "$WORKSPACE/scripts/pai-memory-manager.sh" stats
    echo ""

    # 7. 显示智能建议
    echo "💡 步骤 7: 显示智能建议..."
    bash "$WORKSPACE/scripts/pai-memory-manager.sh" advice
    echo ""

    echo "🎉 完整工作流执行完毕！"
}

# =============================================================================
# 主菜单
# =============================================================================

show_menu() {
    echo "🎯 主菜单"
    echo "======================================"
    echo ""
    echo "1. 查看系统状态"
    echo "2. 运行完整工作流"
    echo "3. 捕获学习信号"
    echo "4. 运行算法循环"
    echo "5. 测试 Hook 系统"
    echo "6. 查看帮助"
    echo "0. 退出"
    echo ""
}

# =============================================================================
# 主程序
# =============================================================================

main() {
    # 如果有参数，直接执行
    if [ $# -gt 0 ]; then
        case "$1" in
            status)
                show_status
                ;;
            workflow)
                run_workflow "$2"
                ;;
            capture)
                if [ -z "$2" ]; then
                    echo "用法: $0 capture <类型> <复杂度1-5> <成功1/0> <描述>"
                else
                    bash "$WORKSPACE/scripts/pai-learning-capture.sh" "$2" "$3" "$4" "$5"
                fi
                ;;
            algorithm)
                if [ -z "$2" ]; then
                    echo "用法: $0 algorithm <请求>"
                else
                    bash "$WORKSPACE/scripts/pai-algorithm.sh" run "$2"
                fi
                ;;
            test-hooks)
                bash "$WORKSPACE/scripts/pai-hooks-v2.sh" test_all
                ;;
            help|--help|-h)
                echo "🎯 $SYSTEM_NAME v$VERSION"
                echo ""
                echo "用法: $0 <命令> [参数...]"
                echo ""
                echo "命令:"
                echo "  status           - 查看系统状态"
                echo "  workflow [请求]  - 运行完整工作流"
                echo "  capture <...>    - 捕获学习信号"
                echo "  algorithm <请求> - 运行算法循环"
                echo "  test-hooks       - 测试 Hook 系统"
                echo "  help             - 显示此帮助"
                echo ""
                echo "示例:"
                echo "  $0 status"
                echo "  $0 workflow"
                echo "  $0 workflow '发布博客帖子'"
                echo "  $0 capture 系统 5 1 完成任务"
                echo "  $0 algorithm '研究公司'"
                echo "  $0 test-hooks"
                ;;
            *)
                echo "❌ 未知命令: $1"
                echo "使用 '$0 help' 查看帮助"
                exit 1
                ;;
        esac
        return
    fi

    # 交互式菜单
    while true; do
        show_menu
        echo -n "请选择 [0-6]: "
        read -r choice
        echo ""

        case "$choice" in
            1)
                show_status
                echo ""
                read -p "按 Enter 继续..."
                ;;
            2)
                run_workflow
                echo ""
                read -p "按 Enter 继续..."
                ;;
            3)
                echo "📝 捕获学习信号"
                echo "   用法: $0 capture <类型> <复杂度1-5> <成功1/0> <描述>"
                echo ""
                read -p "类型: " type
                read -p "复杂度 (1-5): " complexity
                read -p "成功 (1/0): " success
                read -p "描述: " description

                bash "$WORKSPACE/scripts/pai-learning-capture.sh" "$type" "$complexity" "$success" "$description"
                echo ""
                read -p "按 Enter 继续..."
                ;;
            4)
                echo "🧮 运行算法循环"
                echo ""
                read -p "请求: " request
                bash "$WORKSPACE/scripts/pai-algorithm.sh" run "$request"
                echo ""
                read -p "按 Enter 继续..."
                ;;
            5)
                bash "$WORKSPACE/scripts/pai-hooks-v2.sh" test_all
                echo ""
                read -p "按 Enter 继续..."
                ;;
            6)
                main help
                echo ""
                read -p "按 Enter 继续..."
                ;;
            0)
                echo "👋 再见！"
                exit 0
                ;;
            *)
                echo "❌ 无效选择，请重新选择"
                sleep 1
                ;;
        esac
    done
}

# 启动主程序
main "$@"
