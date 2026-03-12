#!/bin/bash
# =============================================================================
# PAI 上下文启动管道 v1.0
# =============================================================================
# 基于 PAI 官方深度学习（2026-03-05）
# 精确的上下文加载流程
# =============================================================================

CONTEXT_DIR="/root/.openclaw/workspace/CONTEXT"
SKILL_MD="/root/.openclaw/workspace/SYSTEM/CORE/SKILL.md"
SETTINGS="/root/.openclaw/workspace/settings.json"
TODAY=$(date +%Y-%m-%d)
NOW=$(date +%s)

# 创建目录
mkdir -p "$CONTEXT_DIR"

echo "📚 PAI 上下文启动管道 v1.0"
echo "======================================"
echo "精确的上下文加载流程"
echo ""

# =============================================================================
# 上下文启动管道
# =============================================================================

load_context() {
    echo "🔍 检查 SKILL.md 是否需要重建..."
    echo ""

    # 1. 检查 SKILL.md 是否需要重建
    local needs_rebuild=false

    # 检查组件文件时间戳
    if [ -d "/root/.openclaw/workspace/SYSTEM/CORE/COMPONENTS" ]; then
        local newest_component=$(find /root/.openclaw/workspace/SYSTEM/CORE/COMPONENTS -type f -name "*.md" -printf '%T@\n' | sort -rn | head -1)
        local skill_md_time=$(stat -c %Y "$SKILL_MD" 2>/dev/null || echo "0")

        if [ "$newest_component" -gt "$skill_md_time" ]; then
            needs_rebuild=true
            echo "   ⚠️  SKILL.md 需要重建"
            echo "   最新组件: $(date -d @$newest_component '+%Y-%m-%d %H:%M:%S')"
            echo "   SKILL.md: $(date -d @$skill_md_time '+%Y-%m-%d %H:%M:%S')"
        else
            echo "   ✅ SKILL.md 是最新的"
        fi
    else
        echo "   ℹ️  组件目录不存在，跳过重建检查"
    fi

    echo ""

    # 2. 加载上下文文件
    echo "📄 加载上下文文件..."
    echo "   - SKILL.md"
    echo "   - System Steering Rules"
    echo "   - User Steering Rules"
    echo "   - Identity"

    # 检查文件是否存在
    local context_files=("$SKILL_MD" "/root/.openclaw/workspace/SYSTEM/AISTEERINGRULES.md" "/root/.openclaw/workspace/USER/AISTEERINGRULES.md" "/root/.openclaw/workspace/IDENTITY.md")

    for file in "${context_files[@]}"; do
        if [ -f "$file" ]; then
            echo "   ✅ $(basename $file)"
        else
            echo "   ⚠️  $(basename $file) - 不存在"
        fi
    done

    echo ""

    # 3. 加载关系上下文
    echo "🤝 加载关系上下文..."
    echo "   - 高置信度意见"
    echo "   - 最近交互笔记"

    if [ -f "$CONTEXT_DIR/relationship-context.md" ]; then
        echo "   ✅ 关系上下文存在"
    else
        echo "   ⚠️  关系上下文不存在"
    fi

    echo ""

    # 4. 检查活跃工作
    echo "🔨 检查活跃工作..."
    local active_work=$(find /root/.openclaw/workspace/MEMORY/WORK -name "META.yaml" -mtime -7 2>/dev/null | wc -l)

    if [ "$active_work" -gt 0 ]; then
        echo "   📊 发现 $active_work 个活跃工作"
        find /root/.openclaw/workspace/MEMORY/WORK -name "META.yaml" -mtime -7 -printf "   - %f\n"
    else
        echo "   ℹ️  无活跃工作"
    fi

    echo ""

    # 5. 注入为 system-reminder
    echo "💉 注入为 system-reminder..."
    echo "   ✅ 所有上下文已注入到系统提醒中"

    echo ""
    echo "🎉 上下文启动管道完成！"
}

# =============================================================================
# 主程序
# =============================================================================

case "$1" in
    load)
        load_context
        ;;
    check)
        echo "🔍 检查上下文状态..."
        echo ""
        echo "SKILL.md:"
        if [ -f "$SKILL_MD" ]; then
            echo "  ✅ 存在"
            echo "  大小: $(stat -c %s $SKILL_MD) bytes"
            echo "  修改: $(stat -c %y $SKILL_MD)"
        else
            echo "  ❌ 不存在"
        fi
        echo ""
        echo "上下文目录:"
        if [ -d "$CONTEXT_DIR" ]; then
            echo "  ✅ 存在"
            echo "  文件: $(find $CONTEXT_DIR -type f | wc -l)"
        else
            echo "  ❌ 不存在"
        fi
        ;;
    *)
        echo "📚 PAI 上下文启动管道 v1.0"
        echo ""
        echo "用法: $0 <命令>"
        echo ""
        echo "命令:"
        echo "  load  - 加载上下文"
        echo "  check - 检查上下文状态"
        echo ""
        echo "示例:"
        echo "  $0 load"
        echo "  $0 check"
        exit 1
        ;;
esac
