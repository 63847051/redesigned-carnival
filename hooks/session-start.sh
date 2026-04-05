#!/bin/bash
###############################################################################
# SessionStart Hook - 会话开始时自动加载记忆
###############################################################################

echo "🧠 SessionStart Hook - 加载记忆..."

# 获取当前项目路径
project_path="$(pwd)"
project_hash=$(echo "$project_path" | md5sum | cut -d' ' -f1)
project_memory_dir="/root/.openclaw/workspace/projects/$project_hash"

# 检查项目记忆是否存在
if [ -f "$project_memory_dir/memory.md" ]; then
  echo "✅ 发现项目记忆: $project_memory_dir/memory.md"
  echo ""
  echo "## 📖 项目记忆摘要"
  echo ""
  head -50 "$project_memory_dir/memory.md"
  echo ""
  echo "...（更多内容见完整文件）"
else
  echo "⚠️  未发现项目记忆"
  echo "💡 SessionEnd hook 会自动创建项目记忆"
fi

echo ""
echo "🧠 记忆加载完成"
