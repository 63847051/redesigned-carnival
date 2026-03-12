#!/bin/bash
# =============================================================================
# PAI 算法循环 - The Algorithm
# =============================================================================
# 基于 PAI 官方深度学习（2026-03-05）
# 核心发现：脚手架 > 模型
# =============================================================================

ALGORITHM_DIR="/root/.openclaw/workspace/.pai-learning/algorithm"
WORK_MEMORY_DIR="/root/.openclaw/workspace/MEMORY/WORK"
TODAY=$(date +%Y-%m-%d)
NOW=$(date +%s)

# 创建目录
mkdir -p "$ALGORITHM_DIR"
mkdir -p "$WORK_MEMORY_DIR"

echo "🧠 PAI 算法循环 v1.0"
echo "======================================"
echo "基于 PAI 官方深度学习"
echo "核心：脚手架 > 模型"
echo ""

# =============================================================================
# The Algorithm - 7 阶段科学方法
# =============================================================================

run_algorithm() {
    local request="$1"
    local work_unit_name="${2:-task-$(date +%Y%m%d-%H%M%S)}"

    echo "🎯 请求: $request"
    echo "📁 工作单元: $work_unit_name"
    echo ""

    # 创建工作单元目录
    local work_dir="$WORK_MEMORY_DIR/${work_unit_name}"
    mkdir -p "$work_dir"/{items,agents,research,verification}

    # =======================================================================
    # Phase 1: OBSERVE - 反向工程请求
    # =======================================================================

    echo "🔍 Phase 1: OBSERVE"
    echo "   反向工程请求..."
    echo "   - 用户要求什么？"
    echo "   - 暗示了什么？"
    echo "   - 绝对不想要什么？"
    echo ""

    # 创建 ISC（理想状态标准）
    local isc_file="$work_dir/ISC.json"
    cat > "$isc_file" <<EOF
{
  "request": "$request",
  "phase": "OBSERVE",
  "created_at": "$NOW",
  "criteria": []
}
EOF

    echo "   ✅ ISC 文件创建: $isc_file"
    echo ""

    # =======================================================================
    # Phase 2: THINK - 扩展标准，评估能力
    # =======================================================================

    echo "🤔 Phase 2: THINK"
    echo "   扩展标准..."
    echo "   - 评估思考工具"
    echo "   - 验证技能提示"
    echo "   - 选择正确的 agents"
    echo ""

    # =======================================================================
    # Phase 3: PLAN - 最终确定方法
    # =======================================================================

    echo "📋 Phase 3: PLAN"
    echo "   最终确定方法..."
    echo "   - 选择执行能力"
    echo ""

    # =======================================================================
    # Phase 4: BUILD - 创建工件
    # =======================================================================

    echo "🔨 Phase 4: BUILD"
    echo "   创建工件..."
    echo "   - 生成 agents"
    echo "   - 调用技能"
    echo ""

    # =======================================================================
    # Phase 5: EXECUTE - 执行工作
    # =======================================================================

    echo "⚡ Phase 5: EXECUTE"
    echo "   执行工作..."
    echo ""

    # =======================================================================
    # Phase 6: VERIFY - 验证每个标准（关键！）
    # =======================================================================

    echo "✅ Phase 6: VERIFY"
    echo "   验证每个标准..."
    echo "   - 这是高潮！"
    echo "   - 测试每个标准"
    echo "   - 记录证据"
    echo "   - 我们真的成功了吗？"
    echo ""

    # =======================================================================
    # Phase 7: LEARN - 收集见解
    # =======================================================================

    echo "📚 Phase 7: LEARN"
    echo "   收集见解..."
    echo "   - 下次我们会做什么不同？"
    echo ""

    # 创建 META.yaml
    local meta_file="$work_dir/META.yaml"
    cat > "$meta_file" <<EOF
name: "$work_unit_name"
status: "completed"
session_lineage: ["$NOW"]
created_at: "$NOW"
completed_at: "$NOW"
request: "$request"
phases:
  - OBSERVE
  - THINK
  - PLAN
  - BUILD
  - EXECUTE
  - VERIFY
  - LEARN
EOF

    echo "✅ META 文件创建: $meta_file"
    echo ""
    echo "🎉 算法循环完成！"
}

# =============================================================================
# ISC（理想状态标准）系统
# =============================================================================

create_isc_criteria() {
    local request="$1"
    local isc_file="$2"

    echo "🎯 创建 ISC（理想状态标准）..."
    echo ""
    echo "ISC 原则："
    echo "  - 精确的 8 个词"
    echo "  - 状态而非行动"
    echo "  - 二元可测试（2 秒内 YES/NO）"
    echo "  - 粒度化（每个标准一个关注点）"
    echo ""

    # 示例 ISC 标准
    cat > "$isc_file" <<EOF
{
  "request": "$request",
  "criteria": [
    {
      "id": 1,
      "criterion": "示例：内容已校对",
      "testable": true,
      "binary": true,
      "state_not_action": true
    },
    {
      "id": 2,
      "criterion": "示例：Git 提交历史中无凭据",
      "testable": true,
      "binary": true,
      "state_not_action": true
    }
  ]
}
EOF

    echo "✅ ISC 标准创建: $isc_file"
}

# =============================================================================
# 主程序
# =============================================================================

case "$1" in
    run)
        if [ -z "$2" ]; then
            echo "用法: $0 run <请求> [工作单元名称]"
            exit 1
        fi
        run_algorithm "$2" "$3"
        ;;
    isc)
        if [ -z "$2" ]; then
            echo "用法: $0 isc <请求> <ISC文件>"
            exit 1
        fi
        create_isc_criteria "$2" "$3"
        ;;
    *)
        echo "🧠 PAI 算法循环 v1.0"
        echo ""
        echo "用法: $0 <命令> [参数...]"
        echo ""
        echo "命令:"
        echo "  run <请求> [工作单元]  - 运行完整算法循环"
        echo "  isc <请求> <ISC文件>     - 创建 ISC 标准"
        echo ""
        echo "示例:"
        echo "  $0 run '发布博客帖子'"
        echo "  $0 isc '更新网站' /tmp/isc.json"
        exit 1
        ;;
esac
