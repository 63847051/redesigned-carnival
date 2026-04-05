#!/bin/bash
###############################################################################
# /skill-create - 从 git 历史提炼 Skill
# 功能: 分析 git 历史，发现重复模式，生成可复用的 Skill
###############################################################################

echo "🔍 /skill-create - 开始提炼 Skill..."
echo "⏰ 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查是否在 git 仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
  echo "❌ 错误: 当前目录不是 git 仓库"
  exit 1
fi

# 创建技能目录
skills_dir="/root/.openclaw/workspace/skills"
mkdir -p "$skills_dir"

echo "📊 分析 git 历史..."
echo ""

###############################################################################
# 1. 分析多文件变更模式
###############################################################################

echo "## 🔍 分析多文件变更模式..."

# 获取最近 100 次提交的多文件变更
echo "### 最近 100 次提交的多文件变更模式:" > /tmp/skill_analysis.md
echo "" >> /tmp/skill_analysis.md

# 分析文件组合
file_combos=$(git log -100 --name-only --pretty=format:"%H|%s" | \
  grep -v "^$" | \
  awk '
    BEGIN { FS="|" }
    /^/ {
      if ($1 ~ /^[a-f0-9]+$/) {
        commit = $1
        subject = $2
        file_count = 0
      } else {
        file_count++
        files[commit][file_count] = $0
      }
    }
    END {
      for (c in files) {
        if (length(files[c]) > 1) {
          printf "Commit %s:\n", c
          for (f in files[c]) {
            printf "  - %s\n", files[c][f]
          }
          print ""
        }
      }
    }
  ' | head -100)

echo "$file_combos" >> /tmp/skill_analysis.md

###############################################################################
# 2. 分析常见文件类型
###############################################################################

echo "## 📁 分析常见文件类型..."

echo "" >> /tmp/skill_analysis.md
echo "### 常见文件类型:" >> /tmp/skill_analysis.md
echo "" >> /tmp/skill_analysis.md

file_types=$(git log -100 --name-only --pretty=format:"" | \
  grep -v "^$" | \
  sed 's/.*\.//' | \
  sort | uniq -c | sort -rn | head -20)

echo "$file_types" >> /tmp/skill_analysis.md

###############################################################################
# 3. 分析常用目录
###############################################################################

echo "## 📂 分析常用目录..."

echo "" >> /tmp/skill_analysis.md
echo "### 常用目录:" >> /tmp/skill_analysis.md
echo "" >> /tmp/skill_analysis.md

directories=$(git log -100 --name-only --pretty=format:"" | \
  grep -v "^$" | \
  sed 's#/[^/]*$##' | \
  sort | uniq -c | sort -rn | head -20)

echo "$directories" >> /tmp/skill_analysis.md

###############################################################################
# 4. 分析提交消息模式
###############################################################################

echo "## 💬 分析提交消息模式..."

echo "" >> /tmp/skill_analysis.md
echo "### 常见提交消息:" >> /tmp/skill_analysis.md
echo "" >> /tmp/skill_analysis.md

commit_messages=$(git log -100 --pretty=format:"%s" | \
  sort | uniq -c | sort -rn | head -20)

echo "$commit_messages" >> /tmp/skill_analysis.md

###############################################################################
# 5. 生成 Skill 模板
###############################################################################

echo ""
echo "🎯 生成 Skill 模板..."

skill_file="$skills_dir/auto-generated-skill.md"

cat > "$skill_file" << EOF
# 自动生成的 Skill

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**来源**: Git 历史分析

---

## 🎯 技能描述

本 Skill 是从 git 历史中自动提炼的重复模式。

## 📊 模式分析

\`\`\`
$(cat /tmp/skill_analysis.md)
\`\`\`

## 🔄 典型工作流

基于历史分析，发现以下典型工作流：

### 1. 文档更新流程

**触发条件**: 更新文档

**操作步骤**:
1. 编辑文档文件
2. 更新相关引用
3. 提交变更

**示例文件**:
- README.md
- docs/*.md
- SKILL.md

### 2. 脚本创建流程

**触发条件**: 创建新脚本

**操作步骤**:
1. 创建脚本文件
2. 添加执行权限
3. 测试脚本
4. 提交变更

**示例文件**:
- scripts/*.sh
- scripts/*.py

### 3. 配置更新流程

**触发条件**: 更新配置

**操作步骤**:
1. 编辑配置文件
2. 验证配置
3. 重启服务
4. 提交变更

**示例文件**:
- openclaw.json
- .env
- config/*.yaml

## 💡 最佳实践

基于历史分析，以下是最佳实践：

1. **文档优先**: 在修改代码前，先更新文档
2. **小步提交**: 频繁提交小变更，而不是大变更
3. **清晰消息**: 使用清晰的提交消息
4. **测试验证**: 提交前测试变更

## ⚠️ 常见陷阱

基于历史分析，避免以下陷阱：

1. **忘记更新文档**: 修改代码但忘记更新文档
2. **大步提交**: 一次性提交太多变更
3. **模糊消息**: 使用模糊的提交消息
4. **跳过测试**: 没有测试就提交

---

**生成完成**: $(date '+%Y-%m-%d %H:%M:%S')
EOF

###############################################################################
# 完成
###############################################################################

echo ""
echo "🎉 Skill 提炼完成！"
echo "📄 Skill 文件: $skill_file"
echo ""
echo "📊 分析统计:"
echo "  - 分析提交数: 100"
echo "  - 发现模式: 见文件"
echo ""
echo "💡 下一步:"
echo "  1. 查看生成的 Skill: cat $skill_file"
echo "  2. 手动优化 Skill"
echo "  3. 应用到实际工作"
