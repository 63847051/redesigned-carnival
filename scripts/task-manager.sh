#!/bin/bash
# task-manager.sh - 任务管理工具
# 版本: v1.0
# 创建时间: 2026-03-18

set -e

# 配置
TASK_DIR="/root/.openclaw/workspace/shared-context/tasks"
PROJECT_DIR="/root/.openclaw/workspace/shared-context/projects"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 帮助信息
show_help() {
    echo "📋 任务管理工具 v1.0"
    echo ""
    echo "用法:"
    echo "  $0 list                    # 列出所有任务"
    echo "  $0 show <task_id>          # 显示任务详情"
    echo "  $0 create                  # 创建新任务（交互式）"
    echo "  $0 update <task_id>        # 更新任务状态（交互式）"
    echo "  $0 delete <task_id>        # 删除任务"
    echo "  $0 stats                   # 显示统计信息"
    echo ""
    echo "示例:"
    echo "  $0 list"
    echo "  $0 show BL-001"
    echo "  $0 create"
    echo "  $0 update BL-001"
    echo "  $0 stats"
}

# 列出所有任务
list_tasks() {
    echo "📋 所有任务列表"
    echo "===================="
    echo ""
    
    find "$TASK_DIR" -name "*.yaml" -not -name "template.yaml" | sort | while read -r file; do
        local task_id=$(grep "^task_id:" "$file" | cut -d'"' -f2)
        local title=$(grep "^title:" "$file" | cut -d'"' -f2)
        local status=$(grep "^status:" "$file" | awk '{print $2}')
        local assignee=$(grep "^assignee:" "$file" | cut -d'"' -f2)
        local priority=$(grep "^priority:" "$file" | awk '{print $2}')
        
        # 状态图标
        local status_icon=""
        case "$status" in
            "待确认") status_icon="⏳" ;;
            "进行中") status_icon="🔄" ;;
            "已完成") status_icon="✅" ;;
            "已取消") status_icon="❌" ;;
        esac
        
        # 优先级颜色
        local priority_color=""
        case "$priority" in
            "高") priority_color="${RED}" ;;
            "中") priority_color="${YELLOW}" ;;
            "低") priority_color="${GREEN}" ;;
        esac
        
        echo -e "${status_icon} ${task_id}: ${title}"
        echo -e "   状态: ${status} | 负责人: ${assignee} | 优先级: ${priority_color}${priority}${NC}"
        echo ""
    done
}

# 显示任务详情
show_task() {
    local task_id="$1"
    local file="$TASK_DIR/${task_id}.yaml"
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ 任务不存在: ${task_id}${NC}"
        exit 1
    fi
    
    echo "📋 任务详情: ${task_id}"
    echo "===================="
    echo ""
    cat "$file"
}

# 创建新任务
create_task() {
    echo "📝 创建新任务"
    echo "===================="
    echo ""
    
    # 读取任务信息
    read -p "任务ID (如: BL-011): " task_id
    read -p "任务标题: " title
    read -p "任务描述: " description
    read -p "任务类型 (设计/技术/日志/协调): " task_type
    read -p "优先级 (低/中/高): " priority
    read -p "复杂度 (简单/中等/复杂): " complexity
    read -p "负责人 (专家名称): " assignee
    read -p "项目名称: " project
    
    # 创建任务文件
    local file="$TASK_DIR/${task_id}.yaml"
    
    if [ -f "$file" ]; then
        echo -e "${RED}❌ 任务已存在: ${task_id}${NC}"
        exit 1
    fi
    
    cat > "$file" << EOF
# 任务基本信息
task_id: "${task_id}"
title: "${title}"
description: "${description}"

# 分类信息
type: "${task_type}"
category: ""
priority: "${priority}"
complexity: "${complexity}"

# 分配信息
assignee: "${assignee}"
agent_id: ""
model: ""

# 状态跟踪
status: "待确认"
progress: 0

# 时间信息
created: "$(date +%Y-%m-%d)"
updated: "$(date +%Y-%m-%d)"
deadline: null
started: null
completed: null

# 上下文信息
project: "${project}"
dependencies: []
tags: []

# 结果信息
result: null
notes: []
EOF
    
    echo -e "${GREEN}✅ 任务创建成功: ${task_id}${NC}"
    echo "文件: ${file}"
}

# 更新任务状态
update_task() {
    local task_id="$1"
    local file="$TASK_DIR/${task_id}.yaml"
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ 任务不存在: ${task_id}${NC}"
        exit 1
    fi
    
    echo "📝 更新任务: ${task_id}"
    echo "===================="
    echo ""
    
    # 显示当前状态
    echo "当前状态:"
    grep "^status:" "$file"
    grep "^progress:" "$file"
    echo ""
    
    # 读取新状态
    read -p "新状态 (待确认/进行中/已完成/已取消): " new_status
    read -p "新进度 (0-100): " new_progress
    
    # 更新文件
    sed -i "s/^status:.*/status: \"${new_status}\"/" "$file"
    sed -i "s/^progress:.*/progress: ${new_progress}/" "$file"
    sed -i "s/^updated:.*/updated: \"$(date +%Y-%m-%d)\"/" "$file"
    
    # 如果是已完成，设置完成时间
    if [ "$new_status" = "已完成" ]; then
        sed -i "s/^completed:.*/completed: \"$(date +%Y-%m-%d)\"/" "$file"
    fi
    
    # 如果是从待确认变为进行中，设置开始时间
    if [ "$new_status" = "进行中" ]; then
        if grep -q "^started: null" "$file"; then
            sed -i "s/^started:.*/started: \"$(date +%Y-%m-%d)\"/" "$file"
        fi
    fi
    
    echo -e "${GREEN}✅ 任务更新成功: ${task_id}${NC}"
}

# 删除任务
delete_task() {
    local task_id="$1"
    local file="$TASK_DIR/${task_id}.yaml"
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ 任务不存在: ${task_id}${NC}"
        exit 1
    fi
    
    echo "⚠️  确定要删除任务: ${task_id}?"
    read -p "输入 'yes' 确认删除: " confirm
    
    if [ "$confirm" = "yes" ]; then
        rm "$file"
        echo -e "${GREEN}✅ 任务已删除: ${task_id}${NC}"
    else
        echo "取消删除"
    fi
}

# 显示统计信息
show_stats() {
    echo "📊 任务统计"
    echo "===================="
    echo ""
    
    local total=0
    local completed=0
    local in_progress=0
    local pending=0
    local cancelled=0
    
    find "$TASK_DIR" -name "*.yaml" -not -name "template.yaml" | while read -r file; do
        total=$((total + 1))
        
        local status=$(grep "^status:" "$file" | awk '{print $2}')
        
        case "$status" in
            "已完成") completed=$((completed + 1)) ;;
            "进行中") in_progress=$((in_progress + 1)) ;;
            "待确认") pending=$((pending + 1)) ;;
            "已取消") cancelled=$((cancelled + 1)) ;;
        esac
    done
    
    echo "总任务数: ${total}"
    if [ ${total} -gt 0 ]; then
        echo "✅ 已完成: ${completed} ($((${completed} * 100 / ${total}))%)"
        echo "🔄 进行中: ${in_progress}"
        echo "⏳ 待确认: ${pending}"
        echo "❌ 已取消: ${cancelled}"
    else
        echo "✅ 已完成: 0 (0%)"
        echo "🔄 进行中: 0"
        echo "⏳ 待确认: 0"
        echo "❌ 已取消: 0"
    fi
    echo ""
}

# 主函数
main() {
    case "$1" in
        list)
            list_tasks
            ;;
        show)
            if [ -z "$2" ]; then
                echo -e "${RED}❌ 请指定任务ID${NC}"
                exit 1
            fi
            show_task "$2"
            ;;
        create)
            create_task
            ;;
        update)
            if [ -z "$2" ]; then
                echo -e "${RED}❌ 请指定任务ID${NC}"
                exit 1
            fi
            update_task "$2"
            ;;
        delete)
            if [ -z "$2" ]; then
                echo -e "${RED}❌ 请指定任务ID${NC}"
                exit 1
            fi
            delete_task "$2"
            ;;
        stats)
            show_stats
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}❌ 未知命令: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
