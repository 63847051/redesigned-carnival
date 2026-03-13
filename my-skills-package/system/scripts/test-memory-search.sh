#!/bin/bash
# 记忆系统测试脚本

echo "🧠 记忆系统测试"
echo "================"
echo ""

# 检查依赖
echo "1️⃣ 检查依赖..."
if python3 -c "import sentence_transformers, faiss, numpy" 2>/dev/null; then
    echo "✅ 所有依赖已安装"
else
    echo "❌ 依赖未安装"
    echo "正在安装..."
    pip3 install -q sentence-transformers faiss-cpu numpy
    echo "✅ 依赖安装完成"
fi

echo ""
echo "2️⃣ 检查记忆文件..."
MEMORY_FILES=$(find /root/.openclaw/workspace/memory/long-term -name "*.md" | wc -l)
echo "✅ 找到 $MEMORY_FILES 个记忆文件"

echo ""
echo "3️⃣ 建立索引..."
python3 /root/.openclaw/workspace/scripts/semantic-search.py build

echo ""
echo "4️⃣ 测试搜索..."
echo "搜索 '幸运小行星'..."
python3 /root/.openclaw/workspace/scripts/semantic-search.py search --query "幸运小行星" --top-k 3

echo ""
echo "✅ 测试完成！"
echo "📚 使用文档: /root/.openclaw/workspace/memory/README.md"
