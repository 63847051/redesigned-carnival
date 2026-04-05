#!/bin/bash
# Auto Dream v0.1 - 基础版
# 让 AI 通过"做梦"来整理记忆

set -e

echo "🧠 Auto Dream v0.1 开始..."
echo "⏰ 时间: $(date)"

# 配置
MEMORY_DIR="/root/.openclaw/workspace/memory"
BACKUP_DIR="$MEMORY_DIR/backups/dream-$(date +%Y%m%d-%H%M%S)"
REPORT_FILE="$MEMORY_DIR/dream-report-latest.md"

# Step 1: 备份
echo ""
echo "💾 Step 1: 备份记忆文件..."
mkdir -p "$BACKUP_DIR"
cp "$MEMORY_DIR"/*.md "$BACKUP_DIR/" 2>/dev/null || true
echo "✅ 备份完成: $BACKUP_DIR"

# Step 2: 时间标准化
echo ""
echo "📅 Step 2: 标准化相对时间..."

# 获取相对日期
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)
LAST_WEEK=$(date -d "last week" +%Y-%m-%d)
TODAY=$(date +%Y-%m-%d)

# 统计需要替换的数量
COUNT_YESTERDAY=$(find "$MEMORY_DIR" -name "*.md" -exec grep -l "昨天" {} \; 2>/dev/null | wc -l)
COUNT_LAST_WEEK=$(find "$MEMORY_DIR" -name "*.md" -exec grep -l "上周" {} \; 2>/dev/null | wc -l)
COUNT_TODAY=$(find "$MEMORY_DIR" -name "*.md" -exec grep -l "今天" {} \; 2>/dev/null | wc -l)

# 替换相对时间
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

# Step 3: 统计信息
echo ""
echo "📊 Step 3: 生成统计信息..."
TOTAL_FILES=$(find "$MEMORY_DIR" -name "*.md" | wc -l)
TOTAL_SIZE=$(du -sh "$MEMORY_DIR" | cut -f1)
MEMORY_MD_SIZE=$(wc -c < "$MEMORY_DIR/MEMORY.md" 2>/dev/null || echo "0")

echo "📋 记忆文件数: $TOTAL_FILES"
echo "💾 总大小: $TOTAL_SIZE"
echo "📝 MEMORY.md 大小: $MEMORY_MD_SIZE 字节"

# Step 4: 检测潜在问题
echo ""
echo "🔍 Step 4: 检测潜在问题..."

# 检测重复的"记住"指令
REMEMBER_COUNT=$(grep -r "记住\|记录" "$MEMORY_DIR"/*.md 2>/dev/null | wc -l)
echo "🔄 检测到 $REMEMBER_COUNT 个'记住/记录'指令"

# 检测可能的矛盾
CONFLICT_COUNT=$(grep -r "方案A\|方案B\|启用\|禁用" "$MEMORY_DIR"/*.md 2>/dev/null | wc -l)
echo "⚖️ 检测到 $CONFLICT_COUNT 个可能的配置项"

# Step 5: 生成报告
echo ""
echo "📝 Step 5: 生成报告..."

cat > "$REPORT_FILE" << REPORT
# Auto Dream 报告

**时间**: $(date)
**版本**: v0.1 基础版
**状态**: ✅ 完成

---

## ✅ 完成任务

- [x] 备份记忆文件
- [x] 标准化相对时间
- [x] 生成统计信息
- [x] 检测潜在问题
- [ ] 检测矛盾规则（待实现）
- [ ] 合并重复内容（待实现）

---

## 📊 统计信息

- **记忆文件数**: $TOTAL_FILES
- **总大小**: $TOTAL_SIZE
- **MEMORY.md 大小**: $MEMORY_MD_SIZE 字节
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
bash /root/.openclaw/workspace/scripts/auto-dream-basic.sh
\`\`\`

---

**Auto Dream v0.1** - 让 AI 通过"做梦"来进化 🧠✨
REPORT

echo "✅ 报告已生成: $REPORT_FILE"

# 完成
echo ""
echo "🎉 Auto Dream v0.1 完成！"
echo "⏱️ 总耗时: $SECONDS 秒"
echo ""
echo "📝 查看报告: cat $REPORT_FILE"
echo "💾 查看备份: ls -lh $BACKUP_DIR"
echo ""
echo "💡 提示: 下次运行将实现矛盾规则检测和重复内容合并"
