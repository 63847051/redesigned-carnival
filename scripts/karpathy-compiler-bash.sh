#!/bin/bash
# Karpathy 风格知识库 - Bash 测试

WORKSPACE="/root/.openclaw/workspace"
RAW_DIR="$WORKSPACE/knowledge-base/raw"
WIKI_DIR="$WORKSPACE/knowledge-base/wiki"
INDEX_FILE="$WIKI_DIR/index.md"

echo "🧠 Karpathy 知识库编译器 - Bash 版"
echo "======================================"
echo ""

# Step 1: 扫描文件
echo "📂 Step 1: 扫描原始数据..."
file_count=$(find "$RAW_DIR" -name "*.md" | wc -l)
echo "   找到 $file_count 个文件"
echo ""

# Step 2: 简单编译（不用 LLM，避免超时）
echo "   Step 2: 简单编译..."
compiled=0
for file in $(find "$RAW_DIR" -name "*.md" | head -10); do
    filename=$(basename "$file")
    cp "$file" "$WIKI_DIR/articles/"
    compiled=$((compiled + 1))
done
echo "   编译了 $compiled 个文件"
echo ""

# Step 3: 生成索引
echo "   Step 3: 生成索引..."
cat > "$INDEX_FILE" << EOF
# 知识库索引

**更新时间**: $(date '+%Y-%m-%d %H:%M:%S')
**文档总数**: $file_count

## 文件列表

EOF

for file in $(find "$RAW_DIR" -name "*.md" | head -10); do
    echo "- $(basename "$file")" >> "$INDEX_FILE"
done

echo ""
echo "✅ 编译完成！"
echo ""
echo "📂 Wiki 位置: $WIKI_DIR"
echo "📄 索引文件: $INDEX_FILE"
echo ""
echo "📖 查看索引:"
echo "   cat $INDEX_FILE"
