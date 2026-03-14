#!/bin/bash
# 系统健康检查脚本
# 快速诊断系统状态

echo "🔍 系统健康检查"
echo "══════════════════════════════════"
echo "📅 检查时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. 内存使用
echo "📊 内存使用:"
free -h | grep Mem
MEMORY_USAGE=$(free | awk '/Mem/{printf("%.1f"), $3/$2*100}')
if [ $(echo "$MEMORY_USAGE > 80" | bc -l) -eq 1 ]; then
  echo "  ⚠️ 内存使用过高"
else
  echo "  ✅ 内存使用正常"
fi
echo ""

# 2. 磁盘使用
echo "💾 磁盘使用:"
df -h | grep -E "(Filesystem|/$|/home)"
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
  echo "  ⚠️ 磁盘使用过高"
else
  echo "  ✅ 磁盘使用正常"
fi
echo ""

# 3. 服务状态
echo "🚀 服务状态:"
if systemctl --user is-active --quiet openclaw-gateway; then
  GATEWAY_STATUS="✅ 运行中"
  GATEWAY_RESTART=$(journalctl --user -u openclaw-gateway --no-pager | grep "Scheduled restart job" | wc -l)
else
  GATEWAY_STATUS="❌ 未运行"
fi
echo "  Gateway: $GATEWAY_STATUS"

if systemctl is-active --quiet ai-dashboard.service; then
  DASHBOARD_STATUS="✅ 运行中"
else
  DASHBOARD_STATUS="❌ 未运行"
fi
echo "  Dashboard: $DASHBOARD_STATUS"
echo ""

# 4. 最近错误
echo "📝 最近错误（1 小时内）:"
ERRORS=$(journalctl --user -u openclaw-gateway --since "1 hour ago" --no-pager | grep -i "error\|failed" | tail -3)
if [ -z "$ERRORS" ]; then
  echo "  ✅ 无错误"
else
  echo "$ERRORS" | sed 's/^/  /'
fi
echo ""

# 5. 进程状态
echo "⚙️  进程状态:"
NODE_COUNT=$(ps aux | grep "node server.js" | grep -v grep | wc -l)
echo "  Node.js 进程: $NODE_COUNT 个"
echo ""

# 6. 总结
echo "══════════════════════════════════"
echo "📋 总结:"
if systemctl --user is-active --quiet openclaw-gateway && systemctl is-active --quiet ai-dashboard.service; then
  echo "  ✅ 系统运行正常"
else
  echo "  ⚠️ 部分服务未运行，请检查"
fi
echo ""
