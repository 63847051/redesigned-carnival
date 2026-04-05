#!/bin/bash
# pageindex-rag 风格的记忆检索
# 集成到记忆系统

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"

# 主检索函数
memory_retrieve() {
    local query="$1"
    local top_k="${2:-3}"
    
    echo "🔍 记忆检索: $query"
    
    # QMD 搜索
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
    echo "📊 找到 ${#results[@]} 条结果:"
    for i in "${!results[@]}"; do
        echo "  $((i+1)). ${results[$i]}"
    done
    
    # 返回结果（用于脚本集成）
    printf '%s\n' "${results[@]}"
}

# 如果直接运行，执行测试
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    memory_retrieve "$@"
fi
