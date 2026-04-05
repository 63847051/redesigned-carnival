#!/bin/bash
# pageindex-rag 风格的简化检索器

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"

# 检索函数
search_memory() {
    local query="$1"
    local top_k="${2:-5}"
    
    echo "🔍 检索: $query"
    echo ""
    
    # QMD 搜索
    echo "📊 QMD 搜索结果:"
    qmd search memory "$query" 2>/dev/null | head -"$top_k" | while IFS= read -r line; do
        if [[ "$line" == qmd://* ]]; then
            # 提取文件路径
            path=$(echo "$line" | sed 's|qmd://||' | cut -d':' -f1)
            echo "  ✓ $path"
        fi
    done
    
    # 文件名匹配
    echo ""
    echo "📁 文件名匹配:"
    find "$MEMORY_DIR" -name "*.md" | grep -i "$query" | head -"$top_k" | while read -r file; do
        echo "  ✓ $(basename "$file")"
    done
    
    echo ""
    echo "======================================"
}

# 测试查询
echo "🚀 pageindex-rag 简化检索测试"
echo "======================================"
echo ""

search_memory "部署" 3
search_memory "防护" 3
search_memory "OpenCode" 3

echo ""
echo "✅ 测试完成！"
