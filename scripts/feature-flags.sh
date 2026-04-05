#!/bin/bash
# Feature Flags 管理脚本
# 用于管理 OpenClaw 系统的功能开关

set -e

WORKSPACE="/root/.openclaw/workspace"
CONFIG_FILE="$WORKSPACE/feature-flags.json"
SCRIPTS_DIR="$WORKSPACE/scripts"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# 检查依赖
check_dependencies() {
    if ! command -v jq &> /dev/null; then
        log_warning "jq 未安装，将使用 Python 解析 JSON"
        return 1
    fi
    return 0
}

# 列出所有功能开关
list_flags() {
    log_info "功能开关列表："
    echo ""
    
    if command -v jq &> /dev/null; then
        jq -r '.flags | to_entries[] | "\(.key): \(.value.enabled // "false") - \(.value.description)"' "$CONFIG_FILE" | while read line; do
            if echo "$line" | grep -q "true"; then
                echo -e "${GREEN}✅${NC} $line"
            else
                echo -e "${GRAY}⚪${NC} $line"
            fi
        done
    else
        python3 -c "
import json
with open('$CONFIG_FILE') as f:
    config = json.load(f)
    for key, value in config['flags'].items():
        status = '✅' if value.get('enabled', False) else '⚪'
        print(f'{status} {key}: {value.get(\"enabled\", False)} - {value.get(\"description\", \"\")}')
"
    fi
    
    echo ""
    log_info "已启用: $(jq -r '.metadata.enabled_count' "$CONFIG_FILE" 2>/dev/null || echo "3") 个功能"
    log_info "未启用: $(jq -r '.metadata.disabled_count' "$CONFIG_FILE" 2>/dev/null || echo "7") 个功能"
}

# 检查功能是否启用
check_flag() {
    local flag_name=$1
    
    if [ -z "$flag_name" ]; then
        log_error "请提供功能名称"
        return 1
    fi
    
    if command -v jq &> /dev/null; then
        local enabled=$(jq -r ".flags.${flag_name}.enabled // false" "$CONFIG_FILE")
    else
        local enabled=$(python3 -c "import json; config=json.load(open('$CONFIG_FILE')); print(config['flags'].get('$flag_name', {}).get('enabled', False))")
    fi
    
    if [ "$enabled" = "true" ]; then
        log_success "功能 '$flag_name' 已启用"
        return 0
    else
        log_warning "功能 '$flag_name' 未启用"
        return 1
    fi
}

# 启用功能
enable_flag() {
    local flag_name=$1
    
    if [ -z "$flag_name" ]; then
        log_error "请提供功能名称"
        return 1
    fi
    
    # 检查功能是否存在
    if ! command -v jq &> /dev/null; then
        local exists=$(python3 -c "import json; config=json.load(open('$CONFIG_FILE')); print('exists' if '$flag_name' in config['flags'] else 'not_exists')")
    else
        local exists=$(jq -r ".flags.${flag_name} // \"not_exists\"" "$CONFIG_FILE")
    fi
    
    if [ "$exists" = "not_exists" ]; then
        log_error "功能 '$flag_name' 不存在"
        return 1
    fi
    
    # 启用功能
    if command -v jq &> /dev/null; then
        jq ".flags.${flag_name}.enabled = true | .metadata.enabled_count += 1 | .metadata.disabled_count -= 1" "$CONFIG_FILE" > "${CONFIG_FILE}.tmp" && mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
    else
        python3 << EOF
import json
with open('$CONFIG_FILE') as f:
    config = json.load(f)

if '$flag_name' in config['flags']:
    config['flags']['$flag_name']['enabled'] = True
    config['metadata']['enabled_count'] = config['metadata'].get('enabled_count', 0) + 1
    config['metadata']['disabled_count'] = config['metadata'].get('disabled_count', 0) - 1
    config['metadata']['last_review'] = '$(date +%Y-%m-%d)'
    
    with open('$CONFIG_FILE', 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
EOF
    fi
    
    log_success "功能 '$flag_name' 已启用"
}

# 禁用功能
disable_flag() {
    local flag_name=$1
    
    if [ -z "$flag_name" ]; then
        log_error "请提供功能名称"
        return 1
    fi
    
    # 禁用功能
    if command -v jq &> /dev/null; then
        jq ".flags.${flag_name}.enabled = false | .metadata.enabled_count -= 1 | .metadata.disabled_count += 1" "$CONFIG_FILE" > "${CONFIG_FILE}.tmp" && mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
    else
        python3 << EOF
import json
with open('$CONFIG_FILE') as f:
    config = json.load(f)

if '$flag_name' in config['flags']:
    config['flags']['$flag_name']['enabled'] = False
    config['metadata']['enabled_count'] = config['metadata'].get('enabled_count', 0) - 1
    config['metadata']['disabled_count'] = config['metadata'].get('disabled_count', 0) + 1
    config['metadata']['last_review'] = '$(date +%Y-%m-%d)'
    
    with open('$CONFIG_FILE', 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
EOF
    fi
    
    log_success "功能 '$flag_name' 已禁用"
}

# 获取功能详情
get_flag_info() {
    local flag_name=$1
    
    if [ -z "$flag_name" ]; then
        log_error "请提供功能名称"
        return 1
    fi
    
    log_info "功能 '$flag_name' 详细信息："
    echo ""
    
    if command -v jq &> /dev/null; then
        jq -r ".flags.${flag_name}" "$CONFIG_FILE"
    else
        python3 << EOF
import json
with open('$CONFIG_FILE') as f:
    config = json.load(f)
    if '$flag_name' in config['flags']:
        import pprint
        pprint.pprint(config['flags']['$flag_name'])
    else:
        print("功能 '$flag_name' 不存在")
EOF
    fi
}

# 按组列出功能
list_by_group() {
    local group_name=$1
    
    if [ -z "$group_name" ]; then
        log_error "请提供组名称 (experimental/stable/optimization)"
        return 1
    fi
    
    log_info "组 '$group_name' 的功能："
    echo ""
    
    if command -v jq &> /dev/null; then
        jq -r ".groups.${group_name}.flags[]" "$CONFIG_FILE" | while read flag; do
            check_flag "$flag"
        done
    else
        python3 << EOF
import json
with open('$CONFIG_FILE') as f:
    config = json.load(f)
    if '$group_name' in config['groups']:
        for flag in config['groups']['$group_name']['flags']:
            enabled = config['flags'][flag].get('enabled', False)
            status = '✅' if enabled else '⚪'
            desc = config['flags'][flag].get('description', '')
            print(f'{status} {flag}: {desc}')
EOF
    fi
}

# 主函数
main() {
    local action=$1
    shift
    
    case "$action" in
        list)
            list_flags
            ;;
        check)
            check_flag "$@"
            ;;
        enable)
            enable_flag "$@"
            ;;
        disable)
            disable_flag "$@"
            ;;
        info)
            get_flag_info "$@"
            ;;
        group)
            list_by_group "$@"
            ;;
        *)
            echo "Feature Flags 管理脚本"
            echo ""
            echo "用法: $0 {list|check|enable|disable|info|group} [options]"
            echo ""
            echo "命令:"
            echo "  list                    列出所有功能开关"
            echo "  check <flag_name>        检查功能是否启用"
            echo "  enable <flag_name>       启用功能"
            echo "  disable <flag_name>      禁用功能"
            echo "  info <flag_name>         获取功能详细信息"
            echo "  group <group_name>       按组列出功能"
            echo ""
            echo "示例:"
            echo "  $0 list"
            echo "  $0 check TASK_AGENT_LOOP"
            echo "  $0 enable PROACTIVE_MODE"
            echo "  $0 disable KAIROS_SCHEDULER"
            echo "  $0 info MEMORY_SEARCH"
            echo "  $0 group stable"
            exit 1
            ;;
    esac
}

main "$@"
