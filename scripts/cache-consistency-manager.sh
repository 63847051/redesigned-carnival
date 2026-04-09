#!/bin/bash
# 缓存一致性管理系统 v1.0
# 基于 Claude Code Compaction 设计：版本控制 + 失效策略 + 验证机制

set -e

# =============================================================================
# ⚙️ 配置
# =============================================================================

MEMORY_DIR="/root/.openclaw/workspace/memory"
CACHE_DIR="$MEMORY_DIR/.cache"
STATE_FILE="$MEMORY_DIR/.cache-consistency-state.json"
LOG_FILE="/root/.openclaw/workspace/logs/cache-consistency.log"

# 缓存版本配置
CACHE_TTL_SECONDS=3600  # 1小时
MAX_CACHE_SIZE_MB=100

# =============================================================================
# 📊 状态管理
# =============================================================================

init_state() {
    mkdir -p "$CACHE_DIR"
    mkdir -p "$(dirname "$LOG_FILE")"

    if [ ! -f "$STATE_FILE" ]; then
        cat > "$STATE_FILE" << EOF
{
  "version": 1,
  "last_cleanup": "$(date -Iseconds)",
  "cache_entries": 0,
  "cache_size_mb": 0
}
EOF
    fi
}

get_state_value() {
    local key=$1
    grep -o "\"$key\": [^,}]*" "$STATE_FILE" | cut -d: -f2 | xargs
}

update_state() {
    local entries=$(find "$CACHE_DIR" -type f | wc -l)
    local size=$(du -sm "$CACHE_DIR" | cut -f1)

    cat > "$STATE_FILE" << EOF
{
  "version": 1,
  "last_cleanup": "$(date -Iseconds)",
  "cache_entries": $entries,
  "cache_size_mb": $size
}
EOF
}

# =============================================================================
# 🔄 缓存版本控制
# =============================================================================

get_cache_version() {
    local cache_key=$1
    local version_file="$CACHE_DIR/$cache_key.version"

    if [ -f "$version_file" ]; then
        cat "$version_file"
    else
        echo "0"
    fi
}

set_cache_version() {
    local cache_key=$1
    local version=$2
    local version_file="$CACHE_DIR/$cache_key.version"

    echo "$version" > "$version_file"
}

increment_cache_version() {
    local cache_key=$1
    local current_version=$(get_cache_version "$cache_key")
    set_cache_version "$cache_key" $((current_version + 1))
    echo $((current_version + 1))
}

# =============================================================================
# ⏰ 缓存失效策略
# =============================================================================

is_cache_expired() {
    local cache_key=$1
    local cache_file="$CACHE_DIR/$cache_key"

    if [ ! -f "$cache_file" ]; then
        return 0  # 文件不存在，视为过期
    fi

    local file_time=$(stat -c %Y "$cache_file")
    local current_time=$(date +%s)
    local age=$((current_time - file_time))

    [ $age -ge $CACHE_TTL_SECONDS ]
}

invalidate_cache() {
    local cache_key=$1
    local cache_file="$CACHE_DIR/$cache_key"
    local version_file="$CACHE_DIR/$cache_key.version"

    echo "🗑️ 失效缓存: $cache_key"

    if [ -f "$cache_file" ]; then
        rm "$cache_file"
        echo "  ✅ 已删除缓存文件"
    fi

    if [ -f "$version_file" ]; then
        rm "$version_file"
        echo "  ✅ 已删除版本文件"
    fi

    increment_cache_version "$cache_key"
}

# =============================================================================
# ✅ 缓存验证机制
# =============================================================================

validate_cache() {
    local cache_key=$1
    local cache_file="$CACHE_DIR/$cache_key"

    if [ ! -f "$cache_file" ]; then
        echo "❌ 缓存不存在"
        return 1
    fi

    if is_cache_expired "$cache_key"; then
        echo "⏰ 缓存已过期"
        invalidate_cache "$cache_key"
        return 1
    fi

    # 验证缓存完整性
    if ! grep -q "^# " "$cache_file" 2>/dev/null; then
        echo "⚠️ 缓存损坏"
        invalidate_cache "$cache_key"
        return 1
    fi

    echo "✅ 缓存有效"
    return 0
}

# =============================================================================
# 🧹 自动清理
# =============================================================================

cleanup_cache() {
    echo ""
    echo "🧹 清理过期缓存..."

    local cleaned=0
    local total_size=0

    # 查找并删除过期缓存
    find "$CACHE_DIR" -type f -name "*.md" -mtime +$((CACHE_TTL_SECONDS / 86400)) | while read cache_file; do
        local size=$(du -k "$cache_file" | cut -f1)
        rm "$cache_file"
        cleaned=$((cleaned + 1))
        total_size=$((total_size + size))
        echo "  🗑️ $(basename "$cache_file") ($size KB)"
    done

    echo "✅ 清理完成: $cleaned 个文件, $total_size KB"

    # 检查总大小
    local current_size=$(du -sm "$CACHE_DIR" | cut -f1)
    if [ $current_size -gt $MAX_CACHE_SIZE_MB ]; then
        echo "⚠️ 缓存大小超标: ${current_size}MB > ${MAX_CACHE_SIZE_MB}MB"
        echo "🧹 清理最旧的缓存..."

        # 删除最旧的文件
        find "$CACHE_DIR" -type f -name "*.md" -printf '%T@ %p\n' | \
            sort -n | head -n $((current_size - MAX_CACHE_SIZE_MB)) | \
            cut -d' ' -f2- | xargs rm -v
    fi

    # 更新状态
    update_state
}

# =============================================================================
# 📊 缓存统计
# =============================================================================

show_cache_stats() {
    echo ""
    echo "📊 缓存统计:"
    echo ""

    # 总体统计
    local entries=$(find "$CACHE_DIR" -type f | wc -l)
    local size=$(du -sm "$CACHE_DIR" | cut -f1)

    echo "总体:"
    echo "  - 缓存条目: $entries"
    echo "  - 缓存大小: ${size}MB"
    echo "  - 最大限制: ${MAX_CACHE_SIZE_MB}MB"
    echo ""

    # 过期检查
    local expired=0
    find "$CACHE_DIR" -type f -name "*.md" -mtime +$((CACHE_TTL_SECONDS / 86400)) | while read file; do
        expired=$((expired + 1))
    done 2>/dev/null || true

    echo "健康状态:"
    if [ $expired -eq 0 ]; then
        echo "  ✅ 无过期缓存"
    else
        echo "  ⚠️ $expired 个过期缓存"
    fi

    echo ""
    echo "最近缓存:"
    find "$CACHE_DIR" -type f -name "*.md" -printf '%T+ %p\n' | sort -rn | head -5 | while read line; do
        local file=$(echo "$line" | cut -d' ' -f2-)
        local time=$(echo "$line" | cut -d' ' -f1)
        local size=$(du -k "$file" | cut -f1)
        echo "  - $(basename "$file") (${size}KB, $time)"
    done
}

# =============================================================================
# 🧪 测试函数
# =============================================================================

test_cache_consistency() {
    echo ""
    echo "🧪 测试缓存一致性..."
    echo ""

    # 初始化
    init_state

    # 创建测试缓存
    local test_key="test-cache"
    local test_file="$CACHE_DIR/$test_key.md"

    echo "📝 创建测试缓存..."
    echo "# Test Cache
$(date)
" > "$test_file"

    set_cache_version "$test_key" 1
    echo "✅ 测试缓存已创建 (版本: $(get_cache_version "$test_key"))"

    # 验证缓存
    echo ""
    echo "🔍 验证缓存..."
    if validate_cache "$test_key"; then
        echo "✅ 缓存验证通过"
    else
        echo "❌ 缓存验证失败"
    fi

    # 失效缓存
    echo ""
    echo "🗑️ 失效缓存..."
    invalidate_cache "$test_key"
    echo "✅ 缓存已失效 (版本: $(get_cache_version "$test_key"))"

    # 清理测试文件
    rm -f "$test_file"

    # 显示统计
    echo ""
    show_cache_stats
}

# =============================================================================
# 🚀 主流程
# =============================================================================

main() {
    echo "💾 缓存一致性管理系统 v1.0"
    echo "⏰ 时间: $(date)"
    echo ""

    case "${1:-test}" in
        test)
            test_cache_consistency
            ;;
        cleanup)
            init_state
            cleanup_cache
            ;;
        stats)
            init_state
            show_cache_stats
            ;;
        invalidate)
            if [ -z "$2" ]; then
                echo "用法: $0 invalidate <cache_key>"
                exit 1
            fi
            init_state
            invalidate_cache "$2"
            ;;
        *)
            echo "用法: $0 {test|cleanup|stats|invalidate <key>}"
            exit 1
            ;;
    esac
}

# 执行主流程
main "$@"
