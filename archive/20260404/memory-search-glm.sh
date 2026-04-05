#!/bin/bash
# 使用智谱 API 的记忆搜索脚本

API_KEY="c26c6bd6acfc44cda167b15dc338dabc.Hmfe3HhV5TjJiXqp"
BASE_URL="https://open.bigmodel.cn/api/paas/v4"
MODEL="embedding-2"

# 生成 embedding
generate_embedding() {
    local text="$1"
    curl -s "$BASE_URL/embeddings" \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"input\":\"$text\",\"model\":\"$MODEL\"}" \
        | jq -c '.data[0].embedding'
}

# 搜索记忆（使用全文搜索）
search_memory() {
    local query="$1"

    echo "🔍 搜索记忆: $query"
    echo ""

    # 使用 QMD 全文搜索
    qmd-search "$query" --mode text 2>/dev/null | head -50
}

# 主函数
main() {
    local query="$1"

    if [ -z "$query" ]; then
        echo "使用方法: $0 <搜索关键词>"
        exit 1
    fi

    search_memory "$query"
}

main "$@"
