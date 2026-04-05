#!/bin/bash
###############################################################################
# Continuous Learning v2 - 自动从历史学习
# 功能: 分析今天的对话，提炼学习模式和成功经验
###############################################################################

echo "🧠 Continuous Learning v2 - 开始学习..."
echo "⏰ 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 获取今天的日期
today=$(date +%Y-%m-%d)
log_file="/root/.openclaw/workspace/memory/$today.md"

# 创建学习目录
learning_dir="/root/.openclaw/workspace/learning"
mkdir -p "$learning_dir"

# 创建今天的学习文件
learning_file="$learning_dir/$today.md"

echo "# 学习报告 - $today" > "$learning_file"
echo "" >> "$learning_file"
echo "**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')" >> "$learning_file"
echo "" >> "$learning_file"

# 检查日志文件是否存在
if [ ! -f "$log_file" ]; then
  echo "⚠️  今天的日志不存在: $log_file"
  echo "💡 建议: 先创建今天的日志"
  exit 1
fi

echo "📖 分析今天的日志: $log_file"
echo ""

###############################################################################
# 1. 发现的模式
###############################################################################

echo "## 🔍 发现的模式" >> "$learning_file"
echo "" >> "$learning_file"

echo "🔍 分析学习到的内容..."
patterns=$(grep -i "学习\|掌握\|理解\|领悟" "$log_file" | head -20)

if [ -n "$patterns" ]; then
  echo "$patterns" >> "$learning_file"
  pattern_count=$(echo "$patterns" | wc -l)
  echo "✅ 发现 $pattern_count 个学习模式"
else
  echo "无明确的学习记录" >> "$learning_file"
  echo "⚠️  未发现明确的学习记录"
fi

echo "" >> "$learning_file"

###############################################################################
# 2. 成功案例
###############################################################################

echo "## ✅ 成功案例" >> "$learning_file"
echo "" >> "$learning_file"

echo "✅ 分析成功案例..."
successes=$(grep -i "成功\|完成\|实现\|✅" "$log_file" | head -20)

if [ -n "$successes" ]; then
  echo "$successes" >> "$learning_file"
  success_count=$(echo "$successes" | wc -l)
  echo "✅ 发现 $success_count 个成功案例"
else
  echo "无明确的成功记录" >> "$learning_file"
  echo "⚠️  未发现明确的成功记录"
fi

echo "" >> "$learning_file"

###############################################################################
# 3. 错误教训
###############################################################################

echo "## ❌ 错误教训" >> "$learning_file"
echo "" >> "$learning_file"

echo "❌ 分析错误教训..."
errors=$(grep -i "失败\|错误\|问题\|❌" "$log_file" | head -20)

if [ -n "$errors" ]; then
  echo "$errors" >> "$learning_file"
  error_count=$(echo "$errors" | wc -l)
  echo "✅ 发现 $error_count 个错误教训"
else
  echo "无明确的错误记录" >> "$learning_file"
  echo "✅ 很好！今天没有错误"
fi

echo "" >> "$learning_file"

###############################################################################
# 4. 关键决策
###############################################################################

echo "## 🎯 关键决策" >> "$learning_file"
echo "" >> "$learning_file"

echo "🎯 分析关键决策..."
decisions=$(grep -i "决定\|选择\|采用\|实施" "$log_file" | head -20)

if [ -n "$decisions" ]; then
  echo "$decisions" >> "$learning_file"
  decision_count=$(echo "$decisions" | wc -l)
  echo "✅ 发现 $decision_count 个关键决策"
else
  echo "无明确的决策记录" >> "$learning_file"
  echo "⚠️  未发现明确的决策记录"
fi

echo "" >> "$learning_file"

###############################################################################
# 5. 工作模式
###############################################################################

echo "## 🔄 工作模式" >> "$learning_file"
echo "" >> "$learning_file"

echo "🔄 分析工作模式..."

# 分析最常用的命令
echo "### 常用命令" >> "$learning_file"
echo "" >> "$learning_file"

commands=$(grep -E "^[a-z]+_.*:" "$log_file" | sed 's/:.*//' | sort | uniq -c | sort -rn | head -10)

if [ -n "$commands" ]; then
  echo "$commands" >> "$learning_file"
  echo "✅ 已分析常用命令"
else
  echo "无明确的命令记录" >> "$learning_file"
fi

echo "" >> "$learning_file"

# 分析最常用的工具
echo "### 常用工具" >> "$learning_file"
echo "" >> "$learning_file"

tools=$(grep -i "read\|write\|edit\|exec\|web_fetch\|web_search" "$log_file" | grep -oE "(read|write|edit|exec|web_fetch|web_search)" | sort | uniq -c | sort -rn | head -10)

if [ -n "$tools" ]; then
  echo "$tools" >> "$learning_file"
  echo "✅ 已分析常用工具"
else
  echo "无明确的工具记录" >> "$learning_file"
fi

echo "" >> "$learning_file"

###############################################################################
# 6. 统计信息
###############################################################################

echo "## 📊 统计信息" >> "$learning_file"
echo "" >> "$learning_file"

echo "📊 生成统计信息..."

# 总字符数
total_chars=$(wc -c < "$log_file")
echo "- **总字符数**: $total_chars" >> "$learning_file"

# 总行数
total_lines=$(wc -l < "$log_file")
echo "- **总行数**: $total_lines" >> "$learning_file"

# 学习模式数
if [ -n "$pattern_count" ]; then
  echo "- **学习模式**: $pattern_count 个" >> "$learning_file"
fi

# 成功案例数
if [ -n "$success_count" ]; then
  echo "- **成功案例**: $success_count 个" >> "$learning_file"
fi

# 错误教训数
if [ -n "$error_count" ]; then
  echo "- **错误教训**: $error_count 个" >> "$learning_file"
fi

echo "" >> "$learning_file"

###############################################################################
# 7. 学习总结
###############################################################################

echo "## 🎓 学习总结" >> "$learning_file"
echo "" >> "$learning_file"

echo "🎓 生成学习总结..."

# 总结今天的主要收获
echo "### 主要收获" >> "$learning_file"
echo "" >> "$learning_file"

# 提取 Retain 部分
retain_section=$(sed -n '/## Retain/,/^[A-Z]/p' "$log_file" | head -20)

if [ -n "$retain_section" ]; then
  echo "$retain_section" >> "$learning_file"
  echo "✅ 已提取 Retain 部分"
else
  echo "无 Retain 部分" >> "$learning_file"
fi

echo "" >> "$learning_file"

# 提取待办事项
echo "### 待办事项" >> "$learning_file"
echo "" >> "$learning_file"

todos=$(grep -E "^\- \[ \]" "$log_file" | head -20)

if [ -n "$todos" ]; then
  echo "$todos" >> "$learning_file"
  todo_count=$(echo "$todos" | wc -l)
  echo "✅ 发现 $todo_count 个待办事项"
else
  echo "无待办事项" >> "$learning_file"
  echo "✅ 所有任务已完成"
fi

echo "" >> "$learning_file"

###############################################################################
# 8. 置信度评分
###############################################################################

echo "## 📈 置信度评分" >> "$learning_file"
echo "" >> "$learning_file"

echo "📈 生成置信度评分..."

# 分析学习的置信度
if [ -n "$pattern_count" ] && [ "$pattern_count" -gt 5 ]; then
  echo "✓ \[0.9\] 今天学到了很多新知识（$pattern_count 个模式）" >> "$learning_file"
elif [ -n "$pattern_count" ] && [ "$pattern_count" -gt 2 ]; then
  echo "✓ \[0.7\] 今天学到了一些新知识（$pattern_count 个模式）" >> "$learning_file"
else
  echo "? \[0.5\] 今天的学习较少（$pattern_count 个模式）" >> "$learning_file"
fi

echo "" >> "$learning_file"

# 分析工作的置信度
if [ -n "$success_count" ] && [ "$success_count" -gt 5 ]; then
  echo "✓ \[0.9\] 今天的工作很成功（$success_count 个成功案例）" >> "$learning_file"
elif [ -n "$success_count" ] && [ "$success_count" -gt 2 ]; then
  echo "✓ \[0.7\] 今天的工作较成功（$success_count 个成功案例）" >> "$learning_file"
else
  echo "? \[0.5\] 今天的工作较少成功（$success_count 个成功案例）" >> "$learning_file"
fi

echo "" >> "$learning_file"

###############################################################################
# 完成
###############################################################################

echo "" >> "$learning_file"
echo "---" >> "$learning_file"
echo "" >> "$learning_file"
echo "**学习完成时间**: $(date '+%Y-%m-%d %H:%M:%S')" >> "$learning_file"

echo ""
echo "🎉 学习完成！"
echo "📄 学习报告: $learning_file"
echo ""
echo "📊 学习统计:"
echo "  - 学习模式: ${pattern_count:-0} 个"
echo "  - 成功案例: ${success_count:-0} 个"
echo "  - 错误教训: ${error_count:-0} 个"
echo "  - 关键决策: ${decision_count:-0} 个"
echo ""
echo "💡 下一步:"
echo "  1. 查看学习报告: cat $learning_file"
echo "  2. 提炼成 Skill: bash /root/.openclaw/workspace/scripts/extract-skills.sh"
echo "  3. 更新知识库: bash /root/.openclaw/workspace/scripts/update-memory.sh"
