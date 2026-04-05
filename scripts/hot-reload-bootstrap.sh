#!/bin/bash
###############################################################################
# SOUL 人格热重载脚本
# 功能：检查人格文件状态，计算总字符数，检查是否超过限制
###############################################################################

echo "🔥 SOUL 人格热重载检查"
echo "⏰ 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 基于 Code-Claw 的限制
PER_FILE_LIMIT=20000  # 20K 字符
TOTAL_LIMIT=80000    # 80K 字符

# 人格文件目录
BOOTSTRAP_DIR="/root/.openclaw/workspace"
FILES=("SOUL.md" "IDENTITY.md" "USER.md" "AGENTS.md")

echo "## 📊 字符统计"
echo ""

total_chars=0
file_stats=()

for file in "${FILES[@]}"; do
  filepath="$BOOTSTRAP_DIR/$file"
  if [ -f "$filepath" ]; then
    chars=$(wc -c < "$filepath")
    total_chars=$((total_chars + chars))
    file_stats+=("$file|$chars")
    
    # 检查是否超过单文件限制
    if [ "$chars" -gt "$PER_FILE_LIMIT" ]; then
      echo "⚠️  $file: $chars 字符（超过 $PER_FILE_LIMIT 限制）"
      echo "   建议：截断到 $PER_FILE_LIMIT 字符"
    else
      echo "✅ $file: $chars 字符"
    fi
  else
    echo "⚠️  $file: 文件不存在"
  fi
done

echo ""
echo "📊 总计: $total_chars 字符"

# 检查是否超过总限制
if [ "$total_chars" -gt "$TOTAL_LIMIT" ]; then
  echo "⚠️  总字符数超过 $TOTAL_LIMIT 限制"
  echo "💡 建议：运行 Auto Dream v0.3 整合记忆"
else
  echo "✅ 总字符数在限制内（$TOTAL_LIMIT）"
fi

echo ""
echo "📏 限制配置:"
echo "  - 单文件限制: $PER_FILE_LIMIT 字符"
echo "  - 总限制: $TOTAL_LIMIT 字符"
echo ""

# 显示文件详情
echo "## 📄 文件详情"
echo ""
for stat in "${file_stats[@]}"; do
  IFS='|' read -r file chars <<< "$stat"
  percentage=$((chars * 100 / PER_FILE_LIMIT))
  echo "  - $file: $chars 字符 (${percentage}%)"
done

echo ""
echo "✅ 热重载检查完成"
