#!/bin/bash
# pageindex-rag 集成测试脚本

echo "🚀 pageindex-rag 集成测试"
echo "======================================"

# 检查依赖
echo ""
echo "📋 检查依赖..."

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi
echo "✅ Python3: $(python3 --version)"

# 检查 QMD
if ! command -v qmd &> /dev/null; then
    echo "⚠️  QMD 未安装（可选）"
else
    echo "✅ QMD: $(qmd --version)"
fi

# 检查 OpenClaw
if ! command -v openclaw &> /dev/null; then
    echo "⚠️  OpenClaw 未安装"
else
    echo "✅ OpenClaw: $(openclaw --version)"
fi

# 测试混合检索
echo ""
echo "🔍 测试混合检索..."
echo "======================================"

cd /root/.openclaw/workspace

# 运行测试
if [ -f "scripts/hybrid-retriever-pageindex-style.py" ]; then
    python3 scripts/hybrid-retriever-pageindex-style.py
else
    echo "❌ 测试脚本不存在"
    exit 1
fi

echo ""
echo "✅ 测试完成！"
echo ""
echo "📚 查看集成文档:"
echo "   cat docs/PAGEINDEX-RAG-INTEGRATION.md"
echo ""
echo "🔧 下一步:"
echo "   1. 根据需要调整参数"
echo "   2. 集成到记忆系统"
echo "   3. 性能优化"
