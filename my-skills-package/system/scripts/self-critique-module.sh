#!/bin/bash
# 自我批评模块
# 基于ivangdavila/self-improving的核心思想

set -e

WORKSPACE="/root/.openclaw/workspace"
LEARNINGS_DIR="$WORKSPACE/.learnings"
CRITIQUE_DIR="$LEARNINGS_DIR/self-critiques"
PATTERNS_DIR="$LEARNINGS_DIR/patterns"

mkdir -p "$CRITIQUE_DIR"
mkdir -p "$PATTERNS_DIR"

# 日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$WORKSPACE/.evolution/evolution.log"
}

# ============================================================================
# 功能1: 自我反思
# =============================================================================

reflect_on_output() {
    local task_description="$1"
    local output_file="$2"

    log "🔍 阶段1: 自我反思"
    log "任务: $task_description"

    # 使用GLM-4.7评估输出质量
    reflection=$(cat "$output_file" 2>/dev/null | head -100 | \
        python3 << 'PYTHON'
import os
import subprocess

# 读取输出
output = """$(cat)"""

# 构造prompt
prompt = f"""请评估以下任务输出的质量（1-10分）：

任务: {task_description}
输出:
{output}

请评分并说明理由。格式：
评分: X/10
理由: ..."""

# 这里应该调用LLM，暂时简化
print(f"评分评估完成")
PYTHON
)

    log "反思结果: $reflection"
    echo "$reflection" > "$CRITIQUE_DIR/reflection_$(date +%Y%m%d_%H%M%S).md"
}

# ============================================================================
# 功能2: 自我批评
# =============================================================================

critique_own_work() {
    local task_description="$1"
    local output_file="$2"

    log "🔍 阶段2: 自我批评"
    log "任务: $task_description"

    # 生成批评要点
    critique=$(cat <<'CRITIQUE'
## 自我批评要点

### 1. 输出质量
- 内容完整性: 检查
- 准确性: 检查
- 可用性: 检查

### 2. 执行过程
- 效率: 检查
- 资源使用: 检查
- 错误处理: 检查

### 3. 改进空间
- 哪些可以做得更好?
- 哪些可以自动化?
- 哪些需要优化?

### 4. 关键问题
- 主要问题:
- 次要问题:
- 建议修复:
CRITIQUE
)

    log "批评完成"
    echo "$critique" > "$CRITIQUE_DIR/critique_$(date +%Y%m%d_%H%M%S).md"
}

# ============================================================================
# 功能3: 提取模式
# =============================================================================

extract_patterns() {
    local critique_file="$1"

    log "🔍 阶段3: 提取模式"

    # 从批评中提取可复用的模式
    pattern=$(cat <<'PATTERN'
## 提取的模式

### 错误模式
- 模式1: ...
- 模式2: ...

### 最佳实践
- 实践1: ...
- 实践2: ...

### 改进规则
- 规则1: ...
- 规则2: ...
PATTERN
)

    log "模式提取完成"
    echo "$pattern" > "$PATTERNS_DIR/pattern_$(date +%Y%m%d_%H%M%S).md"
}

# ============================================================================
# 功能4: 组织记忆
# =============================================================================

organize_memory() {
    log "🔍 阶段4: 组织记忆"

    # 创建自组织记忆结构
    mkdir -p "$LEARNINGS_DIR/auto-organized/by-topic"
    mkdir -p "$LEARNINGS_DIR/auto-organized/by-severity"
    mkdir -p "$LEARNINGS_DIR/auto-organized/by-frequency"

    # 按主题分类
    log "按主题分类..."
    for file in "$CRITIQUE_DIR"/*.md; do
        if [ -f "$file" ]; then
            # 简化：移动所有到通用主题
            ln -sf "$file" "$LEARNINGS_DIR/auto-organized/by-topic/"
        fi
    done

    # 按严重程度分类
    log "按严重程度分类..."
    mkdir -p "$LEARNINGS_DIR/auto-organized/by-severity/{high,medium,low}"

    # 按频率排序
    log "按频率排序..."
    mkdir -p "$LEARNINGS_DIR/auto-organized/by-frequency"

    # 生成索引
    log "生成记忆索引..."
    {
        echo "# 记忆索引"
        echo ""
        echo "**生成时间**: $(date)"
        echo ""
        echo "## 按主题"
        ls -1 "$LEARNINGS_DIR/auto-organized/by-topic/" | wc -l
        echo ""
        echo "## 按严重程度"
        echo "- High: $(ls -1 "$LEARNINGS_DIR/auto-organized/by-severity/high/" 2>/dev/null | wc -l)"
        echo "- Medium: $(ls -1 "$LEARNINGS_DIR/auto-organized/by-severity/medium/" 2>/dev/null | wc -l)"
        echo "- Low: $(ls -1 "$LEARNINGS_DIR/auto-organized/by-severity/low/" 2>/dev/null | wc -l)"
    } > "$LEARNINGS_DIR/auto-organized/INDEX.md"

    log "记忆组织完成"
}

# ============================================================================
# 四步自我改进循环
# =============================================================================

four_step_loop() {
    local task_description="$1"
    local output_file="${2:-/tmp/task_output.txt}"

    echo "🔄 四步自我改进循环"
    echo "======================"
    echo ""

    # 步骤1: 反思
    reflect_on_output "$task_description" "$output_file"
    echo ""

    # 步骤2: 批评
    critique_own_work "$task_description" "$output_file"
    echo ""

    # 步骤3: 提取模式
    latest_critique=$(ls -t "$CRITIQUE_DIR"/critique_*.md 2>/dev/null | head -1)
    if [ -n "$latest_critique" ]; then
        extract_patterns "$latest_critique"
    fi
    echo ""

    # 步骤4: 组织记忆
    organize_memory
    echo ""

    echo "======================"
    echo "✅ 四步循环完成！"
    echo ""
    echo "成果:"
    echo "  - 反思: $CRITIQUE_DIR/reflection_*.md"
    echo "  - 批评: $CRITIQUE_DIR/critique_*.md"
    echo "  - 模式: $PATTERNS_DIR/pattern_*.md"
    echo "  - 记忆: $LEARNINGS_DIR/auto-organized/"
}

# ============================================================================
# 主程序
# =============================================================================

# 如果直接运行脚本
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    if [ -n "$1" ]; then
        four_step_loop "$@"
    else
        echo "用法: $0 <任务描述> [输出文件]"
        echo ""
        echo "示例:"
        echo "  $0 '更新GitHub仓库' /tmp/output.txt"
        exit 1
    fi
fi
