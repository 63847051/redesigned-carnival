#!/bin/bash
# pageindex-rag + LLM 排序
# 智能检索系统

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
PYTHON_SCRIPT="$WORKSPACE/scripts/llm-reranker.py"

# 智能检索函数
smart_retrieve() {
    local query="$1"
    local top_k="${2:-5}"
    local use_llm="${3:-1}"  # 是否使用 LLM 排序（默认启用）
    
    echo "🔍 智能检索: $query"
    
    # Step 1: QMD 快速召回
    echo "   Step 1: 快速召回..."
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
    
    echo "   召回: ${#results[@]} 条"
    
    if [ ${#results[@]} -eq 0 ]; then
        echo "   ⚠️  未找到相关记忆"
        return 1
    fi
    
    # Step 2: LLM 智能排序（如果启用）
    if [ "$use_llm" = "1" ] && [ ${#results[@]} -gt 1 ]; then
        echo "   Step 2: LLM 智能排序..."
        
        # 调用 Python 脚本进行 LLM 排序
        local ranked_results=$(python3 "$PYTHON_SCRIPT" "$query" "${results[@]}" 2>&1)
        
        if [ $? -eq 0 ]; then
            # 解析排序结果
            results=()
            while IFS= read -r path; do
                results+=("$path")
            done <<< "$ranked_results"
        else
            echo "   ⚠️ LLM 排序失败，使用原始顺序"
        fi
    fi
    
    # Step 3: 返回 Top 3
    local final_count=3
    echo "   ✅ 返回 Top $final_count"
    
    # 输出结果
    echo "   📊 结果:"
    for i in "${!results[@]}"; do
        [ $i -ge $final_count ] && break
        local path="${results[$i]}"
        local filename=$(basename "$path")
        local fullpath="$WORKSPACE/$path"
        
        echo "      [$((i+1))] $filename"
        
        # 显示文件内容片段
        if [ -f "$fullpath" ]; then
            echo "         路径: $path"
            head -2 "$fullpath" | sed 's/^/         /'
        fi
        echo ""
    done
}

# 如果直接运行，执行检索
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ -z "$1" ]; then
        echo "使用方法: $0 <查询> [top_k] [use_llm: 0/1]"
        echo "示例: $0 \"部署\" 5 1"
        exit 1
    fi
    
    smart_retrieve "$@"
fi
