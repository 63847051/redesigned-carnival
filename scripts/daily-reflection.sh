#!/bin/bash
# =====================================================
# 深度反思脚本 - daily-reflection.sh
# 彬子记忆系统 - 第三道防线第二部分：01:00 执行
# 功能：读取反思素材，深度反思，知识回写
# =====================================================

set -e

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
LOG_FILE="$WORKSPACE/logs/daily-reflection.log"

mkdir -p "$MEMORY_DIR/reflections" "$WORKSPACE/logs"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "========== 深度反思开始 =========="

get_yesterday_date() {
    date -d "yesterday" '+%Y-%m-%d'
}

YESTERDAY=$(get_yesterday_date)
PREP_FILE="$MEMORY_DIR/${YESTERDAY}-reflection-prep.md"
REFLECTION_FILE="$MEMORY_DIR/reflections/${YESTERDAY}.md"

log "日期: $YESTERDAY"
log "素材文件: $PREP_FILE"

if [ ! -f "$PREP_FILE" ]; then
    log "警告: 反思素材文件不存在，尝试生成..."
    python3 "$WORKSPACE/scripts/daily-sync.py"
fi

if [ ! -f "$PREP_FILE" ]; then
    log "错误: 无法生成反思素材，跳过"
    exit 1
fi

# 读取反思素材
log "读取反思素材..."
PREP_CONTENT=$(cat "$PREP_FILE")

# 分析素材
log "分析反思素材..."

# 统计各类别
count_category() {
    echo "$1" | grep -A 20 "^## $2" | grep "^[0-9]\." | wc -l
}
DECISIONS=$(count_category "$PREP_CONTENT" "DECISIONS")
COMPLETIONS=$(count_category "$PREP_CONTENT" "COMPLETIONS")
PROBLEMS=$(count_category "$PREP_CONTENT" "PROBLEMS")
LESSONS=$(count_category "$PREP_CONTENT" "LESSONS")

log "统计: 决策=$DECISIONS, 完成=$COMPLETIONS, 问题=$PROBLEMS, 教训=$LESSONS"

# 生成反思文件
log "生成反思文件..."

mkdir -p "$MEMORY_DIR/reflections"

cat > "$REFLECTION_FILE" << EOF
# 深度反思 - $YESTERDAY

**反思时间**: $(date '+%Y-%m-%d %H:%M:%S')

---

## 📊 今日概览

| 类别 | 数量 |
|------|------|
| 决策 | $DECISIONS |
| 完成 | $COMPLETIONS |
| 问题 | $PROBLEMS |
| 教训 | $LESSONS |

---

## 🎯 关键决策回顾

$(grep -A 20 "^## DECISIONS" "$PREP_FILE" 2>/dev/null | head -25 || echo "*无记录*")

---

## ✅ 完成事项

$(grep -A 20 "^## COMPLETIONS" "$PREP_FILE" 2>/dev/null | head -25 || echo "*无记录*")

---

## 🔧 问题与解决方案

$(grep -A 20 "^## PROBLEMS" "$PREP_FILE" 2>/dev/null | head -25 || echo "*无记录*")

---

## 📚 经验教训

$(grep -A 20 "^## LESSONS" "$PREP_FILE" 2>/dev/null | head -25 || echo "*无记录*")

---

## 💡 反思洞察

EOF

# 添加自动生成的洞察
if [ "$PROBLEMS" -gt 0 ]; then
    echo "- 发现 $PROBLEMS 个问题，需要关注和改进" >> "$REFLECTION_FILE"
fi

if [ "$LESSONS" -gt 0 ]; then
    echo "- 记录了 $LESSONS 条经验教训，有助于未来避免重复错误" >> "$REFLECTION_FILE"
fi

if [ "$DECISIONS" -gt 0 ]; then
    echo "- 做出 $DECISIONS 个重要决策，已记录备查" >> "$REFLECTION_FILE"
fi

if [ "$COMPLETIONS" -gt 0 ]; then
    echo "- 完成 $COMPLETIONS 项任务，工作效率良好" >> "$REFLECTION_FILE"
fi

echo "" >> "$REFLECTION_FILE"
echo "---" >> "$REFLECTION_FILE"
echo "*由 daily-reflection.sh 自动生成*" >> "$REFLECTION_FILE"

log "反思文件已写入: $REFLECTION_FILE"

# 更新知识库索引
update_knowledge_index() {
    local index_file="$MEMORY_DIR/INDEX.md"
    
    if [ ! -f "$index_file" ]; then
        cat > "$index_file" << EOF
# 记忆索引

## 反思记录

EOF
    fi
    
    echo "- [$YESTERDAY](reflections/$YESTERDAY.md)" >> "$index_file"
    log "更新知识索引"
}

update_knowledge_index

log "========== 深度反思完成 =========="
