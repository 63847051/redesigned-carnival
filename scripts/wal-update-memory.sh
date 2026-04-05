#!/bin/bash
# =============================================================================
# WAL 记忆更新脚本 - WAL Memory Update Helper
# =============================================================================
# 功能: 标准化记忆更新流程，自动验证写入结果
# 作者: 大领导 🎯
# 创建: 2026-04-02
# =============================================================================

set -euo pipefail

# =============================================================================
# 配置
# =============================================================================

MEMORY_DIR="${MEMORY_DIR:-/root/.openclaw/workspace/memory}"
SESSION_STATE="${SESSION_STATE:-${MEMORY_DIR}/../SESSION-STATE.md}"
TODAY_LOG="${TODAY_LOG:-${MEMORY_DIR}/$(date +%Y-%m-%d).md}"
VERIFY_SCRIPT="${VERIFY_SCRIPT:-${MEMORY_DIR}/../scripts/wal-verify.sh}"
MAX_RETRIES="${MAX_RETRIES:-3}"
DRY_RUN="${DRY_RUN:-false}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# =============================================================================
# 工具函数
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $@"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $@"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $@"
}

log_error() {
    echo -e "${RED}[✗]${NC} $@"
}

# =============================================================================
# WAL 核心函数
# =============================================================================

wal_write_with_retry() {
    local file=$1
    local content=$2
    local max_retries=${3:-$MAX_RETRIES}

    log_info "写入文件: $file"

    local retry=0
    while [ $retry -lt $max_retries ]; do
        # 尝试写入
        if [ "$DRY_RUN" = "true" ]; then
            log_info "[DRY RUN] 会写入: $file"
        else
            echo "$content" >> "$file"
        fi

        # 验证写入
        if [ "$DRY_RUN" = "false" ]; then
            if [ -x "$VERIFY_SCRIPT" ]; then
                if "$VERIFY_SCRIPT" -q file "$file" "$content" 2>/dev/null; then
                    log_success "写入并验证成功"
                    return 0
                fi
            else
                # 简单验证：检查文件是否存在且非空
                if [ -f "$file" ] && [ -s "$file" ]; then
                    log_success "写入成功（简单验证）"
                    return 0
                fi
            fi
        else
            log_success "[DRY RUN] 写入成功"
            return 0
        fi

        # 失败重试
        retry=$((retry + 1))
        if [ $retry -lt $max_retries ]; then
            log_warning "验证失败，第 $retry 次重试..."
            sleep 1
        fi
    done

    log_error "写入失败，已重试 $max_retries 次"
    return 1
}

wal_update_session_state() {
    local task=$1
    local status=${2:-进行中}
    local details=${3:-}

    log_info "更新 SESSION-STATE.md"

    local content=""
    content+="# 当前任务\\n"
    content+="**任务**: $task\\n"
    content+="**状态**: $status\\n"
    content+="**时间**: $(date '+%Y-%m-%d %H:%M:%S')\\n"

    if [ -n "$details" ]; then
        content+="**详情**: $details\\n"
    fi

    if [ "$DRY_RUN" = "false" ]; then
        echo -e "$content" > "$SESSION_STATE"
    fi

    # 验证
    if [ -x "$VERIFY_SCRIPT" ]; then
        if "$VERIFY_SCRIPT" -q session 2>/dev/null; then
            log_success "SESSION-STATE.md 更新成功"
            return 0
        else
            log_error "SESSION-STATE.md 验证失败"
            return 1
        fi
    fi

    return 0
}

wal_add_retain() {
    local type=$1  # W, B, O
    local domain=$2
    local content=$3
    local confidence=${4:-}

    log_info "添加 Retain 条目: [$type] $domain"

    # 确保今日日志存在
    if [ ! -f "$TODAY_LOG" ]; then
        log_info "创建今日日志: $TODAY_LOG"
        touch "$TODAY_LOG"
    fi

    # 构建 Retain 条目
    local retain_entry=""
    if [ "$type" = "O" ] && [ -n "$confidence" ]; then
        retain_entry="- ${type}(c=${confidence}) @${domain}: ${content}"
    else
        retain_entry="- ${type} @${domain}: ${content}"
    fi

    # 检查是否已有 Retain 段落
    if ! grep -q "^## 🧠 Retain" "$TODAY_LOG" 2>/dev/null; then
        log_info "创建 Retain 段落"
        local retain_section="\\n## 🧠 Retain - 结构化记忆提取\\n\\n"
        retain_section+="### 世界知识 (W) - World Facts\\n"
        retain_section+="_客观的、持久的事实性知识_\\n\\n"
        retain_section+="### 行为记录 (B) - Behavior\\n"
        retain_section+="_Agent 执行的具体行动和项目进展_\\n\\n"
        retain_section+="### 观点偏好 (O) - Opinions\\n"
        retain_section+="_带主观判断的观点、偏好、趋势观察_\\n"

        if [ "$DRY_RUN" = "false" ]; then
            echo -e "$retain_section" >> "$TODAY_LOG"
        fi
    fi

    # 添加条目到对应段落
    local section_pattern=""
    case $type in
        W)
            section_pattern="^### 世界知识"
            ;;
        B)
            section_pattern="^### 行为记录"
            ;;
        O)
            section_pattern="^### 观点偏好"
            ;;
        *)
            log_error "未知的 Retain 类型: $type"
            return 1
            ;;
    esac

    # 找到对应段落并添加
    if [ "$DRY_RUN" = "false" ]; then
        # 使用 sed 在对应段落后添加
        if grep -q "$section_pattern" "$TODAY_LOG"; then
            # 找到段落后的第一个空行，在其后插入
            sed -i "/$section_pattern/,/^### /{ /^### /! s|^###.*|&\\n$retain_entry|; }" "$TODAY_LOG" 2>/dev/null || \
                echo "$retain_entry" >> "$TODAY_LOG"
        else
            echo "$retain_entry" >> "$TODAY_LOG"
        fi
    fi

    # 验证
    if [ -x "$VERIFY_SCRIPT" ]; then
        if "$VERIFY_SCRIPT" -q retain "$TODAY_LOG" 2>/dev/null; then
            log_success "Retain 条目添加成功"
            return 0
        else
            log_warning "Retain 格式验证失败（可能格式不正确）"
            return 0  # 不阻塞
        fi
    fi

    return 0
}

wal_log_decision() {
    local decision=$1
    local reason=${2:-}
    local impact=${3:-}

    log_info "记录决策: $decision"

    local content="\\n### $(date '+%Y-%m-%d %H:%M') - $decision\\n"
    if [ -n "$reason" ]; then
        content+="**原因**: $reason\\n"
    fi
    if [ -n "$impact" ]; then
        content+="**影响**: $impact\\n"
    fi

    # 写入决策日志
    local decisions_log="${MEMORY_DIR}/decisions-log.md"
    wal_write_with_retry "$decisions_log" "$content"

    # 同时添加 Retain 条目
    wal_add_retain "O" "决策" "$decision" "0.8"

    return 0
}

wal_complete_task() {
    local task=$1
    local result=${2:-完成}

    log_info "完成任务: $task"

    # 更新 SESSION-STATE.md
    wal_update_session_state "$task" "已完成" "$result"

    # 添加到 Retain
    wal_add_retain "B" "任务" "完成：$task"

    # 写入今日日志
    local log_entry="\\n### ✅ $task\\n"
    log_entry+="**完成时间**: $(date '+%Y-%m-%d %H:%M:%S')\\n"
    log_entry+="**结果**: $result\\n"

    wal_write_with_retry "$TODAY_LOG" "$log_entry"

    return 0
}

# =============================================================================
# 主流程
# =============================================================================

show_usage() {
    cat << EOF
用法: $0 <命令> [参数]

命令:
  retain <W|B|O> <领域> <内容> [信心度]  添加 Retain 条目
  decision <决策> [原因] [影响]           记录决策
  complete <任务> [结果]                 完成任务
  session <任务> [状态] [详情]           更新 SESSION-STATE.md
  write <文件> <内容>                    写入并验证文件

选项:
  --dry-run    预演模式，不实际写入
  --help       显示帮助

示例:
  # 添加世界知识
  $0 retain W "飞书API" "飞书不支持 img 标签"

  # 记录行为
  $0 retain B "项目" "完成 Agent-Reach 安装"

  # 记录观点
  $0 retain O "策略" "深度长文更受欢迎" 0.9

  # 记录决策
  $0 decision "使用智谱 AI embeddings" "免费且 1024 维"

  # 完成任务
  $0 complete "记忆清理脚本" "3 个脚本全部测试通过"

  # 更新会话状态
  $0 session "创建 WAL 验证工具" "进行中"

  # 写入文件
  $0 write memory/2026-04-02.md "新内容"

EOF
}

main() {
    if [ $# -eq 0 ]; then
        show_usage
        exit 0
    fi

    local command=$1
    shift

    case $command in
        retain)
            if [ $# -lt 3 ]; then
                log_error "参数不足"
                show_usage
                exit 1
            fi
            wal_add_retain "$@"
            ;;
        decision)
            if [ $# -lt 1 ]; then
                log_error "参数不足"
                show_usage
                exit 1
            fi
            wal_log_decision "$@"
            ;;
        complete)
            if [ $# -lt 1 ]; then
                log_error "参数不足"
                show_usage
                exit 1
            fi
            wal_complete_task "$@"
            ;;
        session)
            if [ $# -lt 1 ]; then
                log_error "参数不足"
                show_usage
                exit 1
            fi
            wal_update_session_state "$@"
            ;;
        write)
            if [ $# -lt 2 ]; then
                log_error "参数不足"
                show_usage
                exit 1
            fi
            wal_write_with_retry "$@"
            ;;
        --dry-run)
            DRY_RUN=true
            main "$@"
            ;;
        --help|"")
            show_usage
            exit 0
            ;;
        *)
            log_error "未知命令: $command"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
