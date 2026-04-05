#!/bin/bash
###############################################################################
# Git Worktrees - 真正的并行能力
# 功能: 创建和管理多个独立工作目录
###############################################################################

echo "🌳 Git Worktrees - 真正的并行能力"
echo "⏰ 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查是否在 git 仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
  echo "❌ 错误: 当前目录不是 git 仓库"
  echo "💡 建议: 先初始化 git 仓库"
  exit 1
fi

###############################################################################
# 1. 列出现有的 worktrees
###############################################################################

echo "## 📂 现有的 Worktrees"
echo ""

if git worktree list > /dev/null 2>&1; then
  git worktree list
  echo ""
  
  # 统计数量
  worktree_count=$(git worktree list | wc -l)
  echo "✅ 发现 $worktree_count 个 worktree"
else
  echo "⚠️  没有发现 worktree"
  echo "💡 这是正常的，worktree 需要手动创建"
fi

echo ""

###############################################################################
# 2. 创建新的 worktree（示例）
###############################################################################

echo "## 🔧 创建新的 Worktree"
echo ""

echo "### 创建 worktree 的步骤:"
echo ""
echo "1. 创建 bugfix worktree:"
echo "   git worktree add ../project-bugfix bugfix/"
echo ""
echo "2. 创建 feature worktree:"
echo "   git worktree add ../project-feature feature/"
echo ""
echo "3. 创建 experiment worktree:"
echo "   git worktree add ../project-experiment experiment/"
echo ""

# 提供交互式创建
read -p "是否要创建新的 worktree？(y/n): " create_worktree

if [ "$create_worktree" = "y" ] || [ "$create_worktree" = "Y" ]; then
  echo ""
  read -p "输入 worktree 路径 (如 ../project-bugfix): " worktree_path
  read -p "输入分支名 (如 bugfix/memory-leak): " branch_name
  
  if [ -n "$worktree_path" ] && [ -n "$branch_name" ]; then
    echo ""
    echo "🔧 创建 worktree: $worktree_path (分支: $branch_name)"
    
    if git worktree add "$worktree_path" "$branch_name"; then
      echo "✅ Worktree 创建成功！"
      echo ""
      echo "📁 Worktree 路径: $worktree_path"
      echo "🌿 分支名称: $branch_name"
      echo ""
      echo "💡 下一步:"
      echo "  cd $worktree_path"
      echo "  # 在这里工作，与主目录完全独立"
    else
      echo "❌ Worktree 创建失败"
      echo "💡 可能的原因:"
      echo "  - 路径已存在"
      echo "  - 分支不存在"
      echo "  - 权限问题"
    fi
  else
    echo "⚠️  路径或分支名为空，跳过创建"
  fi
else
  echo "⏭️  跳过创建"
fi

echo ""

###############################################################################
# 3. Worktree 使用指南
###############################################################################

echo "## 📖 Worktree 使用指南"
echo ""

echo "### 基本操作"
echo ""
echo "# 列出所有 worktree"
echo "git worktree list"
echo ""
echo "# 创建新 worktree"
echo "git worktree add ../project-bugfix bugfix/"
echo ""
echo "# 删除 worktree"
echo "git worktree remove ../project-bugfix"
echo ""
echo "# 清理过期的 worktree"
echo "git worktree prune"
echo ""

echo "### 典型工作流"
echo ""
echo "# 1. 创建 bugfix worktree"
echo "git worktree add ../project-bugfix bugfix/memory-leak"
echo "cd ../project-bugfix"
echo "# 修复 bug..."
echo "git add ."
echo "git commit -m 'Fix memory leak'"
echo "cd ../project  # 回到主目录"
echo ""
echo "# 2. 创建 feature worktree"
echo "git worktree add ../project-feature feature/export-api"
echo "cd ../project-feature"
echo "# 开发功能..."
echo "git add ."
echo "git commit -m 'Add export API'"
echo "cd ../project  # 回到主目录"
echo ""
echo "# 3. 同时工作（两个终端）"
echo "# 终端 1:"
echo "cd ../project-bugfix && claude"
echo "# 终端 2:"
echo "cd ../project-feature && claude"
echo ""

###############################################################################
# 4. Worktree vs 分支切换
###############################################################################

echo "## 🔄 Worktree vs 分支切换"
echo ""

echo "### 传统方式（分支切换）"
echo ""
echo "# 只能同时工作在一个分支上"
echo "git checkout bugfix-1"
echo "# 修复 bug..."
echo "git commit -am 'Fix bug 1'"
echo ""
echo "git checkout bugfix-2"
echo "# 修复 bug..."
echo "git commit -am 'Fix bug 2'"
echo ""
echo "⚠️  问题:"
echo "  - 需要频繁切换分支"
echo "  - 可能遇到冲突"
echo "  - 无法同时工作"
echo ""

echo "### Worktree 方式（并行工作）"
echo ""
echo "# 可以同时工作在多个分支上"
echo "git worktree add ../project-bugfix-1 bugfix-1"
echo "git worktree add ../project-bugfix-2 bugfix-2"
echo ""
echo "# 终端 1: 修复 bug-1"
echo "cd ../project-bugfix-1 && claude"
echo ""
echo "# 终端 2: 修复 bug-2（同时进行）"
echo "cd ../project-bugfix-2 && claude"
echo ""
echo "✅ 优势:"
echo "  - 无需切换分支"
echo "  - 完全独立工作"
echo "  - 可以同时进行"
echo "  - 共享 git 历史"
echo ""

###############################################################################
# 5. 实战案例
###############################################################################

echo "## 💼 实战案例"
echo ""

echo "### 案例 1: 修复多个 bug"
echo ""
echo "# 场景: 需要同时修复 3 个 bug"
echo ""
echo "# 创建 3 个 worktree"
echo "git worktree add ../bugfix-1 bugfix/issue-101"
echo "git worktree add ../bugfix-2 bugfix/issue-102"
echo "git worktree add ../bugfix-3 bugfix/issue-103"
echo ""
echo "# 同时工作（3 个终端）"
echo "cd ../bugfix-1 && claude  # 终端 1"
echo "cd ../bugfix-2 && claude  # 终端 2"
echo "cd ../bugfix-3 && claude  # 终端 3"
echo ""

echo "### 案例 2: 开发多个 feature"
echo ""
echo "# 场景: 需要同时开发 2 个 feature"
echo ""
echo "# 创建 2 个 worktree"
echo "git worktree add ../feature-a feature/a"
echo "git worktree add ../feature-b feature/b"
echo ""
echo "# 同时开发（2 个终端）"
echo "cd ../feature-a && claude  # 终端 1"
echo "cd ../feature-b && claude  # 终端 2"
echo ""

echo "### 案例 3: Code Review + 开发"
echo ""
echo "# 场景: 需要 review 代码，同时继续开发"
echo ""
echo "# 创建 review worktree"
echo "git worktree add ../review pr/123"
echo ""
echo "# 同时工作（2 个终端）"
echo "cd ../review && claude  # 终端 1: review PR"
echo "# 在主目录继续开发     # 终端 2: 继续开发"
echo ""

###############################################################################
# 6. 清理和维护
###############################################################################

echo "## 🧹 清理和维护"
echo ""

echo "### 删除 worktree"
echo ""
echo "# 删除特定 worktree"
echo "git worktree remove ../project-bugfix"
echo ""
echo "# 删除后清理"
echo "git worktree prune"
echo ""

echo "### 查看状态"
echo ""
echo "# 列出所有 worktree"
echo "git worktree list"
echo ""
echo "# 查看每个 worktree 的状态"
echo "for wt in \$(git worktree list | awk '{print \$1}'); do"
echo "  echo \"Worktree: \$wt\""
echo "  cd \"\$wt\" && git status"
echo "  cd -"
echo "done"
echo ""

###############################################################################
# 7. 注意事项
###############################################################################

echo "## ⚠️  注意事项"
echo ""

echo "### 1. 路径问题"
echo ""
echo "⚠️  不要创建嵌套的 worktree"
echo "❌ 错误: git worktree add ./subdir bugfix"
echo "✅ 正确: git worktree add ../project-bugfix bugfix"
echo ""

echo "### 2. 分支问题"
echo ""
echo "⚠️  确保分支存在"
echo "# 先创建分支"
echo "git branch bugfix/memory-leak"
echo "# 再创建 worktree"
echo "git worktree add ../project-bugfix bugfix/memory-leak"
echo ""

echo "### 3. 清理问题"
echo ""
echo "⚠️  删除 worktree 前先删除目录"
echo "git worktree remove ../project-bugfix"
echo "# 如果失败，手动删除"
echo "rm -rf ../project-bugfix"
echo "git worktree prune"
echo ""

###############################################################################
# 完成
###############################################################################

echo ""
echo "🎉 完成！"
echo ""
echo "📊 Git Worktrees 统计:"
echo "  - 现有 worktree: $worktree_count 个"
echo "  - Git 仓库: 已确认"
echo "  - 工作目录: $(pwd)"
echo ""
echo "💡 下一步:"
echo "  1. 创建 worktree 进行并行工作"
echo "  2. 在不同 worktree 中同时使用不同的 Agent"
echo "  3. 定期清理过期的 worktree"
echo ""
echo "📖 更多信息:"
echo "  - git worktree help"
echo "  - git worktree list"
echo "  - https://git-scm.com/docs/git-worktree"
