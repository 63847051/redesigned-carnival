#!/bin/bash

##############################################################################
# 集成工作流使用示例
##############################################################################

# 示例 1: 技术任务
echo "========================================="
echo "示例 1: 技术任务 - 写一个 Python 脚本"
echo "========================================="
echo ""

~/.openclaw/workspace/scripts/integrated-workflow.sh execute \
    TASK-001 \
    tech \
    "写一个Python爬虫脚本，抓取网页数据" \
    /root/output/TASK-001

echo ""
echo "按 Enter 继续..."
read

# 示例 2: 日志任务
echo ""
echo "========================================="
echo "示例 2: 日志任务 - 更新工作日志"
echo "========================================="
echo ""

~/.openclaw/workspace/scripts/integrated-workflow.sh execute \
    TASK-002 \
    log \
    "更新今日工作日志" \
    /root/output/TASK-002

echo ""
echo "按 Enter 继续..."
read

# 示例 3: 设计任务
echo ""
echo "========================================="
echo "示例 3: 设计任务 - 设计会议室平面图"
echo "========================================="
echo ""

~/.openclaw/workspace/scripts/integrated-workflow.sh execute \
    TASK-003 \
    design \
    "设计3F会议室平面图" \
    /root/output/TASK-003

echo ""
echo "所有示例完成！"
