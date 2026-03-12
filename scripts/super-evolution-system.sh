#!/bin/bash
# 🧬 超级进化系统（SES）v2.0 - 主脚本
# 整合双轨 + 可执行 + 完整系统 + EvoMap

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🧬 超级进化系统（SES）v2.0${NC}"
echo -e "${BLUE}=======================${NC}"
echo ""

# 显示系统状态
echo "📊 系统状态："
echo "  双轨进化：✅ 运行中"
echo "  可执行进化：✅ 已部署"
echo "  完整进化系统：✅ 已整合"
echo "  EvoMap：⏳ 等待连接"
echo ""

# 显示进化统计
echo "📈 进化统计："
echo "  错误记录：$(ls -1 .learnings/errors/*.md 2>/dev/null | wc -l) 个"
echo "  设计模式：$(ls -1 .learnings/design-patterns/*.md 2>/dev/null | wc -l) 个"
echo "  EvoMap 资产：$(ls -1 .evomap/*.md 2>/dev/null | wc -l) 个"
echo "  自动化脚本：$(ls -1 scripts/*.sh 2>/dev/null | wc -l) 个"
echo ""

# 显示核心流程
echo "🔄 核心流程："
echo "  1. 任务/错误/反馈"
echo "  2. 双轨-轨道1 触发"
echo "  3. 完整系统-8 大模式处理"
echo "  4. 可执行系统-检查和评估"
echo "  5. 双轨-轨道1 记录学习"
echo "  6. EvoMap 准备发布"
echo "  7. 系统级进化"
echo ""

# 显示功能
echo "🎯 主要功能："
echo "  [1] 运行进化检查"
echo "  [2] 记录错误"
echo "  [3] 提取模式"
echo "  [4] 追踪统计"
echo "  [5] 准备发布"
echo "  [q] 退出"
echo ""

# 主循环
while true; do
    read -p "请选择功能 (1-5/q): " choice
    
    case $choice in
        1)
            echo -e "${GREEN}▶️️  运行进化检查...${NC}"
            bash scripts/core-logic-check.sh
            bash scripts/task-evaluation.sh
            echo ""
            ;;
        2)
            echo -e "${GREEN}📝 记录错误...${NC}"
            read -p "错误名称: " error_name
            read -p "错误描述: " error_desc
            bash scripts/log-error.sh "$error_name" "$error_desc"
            echo ""
            ;;
        3)
            echo -e "${GREEN}🔍 提取模式...${NC}"
            bash scripts/extract-patterns.sh
            echo ""
            ;;
        4)
            echo -e "${GREEN}📊 追踪统计...${NC}"
            bash scripts/track-evolution.sh
            echo ""
            ;;
        5)
            echo -e "${GREEN}🚀 准备发布...${NC}"
            echo "📦 当前 EvoMap 资产："
            ls -1 .evomap/*.md 2>/dev/null | head -10
            echo "⏳ 等待 EvoMap Hub 恢复"
            echo ""
            ;;
        q)
            echo -e "${GREEN}👋 退出超级进化系统${NC}"
            exit 0
            ;;
        *)
            echo -e "${YELLOW}❓ 无效选择，请重试${NC}"
            echo ""
            ;;
    esac
done
