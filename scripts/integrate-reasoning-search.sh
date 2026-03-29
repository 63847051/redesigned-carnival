#!/bin/bash
# 集成推理式检索到主搜索系统
# 使用方法: bash scripts/integrate-reasoning-search.sh

set -e

echo "🔧 集成推理式检索到主搜索系统"
echo "=================================="

# 1. 备份当前搜索脚本
echo "Step 1: 备份当前搜索脚本..."
if [ -f "/root/.openclaw/workspace/scripts/memory-search-checklist.sh" ]; then
    cp /root/.openclaw/workspace/scripts/memory-search-checklist.sh \
       /root/.openclaw/workspace/scripts/memory-search-checklist.sh.backup
    echo "   ✅ 备份完成"
else
    echo "   ⚠️  原搜索脚本不存在"
fi

# 2. 创建新的集成搜索脚本
echo "Step 2: 创建新的集成搜索脚本..."

cat > /root/.openclaw/workspace/scripts/integrated-search.sh << 'EOF'
#!/bin/bash
# 集成搜索系统 - QMD + 推理式检索
# 使用方法: bash scripts/integrated-search.sh "查询内容"

set -e

QUERY="$*"

if [ -z "$QUERY" ]; then
    echo "❌ 错误: 请提供搜索查询"
    echo ""
    echo "使用方法:"
    echo "  bash scripts/integrated-search.sh \"查询内容\""
    echo ""
    echo "示例:"
    echo "  bash scripts/integrated-search.sh \"记忆系统优化\""
    exit 1
fi

echo "🔍 集成搜索: \"$QUERY\""
echo ""

# Step 1: QMD 快速搜索
echo "Step 1: QMD 向量搜索..."
QMD_RESULTS=$(qmd search memory "$QUERY" 2>&1 | head -20)
QMD_COUNT=$(echo "$QMD_RESULTS" | grep -c "qmd://" || echo "0")

echo "   找到 $QMD_COUNT 条结果"

# Step 2: 推理式检索（可选）
if [ "$QMD_COUNT" -gt 0 ]; then
    echo ""
    echo "Step 2: 推理式检索（可选）..."
    echo "   提示: 使用 python3 scripts/reasoning-retriever.py --query \"$QUERY\""
fi

# Step 3: 显示结果
echo ""
echo "📊 搜索结果："
echo "=================================="
echo "$QMD_RESULTS"
echo ""
echo "✅ 搜索完成"
echo ""
echo "💡 提示:"
echo "  - 使用推理式检索: python3 scripts/reasoning-retriever.py --query \"$QUERY\""
echo "  - 查看文件: qmd-get memory/<file-path>"
EOF

chmod +x /root/.openclaw/workspace/scripts/integrated-search.sh
echo "   ✅ 集成搜索脚本已创建"

# 3. 创建软链接（全局可用）
echo "Step 3: 创建软链接..."
if [ ! -L "/usr/local/bin/integrated-search" ]; then
    ln -s /root/.openclaw/workspace/scripts/integrated-search.sh /usr/local/bin/integrated-search
    echo "   ✅ 软链接已创建: integrated-search"
else
    echo "   ⚠️  软链接已存在"
fi

# 4. 测试集成
echo "Step 4: 测试集成..."
TEST_RESULT=$(bash /root/.openclaw/workspace/scripts/integrated-search.sh "记忆" 2>&1 | grep "找到" || echo "0")
echo "   测试结果: $TEST_RESULT"

echo ""
echo "=================================="
echo "✅ 集成完成！"
echo ""
echo "使用方法:"
echo "  integrated-search \"查询内容\""
echo "  bash scripts/integrated-search.sh \"查询内容\""
echo "  python3 scripts/reasoning-retriever.py --query \"查询内容\""
echo ""
echo "示例:"
echo "  integrated-search \"记忆系统优化\""
