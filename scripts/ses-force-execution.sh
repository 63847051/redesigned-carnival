#!/bin/bash
# 🧬 超级进化系统（SES）v2.0 - 强制执行版本
# 确保每次任务都按照系统执行

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🧬 超级进化系统（SES）v2.0${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# 强制执行：任务前检查
echo -e "${YELLOW}📋 [强制] 任务前检查${NC}"
echo ""

# 1. 错误驱动模式检查
echo "❓ 模式1（错误驱动）："
echo "   - 这是从错误中学到的吗？"
echo "   - 有相关的错误记录吗？"
echo ""

# 2. 可执行模式检查
echo "❓ 模式2（可执行）："
echo "   - 有可执行的脚本吗？"
echo "   - 会自动执行吗？"
echo ""

# 3. 双轨进化检查
echo "❓ 模式3（双轨）："
echo "   - 记录到 .learnings/ 了吗？"
echo "   - 准备发布到 EvoMap 吗？"
echo ""

# 4. 透明化模式检查
echo "❓ 模式4（透明化）："
echo "   - 会汇报分配过程吗？"
echo "   - 会说明为什么这样选择吗？"
echo ""

# 5. 多层防护检查
echo "❓ 模式5（多层防护）："
echo "   - 有备用方案吗？"
echo "   - 会自动降级吗？"
echo ""

# 6. 动态分配检查
echo "❓ 模式6（动态分配）："
echo "   - 这是最合适的 API 吗？"
echo "   - 成本最优吗？"
echo ""

# 7. 自动化检查
echo "❓ 模式7（自动化）："
echo "   - 可以自动化执行吗？"
echo "   - 减少人工干预吗？"
echo ""

# 8. 用户反馈检查
echo "❓ 模式8（用户反馈）："
echo "   - 满足用户需求吗？"
echo "   - 用户会满意吗？"
echo ""

# 强制决策点
echo -e "${RED}⚠️  强制决策点${NC}"
echo ""
echo "必须满足："
echo "  [ ] 确认这不是一个重复的错误"
echo "  [ ] 确认这是最优的资源分配"
echo "  [ ] 确认会透明化汇报"
echo "  [ ] 确认会记录学习"
echo ""

# 最终确认
read -p "所有检查都通过了吗？(y/n): " confirm
echo ""

if [ "$confirm" != "y" ]; then
    echo -e "${RED}❌ 检查未通过，请重新评估任务${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 检查通过！可以执行任务${NC}"
echo ""

# 返回成功
exit 0
