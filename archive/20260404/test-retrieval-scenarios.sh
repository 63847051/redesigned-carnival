#!/bin/bash
# 推理式检索综合测试
# 测试多种场景

echo "🧪 推理式检索综合测试"
echo "===================="
echo ""

# 测试场景
SCENARIOS=(
    "蓝色光标"
    "记忆系统优化"
    "性能提升"
    "自动化"
)

TOTAL=0
PASSED=0

for query in "${SCENARIOS[@]}"; do
    TOTAL=$((TOTAL + 1))
    echo "测试 $TOTAL: \"$query\""
    echo "--------------------"

    # 使用 QMD 搜索
    RESULT=$(qmd search memory "$query" 2>&1 | grep -c "qmd://" || echo "0")

    if [ "$RESULT" -gt 0 ]; then
        echo "✅ 通过: 找到 $RESULT 条结果"
        PASSED=$((PASSED + 1))
    else
        echo "❌ 失败: 未找到结果"
    fi
    echo ""
done

echo "===================="
echo "📊 测试结果:"
echo "  总数: $TOTAL"
echo "  通过: $PASSED"
echo "  失败: $((TOTAL - PASSED))"
echo ""

if [ "$PASSED" -eq "$TOTAL" ]; then
    echo "🎉 所有测试通过！"
    exit 0
else
    echo "⚠️  部分测试失败"
    exit 1
fi
