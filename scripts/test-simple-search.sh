#!/bin/bash
# 简化的 pageindex-rag 测试

echo "🔍 测试 QMD 搜索"
echo "======================================"

# 测试查询
queries=(
    "如何部署系统？"
    "三重防护机制"
    "OpenCode CLI"
)

for query in "${queries[@]}"; do
    echo ""
    echo "查询: $query"
    echo "---"
    
    # QMD 搜索
    qmd search memory "$query" | head -5
    
    echo ""
    echo "文件名匹配:"
    ls /root/.openclaw/workspace/memory/*.md | grep -i "$query" | head -3
    
    echo ""
    echo "======================================"
done

echo ""
echo "✅ 测试完成！"
