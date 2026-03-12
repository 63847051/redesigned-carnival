#!/bin/bash
# 飞书群 @ 提及路由系统
# 自主进化系统 5.8

echo "🎯 飞书群 @ 提及路由系统"
echo "======================"
echo ""
echo "当前时间: $(date)"
echo ""

# 检查是否是 @ 提及
MENTION_TEXT="$1"

echo "📝 收到 @ 提及: $MENTION_TEXT"
echo ""

# 判断路由到哪个 Agent
case "$MENTION_TEXT" in
    *"大领导"*|*"设计"*|*"室内"*|*"图纸"*)
        echo "🏠 路由到: 室内设计专家（Builder）"
        echo "任务类型: 设计任务"
        # 调用 Builder Agent
        # openclaw agent --agent builder --message "$@"
        ;;

    *"技术"*|*"代码"*|*"开发"*|*"爬虫"*)
        echo "💻 路由到: 技术专家（Tech）"
        echo "任务类型: 技术任务"
        # 调用 Tech Agent
        # openclaw agent --agent tech --message "$@"
        ;;

    *"小蓝"*|*"日志"*|*"记录"*|*"工作"*)
        echo "📋 路由到: 小蓝（Ops）"
        echo "任务类型: 日志管理"
        # 调用 Ops Agent
        # openclaw agent --agent ops --message "$@"
        ;;

    *)
        echo "🎯 路由到: 主控 Agent（Orchestrator）"
        echo "任务类型: 综合任务"
        # 主控 Agent 处理
        ;;
esac

echo ""
echo "✅ 路由完成"
echo ""
