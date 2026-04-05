#!/bin/bash
# QMD 搜索缓存

CACHE_DIR="/tmp/pageindex-cache"
CACHE_TTL=300  # 5分钟

cache_search() {
    local query="$1"
    local cache_file="$CACHE_DIR/$(echo "$query" | md5sum | cut -d' ' -f1).txt"
    
    # 检查缓存
    if [ -f "$cache_file" ]; then
        local cache_age=$(($(date +%s) - $(stat -c %Y "$cache_file")))
        if [ $cache_age -lt $CACHE_TTL ]; then
            echo "📦 缓存命中"
            cat "$cache_file"
            return 0
        fi
    fi
    
    # 执行搜索
    qmd search memory "$query" | tee "$cache_file"
}
