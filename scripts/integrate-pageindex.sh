#!/bin/bash
# pageindex-rag 集成到记忆系统

echo "🔧 将 pageindex-rag 集成到记忆系统"
echo "======================================"
echo ""

# 1. 备份现有检索脚本
echo "📋 步骤 1: 备份现有脚本..."
if [ -f "scripts/reasoning-retriever.py" ]; then
    cp scripts/reasoning-retriever.py scripts/reasoning-retriever.py.backup
    echo "  ✓ 已备份 reasoning-retriever.py"
fi

if [ -f "scripts/iterative-retriever.py" ]; then
    cp scripts/iterative-retriever.py scripts/iterative-retriever.py.backup
    echo "  ✓ 已备份 iterative-retriever.py"
fi

echo ""

# 2. 创建集成脚本
echo "📋 步骤 2: 创建集成脚本..."
cat > /root/.openclaw/workspace/scripts/pageindex-retriever.sh << 'EOF'
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
        while IFS= read -r file; do
            results+=("$file")
        done < <(find "$MEMORY_DIR" -name "*.md" | grep -i "$query" | head -"$((top_k - ${#results[@]}"))")
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
EOF

chmod +x /root/.openclaw/workspace/scripts/pageindex-retriever.sh
echo "  ✓ 已创建 pageindex-retriever.sh"

echo ""

# 3. 更新记忆检索 Hook
echo "📋 步骤 3: 更新记忆检索 Hook..."
if [ -d ".agents/skills/memory-search-hook" ]; then
    # 备份
    cp .agents/skills/memory-search-hook/SKILL.md .agents/skills/memory-search-hook/SKILL.md.backup
    
    # 更新（添加 pageindex-rag 选项）
    cat >> .agents/skills/memory-search-hook/SKILL.md << 'EOH'

## pageindex-rag 集成

### 快速检索（pageindex-rag 风格）

```bash
# 使用 pageindex-retriever
bash /root/.openclaw/workspace/scripts/pageindex-retriever.sh "查询内容"
```

**优势**：
- ✅ 快速（QMD 毫秒级）
- ✅ 准确（语义搜索）
- ✅ 简单（无需向量数据库）

EOH
    
    echo "  ✓ 已更新 memory-search-hook"
fi

echo ""
echo "✅ 集成完成！"
echo ""
echo "🚀 测试集成:"
echo "   bash scripts/pageindex-retriever.sh \"部署\""
echo ""
echo "📚 查看文档:"
echo "   cat docs/PAGEINDEX-RAG-INTEGRATION.md"
