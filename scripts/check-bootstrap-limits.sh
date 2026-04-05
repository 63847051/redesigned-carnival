#!/bin/bash
###############################################################################
# 字符上限管控脚本
# 基于 Code-Claw 的实现
###############################################################################

echo "📏 字符上限管控检查"
echo "⏰ 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Code-Claw 的限制
PER_FILE_LIMIT=20000  # 20K 字符
TOTAL_LIMIT=80000    # 80K 字符

# 人格文件目录
BOOTSTRAP_DIR="/root/.openclaw/workspace"
FILES=("SOUL.md" "IDENTITY.md" "USER.md" "AGENTS.md")

echo "## 📊 字符统计"
echo ""

total_chars=0
for file in "${FILES[@]}"; do
  filepath="$BOOTSTRAP_DIR/$file"
  if [ -f "$filepath" ]; then
    chars=$(wc -c < "$filepath")
    total_chars=$((total_chars + chars))
    
    # 检查是否超过单文件限制
    if [ "$chars" -gt "$PER_FILE_LIMIT" ]; then
      echo "⚠️  $file: $chars 字符（超过 $PER_FILE_LIMIT 限制）"
    else
      echo "✅ $file: $chars 字符"
    fi
  fi
done

echo ""
echo "总计: $total_chars 字符"

# 检查是否超过总限制
if [ "$total_chars" -gt "$TOTAL_LIMIT" ]; then
  echo "⚠️  总字符数超过 $TOTAL_LIMIT 限制"
else
  echo "✅ 总字符数在限制内"
fi

echo ""
echo "📏 限制配置:"
echo "  - 单文件限制: $PER_FILE_LIMIT 字符"
echo "  - 总限制: $TOTAL_LIMIT 字符"
echo ""
echo "✅ 检查完成"
