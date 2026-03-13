#!/bin/bash
# 🚀 防护进化脚本
# 分析防护数据，优化防护策略

set -e

GREEN='\033[032m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 防护系统进化分析${NC}"
echo -e "${GREEN}=====================${NC}"
echo ""

# 统计防护事件
echo "📊 防护事件统计:"
echo ""

# 检查错误记录
echo "🔍 错误模式分析:"
if [ -d .learnings/errors ]; then
    error_count=$(ls -1 .learnings/errors/*.md 2>/dev/null | wc -l)
    echo "  错误总数: ${error_count} 个"
    
    # 分析错误类型
    echo "  最近 10 个错误:"
    ls -1t .learnings/errors/*.md 2>/dev/null | head -10 | while read file; do
        echo "    - $(basename "$file")"
    done
else
    echo "  无错误记录"
fi
echo ""

# 统计防护脚本
echo "🔧 防护脚本:"
ls -1 scripts/protection*.sh 2>/dev/null | head -5 | while read file; do
    echo "  - $(basename "$file")"
done
echo ""

# 防护进化建议
echo "💡 防护进化建议:"
echo "  1. 根据错误模式设计新防护"
echo "  2. 优化阈值设置"
echo "  3. 增加自动化程度"
echo "  4. 发布到 EvoMap"
echo ""

echo -e "${GREEN}✅ 防护进化分析完成${NC}"
echo ""

exit 0
