#!/bin/bash
# Session Memory 渐进式笔记系统
# 基于 Open-ClaudeCode 设计：长对话中实时更新笔记，防止失忆

set -e

echo "📝 Session Memory 渐进式笔记系统"
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
# 📝 生成渐进式笔记
# =============================================================================

generate_progressive_notes() {
    echo ""
    echo "📝 生成渐进式笔记..."
    
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
    
    # 生成笔记内容
    cat > "$SESSION_MEMORY_FILE" << NOTES
# Session Memory - 渐进式笔记

**更新时间**: $(date -Iseconds)
**会话长度**: $(grep -c "^##" "$TODAY_LOG") 轮

## 🎯 关键决策

\`\`\`
$DECISIONS
\`\`\`

## ⚠️ 错误与教训

\`\`\`
$ERRORS
\`\`\`

## 📅 重要事件

\`\`\`
$EVENTS
\`\`\`

## 📊 会话统计

- 总对话数: $(grep -c "^##" "$TODAY_LOG")
- 用户消息: $(grep -c "用户:" "$TODAY_LOG" 2>/dev/null || echo "N/A")
- 系统消息: $(grep -c "系统:" "$TODAY_LOG" 2>/dev/null || echo "N/A")

---

**下次更新**: 再增加 $UPDATE_INTERVAL 轮对话或达到 $MAX_CONVERSATION_LENGTH 轮
NOTES

    echo "✅ 渐进式笔记已生成: $SESSION_MEMORY_FILE"
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
  "version": "1.0-progressive"
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
    
    # Step 3: 生成渐进式笔记
    generate_progressive_notes
    
    # Step 4: 更新状态
    update_state
    
    echo ""
    echo "🎉 Session Memory 更新完成！"
}

# 执行主流程
main
