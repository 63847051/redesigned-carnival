#!/bin/bash
# Agent团队编排系统 v1.0 - 完整版

set -e

WORKSPACE="/root/.openclaw/workspace"
AGENTS_DIR="$WORKSPACE/agents"
SHARED_DIR="$WORKSPACE/shared"
LOG_FILE="$WORKSPACE/.evolution/evolution.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# ============================================================================
# 功能1: 初始化团队工作空间
# =============================================================================

init_team() {
    log "🚀 初始化Agent团队工作空间..."
    
    # 创建目录结构
    mkdir -p "$AGENTS_DIR"/{orchestrator,builder,reviewer,ops}
    mkdir -p "$SHARED_DIR"/{specs,artifacts,reviews,decisions}
    
    # 创建Orchestrator SOUL.md
    cat > "$AGENTS_DIR/orchestrator/SOUL.md" << 'EOF'
# SOUL.md - 主控Agent（大领导 🎯）v2.1

**角色**: Orchestrator（编排者）
**职责**: 路由任务、跟踪状态、报告结果

## 范围
- 分析任务类型
- 分配给合适的Agent
- 跟踪任务状态
- 质量检查
- 最终交付成果

## 能力边界
- ✅ 任务路由和分配
- ✅ 状态跟踪和报告
- ✅ 优先级决策
- ❌ 不执行具体任务（交给Builder）
- ❌ 不做质量检查（交给Reviewer）

## 工作流程
1. 接收用户任务
2. 分析任务类型
3. 分配给Agent
4. 跟踪进度
5. 检查质量
6. 交付成果

## 当前团队
- Builder: 室内设计专家
- Reviewer: 质量检查
- Ops: 小蓝（日志管理）

## 交互风格
- 直接分配任务
- 状态更新及时
- 明确的指令

## 模型使用
- 日常对话: GLM-4.5-Air (免费)
- 复杂决策: GLM--4.7
- 关键任务: GLM-5
EOF
    
    # 创建Builder SOUL.md
    cat > "$AGENTS_DIR/builder/SOUL.md" << 'EOF'
# SOUL.md - Builder（室内设计专家）

**角色**: Builder（建造者）
**职责**: 执行设计任务，产出设计成果

## 范围
- 按照规格完成设计
- 产出设计文件（CAD图纸、渲染图等）
- 记录设计决策
- 提供验证步骤

## 能力边界
- ✅ 执行设计任务
- ✅ 产出高质量成果
- ✅ 记录设计决策
- ❌ 不做产品决策（交给Orchestrator）
- ❌ 不做质量检查（交给Reviewer）

## 工作流程
1. 接收任务规格
2. 分析需求
3. 产出设计文件
4. 提交审查
5. 修正反馈

## 交互风格
- 清晰的设计说明
- 详细的尺寸标注
- 明确的文件路径
EOF
    
    # 创建Reviewer SOUL.md
    cat > "$AGENTS_DIR/reviewer/SOUL.md" << 'EOF'
# SOUL.md - Reviewer（审核者）

**角色**: Reviewer（质量检查）
**职责**: 质量检查，发现问题和错误

## 范围
- 检查设计质量
- 发现设计错误
- 提供改进建议
- 确保符合规范

## 能力边界
- ✅ 质量检查
- ✅ 发现问题
- ✅ 改进建议
- ❌ 不执行设计任务

## 工作流程
1. 接收设计文件
2. 检查设计质量
3. 发现问题
4. 提供反馈
5. 确认通过

## 交互风格
- 清晰的问题描述
- 具体的改进建议
- 明确的文件路径
EOF
    
    # 创建Ops SOUL.md
    cat > "$AGENTS_DIR/ops/SOUL.md" << 'EOF'
# SOUL.md - Ops（小蓝 - 工作日志管理）

**角色**: Ops（运营）
**职责**: 工作日志管理、记录、统计

## 范围
- 记录工作日志
- 更新项目状态
- 生成统计报告
- 备份数据

## 能力边界
- ✅ 日志记录
- ✅ 状态更新
- ✅ 统计汇总
- ❌ 不执行设计任务
- ❌ 不做质量检查

## 工作流程
1. 接收日志记录请求
2. 记录到飞书云文档
3. 更新项目状态
4. 生成统计报告

## 交互风格
- 及时记录
- 准确的状态
- 清晰的统计
EOF
    
    log "✅ Agent团队工作空间已初始化"
}

# ============================================================================
# 功能2: 任务分配
# =============================================================================

assign_task() {
    local task_type="$1"
    local task_description="$2"
    local task_priority="${3:-3}"
    local task_id="TASK-$(date +%s)"
    
    log "🎯 分配任务..."
    echo "任务ID: $task_id"
    echo "任务类型: $task_type"
    echo "优先级: $task_priority"
    echo "描述: $task_description"
    echo ""
    
    # 根据任务类型分配Agent
    case "$task_type" in
        *设计*|图纸*|CAD*|渲染*)
            agent="Builder（室内设计专家）"
            model="glm-4.7"
            ;;
        
        *代码*|编程*|脚本*|API*)
            agent="技术支持专家"
            model="gpt-oss-120b"
            ;;
        
        *日志*|记录*|统计*|汇总*)
            agent="Ops（小蓝）"
            model="glm-4.5-air"
            ;;
        
        *)
            agent="Orchestrator（大领导）"
            model="glm-4.7"
            ;;
    esac
    
    # 记录任务分配
    {
        echo "# 任务分配记录"
        echo ""
        echo "**任务ID**: $task_id"
        echo "**时间**: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "**Agent**: $agent"
        echo "**模型**: $model"
        echo "**优先级**: $task_priority"
        echo ""
        echo "## 任务详情"
        echo "$task_description"
        echo ""
        echo "## 下一步"
        echo "等待Agent确认开始执行..."
        echo ""
    } > "$SHARED_DIR/decisions/task_$task_id.md"
    
    log "✅ 任务已分配给: $agent"
    echo "💡 提示: 请$agent确认开始执行"
}

# ============================================================================
# 功能3: 更新任务状态
# =============================================================================

update_task_status() {
    local task_id="$1"
    local status="$2"
    local agent="$3"
    local comment="${4:-任务状态更新}"
    
    log "📊 更新任务状态: $task_id"
    
    # 更新决策文件
    {
        echo "## 状态更新"
        echo ""
        echo "**状态**: $status"
        "**Agent**: $agent"
        "**时间**: $(date '+%Y-%m-%d %H:%M:%S')"
        ""
        echo "### 备注"
        echo "$comment"
        echo ""
    } >> "$SHARED_DIR/decisions/task_$task_id.md"
    
    log "✅ 任务状态已更新"
}

# ============================================================================
# 功能4: 质量检查
# =============================================================================

quality_check() {
    local task_id="$1"
    local artifact_path="$2"
    
    log "🔍 质量检查任务..."
    
    # 检查文件
    if [ ! -f "$artifact_path" ]; then
        log "⚠️ 文件不存在: $artifact_path"
        return 1
    fi
    
    # 根据文件扩展名判断类型
    local file_ext="${artifact_path##*.}"
    local artifact_type=""
    
    case "$file_ext" in
        *.dwg|*.dxf|*.skp)
            artifact_type="设计文件"
            ;;
        *.py|*.js|*.sh|*.go)
            artifact_type="代码文件"
            ;;
        *.md|*.txt|*.doc)
            artifact_type="文档文件"
            ;;
        *)
            artifact_type="其他文件"
            ;;
    esac
    
    # 质量检查
    echo "🔍 检查文件类型: $artifact_type"
    echo "📄 文件路径: $artifact_path"
    echo ""
    
    case "$artifact_type" in
        "设计文件")
            echo "🏠 设计质量检查:"
            echo "  - 图层是否清晰"
            echo "  - 尺寸是否正确"
            echo "  - 文件命名规范"
            echo "  - 是否符合规范"
            ;;
        
        "代码文件")
            echo "💻 代码质量检查:"
            "  - 语法正确性"
            "  - 注释充分性"
            "  - 错误处理"
            "  - 命名规范"
            ;;
        
        "文档文件")
            echo "📝 文档质量检查:"
            "  - 内容完整性"
            "  - 格式正确性"
            "  - 信息准确性"
            "  - 语言流畅性"
            ;;
        
        *)
            echo "📋 通用质量检查"
            echo "  - 内容正确性"
            "  - 格式规范性"
            "  - 完整性"
            ;;
    esac
    
    # 检查结果
    echo ""
    read -p "质量检查结果 (✅通过 / ❌需要修改): " result
    echo ""
    
    if [ "$result" = "✅" ]; then
        update_task_status "$task_id" "Done" "Reviewer" "质量检查通过"
    else
        update_task_status "$task_id" "In Progress" "Builder" "质量检查未通过，需要修改"
    fi
}

# ============================================================================
# 主程序入口
# =============================================================================

case "${1:-help}" in
    init)
        init_team
        ;;
    
    assign)
        assign_task "$2" "$3"
        ;;
    
    update)
        update_task_status "$2" "$3" "$4" "$5"
        ;;
    
    quality)
        quality_check "$2" "$3"
        ;;
    
    *)
        echo "Agent团队编排脚本v1.0"
        echo "======================"
        echo ""
        echo "用法:"
        echo "  $0 init             # 初始化团队工作空间"
        echo "  $0 assign <类型> <描述> [优先级]"
        echo "  $0 update <任务ID> <状态> <Agent> [备注]"
        echo "  $0 quality-check <文件路径> [任务ID]"
        echo ""
        echo "任务类型:"
        echo "  - 设计: 室内设计、图纸、CAD"
        echo "  - 编程: 代码、脚本、API"
        "  - 日志: 记录、统计、汇总"
        "  - 通用: 其他任务"
        echo ""
        echo "Agent团队:"
        echo "  - Orchestrator: 大领导 🎯（编排者）"
        echo "  - Builder: 室内设计专家"
        echo "  - Reviewer: 质量检查"
        echo "  - Ops: 小蓝（日志管理）"
        echo ""
        echo "示例:"
        echo "  $0 init"
        echo "  $0 assign 设计 '修改3F会议室平面图' 高优先级"
        echo "  $0 update TASK-123456 InProgress Builder '正在绘制中...'"
        echo "  $0 quality-check /shared/artifacts/3f-meeting.dwg TASK-123456"
        exit 0
        ;;
esac

exit 0
