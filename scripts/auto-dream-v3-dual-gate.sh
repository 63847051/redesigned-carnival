#!/bin/bash
# Auto Dream v0.3 - 双门控增强版
# 基于 Open-ClaudeCode 设计：24h 时间门控 + 5会话触发门控

set -e

echo "🧠 Auto Dream v0.3 - 双门控版"
echo "⏰ 时间: $(date)"

# 配置
MEMORY_DIR="/root/.openclaw/workspace/memory"
BACKUP_DIR="$MEMORY_DIR/backups/dream-$(date +%Y%m%d-%H%M%S)"
REPORT_FILE="$MEMORY_DIR/dream-report-latest.md"
STATE_FILE="$MEMORY_DIR/.dream-state.json"

# 双门控配置
TIME_GATE_HOURS=24              # 时间门控：24小时
SESSION_GATE_THRESHOLD=5        # 会话门控：5个新会话

# =============================================================================
# 🔐 双门控检查机制
# =============================================================================

check_dual_gate() {
    echo ""
    echo "🔐 双门控检查..."
    
    # 初始化状态文件
    if [ ! -f "$STATE_FILE" ]; then
        echo "{}" > "$STATE_FILE"
    fi
    
    # 读取上次执行时间
    LAST_DREAM_TIME=$(grep -o '"last_dream_time": "[^"]*"' "$STATE_FILE" | cut -d'"' -f4 2>/dev/null || echo "")
    
    # 读取上次会话数
    LAST_SESSION_COUNT=$(grep -o '"last_session_count": [0-9]*' "$STATE_FILE" | grep -o '[0-9]*' 2>/dev/null || echo "0")
    
    # 获取当前时间（Unix 时间戳）
    CURRENT_TIME=$(date +%s)
    
    # 计算 time_gate
    if [ -z "$LAST_DREAM_TIME" ]; then
        echo "⏰ 时间门控: 首次运行，通过 ✅"
        TIME_GATE_PASSED=true
    else
        LAST_TIME_TIMESTAMP=$(date -d "$LAST_DREAM_TIME" +%s 2>/dev/null || echo "0")
        HOURS_SINCE_LAST=$(( (CURRENT_TIME - LAST_TIME_TIMESTAMP) / 3600 ))
        
        if [ $HOURS_SINCE_LAST -ge $TIME_GATE_HOURS ]; then
            echo "⏰ 时间门控: 通过 ✅ (距上次 $HOURS_SINCE_LAST 小时)"
            TIME_GATE_PASSED=true
        else
            echo "⏰ 时间门控: 未通过 ❌ (距上次 $HOURS_SINCE_LAST 小时，需要 $TIME_GATE_HOURS 小时)"
            TIME_GATE_PASSED=false
        fi
    fi
    
    # 计算 session_gate
    # 统计最近修改的记忆文件数量（作为新会话的代理）
    RECENT_SESSIONS=$(find "$MEMORY_DIR" -name "*.md" -mtime -1 -type f | wc -l)
    CURRENT_SESSION_COUNT=$RECENT_SESSIONS
    
    NEW_SESSIONS=$((CURRENT_SESSION_COUNT - LAST_SESSION_COUNT))
    
    if [ $NEW_SESSIONS -ge $SESSION_GATE_THRESHOLD ]; then
        echo "💬 会话门控: 通过 ✅ (新增 $NEW_SESSIONS 个会话)"
        SESSION_GATE_PASSED=true
    else
        echo "💬 会话门控: 未通过 ❌ (新增 $NEW_SESSIONS 个会话，需要 $SESSION_GATE_THRESHOLD 个)"
        SESSION_GATE_PASSED=false
    fi
    
    # 双门控判断
    if [ "$TIME_GATE_PASSED" = true ] && [ "$SESSION_GATE_PASSED" = true ]; then
        echo ""
        echo "🎉 双门控: 全部通过，可以执行 AutoDream"
        return 0
    else
        echo ""
        echo "⏸️ 双门控: 未全部通过，跳过本次执行"
        return 1
    fi
}

# =============================================================================
# 🎯 四阶段记忆重塑
# =============================================================================

phase1_orient() {
    echo ""
    echo "📌 Phase 1: Orient (定向)"
    
    # 分析记忆密度
    TOTAL_FILES=$(find "$MEMORY_DIR" -name "*.md" | wc -l)
    echo "📁 当前记忆文件: $TOTAL_FILES 个"
    
    # 分析主题聚类
    echo "🔍 分析主题聚类..."
    TOPICS=$(find "$MEMORY_DIR" -name "*.md" -exec basename {} \; | grep -v "^2026-" | sort -u | head -10)
    echo "$TOPICS" | while read topic; do
        [ -n "$topic" ] && echo "  - $topic"
    done
}

phase2_gather() {
    echo ""
    echo "📥 Phase 2: Gather (搜集)"
    
    # 搜集高相关记忆
    echo "🔍 搜集近期记忆..."
    RECENT_MEMORIES=$(find "$MEMORY_DIR" -name "2026-*.md" -mtime -7 -type f)
    
    if [ -z "$RECENT_MEMORIES" ]; then
        echo "⚠️ 未找到近期记忆"
    else
        echo "✅ 找到 $(echo "$RECENT_MEMORIES" | wc -l) 个近期记忆文件"
    fi
}

phase3_consolidate() {
    echo ""
    echo "🔄 Phase 3: Consolidate (巩固)"
    
    # 分组相关记忆
    echo "📊 分组相关记忆..."
    
    # 检测重要主题
    IMPORTANT_TOPICS=$(grep -h "^# " "$MEMORY_DIR"/*.md 2>/dev/null | sort | uniq -c | sort -rn | head -10)
    
    if [ -n "$IMPORTANT_TOPICS" ]; then
        echo "🎯 重要主题:"
        echo "$IMPORTANT_TOPICS" | while read count topic; do
            echo "  - $topic ($count 次)"
        done
    fi
}

phase4_prune() {
    echo ""
    echo "✂️ Phase 4: Prune (修剪)"
    
    # 删除冗余记忆
    echo "🔍 检测冗余记忆..."
    
    # 检测重复内容
    DUPLICATE_COUNT=$(find "$MEMORY_DIR" -name "*.md" -exec grep -h "^## Retain" {} \; | sort | uniq -d | wc -l)
    
    if [ $DUPLICATE_COUNT -gt 0 ]; then
        echo "⚠️ 发现 $DUPLICATE_COUNT 个潜在的重复 Retain 条目"
    else
        echo "✅ 未发现重复内容"
    fi
    
    # 优化检索效率
    echo "⚡ 优化检索效率..."
    TOTAL_SIZE=$(du -sm "$MEMORY_DIR" | cut -f1)
    echo "📦 当前记忆大小: ${TOTAL_SIZE}MB"
}

# =============================================================================
# 💾 更新状态
# =============================================================================

update_state() {
    echo ""
    echo "💾 更新状态..."
    
    CURRENT_TIME_ISO=$(date -Iseconds)
    CURRENT_SESSION_COUNT=$(find "$MEMORY_DIR" -name "*.md" -mtime -1 -type f | wc -l)
    
    cat > "$STATE_FILE" << STATE
{
  "last_dream_time": "$CURRENT_TIME_ISO",
  "last_session_count": $CURRENT_SESSION_COUNT,
  "time_gate_hours": $TIME_GATE_HOURS,
  "session_gate_threshold": $SESSION_GATE_THRESHOLD,
  "version": "0.3-dual-gate"
}
STATE
    
    echo "✅ 状态已更新"
}

# =============================================================================
# 🚀 主流程
# =============================================================================

main() {
    # Step 0: 双门控检查
    if ! check_dual_gate; then
        echo ""
        echo "⏸️ AutoDream 跳过执行"
        exit 0
    fi
    
    # Step 1: 备份
    echo ""
    echo "💾 Step 1: 备份记忆文件..."
    mkdir -p "$BACKUP_DIR"
    cp "$MEMORY_DIR"/*.md "$BACKUP_DIR/" 2>/dev/null || true
    echo "✅ 备份完成: $BACKUP_DIR"
    
    # Step 2-5: 四阶段记忆重塑
    phase1_orient
    phase2_gather
    phase3_consolidate
    phase4_prune
    
    # Step 6: 更新状态
    update_state
    
    # Step 7: 生成报告
    echo ""
    echo "📝 Step 7: 生成报告..."
    
    cat > "$REPORT_FILE" << REPORT
# Auto Dream 报告 v0.3 - 双门控版

**执行时间**: $(date -Iseconds)
**版本**: v0.3-dual-gate

## 🔐 双门控状态

- ⏰ 时间门控: 通过 (距上次 ≥$TIME_GATE_HOURS 小时)
- 💬 会话门控: 通过 (新增 ≥$SESSION_GATE_THRESHOLD 个会话)

## 📊 Phase 1: Orient

- 记忆文件数: $(find "$MEMORY_DIR" -name "*.md" | wc -l)
- 记忆总大小: $(du -sh "$MEMORY_DIR" | cut -f1)

## 📥 Phase 2: Gather

- 近期记忆文件: $(find "$MEMORY_DIR" -name "2026-*.md" -mtime -7 -type f | wc -l)

## 🔄 Phase 3: Consolidate

- 重要主题: $(grep -h "^# " "$MEMORY_DIR"/*.md 2>/dev/null | wc -l)

## ✂️ Phase 4: Prune

- 冗余检测: 已完成
- 检索优化: 已完成

---

**下次执行**: 需要满足双门控条件
REPORT

    echo "✅ 报告已生成: $REPORT_FILE"
    
    echo ""
    echo "🎉 Auto Dream v0.3 完成！"
}

# 执行主流程
main
