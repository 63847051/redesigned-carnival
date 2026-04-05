#!/bin/bash
###############################################################################
# Memory Persistence Hooks - 记忆持久化钩子
# 功能: SessionStart 自动加载记忆，SessionEnd 自动保存记忆
###############################################################################

echo "🧠 Memory Persistence Hooks - 记忆持久化"
echo "⏰ 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

###############################################################################
# 1. 创建记忆目录结构
###############################################################################

echo "## 📁 创建记忆目录结构"
echo ""

# 创建记忆目录
memory_dir="/root/.openclaw/workspace/memory"
projects_dir="/root/.openclaw/workspace/projects"

mkdir -p "$memory_dir"
mkdir -p "$projects_dir"

echo "✅ 记忆目录: $memory_dir"
echo "✅ 项目目录: $projects_dir"
echo ""

###############################################################################
# 2. 创建 SessionStart Hook
###############################################################################

echo "## 🚀 创建 SessionStart Hook"
echo ""

# 创建 hooks 目录
hooks_dir="/root/.openclaw/workspace/hooks"
mkdir -p "$hooks_dir"

# 创建 SessionStart hook
cat > "$hooks_dir/session-start.sh" << 'EOF'
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
EOF

chmod +x "$hooks_dir/session-start.sh"

echo "✅ SessionStart Hook: $hooks_dir/session-start.sh"
echo ""

###############################################################################
# 3. 创建 SessionEnd Hook
###############################################################################

echo "## 🏁 创建 SessionEnd Hook"
echo ""

# 创建 SessionEnd hook
cat > "$hooks_dir/session-end.sh" << 'EOF'
#!/bin/bash
###############################################################################
# SessionEnd Hook - 会话结束时自动保存记忆
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
# 提取关键信息
###############################################################################

# 创建临时文件
temp_memory="/tmp/session-end-memory.md"

cat > "$temp_memory" << EOF
# 项目记忆 - 自动生成

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**项目路径**: $project_path
**项目哈希**: $project_hash

---

## 🎯 项目概览

### 项目名称
$(basename "$project_path")

### 项目路径
$project_path

### 最后更新
$(date '+%Y-%m-%d %H:%M:%S')

---

## 🧠 今天的决策

$(grep -i "决定\|选择\|采用\|实施" "$daily_log" | head -10)

---

## ✅ 成功经验

$(grep -i "成功\|完成\|实现\|✅" "$daily_log" | head -10)

---

## ❌ 错误教训

$(grep -i "失败\|错误\|问题\|❌" "$daily_log" | head -10)

---

## 🔧 技术细节

$(grep -i "配置\|安装\|部署\|设置" "$daily_log" | head -10)

---

## 📝 待办事项

$(grep "^\- \[ \]" "$daily_log" | head -10)

---

## 🎓 学习记录

$(grep -i "学习\|掌握\|理解" "$daily_log" | head -10)

---

**记忆完成**: $(date '+%Y-%m-%d %H:%M:%S')
EOF

###############################################################################
# 合并到项目记忆
###############################################################################

if [ -f "$project_memory" ]; then
  echo "📄 项目记忆已存在，追加新内容..."
  echo "" >> "$project_memory"
  cat "$temp_memory" >> "$project_memory"
else
  echo "📄 创建新的项目记忆..."
  cat "$temp_memory" > "$project_memory"
fi

# 清理临时文件
rm -f "$temp_memory"

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
EOF

chmod +x "$hooks_dir/session-end.sh"

echo "✅ SessionEnd Hook: $hooks_dir/session-end.sh"
echo ""

###############################################################################
# 4. 创建手动触发脚本
###############################################################################

echo "## 🔧 创建手动触发脚本"
echo ""

# 创建手动触发脚本
cat > "$hooks_dir/trigger-hooks.sh" << 'EOF'
#!/bin/bash
###############################################################################
# 手动触发 Hooks
###############################################################################

echo "🔧 手动触发 Hooks"
echo ""

# 触发 SessionStart
echo "## 🚀 触发 SessionStart Hook"
bash /root/.openclaw/workspace/hooks/session-start.sh
echo ""

# 触发 SessionEnd
echo "## 🏁 触发 SessionEnd Hook"
bash /root/.openclaw/workspace/hooks/session-end.sh
echo ""

echo "✅ Hooks 触发完成"
EOF

chmod +x "$hooks_dir/trigger-hooks.sh"

echo "✅ 手动触发脚本: $hooks_dir/trigger-hooks.sh"
echo ""

###############################################################################
# 5. 创建使用指南
###############################################################################

echo "## 📖 使用指南"
echo ""

cat > "$memory_dir/USAGE-GUIDE.md" << EOF
# Memory Persistence Hooks 使用指南

**创建时间**: $(date '+%Y-%m-%d %H:%M:%S')

---

## 🎯 功能说明

Memory Persistence Hooks 让 AI 自动记住项目相关的决策、模式和经验。

### 两个 Hook

1. **SessionStart Hook** - 会话开始时自动加载记忆
2. **SessionEnd Hook** - 会话结束时自动保存记忆

---

## 🚀 自动触发

### SessionStart Hook

**触发时机**: 会话开始时自动触发

**功能**:
- 检查项目记忆是否存在
- 显示项目记忆摘要
- 帮助 AI 快速了解项目背景

### SessionEnd Hook

**触发时机**: 会话结束时自动触发

**功能**:
- 分析今天的日志
- 提取关键决策和经验
- 追加到项目记忆

---

## 🔧 手动触发

### 触发 SessionStart

\`\`\`bash
bash /root/.openclaw/workspace/hooks/session-start.sh
\`\`\`

### 触发 SessionEnd

\`\`\`bash
bash /root/.openclaw/workspace/hooks/session-end.sh
\`\`\`

### 同时触发两个 Hook

\`\`\`bash
bash /root/.openclaw/workspace/hooks/trigger-hooks.sh
\`\`\`

---

## 📁 记忆位置

### 项目记忆

\`\`\`
/root/.openclaw/workspace/projects/<project-hash>/memory.md
\`\`\`

### 今天的日志

\`\`\`
/root/.openclaw/workspace/memory/<today>.md
\`\`\`

---

## 💡 工作原理

### SessionStart

1. 计算当前项目的哈希值
2. 检查项目记忆是否存在
3. 如果存在，显示记忆摘要
4. 帮助 AI 快速了解项目背景

### SessionEnd

1. 分析今天的日志
2. 提取关键信息:
   - 今天的决策
   - 成功经验
   - 错误教训
   - 技术细节
   - 待办事项
   - 学习记录
3. 追加到项目记忆

---

## 🎯 效果

### SessionStart

- ✅ 快速了解项目背景
- ✅ 记住之前的决策
- ✅ 避免重复错误

### SessionEnd

- ✅ 自动保存记忆
- ✅ 提取关键经验
- ✅ 积累项目知识

---

## 📊 记忆内容

项目记忆包含:

- 🎯 项目概览
- 🧠 今天的决策
- ✅ 成功经验
- ❌ 错误教训
- 🔧 技术细节
- 📝 待办事项
- 🎓 学习记录

---

## 💡 最佳实践

1. **每个项目一个记忆** - 不同项目的记忆分开存储
2. **定期回顾记忆** - 每周回顾一次项目记忆
3. **清理过期记忆** - 定期清理过期的记忆
4. **备份重要记忆** - 定期备份重要的项目记忆

---

**使用指南完成**: $(date '+%Y-%m-%d %H:%M:%S')
EOF

echo "✅ 使用指南: $memory_dir/USAGE-GUIDE.md"
echo ""

###############################################################################
# 6. 测试 Hooks
###############################################################################

echo "## 🧪 测试 Hooks"
echo ""

echo "### 测试 SessionStart Hook"
bash "$hooks_dir/session-start.sh"
echo ""

echo "### 测试 SessionEnd Hook"
bash "$hooks_dir/session-end.sh"
echo ""

###############################################################################
# 完成
###############################################################################

echo "🎉 Memory Persistence Hooks 完成设置！"
echo ""
echo "📊 设置统计:"
echo "  - SessionStart Hook: ✅ 已创建"
echo "  - SessionEnd Hook: ✅ 已创建"
echo "  - 手动触发脚本: ✅ 已创建"
echo "  - 使用指南: ✅ 已创建"
echo ""
echo "💡 下一步:"
echo "  1. 查看使用指南: cat $memory_dir/USAGE-GUIDE.md"
echo "  2. 手动测试 Hooks: bash $hooks_dir/trigger-hooks.sh"
echo "  3. 在会话中自动触发"
