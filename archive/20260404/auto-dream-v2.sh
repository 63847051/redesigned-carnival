#!/bin/bash
# Auto Dream v0.2 - 基于 Open-ClaudeCode 源码学习

set -e

MEMORY_DIR="/root/.openclaw/workspace/memory"
LOCK_FILE="$MEMORY_DIR/.dream-lock"
LAST_SCAN_FILE="$MEMORY_DIR/.last-scan"
LAST_CONSOLIDATED_FILE="$MEMORY_DIR/.last-consolidated"
BACKUP_DIR="$MEMORY_DIR/backups/dream-$(date +%Y%m%d-%H%M%S)"
REPORT_FILE="$MEMORY_DIR/dream-report-latest.md"

# 配置
MIN_HOURS=24
MIN_SESSIONS=5
SCAN_INTERVAL=600  # 10 分钟

echo "🧠 Auto Dream v0.2 开始..."
echo "⏰ 时间: $(date)"

# --- 锁门 ---
if [ -f "$LOCK_FILE" ]; then
  echo "⚠️ Auto Dream 正在运行中"
  exit 1
fi

touch "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

# --- 扫描节流 ---
if [ -f "$LAST_SCAN_FILE" ]; then
  last_scan=$(stat -c %Y "$LAST_SCAN_FILE" 2>/dev/null || echo 0)
  now=$(date +%s)
  diff=$((now - last_scan))
  
  if [ $diff -lt $SCAN_INTERVAL ]; then
    echo "⏰ 扫描节流：距上次扫描仅 ${diff}s"
    exit 0
  fi
fi

touch "$LAST_SCAN_FILE"

# --- 时间门 ---
if [ -f "$LAST_CONSOLIDATED_FILE" ]; then
  last_consolidated=$(stat -c %Y "$LAST_CONSOLIDATED_FILE" 2>/dev/null || echo 0)
  now=$(date +%s)
  hours_since=$(( (now - last_consolidated) / 3600 ))
  
  if [ $hours_since -lt $MIN_HOURS ]; then
    echo "⏰ 时间门：距上次整理仅 ${hours_since}h，需要 ${MIN_HOURS}h"
    exit 0
  fi
fi

# --- 会话门 ---
SESSIONS_DIR="/root/.openclaw/agents/main/sessions"
if [ -d "$SESSIONS_DIR" ]; then
  recent_sessions=$(find "$SESSIONS_DIR" -name "*.jsonl" -mtime -1 | wc -l)
  
  if [ $recent_sessions -lt $MIN_SESSIONS ]; then
    echo "📊 会话门：仅 ${recent_sessions} 个会话，需要 ${MIN_SESSIONS} 个"
    exit 0
  fi
fi

# --- 开始整理 ---
echo "✅ 所有条件满足，开始整理..."

# Step 1: 备份
echo "💾 Step 1: 备份..."
mkdir -p "$BACKUP_DIR"
cp "$MEMORY_DIR"/*.md "$BACKUP_DIR/" 2>/dev/null || true
echo "✅ 备份完成: $BACKUP_DIR"

# Step 2: 时间标准化
echo "📅 Step 2: 标准化时间..."
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)
LAST_WEEK=$(date -d "last week" +%Y-%m-%d)
TODAY=$(date +%Y-%m-%d)

COUNT_YESTERDAY=$(find "$MEMORY_DIR" -name "*.md" -exec grep -l "昨天" {} \; 2>/dev/null | wc -l)
COUNT_LAST_WEEK=$(find "$MEMORY_DIR" -name "*.md" -exec grep -l "上周" {} \; 2>/dev/null | wc -l)
COUNT_TODAY=$(find "$MEMORY_DIR" -name "*.md" -exec grep -l "今天" {} \; 2>/dev/null | wc -l)

if [ $COUNT_YESTERDAY -gt 0 ]; then
  find "$MEMORY_DIR" -name "*.md" -exec sed -i "s/昨天/$YESTERDAY/g" {} \;
  echo "✅ 已替换 $COUNT_YESTERDAY 个'昨天'为 $YESTERDAY"
fi

if [ $COUNT_LAST_WEEK -gt 0 ]; then
  find "$MEMORY_DIR" -name "*.md" -exec sed -i "s/上周/$LAST_WEEK/g" {} \;
  echo "✅ 已替换 $COUNT_LAST_WEEK 个'上周'为 $LAST_WEEK"
fi

if [ $COUNT_TODAY -gt 0 ]; then
  find "$MEMORY_DIR" -name "*.md" -exec sed -i "s/今天/$TODAY/g" {} \;
  echo "✅ 已替换 $COUNT_TODAY 个'今天'为 $TODAY"
fi

# Step 3: 检测潜在问题
echo "🔍 Step 3: 检测问题..."
REMEMBER_COUNT=$(grep -r "记住\|记录" "$MEMORY_DIR"/*.md 2>/dev/null | wc -l)
CONFLICT_COUNT=$(grep -r "方案A\|方案B\|启用\|禁用" "$MEMORY_DIR"/*.md 2>/dev/null | wc -l)

echo "🔄 检测到 $REMEMBER_COUNT 个'记住/记录'指令"
echo "⚖️ 检测到 $CONFLICT_COUNT 个可能的配置项"

# Step 4: 生成报告
echo "📝 Step 4: 生成报告..."

TOTAL_FILES=$(find "$MEMORY_DIR" -name "*.md" | wc -l)
TOTAL_SIZE=$(du -sh "$MEMORY_DIR" | cut -f1)

cat > "$REPORT_FILE" << REPORT
# Auto Dream 报告 v0.2

**时间**: $(date)
**版本**: v0.2（基于 Open-ClaudeCode 源码学习）
**状态**: ✅ 完成

---

## ✅ 通过的检查

- [x] **锁门** - 无其他进程运行
- [x] **扫描节流** - 距上次扫描已超过 10 分钟
- [x] **时间门** - 距上次整理已超过 24 小时
- [x] **会话门** - 累计会话数 >= 5 个

---

## 📊 整理统计

- **记忆文件数**: $TOTAL_FILES
- **总大小**: $TOTAL_SIZE
- **备份位置**: \`$BACKUP_DIR\`

---

## 📅 时间标准化

- **替换"昨天"**: $COUNT_YESTERDAY 次 → \`$YESTERDAY\`
- **替换"上周"**: $COUNT_LAST_WEEK 次 → \`$LAST_WEEK\`
- **替换"今天"**: $COUNT_TODAY 次 → \`$TODAY\`

---

## 🔍 潜在问题

- **"记住/记录"指令**: $REMEMBER_COUNT 个
- **可能的配置项**: $CONFLICT_COUNT 个

---

## 💡 改进建议

1. **实现矛盾规则检测** - 自动发现并解决配置冲突
2. **实现重复内容合并** - 减少冗余信息
3. **添加自动触发** - 满足条件时自动运行
4. **优化报告格式** - 更直观的可视化

---

## 🚀 下次运行

建议在以下情况运行：
- 距离上次运行超过 24 小时
- 新增了 5 条以上对话记录
- 感觉记忆文件混乱时

**运行命令**:
\`\`\`bash
bash /root/.openclaw/workspace/scripts/auto-dream-v2.sh
\`\`\`

---

**Auto Dream v0.2** - 让 AI 通过"做梦"来进化 🧠✨

**基于**: Open-ClaudeCode v2.1.88 源码学习
**改进**: 添加锁机制、扫描节流、会话门检查
REPORT

# 更新最后整理时间
touch "$LAST_CONSOLIDATED_FILE"

echo "📝 报告已生成: $REPORT_FILE"
echo ""
echo "🎉 Auto Dream v0.2 完成！"
echo "⏱️ 总耗时: $SECONDS 秒"
echo ""
echo "📊 查看报告: cat $REPORT_FILE"
echo "💾 查看备份: ls -lh $BACKUP_DIR"
echo ""
echo "💡 提示: 下次运行将实现矛盾规则检测和重复内容合并"
