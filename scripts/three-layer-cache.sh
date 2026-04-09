#!/bin/bash
# 三层缓存体系
# 基于 Open-ClaudeCode 设计：L1/L2/L3 三层缓存 + Feature Flag 控制

set -e

echo "⚡ 三层缓存体系"
echo "⏰ 时间: $(date)"

# 配置
MEMORY_DIR="/root/.openclaw/workspace/memory"
CACHE_DIR="$MEMORY_DIR/cache"
STATE_FILE="$MEMORY_DIR/.cache-state.json"

# 三层缓存配置
L1_HOT_TTL=300           # L1 热缓存：5分钟
L2_WARM_TTL=3600         # L2 温缓存：1小时
L3_COLD_TTL=86400        # L3 冷缓存：24小时

# Feature Flag 配置
FEATURE_FLAG_URL=""      # 远程 Feature Flag URL（可选）
LOCAL_FLAG_FILE="$MEMORY_DIR/.feature-flags.json"

# =============================================================================
# 🚀 Feature Flag 系统
# =============================================================================

load_feature_flags() {
    echo ""
    echo "🚀 加载 Feature Flags..."
    
    # 优先从远程加载
    if [ -n "$FEATURE_FLAG_URL" ]; then
        echo "🌐 尝试从远程加载..."
        REMOTE_FLAGS=$(curl -s "$FEATURE_FLAG_URL" 2>/dev/null || echo "")
        
        if [ -n "$REMOTE_FLAGS" ]; then
            echo "$REMOTE_FLAGS" > "$LOCAL_FLAG_FILE"
            echo "✅ 远程 Flags 已加载"
            return
        fi
    fi
    
    # 从本地文件加载
    if [ -f "$LOCAL_FLAG_FILE" ]; then
        echo "📁 从本地加载..."
        echo "✅ 本地 Flags 已加载"
    else
        # 创建默认 Flags
        cat > "$LOCAL_FLAG_FILE" << FLAGS
{
  "enable_cache_v3": true,
  "enable_l1_hot": true,
  "enable_l2_warm": true,
  "enable_l3_cold": true,
  "enable_compression": false,
  "version": "1.0"
}
FLAGS
        echo "✅ 默认 Flags 已创建"
    fi
}

check_feature_flag() {
    local flag_name=$1
    local default_value=${2:-false}
    
    if [ -f "$LOCAL_FLAG_FILE" ]; then
        local value=$(grep -o "\"$flag_name\": [^,}]*" "$LOCAL_FLAG_FILE" | cut -d' ' -f2)
        
        if [ "$value" = "true" ]; then
            return 0  # true
        else
            return 1  # false
        fi
    fi
    
    return $default_value
}

# =============================================================================
# ⚡ 三层缓存实现
# =============================================================================

init_cache_layers() {
    echo ""
    echo "⚡ 初始化三层缓存..."
    
    mkdir -p "$CACHE_DIR"/{l1_hot,l2_warm,l3_cold}
    
    echo "✅ L1 热缓存 (5分钟 TTL): $CACHE_DIR/l1_hot"
    echo "✅ L2 温缓存 (1小时 TTL): $CACHE_DIR/l2_warm"
    echo "✅ L3 冷缓存 (24小时 TTL): $CACHE_DIR/l3_cold"
}

put_to_cache() {
    local layer=$1
    local key=$2
    local value=$3
    
    local cache_file="$CACHE_DIR/${layer}/${key}.cache"
    
    # 写入缓存
    cat > "$cache_file" << CACHE
{
  "key": "$key",
  "value": $value,
  "created_at": $(date +%s),
  "ttl": $([ "$layer" = "l1_hot" ] && echo $L1_HOT_TTL || [ "$layer" = "l2_warm" ] && echo $L2_WARM_TTL || echo $L3_COLD_TTL)
}
CACHE
    
    echo "✅ 缓存已写入: $layer/$key"
}

get_from_cache() {
    local layer=$1
    local key=$2
    
    local cache_file="$CACHE_DIR/${layer}/${key}.cache"
    
    if [ ! -f "$cache_file" ]; then
        echo "⏸️ 缓存未命中: $layer/$key"
        return 1
    fi
    
    # 检查是否过期
    local created_at=$(grep -o '"created_at": [0-9]*' "$cache_file" | grep -o '[0-9]*')
    local ttl=$(grep -o '"ttl": [0-9]*' "$cache_file" | grep -o '[0-9]*')
    local current_time=$(date +%s)
    
    local age=$((current_time - created_at))
    
    if [ $age -gt $ttl ]; then
        echo "⏰ 缓存已过期: $layer/$key (age: ${age}s, ttl: ${ttl}s)"
        rm "$cache_file"
        return 1
    fi
    
    echo "✅ 缓存命中: $layer/$key"
    grep -o '"value": [^}]*' "$cache_file" | cut -d' ' -f2-
    return 0
}

# =============================================================================
# 🧹 缓存清理
# =============================================================================

clean_expired_cache() {
    echo ""
    echo "🧹 清理过期缓存..."
    
    local current_time=$(date +%s)
    local cleaned=0
    
    for layer in l1_hot l2_warm l3_cold; do
        for cache_file in "$CACHE_DIR/$layer"/*.cache; do
            if [ -f "$cache_file" ]; then
                local created_at=$(grep -o '"created_at": [0-9]*' "$cache_file" | grep -o '[0-9]*')
                local ttl=$(grep -o '"ttl": [0-9]*' "$cache_file" | grep -o '[0-9]*')
                
                if [ -n "$created_at" ] && [ -n "$ttl" ]; then
                    local age=$((current_time - created_at))
                    
                    if [ $age -gt $ttl ]; then
                        rm "$cache_file"
                        cleaned=$((cleaned + 1))
                    fi
                fi
            fi
        done
    done
    
    echo "✅ 已清理 $cleaned 个过期缓存"
}

# =============================================================================
# 📊 缓存统计
# =============================================================================

cache_stats() {
    echo ""
    echo "📊 缓存统计..."
    
    local l1_count=$(ls -1 "$CACHE_DIR/l1_hot"/*.cache 2>/dev/null | wc -l)
    local l2_count=$(ls -1 "$CACHE_DIR/l2_warm"/*.cache 2>/dev/null | wc -l)
    local l3_count=$(ls -1 "$CACHE_DIR/l3_cold"/*.cache 2>/dev/null | wc -l)
    
    echo "📈 L1 热缓存: $l1_count 项"
    echo "📈 L2 温缓存: $l2_count 项"
    echo "📈 L3 冷缓存: $l3_count 项"
    echo "📈 总计: $((l1_count + l2_count + l3_count)) 项"
}

# =============================================================================
# 🚀 主流程
# =============================================================================

main() {
    # Step 1: 加载 Feature Flags
    load_feature_flags
    
    # Step 2: 检查是否启用三层缓存
    if ! check_feature_flag "enable_cache_v3"; then
        echo ""
        echo "⏸️ 三层缓存未启用 (Feature Flag: enable_cache_v3 = false)"
        exit 0
    fi
    
    echo "✅ 三层缓存已启用"
    
    # Step 3: 初始化缓存层
    init_cache_layers
    
    # Step 4: 清理过期缓存
    clean_expired_cache
    
    # Step 5: 显示统计
    cache_stats
    
    # Step 6: 示例：写入和读取测试缓存
    echo ""
    echo "🧪 测试缓存..."
    
    # 写入测试
    put_to_cache "l1_hot" "test_key" '"test_value"'
    
    # 读取测试
    get_from_cache "l1_hot" "test_key"
    
    echo ""
    echo "🎉 三层缓存系统运行正常！"
}

# 执行主流程
main
