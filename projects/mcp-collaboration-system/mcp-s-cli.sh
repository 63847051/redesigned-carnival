#!/bin/bash
# MCP-S 快速启动脚本

echo "================================"
echo "MCP-S 多智能体协作系统 v1.0"
echo "================================"
echo ""

PROJECT_DIR="/root/.openclaw/workspace/projects/mcp-collaboration-system"
cd "$PROJECT_DIR" || exit 1

# 显示菜单
show_menu() {
    echo "请选择操作:"
    echo "  1. 运行完整测试"
    echo "  2. 运行示例工作流"
    echo "  3. 查看系统状态"
    echo "  4. 创建自定义工作流"
    echo "  5. 查看日志"
    echo "  6. 退出"
    echo ""
    read -p "请输入选项 [1-6]: " choice
}

# 运行测试
run_tests() {
    echo ""
    echo "================================"
    echo "运行 MCP-S 测试套件"
    echo "================================"
    python3 test_mcp_workflow.py
    echo ""
    read -p "按 Enter 继续..."
}

# 运行示例工作流
run_example() {
    echo ""
    echo "================================"
    echo "运行示例工作流"
    echo "================================"

    python3 << 'EOF'
import asyncio
import sys
sys.path.append('/root/.openclaw/workspace/projects/mcp-collaboration-system')

from mcp_workflow import create_simple_workflow, Task

async def main():
    tasks = [
        Task("t1", "数据采集", "agent_a"),
        Task("t2", "数据清洗", "agent_b", dependencies=["t1"]),
        Task("t3", "数据分析", "agent_c", dependencies=["t2"]),
        Task("t4", "生成报告", "agent_d", dependencies=["t3"]),
    ]

    workflow = create_simple_workflow("example", "示例工作流", tasks)

    print("执行示例工作流...")
    result = await workflow.execute()

    print(f"\n结果:")
    print(f"  状态: {result.status.value}")
    print(f"  完成: {result.tasks_completed}")
    print(f"  失败: {result.tasks_failed}")
    print(f"  耗时: {result.total_execution_time:.2f}秒")

    print("\n工作流详情:")
    print(workflow.visualize_workflow())

asyncio.run(main())
EOF

    echo ""
    read -p "按 Enter 继续..."
}

# 查看系统状态
show_status() {
    echo ""
    echo "================================"
    echo "MCP-S 系统状态"
    echo "================================"
    echo ""

    # 检查文件
    echo "📁 核心文件:"
    for file in dag_scheduler.py role_pool.py quality_gate.py prompt_template.py mcp_workflow.py; do
        if [ -f "$file" ]; then
            echo "  ✅ $file"
        else
            echo "  ❌ $file (缺失)"
        fi
    done
    echo ""

    # 检查配置
    echo "⚙️  配置文件:"
    for file in mcp-s-config.json quality-standards.json prompt-templates.json; do
        if [ -f "$file" ]; then
            echo "  ✅ $file"
        else
            echo "  ❌ $file (缺失)"
        fi
    done
    echo ""

    # 运行测试状态
    echo "🧪 测试状态:"
    if python3 test_mcp_workflow.py > /tmp/test_output.txt 2>&1; then
        echo "  ✅ 所有测试通过"
    else
        echo "  ⚠️  部分测试失败"
        echo "  查看: /tmp/test_output.txt"
    fi
    echo ""

    read -p "按 Enter 继续..."
}

# 创建自定义工作流
create_workflow() {
    echo ""
    echo "================================"
    echo "创建自定义工作流"
    echo "================================"
    echo ""

    read -p "工作流名称: " workflow_name
    read -p "工作流描述: " workflow_desc

    echo ""
    echo "添加任务（格式: 任务名,Agent ID,依赖任务ID（逗号分隔，无依赖留空））"
    echo "输入空行完成"

    tasks=()
    while true; do
        read -p "任务: " input
        if [ -z "$input" ]; then
            break
        fi

        IFS=',' read -r task_name agent_id deps <<< "$input"

        task_name=$(echo "$task_name" | xargs)
        agent_id=$(echo "$agent_id" | xargs)
        deps=$(echo "$deps" | xargs)

        if [ -n "$deps" ]; then
            tasks+=("Task(\"$task_name\", \"$agent_id\", dependencies=[\"$deps\"])")
        else
            tasks+=("Task(\"$task_name\", \"$agent_id\")")
        fi
    done

    # 生成工作流代码
    workflow_file="custom_${workflow_name// /_}.py"

    cat > "$workflow_file" << EOF
#!/usr/bin/env python3
"""自定义工作流: $workflow_name"""

import asyncio
import sys
sys.path.append('/root/.openclaw/workspace/projects/mcp-collaboration-system')

from mcp_workflow import create_simple_workflow, Task

async def main():
    tasks = [
$(printf "        %s\n" "${tasks[@]}")
    ]

    workflow = create_simple_workflow(
        workflow_id="${workflow_name// /_}",
        name="$workflow_name",
        tasks=tasks
    )

    print("执行工作流: $workflow_name")
    result = await workflow.execute()

    print(f"\n结果:")
    print(f"  状态: {result.status.value}")
    print(f"  完成: {result.tasks_completed}")
    print(f"  失败: {result.tasks_failed}")
    print(f"  耗时: {result.total_execution_time:.2f}秒")

if __name__ == "__main__":
    asyncio.run(main())
EOF

    echo ""
    echo "✅ 工作流已创建: $workflow_file"
    echo ""
    echo "运行方式:"
    echo "  python3 $workflow_file"
    echo ""
    read -p "按 Enter 继续..."
}

# 查看日志
view_logs() {
    echo ""
    echo "================================"
    echo "最近的日志"
    echo "================================"
    echo ""

    if [ -f "/tmp/test_output.txt" ]; then
        tail -50 /tmp/test_output.txt
    else
        echo "没有找到日志文件"
    fi

    echo ""
    read -p "按 Enter 继续..."
}

# 主循环
while true; do
    show_menu

    case $choice in
        1) run_tests ;;
        2) run_example ;;
        3) show_status ;;
        4) create_workflow ;;
        5) view_logs ;;
        6)
            echo ""
            echo "再见！"
            exit 0
            ;;
        *)
            echo ""
            echo "无效选项，请重试"
            sleep 1
            ;;
    esac
done
