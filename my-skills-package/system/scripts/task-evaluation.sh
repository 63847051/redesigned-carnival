#!/bin/bash
# 任务后评估脚本
# 每次任务后执行，评估是否符合核心逻辑

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}📊 任务后评估${NC}"
echo ""

# 评估问题
echo "请回答以下问题："
echo ""

echo "1. 我分配这个任务了吗？"
echo "   - 是：继续"
echo "   - 否：记录错误"
echo ""

echo "2. 我用了最合适的 API 吗？"
echo "   - 是：继续"
echo "   - 否：需要改进"
echo ""

echo "3. 我透明化汇报了吗？"
echo "   - 说了用了谁"
echo "   - 说了什么模型"
echo "   - 说了为什么"
echo ""

echo "4. 我给了直接答案吗？"
echo "   - 是：优秀"
echo "   - 否：需要改进"
echo ""

echo "5. 我验证信息了吗？"
echo "   - 是：优秀"
echo "   - 否：需要改进"
echo ""

echo -e "${GREEN}✅ 评估完成${NC}"
echo ""

exit 0
