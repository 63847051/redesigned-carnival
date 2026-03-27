#!/bin/bash
# 智能任务分配脚本
# 根据任务类型自动选择正确的 Agent 和调用方式

TASK="$1"
TASK_TYPE="$2"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🎯 智能任务分配${NC}"
echo "任务: $TASK"
echo ""

# 检测任务类型（如果未指定）
if [ -z "$TASK_TYPE" ]; then
    if echo "$TASK" | grep -qE "代码|脚本|爬虫|API|数据|前端|开发|编程"; then
        TASK_TYPE="tech"
    elif echo "$TASK" | grep -qE "日志|记录|任务|进度|统计|汇总"; then
        TASK_TYPE="log"
    elif echo "$TASK" | grep -qE "设计|图纸|平面图|立面图|天花|地面|排砖"; then
        TASK_TYPE="design"
    else
        TASK_TYPE="general"
    fi
fi

echo -e "${YELLOW}检测到任务类型: $TASK_TYPE${NC}"
echo ""

# 根据任务类型分配
case $TASK_TYPE in
    tech)
        echo -e "${GREEN}→ 分配给: 小新（技术支持专家）${NC}"
        echo "调用方式: OpenCode CLI"
        echo "模型: opencode/minimax-m2.5-free"
        echo ""
        opencode -m opencode/minimax-m2.5-free run "$TASK"
        ;;

    log)
        echo -e "${GREEN}→ 分配给: 小蓝（工作日志管理专家）${NC}"
        echo "调用方式: sessions_spawn"
        echo "模型: glmcode/glm-4.5-air"
        echo ""
        echo "注意: 需要在 OpenClaw 主会话中执行以下命令："
        echo "sessions_spawn -runtime subagent -model glmcode/glm-4.5-air -label 'xiaolan-task' -task \"$TASK\""
        ;;

    design)
        echo -e "${GREEN}→ 分配给: 设计专家${NC}"
        echo "调用方式: sessions_spawn"
        echo "模型: glmcode/glm-4.6"
        echo ""
        echo "注意: 需要在 OpenClaw 主会话中执行以下命令："
        echo "sessions_spawn -runtime subagent -model glmcode/glm-4.6 -label 'design-task' -task \"$TASK\""
        ;;

    *)
        echo -e "${YELLOW}→ 通用任务，由大领导直接处理${NC}"
        echo ""
        echo "任务: $TASK"
        ;;
esac

echo ""
echo -e "${GREEN}✅ 任务分配完成${NC}"
