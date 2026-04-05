#!/bin/bash
# 并行搜索（多查询）

queries=("部署" "防护" "OpenCode")

for query in "${queries[@]}"; do
    (
        echo "🔍 搜索: $query"
        bash /root/.openclaw/workspace/scripts/pageindex-retriever.sh "$query" 3
        echo ""
    ) &
done

wait
echo "✅ 所有搜索完成"
