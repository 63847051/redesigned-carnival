#!/bin/bash
# 核心逻辑强制检查脚本
# 每次任务前必须执行

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🎯 核心逻辑检查${NC}"
echo ""

# 核心逻辑检查
check_core_logic() {
    echo "📋 核心逻辑检查清单："
    echo ""

    # 检查 1：任务分析
    echo "1. 任务分析"
    echo "   - 这个任务需要什么能力？"
    echo "   - 哪个 API 最擅长？"
    echo "   - 哪个 API 最快？"
    echo "   - 哪个 API 最便宜？"
    echo ""

    # 检查 2：分配决策
    echo "2. 分配决策"
    echo "   - 我可以分配这个任务吗？"
    echo "   - 是否必须我（GLM-4.7）处理？"
    echo "   - 应该用哪个 API？"
    echo ""

    # 检查 3：透明化
    echo "3. 透明化准备"
    echo "   - 我会汇报用了谁吗？"
    echo "   - 我会汇报什么模型吗？"
    echo "   - 我会汇报为什么吗？"
    echo ""

    # 检查 4：用户体验
    echo "4. 用户体验"
    echo "   - 我会给直接答案吗？"
    echo "   - 我会让用户自己去查吗？"
    echo "   - 我会验证信息吗？"
    echo ""
}

# 执行检查
check_core_logic

echo -e "${GREEN}✅ 检查完成${NC}"
echo ""
echo -e "${YELLOW}💡 记住：我是大领导，我的核心是分配！${NC}"
echo ""

# 返回成功
exit 0
