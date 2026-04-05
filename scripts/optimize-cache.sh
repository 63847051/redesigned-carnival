#!/bin/bash
# 缓存机制优化脚本
# 参考 Claude Code 的缓存优化策略

set -e

WORKSPACE="/root/.openclaw/workspace"
SCRIPTS_DIR="$WORKSPACE/scripts"
TOOLS_CACHE="$WORKSPACE/.cache/tools"
CONFIG_CACHE="$WORKSPACE/.cache/config"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

# 创建缓存目录
init_cache() {
    log_info "初始化缓存目录..."
    
    mkdir -p "$TOOLS_CACHE"
    mkdir -p "$CONFIG_CACHE"
    
    log_success "缓存目录已创建"
}

# 优化工具排序（按字母表锁死）
optimize_tool_order() {
    log_info "优化工具排序..."
    
    # 获取所有脚本
    find "$SCRIPTS_DIR" -name "*.sh" -o -name "*.py" | sort > "$TOOLS_CACHE/tools_list.txt"
    
    # 生成排序后的工具索引
    {
        echo "# 工具索引（按字母表排序）"
        echo "# 生成时间: $(date)"
        echo ""
        
        # Shell 脚本
        echo "## Shell 脚本"
        find "$SCRIPTS_DIR" -name "*.sh" | sort | while read script; do
            basename "$script"
        done
        
        echo ""
        
        # Python 脚本
        echo "## Python 脚本"
        find "$SCRIPTS_DIR" -name "*.py" | sort | while read script; do
            basename "$script"
        done
        
    } > "$TOOLS_CACHE/tools_index.md"
    
    log_success "工具排序已优化"
    log_info "工具列表: $(wc -l < "$TOOLS_CACHE/tools_list.txt") 个"
}

# 优化配置文件命名（使用内容哈希）
optimize_config_naming() {
    log_info "优化配置文件命名..."
    
    # 处理主要配置文件
    for config_file in "$WORKSPACE"/{SOUL.md,IDENTITY.md,AGENTS.md,MEMORY.md,HEARTBEAT.md}; do
        if [ -f "$config_file" ]; then
            # 计算内容哈希
            filename=$(basename "$config_file")
            hash=$(md5sum "$config_file" | cut -d' ' -f1)
            
            # 创建符号链接（使用哈希值）
            ln -sf "$config_file" "$CONFIG_CACHE/${filename}.${hash}"
            
            log_info "  $filename -> ${filename}.${hash}"
        fi
    done
    
    log_success "配置文件命名已优化"
}

# 生成缓存统计
cache_stats() {
    log_info "缓存统计："
    echo ""
    
    echo "工具缓存:"
    echo "  目录: $TOOLS_CACHE"
    echo "  文件: $(find "$TOOLS_CACHE" -type f | wc -l) 个"
    echo "  大小: $(du -sh "$TOOLS_CACHE" 2>/dev/null | cut -f1)"
    echo ""
    
    echo "配置缓存:"
    echo "  目录: $CONFIG_CACHE"
    echo "  文件: $(find "$CONFIG_CACHE" -type f | wc -l) 个"
    echo "  大小: $(du -sh "$CONFIG_CACHE" 2>/dev/null | cut -f1)"
}

# 清理缓存
clean_cache() {
    log_info "清理缓存..."
    
    rm -rf "$TOOLS_CACHE"
    rm -rf "$CONFIG_CACHE"
    
    log_success "缓存已清理"
}

# 验证缓存
verify_cache() {
    log_info "验证缓存..."
    
    if [ -d "$TOOLS_CACHE" ]; then
        log_success "工具缓存存在"
    else
        log_warning "工具缓存不存在"
    fi
    
    if [ -d "$CONFIG_CACHE" ]; then
        log_success "配置缓存存在"
    else
        log_warning "配置缓存不存在"
    fi
}

# 主函数
main() {
    local action=$1
    
    case "$action" in
        init)
            init_cache
            ;;
        
        optimize)
            init_cache
            optimize_tool_order
            optimize_config_naming
            cache_stats
            ;;
        
        stats)
            cache_stats
            ;;
        
        clean)
            clean_cache
            ;;
        
        verify)
            verify_cache
            ;;
        
        *)
            echo "缓存机制优化脚本"
            echo ""
            echo "用法: $0 {init|optimize|stats|clean|verify}"
            echo ""
            echo "命令:"
            echo "  init     - 初始化缓存目录"
            echo "  optimize - 优化缓存（排序+命名）"
            echo "  stats    - 显示缓存统计"
            echo "  clean    - 清理缓存"
            echo "  verify   - 验证缓存"
            echo ""
            exit 1
            ;;
    esac
}

main "$@"
