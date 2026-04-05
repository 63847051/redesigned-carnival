#!/bin/bash
###############################################################################
# SessionEnd Hook - 会话结束时自动保存记忆（修复版）
###############################################################################

echo "🧠 SessionEnd Hook - 保存记忆..."

# 获取当前项目路径
project_path="$(pwd)"
project_hash=$(echo "$project_path" | md5sum | cut -d' ' -f1)
project_memory_dir="/root/.openclaw/workspace/projects/$project_hash"

# 创建项目记忆目录
mkdir -p "$project_memory_dir"

# 项目记忆文件
project_memory="$project_memory_dir/memory.md"

echo "📁 项目记忆目录: $project_memory_dir"
echo "📄 项目记忆文件: $project_memory"
echo ""

# 获取今天的日期
today=$(date +%Y-%m-%d)
daily_log="/root/.openclaw/workspace/memory/$today.md"

# 检查今天的日志是否存在
if [ ! -f "$daily_log" ]; then
  echo "⚠️  今天的日志不存在: $daily_log"
  echo "💡 跳过记忆提取"
  exit 0
fi

echo "📖 分析今天的日志..."
echo ""

###############################################################################
# 提取关键信息并直接写入文件
###############################################################################

# 创建或追加到项目记忆
{
  echo "# 项目记忆 - 自动生成"
  echo ""
  echo "**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "**项目路径**: $project_path"
  echo "**项目哈希**: $project_hash"
  echo ""
  echo "---"
  echo ""
  echo "## 🎯 项目概览"
  echo ""
  echo "### 项目名称"
  echo "$(basename "$project_path")"
  echo ""
  echo "### 项目路径"
  echo "$project_path"
  echo ""
  echo "### 最后更新"
  echo "$(date '+%Y-%m-%d %H:%M:%S')"
  echo ""
  echo "---"
  echo ""
  echo "## 🧠 今天的决策"
  echo ""
  grep -i "决定\|选择\|采用\|实施" "$daily_log" | head -10 || echo "无明确决策"
  echo ""
  echo "---"
  echo ""
  echo "## ✅ 成功经验"
  echo ""
  grep -i "成功\|完成\|实现" "$daily_log" | head -10 || echo "无成功记录"
  echo ""
  echo "---"
  echo ""
  echo "## ❌ 错误教训"
  echo ""
  grep -i "失败\|错误\|问题" "$daily_log" | head -10 || echo "无错误记录"
  echo ""
  echo "---"
  echo ""
  echo "## 🔧 技术细节"
  echo ""
  grep -i "配置\|安装\|部署\|设置" "$daily_log" | head -10 || echo "无技术细节"
  echo ""
  echo "---"
  echo ""
  echo "## 📝 待办事项"
  echo ""
  grep "^\- \[ \]" "$daily_log" | head -10 || echo "无待办事项"
  echo ""
  echo "---"
  echo ""
  echo "## 🎓 学习记录"
  echo ""
  grep -i "学习\|掌握\|理解" "$daily_log" | head -10 || echo "无学习记录"
  echo ""
  echo "---"
  echo ""
  echo "**记忆完成**: $(date '+%Y-%m-%d %H:%M:%S')"
} >> "$project_memory"

echo ""
echo "✅ 记忆已保存到: $project_memory"
echo ""
echo "📊 记忆统计:"
echo "  - 文件大小: $(wc -c < "$project_memory") 字节"
echo "  - 总行数: $(wc -l < "$project_memory") 行"
echo ""

###############################################################################
# 记忆摘要
###############################################################################

echo "## 📖 记忆摘要"
echo ""
head -30 "$project_memory"
echo ""
echo "...（更多内容见完整文件）"

echo ""
echo "🧠 记忆保存完成"
