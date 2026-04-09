#!/bin/bash
# Session Memory v0.2 - 思考-输出分离版
# 基于 Claude Code Compaction 设计：<analysis> 草稿区 + 后处理剥离

set -e

echo "📝 Session Memory v0.2 - 思考-输出分离版"
echo "⏰ 时间: $(date)"

# 配置
MEMORY_DIR="/root/.openclaw/workspace/memory"
SESSION_MEMORY_FILE="$MEMORY_DIR/session-memory.md"
STATE_FILE="$MEMORY_DIR/.session-memory-state.json"

# 渐进式笔记配置
UPDATE_INTERVAL=5              # 每 N 轮对话更新一次
MAX_CONVERSATION_LENGTH=20     # 超过此长度开始渐进式笔记

# =============================================================================
# 📊 检测会话状态
# =============================================================================

detect_session_state() {
    echo ""
    echo "🔍 检测会话状态..."
    
    # 读取状态
    if [ -f "$STATE_FILE" ]; then
        LAST_UPDATE_COUNT=$(grep -o '"last_update_count": [0-9]*' "$STATE_FILE" | grep -o '[0-9]*' 2>/dev/null || echo "0")
        echo "📊 上次更新时的对话数: $LAST_UPDATE_COUNT"
    else
        LAST_UPDATE_COUNT=0
        echo "📊 首次运行"
    fi
    
    # 获取当前对话数（使用今日日志作为代理）
    TODAY_LOG=$(find "$MEMORY_DIR" -name "2026-$(date +%m-%d).md" -type f)
    
    if [ -n "$TODAY_LOG" ]; then
        # 统计对话条目数（简化版：统计标题数量）
        CURRENT_COUNT=$(grep -c "^##" "$TODAY_LOG" 2>/dev/null || echo "0")
        echo "📊 当前对话数: $CURRENT_COUNT"
    else
        CURRENT_COUNT=0
        echo "📊 当前对话数: 0"
    fi
    
    # 计算新增对话数
    NEW_CONVERSATIONS=$((CURRENT_COUNT - LAST_UPDATE_COUNT))
    echo "➕ 新增对话: $NEW_CONVERSATIONS"
    
    # 判断是否需要更新
    if [ $CURRENT_COUNT -ge $MAX_CONVERSATION_LENGTH ]; then
        echo "✅ 会话长度达到阈值 ($MAX_CONVERSATION_LENGTH)，启用渐进式笔记"
        SHOULD_UPDATE=true
    elif [ $NEW_CONVERSATIONS -ge $UPDATE_INTERVAL ]; then
        echo "✅ 新增对话达到阈值 ($UPDATE_INTERVAL)，更新渐进式笔记"
        SHOULD_UPDATE=true
    else
        echo "⏸️ 未达到更新阈值，跳过"
        SHOULD_UPDATE=false
    fi
}

# =============================================================================
# 📝 生成渐进式笔记（应用思考-输出分离）
# =============================================================================

generate_progressive_notes() {
    echo ""
    echo "📝 生成渐进式笔记（思考-输出分离版）..."
    
    # 读取今日日志
    TODAY_LOG=$(find "$MEMORY_DIR" -name "2026-$(date +%m-%d).md" -type f)
    
    if [ -z "$TODAY_LOG" ]; then
        echo "⚠️ 未找到今日日志"
        return
    fi
    
    # 提取关键信息
    echo "🔍 提取关键信息..."
    
    # 1. 提取决策（TODO、决定、记住）
    DECISIONS=$(grep -E "^\- \*\*.*\*\*:.*(?:TODO|决定|记住|记住)" "$TODAY_LOG" 2>/dev/null || echo "")
    
    # 2. 提取错误和教训
    ERRORS=$(grep -E "错误|失败|问题" "$TODAY_LOG" 2>/dev/null || echo "")
    
    # 3. 提取重要事件
    EVENTS=$(grep -E "^#{2,3}" "$TODAY_LOG" 2>/dev/null | head -10)
    
    # ⭐ 应用"思考-输出分离"
    cat > "$SESSION_MEMORY_FILE" << NOTES
# Session Memory - 渐进式笔记（思考-输出分离版）

<analysis>
请先在草稿区思考：
1. 回顾最近的对话内容
2. 识别关键信息（决策、错误、事件）
3. 组织结构化笔记

当前对话数：$CURRENT_COUNT
新增对话：$NEW_CONVERSATIONS
决策数量：$(echo "$DECISIONS" | grep -c "^-")
错误数量：$(echo "$ERRORS" | grep -c "^-")
事件数量：$(echo "$EVENTS" | wc -l)
</analysis>

<summary>
## 会话标题

### 📊 对话统计
- **当前对话数**: $CURRENT_COUNT
- **新增对话**: $NEW_CONVERSATIONS
- **更新频率**: 每 $UPDATE_INTERVAL 轮对话更新一次

### 🎯 当前工作状态
$(echo "$DECISIONS" | head -5)

### ⚠️ 错误和修正
$(echo "$ERRORS" | head -5)

### 📅 重要事件
$(echo "$EVENTS" | head -10)

### 🔧 下一步行动
- 继续监控对话进展
- 在达到 $UPDATE_INTERVAL 轮对话时再次更新
- 在超过 $MAX_CONVERSATION_LENGTH 轮时启用渐进式笔记

---

**最后更新**: $(date -Iseconds)
**下次更新**: 再增加 $UPDATE_INTERVAL 轮对话或达到 $MAX_CONVERSATION_LENGTH 轮
</summary>
NOTES

    # ⭐ 后处理：剥离草稿区（重要！）
    # 第一步：删除 <analysis> 标签及其内容
    sed -i '/<analysis>/,/<\/analysis>/d' "$SESSION_MEMORY_FILE"
    
    # 第二步：把 <summary> XML 标签替换成可读的纯文本标题
    sed -i 's/<summary>/Summary:/g' "$SESSION_MEMORY_FILE"
    
    # 第三步：清理多余空行
    sed -i '/^\s*$/d' "$SESSION_MEMORY_FILE"
    
    echo "✅ 渐进式笔记已生成（思考-输出分离版）: $SESSION_MEMORY_FILE"
}

# =============================================================================
# 💾 更新状态
# =============================================================================

update_state() {
    echo ""
    echo "💾 更新状态..."
    
    # 获取当前对话数
    TODAY_LOG=$(find "$MEMORY_DIR" -name "2026-$(date +%m-%d).md" -type f)
    CURRENT_COUNT=0
    
    if [ -n "$TODAY_LOG" ]; then
        CURRENT_COUNT=$(grep -c "^##" "$TODAY_LOG" 2>/dev/null || echo "0")
    fi
    
    cat > "$STATE_FILE" << STATE
{
  "last_update_time": "$(date -Iseconds)",
  "last_update_count": $CURRENT_COUNT,
  "update_interval": $UPDATE_INTERVAL,
  "max_conversation_length": $MAX_CONVERSATION_LENGTH,
  "version": "0.2-thinking-output-separation",
  "features": ["thinking-output-separation", "circuit-breaker"]
}
STATE
    
    echo "✅ 状态已更新"
}

# =============================================================================
# 🚀 主流程
# =============================================================================

main() {
    # Step 1: 检测会话状态
    detect_session_state
    
    # Step 2: 判断是否需要更新
    if [ "$SHOULD_UPDATE" = false ]; then
        echo ""
        echo "⏸️ Session Memory 跳过更新"
        exit 0
    fi
    
    # Step 3: 生成渐进式笔记（思考-输出分离）
    generate_progressive_notes
    
    # Step 4: 更新状态
    update_state
    
    echo ""
    echo "🎉 Session Memory v0.2 更新完成！"
}

# 执行主流程
main
