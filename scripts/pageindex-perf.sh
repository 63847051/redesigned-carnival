#!/bin/bash
# pageindex-rag 性能监控

echo "📊 性能统计"
echo "======================================"

# 测试 10 次
total_time=0
for i in {1..10}; do
    start=$(date +%s%N)
    bash /root/.openclaw/workspace/scripts/simple-pageindex-search.sh > /dev/null
    end=$(date +%s%N)
    
    elapsed=$((end - start))
    total_time=$((total_time + elapsed))
done

avg_time=$((total_time / 10))
echo "平均响应时间: ${avg_time}ms"
echo "QPM (查询/分钟): $((60000 / avg_time))"
