#!/bin/bash
# 记忆健康监控脚本
# 每日检查记忆系统的健康状态

echo "📊 记忆健康监控报告"
echo "========================================"
echo "检查时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 问题计数
issues=0

# 1. 检查 MEMORY.md 是否超出 2000 tokens
echo "📝 1. 检查 MEMORY.md 大小"
memory_file="/root/.openclaw/workspace/MEMORY.md"
if [ -f "$memory_file" ]; then
    # 粗略估算：中文字符约 1.5 tokens，英文约 0.75 tokens
    size=$(wc -m < "$memory_file")
    estimated_tokens=$((size * 3 / 4))

    echo "   文件大小: $size 字符"
    echo "   估算 Tokens: $estimated_tokens"

    if [ $estimated_tokens -gt 2000 ]; then
        echo -e "   ${RED}❌ 超出 2000 tokens 限制${NC}"
        ((issues++))
    else
        echo -e "   ${GREEN}✅ 在限制范围内${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠️  文件不存在${NC}"
fi
echo ""

# 2. 检查今日日志是否有 Retain 段落
echo "📝 2. 检查今日日志 Retain 格式"
today=$(date '+%Y-%m-%d')
memory_today="/root/.openclaw/workspace/memory/$today.md"

if [ -f "$memory_today" ]; then
    if grep -q "^## Retain" "$memory_today"; then
        echo -e "   ${GREEN}✅ 包含 Retain 段落${NC}"
    else
        echo -e "   ${YELLOW}⚠️  缺少 Retain 段落${NC}"
        ((issues++))
    fi
else
    echo -e "   ${YELLOW}⚠️  今日日志不存在${NC}"
fi
echo ""

# 3. 检查 SESSION-STATE.md 是否超过 24 小时未更新
echo "📝 3. 检查 SESSION-STATE.md 更新时间"
session_state="/root/.openclaw/workspace/SESSION-STATE.md"

if [ -f "$session_state" ]; then
    # 获取文件修改时间（Unix 时间戳）
    modified=$(stat -c %Y "$session_state")
    now=$(date +%s)
    diff=$((now - modified))
    hours=$((diff / 3600))

    echo "   上次更新: $hours 小时前"

    if [ $hours -gt 24 ]; then
        echo -e "   ${RED}❌ 超过 24 小时未更新${NC}"
        ((issues++))
    else
        echo -e "   ${GREEN}✅ 更新及时${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠️  文件不存在${NC}"
fi
echo ""

# 4. 检查是否有相互矛盾的规则
echo "📝 4. 检查矛盾规则"
# 简单检查：查找"应该"和"不应该"同时存在的情况
if [ -f "$memory_file" ]; then
    contradictory_rules=$(grep -i "应该\|不应该" "$memory_file" | wc -l)
    echo "   发现规则: $contradictory_rules 条"

    # 这里只是简单计数，实际需要更复杂的语义分析
    if [ $contradictory_rules -gt 10 ]; then
        echo -e "   ${YELLOW}⚠️  规则较多，建议人工审查${NC}"
    else
        echo -e "   ${GREEN}✅ 规则数量正常${NC}"
    fi
fi
echo ""

# 5. 检查最近 7 天是否有重复事故
echo "📝 5. 检查重复事故"
incidents_file="/root/.openclaw/workspace/bank/lessons-learned/critical-rules.md"

if [ -f "$incidents_file" ]; then
    # 统计最近 7 天的事故
    recent_incidents=$(find /root/.openclaw/workspace/bank/lessons-learned/ -name "*.md" -mtime -7 | wc -l)
    echo "   最近 7 天事故: $recent_incidents 次"

    if [ $recent_incidents -gt 5 ]; then
        echo -e "   ${RED}❌ 事故频繁，需要关注${NC}"
        ((issues++))
    else
        echo -e "   ${GREEN}✅ 事故数量正常${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠️  事故记录文件不存在${NC}"
fi
echo ""

# 6. 检查 memory/ 目录大小
echo "📝 6. 检查 memory/ 目录"
memory_dir="/root/.openclaw/workspace/memory"

if [ -d "$memory_dir" ]; then
    file_count=$(find "$memory_dir" -name "*.md" | wc -l)
    echo "   日志文件数: $file_count"

    if [ $file_count -gt 100 ]; then
        echo -e "   ${YELLOW}⚠️  文件过多，建议归档${NC}"
    else
        echo -e "   ${GREEN}✅ 文件数量正常${NC}"
    fi
fi
echo ""

# 总结
echo "========================================"
if [ $issues -eq 0 ]; then
    echo -e "${GREEN}✅ 记忆系统健康${NC}"
    exit 0
else
    echo -e "${RED}❌ 发现 $issues 个问题${NC}"
    exit 1
fi
