#!/bin/bash
# pageindex-rag 记忆搜索集成
# 作为默认记忆搜索方法

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"

# 记忆搜索函数（pageindex-rag 风格）
memory_search() {
    local query="$1"
    local top_k="${2:-5}"
    
    echo "🔍 记忆搜索: $query"
    
    # QMD 搜索（主要方法）
    local results=()
    while IFS= read -r line; do
        if [[ "$line" == qmd://* ]]; then
            path=$(echo "$line" | sed 's|qmd://||' | cut -d':' -f1)
            results+=("$path")
        fi
    done < <(qmd search memory "$query" 2>/dev/null | head -"$top_k")
    
    # 文件名匹配（补充）
    if [ ${#results[@]} -lt "$top_k" ]; then
        local remaining=$((top_k - ${#results[@]}))
        while IFS= read -r file && [ $remaining -gt 0 ]; do
            results+=("$file")
            ((remaining--))
        done < <(find "$MEMORY_DIR" -name "*.md" | grep -i "$query" | head -"$remaining")
    fi
    
    # 输出结果
    if [ ${#results[@]} -eq 0 ]; then
        echo "  ⚠️  未找到相关记忆"
        return 1
    fi
    
    echo "  📊 找到 ${#results[@]} 条相关记忆:"
    for i in "${!results[@]}"; do
        local path="${results[$i]}"
        local filename=$(basename "$path")
        local fullpath="$WORKSPACE/$path"
        
        echo "    [$((i+1))] $filename"
        
        # 显示文件内容片段（如果文件存在）
        if [ -f "$fullpath" ]; then
            echo "       路径: $path"
            # 显示前 2 行内容
            head -2 "$fullpath" | sed 's/^/       /'
        fi
        echo ""
    done
    
    return 0
}

# 如果直接运行，执行搜索
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ -z "$1" ]; then
        echo "使用方法: $0 <查询> [top_k]"
        echo "示例: $0 \"部署\" 3"
        exit 1
    fi
    
    memory_search "$@"
fi
