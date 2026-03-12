#!/bin/bash
# 🧬 超级进化系统（SES）v2.0 - 自动集成脚本
# 集成所有进化脚本，确保每次任务都执行

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 主函数
main() {
    case "$1" in
        pre-check)
            # 任务前强制检查
            bash scripts/ses-force-execution.sh
            ;;
        post-eval)
            # 任务后强制评估
            bash scripts/ses-post-task-eval.sh
            ;;
        log-error)
            # 记录错误
            error_name="$2"
            error_desc="$3"
            bash scripts/log-error.sh "$error_name" "$error_desc"
            ;;
        extract)
            # 提取模式
            bash scripts/extract-patterns.sh
            ;;
        track)
            # 追踪统计
            bash scripts/track-evolution.sh
            ;;
        *)
            echo "🧬 超级进化系统（SES）v2.0"
            echo ""
            echo "用法："
            echo "  $0 pre-check          # 任务前检查"
            echo "  $0 post-eval          # 任务后评估"
            echo "  $0 log-error <name> <desc> # 记录错误"
            echo "  $0 extract            # 提取模式"
            echo "  $0 track              # 追踪统计"
            echo ""
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
