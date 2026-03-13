#!/bin/bash
# 心跳进化脚本 - 自动学习和改进
# 每次心跳时自动执行

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 学习目录
LEARNINGS_DIR="/root/.openclaw/workspace/.learnings"
ERRORS_DIR="$LEARNINGS_DIR/errors"
IMPROVEMENTS_DIR="$LEARNINGS_DIR/improvements"
BEST_PRACTICES_DIR="$LEARNINGS_DIR/best-practices"

# 创建目录
mkdir -p "$ERRORS_DIR" "$IMPROVEMENTS_DIR" "$BEST_PRACTICES_DIR"

echo -e "${YELLOW}🧬 开始自动进化分析...${NC}"

# 1. 检查最近的错误
echo ""
echo -e "${YELLOW}📋 检查最近的错误...${NC}"

# 检查 Gateway 日志中的错误
RECENT_ERRORS=$(journalctl --user -u openclaw-gateway --since "1 hour ago" --no-pager | grep -i "error\|failed" | tail -5)

if [ -n "$RECENT_ERRORS" ]; then
    echo -e "${RED}发现最近的错误:${NC}"
    echo "$RECENT_ERRORS"
    
    # 记录错误
    ERROR_FILE="$ERRORS_DIR/error_$(date +%Y%m%d_%H%M%S).md"
    cat > "$ERROR_FILE" << EOF
# 错误记录

**时间**: $(date)
**来源**: Gateway 日志

\`\`\`
$RECENT_ERRORS
\`\`\`

## 分析

待分析...

## 建议

待补充...
EOF
    echo -e "${YELLOW}✓ 错误已记录: $ERROR_FILE${NC}"
else
    echo -e "${GREEN}✓ 无最近错误${NC}"
fi

# 2. 检查系统健康状态
echo ""
echo -e "${YELLOW}📊 检查系统健康状态...${NC}"

# Gateway 状态
if systemctl --user is-active --quiet openclaw-gateway; then
    echo -e "${GREEN}✓ Gateway 运行正常${NC}"
else
    echo -e "${RED}❌ Gateway 未运行${NC}"
fi

# 内存使用
MEM_USAGE=$(free | awk '/Mem/{printf("%.1f"), $3/$2*100}')
echo "内存使用: ${MEM_USAGE}%"

if (( $(echo "$MEM_USAGE > 80" | bc -l) )); then
    echo -e "${YELLOW}⚠️ 内存使用较高${NC}"
fi

# 3. 生成进化报告
echo ""
echo -e "${YELLOW}📝 生成进化报告...${NC}"

EVOLUTION_REPORT="$LEARNINGS_DIR/evolution_report_$(date +%Y%m%d_%H%M%S).md"

cat > "$EVOLUTION_REPORT" << EOF
# 进化报告

**生成时间**: $(date)
**系统版本**: $(openclaw --version 2>/dev/null || echo "未知")

## 系统状态

- Gateway: $(systemctl --user is-active openclaw-gateway && echo "✅ 运行中" || echo "❌ 未运行")
- 内存使用: ${MEM_USAGE}%
- 错误数量: $(echo "$RECENT_ERRORS" | grep -c "^" || echo "0")

## 最近错误

$(if [ -n "$RECENT_ERRORS" ]; then
    echo "\`\`\`"
    echo "$RECENT_ERRORS"
    echo "\`\`\`"
else
    echo "无错误"
fi)

## 改进建议

1. 定期检查日志
2. 监控内存使用
3. 及时更新系统

## 待办事项

- [ ] 分析错误模式
- [ ] 优化工作流程
- [ ] 提取最佳实践

---

*此报告由 heartbeat-evolution.sh 自动生成*
EOF

echo -e "${GREEN}✓ 进化报告已生成: $EVOLUTION_REPORT${NC}"

# 4. 清理旧报告（保留最近 7 天）
find "$LEARNINGS_DIR" -name "*.md" -mtime +7 -delete 2>/dev/null || true

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ 进化分析完成${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 关键规则检查
echo ""
echo "🚨 关键规则检查："
bash /root/.openclaw/workspace/scripts/check-critical-rules.sh
