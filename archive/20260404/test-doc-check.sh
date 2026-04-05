#!/bin/bash
# 简单的文档质量检查测试脚本

echo "📋 文档质量检查系统测试"
echo "=========================="

# 测试文件
test_file="/root/.openclaw/workspace/templates/docs/test-example.md"

echo "📄 测试文件: $test_file"

# 检查必需章节
REQUIRED_SECTIONS="标题|描述|步骤|验证"

echo "🔍 检查必需章节: $REQUIRED_SECTIONS"

# 检查每个章节
sections_found=0
for section in $REQUIRED_SECTIONS; do
    if grep -qE "^##\s*$section|^###\s*$section" "$test_file"; then
        echo "✅ 找到章节: $section"
        sections_found=$((sections_found + 1))
    else
        echo "❌ 缺少章节: $section"
    fi
done

# 输出结果
echo ""
echo "📊 检查结果:"
echo "- 总章节数: $(echo $REQUIRED_SECTIONS | wc -w)"
echo "- 已找到: $sections_found"

if [ $sections_found -eq $(echo $REQUIRED_SECTIONS | wc -w) ]; then
    echo "✅ 文档质量检查通过!"
    exit 0
else
    echo "❌ 文档质量检查未通过!"
    exit 1
fi