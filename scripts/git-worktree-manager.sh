#!/bin/bash
# Git Worktree 管理脚本
# 使用方法: bash scripts/git-worktree-manager.sh <command> [args]

set -e

WORKTREES_DIR="$HOME/.git-worktrees"

# 显示帮助
show_help() {
    echo "Git Worktree 管理脚本"
    echo ""
    echo "用法:"
    echo "  bash scripts/git-worktree-manager.sh create <branch> [path]"
    echo "  bash scripts/git-worktree-manager.sh list"
    echo "  bash scripts/git-worktree-manager.sh remove <path>"
    echo ""
    echo "命令:"
    echo "  create  - 创建新的 worktree"
    echo "  list    - 列出所有 worktrees"
    echo "  remove  - 删除 worktree"
    echo ""
    echo "示例:"
    echo "  bash scripts/git-worktree-manager.sh create feature/new-feature"
    echo "  bash scripts/git-worktree-manager.sh create feature/new-feature ~/workspace/new-feature"
    echo "  bash scripts/git-worktree-manager.sh list"
    echo "  bash scripts/git-worktree-manager.sh remove ~/workspace/new-feature"
}

# 创建 worktree
create_worktree() {
    local branch="$1"
    local path="${2:-}"
    
    if [ -z "$branch" ]; then
        echo "❌ 错误: 请指定分支名称"
        show_help
        exit 1
    fi
    
    # 如果没有指定路径，使用默认路径
    if [ -z "$path" ]; then
        path="$WORKTREES_DIR/$(basename $branch)"
    fi
    
    echo "🔧 创建 Git Worktree"
    echo "   分支: $branch"
    echo "   路径: $path"
    echo ""
    
    # 创建目录
    mkdir -p "$path"
    
    # 添加 worktree
    git worktree add "$path" "$branch"
    
    echo "✅ Worktree 创建成功！"
    echo ""
    echo "📍 位置: $path"
    echo "🔀 分支: $branch"
    echo ""
    echo "💡 使用方法:"
    echo "   cd $path"
    echo "   # 开始工作..."
}

# 列出 worktrees
list_worktrees() {
    echo "📋 Git Worktree 列表"
    echo ""
    
    git worktree list
    
    echo ""
    echo "💡 提示:"
    echo "   使用 'git worktree remove <path>' 删除 worktree"
}

# 删除 worktree
remove_worktree() {
    local path="$1"
    
    if [ -z "$path" ]; then
        echo "❌ 错误: 请指定 worktree 路径"
        show_help
        exit 1
    fi
    
    echo "🗑️  删除 Git Worktree"
    echo "   路径: $path"
    echo ""
    
    # 删除 worktree
    git worktree remove "$path"
    
    echo "✅ Worktree 删除成功！"
}

# 主流程
case "${1:-}" in
    create)
        create_worktree "$2" "$3"
        ;;
    list)
        list_worktrees
        ;;
    remove)
        remove_worktree "$2"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        exit 1
        ;;
esac
