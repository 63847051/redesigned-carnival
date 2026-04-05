#!/bin/bash
###############################################################################
# sessions_list + history - 监控子 Agent 状态
# 功能: 查看活跃 session，查看完整对话记录
###############################################################################

echo "🔍 sessions_list + history - 开始监控..."
echo "⏰ 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

###############################################################################
# 1. 模拟 sessions_list（查看活跃 session）
###############################################################################

echo "## 📊 活跃的 Session"
echo ""

# 检查是否有 sessions 目录
sessions_dir="/root/.openclaw/workspace/sessions"

if [ ! -d "$sessions_dir" ]; then
  echo "⚠️  sessions 目录不存在: $sessions_dir"
  echo "💡 建议: sessions_spawn 创建的 session 会存储在这里"
else
  echo "📁 发现 sessions 目录: $sessions_dir"
  echo ""
  
  # 列出最近的 session
  echo "### 最近的 Session:"
  echo ""
  
  # 查找最近的子 Agent 日志
  recent_sessions=$(find "$sessions_dir" -name "*.md" -type f -mtime -1 2>/dev/null | head -10)
  
  if [ -n "$recent_sessions" ]; then
    echo "$recent_sessions" | while read session_file; do
      echo "- $(basename "$session_file")"
      echo "  路径: $session_file"
      echo "  修改时间: $(stat -c %y "$session_file" 2>/dev/null | cut -d'.' -f1)"
      echo "  大小: $(stat -c %s "$session_file" 2>/dev/null) 字节"
      echo ""
    done
  else
    echo "⚠️  没有找到最近的 session"
  fi
fi

###############################################################################
# 2. 模拟 sessions_history（查看完整对话记录）
###############################################################################

echo ""
echo "## 📖 完整对话记录"
echo ""

# 检查今天的日志
today=$(date +%Y-%m-%d)
log_file="/root/.openclaw/workspace/memory/$today.md"

if [ -f "$log_file" ]; then
  echo "📄 今天的日志: $log_file"
  echo ""
  
  # 提取关键对话
  echo "### 关键对话摘要:"
  echo ""
  
  # 提取用户消息
  echo "#### 用户消息:"
  grep -E "ou_[0-9a-f]+:" "$log_file" | tail -5
  echo ""
  
  # 提取我的回复
  echo "#### 我的回复:"
  grep -E "^## |^### " "$log_file" | tail -5
  echo ""
  
  # 提取决策
  echo "#### 关键决策:"
  grep -E "决定\|选择\|采用" "$log_file" | tail -5
  echo ""
  
else
  echo "⚠️  今天的日志不存在: $log_file"
fi

###############################################################################
# 3. 分析 session 状态
###############################################################################

echo ""
echo "## 📊 Session 状态分析"
echo ""

# 分析今天的活动
if [ -f "$log_file" ]; then
  # 统计用户消息数
  user_messages=$(grep -c "ou_[0-9a-f]*:" "$log_file" 2>/dev/null || echo 0)
  echo "- 用户消息: $user_messages 条"
  
  # 统计我的回复数
  my_replies=$(grep -c "^## \|^### " "$log_file" 2>/dev/null || echo 0)
  echo "- 我的回复: $my_replies 条"
  
  # 统计工具调用
  tool_calls=$(grep -c "toolCall\|Tool result" "$log_file" 2>/dev/null || echo 0)
  echo "- 工具调用: $tool_calls 次"
  
  # 统计学习记录
  learning_records=$(grep -c "学习\|掌握\|理解" "$log_file" 2>/dev/null || echo 0)
  echo "- 学习记录: $learning_records 条"
  
  # 统计成功案例
  success_records=$(grep -c "成功\|完成\|✅" "$log_file" 2>/dev/null || echo 0)
  echo "- 成功案例: $success_records 条"
  
  echo ""
fi

###############################################################################
# 4. 生成监控报告
###############################################################################

echo "## 📋 监控报告"
echo ""

# 创建监控报告目录
monitor_dir="/root/.openclaw/workspace/monitoring-reports"
mkdir -p "$monitor_dir"

# 创建今天的监控报告
report_file="$monitor_dir/$today.md"

cat > "$report_file" << EOF
# 监控报告 - $today

**监控时间**: $(date '+%Y-%m-%d %H:%M:%S')

---

## Session 概览

$(if [ -d "$sessions_dir" ]; then
  echo "✅ sessions 目录存在"
  recent_count=$(find "$sessions_dir" -name "*.md" -type f -mtime -1 2>/dev/null | wc -l)
  echo "- 最近 24 小时的 session: $recent_count 个"
else
  echo "⚠️  sessions 目录不存在"
fi)

## 对话统计

$(if [ -f "$log_file" ]; then
  echo "- 用户消息: $user_messages 条"
  echo "- 我的回复: $my_replies 条"
  echo "- 工具调用: $tool_calls 次"
  echo "- 学习记录: $learning_records 条"
  echo "- 成功案例: $success_records 条"
fi)

## 活动评估

$(if [ -f "$log_file" ]; then
  if [ "$user_messages" -gt 20 ]; then
    echo "✅ 活动频繁（$user_messages 条用户消息）"
  elif [ "$user_messages" -gt 10 ]; then
    echo "✅ 活动正常（$user_messages 条用户消息）"
  else
    echo "⚠️  活动较少（$user_messages 条用户消息）"
  fi
  
  if [ "$learning_records" -gt 10 ]; then
    echo "🧠 学习积极（$learning_records 条学习记录）"
  elif [ "$learning_records" -gt 5 ]; then
    echo "🧠 学习正常（$learning_records 条学习记录）"
  else
    echo "⚠️  学习较少（$learning_records 条学习记录）"
  fi
fi)

## 建议

$(if [ -f "$log_file" ]; then
  if [ "$user_messages" -lt 10 ]; then
    echo "- 💡 建议增加与用户的互动"
  fi
  
  if [ "$learning_records" -lt 5 ]; then
    echo "- 💡 建议每天学习新东西"
  fi
  
  if [ "$success_records" -gt 10 ]; then
    echo "- ✅ 工作质量很好，继续保持"
  fi
fi)

---

**监控完成**: $(date '+%Y-%m-%d %H:%M:%S')
EOF

echo "📄 监控报告: $report_file"

echo ""

###############################################################################
# 5. 实时监控提示
###############################################################################

echo "## 💡 实时监控建议"
echo ""

echo "如果需要实时监控子 Agent，可以："
echo ""
echo "1. 定期运行此脚本"
echo "   bash /root/.openclaw/workspace/scripts/monitor-agents.sh"
echo ""
echo "2. 查看特定 session 的详细记录"
echo "   cat /root/.openclaw/workspace/sessions/<session-id>.md"
echo ""
echo "3. 查看今天的对话记录"
echo "   cat /root/.openclaw/workspace/memory/$today.md"
echo ""

###############################################################################
# 完成
###############################################################################

echo "🎉 监控完成！"
echo ""
echo "📊 监控统计:"
echo "  - sessions 目录: 已检查"
echo "  - 对话记录: 已分析"
echo "  - Session 状态: 已评估"
echo "  - 监控报告: 已生成"
echo ""
echo "💡 下一步:"
echo "  1. 查看监控报告: cat $report_file"
echo "  2. 定期运行此脚本"
echo "  3. 根据报告优化工作"
