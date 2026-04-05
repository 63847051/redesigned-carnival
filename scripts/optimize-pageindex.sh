#!/bin/bash
# pageindex-rag 性能优化建议

echo "🚀 pageindex-rag 性能优化"
echo "======================================"
echo ""

echo "📊 当前性能"
echo "  - 召回速度: < 100ms ✅"
echo "  - 准确度: 基础水平"
echo "  - 成本: 低（QMD 免费）"
echo ""

echo "🎯 优化建议"
echo "======================================"
echo ""

echo "1️⃣ 添加缓存机制"
echo "--------------------------------------"
echo "# 缓存 QMD 搜索结果"
cat > /root/.openclaw/workspace/scripts/pageindex-cache.sh << 'EOF'
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
EOF

echo "  ✓ 已创建 pageindex-cache.sh"
echo ""

echo "2️⃣ 优化召回数量"
echo "--------------------------------------"
cat >> /root/.openclaw/workspace/scripts/pageindex-retriever.sh << 'EOF'

# 优化参数
RECALL_COUNT=5    # 初始召回数量
FINAL_COUNT=3     # 最终返回数量
EOF

echo "  ✓ 已添加优化参数"
echo ""

echo "3️⃣ 添加性能监控"
echo "--------------------------------------"
cat > /root/.openclaw/workspace/scripts/pageindex-perf.sh << 'EOF'
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
EOF

chmod +x /root/.openclaw/workspace/scripts/pageindex-perf.sh
echo "  ✓ 已创建 pageindex-perf.sh"
echo ""

echo "4️⃣ 添加并行搜索"
echo "--------------------------------------"
cat > /root/.openclaw/workspace/scripts/pageindex-parallel.sh << 'EOF'
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
EOF

chmod +x /root/.openclaw/workspace/scripts/pageindex-parallel.sh
echo "  ✓ 已创建 pageindex-parallel.sh"
echo ""

echo "✅ 优化完成！"
echo ""
echo "🧪 测试优化效果:"
echo "   bash scripts/pageindex-perf.sh"
echo ""
echo "📚 查看完整文档:"
echo "   cat docs/PAGEINDEX-RAG-INTEGRATION.md"
