#!/bin/bash
# 🧬 超级进化系统（SES）v2.0 - 任务后强制评估
# 确保每次任务后都评估和进化

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}📊 任务后强制评估${NC}"
echo -e "${GREEN}===================${NC}"
echo ""

# 1. 任务分配评估
echo "📋 任务分配评估："
echo "  ❓ 我分配这个任务了吗？"
read -p "  [y/n]: " allocated
echo ""

# 2. API 选择评估
echo "🎯 API 选择评估："
echo "  ❓ 我用了最合适的 API 吗？"
read -p "  [y/n]: " optimal
echo ""

# 3. 透明化评估
echo "💡 透明化评估："
echo "  ❓ 我透明化汇报了吗？"
echo "  ❓ 我说了用了谁、什么模型、为什么吗？"
read -p "  [y/n]: " transparent
echo ""

# 4. 直接答案评估
echo "🎯 直接答案评估："
echo "  ❓ 我给用户直接答案了吗？"
echo "  ❓ 我让用户自己去查了吗？"
read -p "  [y/n]: " direct_answer
echo ""

# 5. 验证评估
echo "✅ 验证评估："
echo "  ❓ 我验证信息了吗？"
echo "  ❓ 我给出准确答案了吗？"
read -p "  [y/n]:" verified
echo ""

# 6. 学习记录评估
echo "📚 学习记录评估："
echo "  ❓ 我记录学习了吗？"
echo "  ❓ 我提取模式了吗？"
read -p "  [y/n]:" learned
echo ""

# 7. 改进建议
echo "💡 改进建议："
echo "  下次可以做得更好的地方："
read -p "  [输入建议，回车跳过]: " improvement
echo ""

# 统计评分
score=0
[ "$allocated" == "y" ] && ((score++))
[ "$optimal" == "y" ] && ((score++))
[ "$transparent" == "y" ] && ((score++))
[ "$direct_answer" == "y" ] && ((score++))
[ "$verified" == "y" ] && ((score++))
[ "$learned" == "y" ] && ((score++))

echo ""
echo -e "${GREEN}📊 本次评估得分：${score}/5${NC}"
echo ""

if [ $score -eq 5 ]; then
    echo -e "${GREEN}✨ 完美！继续保持！${NC}"
elif [ $score -ge 4 ]; then
    echo -e "${GREEN}✅ 很好！还有提升空间${NC}"
elif [ $ge 3 ]; then
    echo -e "${YELLOW}⚠️  一般，需要改进${NC}"
else
    echo -e "${RED}❌ 需要重点改进${NC}"
    echo -e "${RED}   请重新学习核心逻辑！${NC}"
fi

echo ""

# 记录评估结果
mkdir -p .learnings/evaluations
cat > .learnings/evaluations/$(date +%Y%m%d-%H%M%S).md << EOF
# 任务后评估

**时间**: $(date '+%Y-%m-%d %H:%M:%S')

**评分**: ${score}/5

## 检查项
- [x] 任务分配: ${allocated}
- [x] API 选择: ${optimal}
- [x] 透明化: ${transparent}
- [x] 直接答案: ${direct_answer}
- [x] 验证: ${verified}
- [x] 学习记录: ${learned}

## 改进建议
${improvement}

EOF

echo "✅ 评估已记录"
echo ""

exit 0
