#!/bin/bash
# OpenClaw 管理工具
# 提供常用的系统管理功能

case "$1" in
  dashboard-status)
    systemctl status ai-dashboard.service --no-pager
    ;;
  
  dashboard-start)
    systemctl start ai-dashboard.service
    echo "✅ Dashboard 已启动"
    ;;
  
  dashboard-stop)
    systemctl stop ai-dashboard.service
    echo "✅ Dashboard 已停止"
    ;;
  
  dashboard-restart)
    systemctl restart ai-dashboard.service
    echo "✅ Dashboard 已重启"
    ;;
  
  logs)
    cd /root/.openclaw/workspace/ai-team-dashboard/dashboard
    ./monitor-logs.sh
    ;;
  
  analyze-logs)
    cd /root/.openclaw/workspace/ai-team-dashboard/dashboard
    ./analyze-logs.sh
    ;;
  
  evolution)
    bash /root/.openclaw/workspace/scripts/self-evolution-system.sh
    ;;
  
  health)
    bash /root/.openclaw/workspace/scripts/health-check.sh
    ;;
  
  wechat)
    shift
    bash /root/.openclaw/workspace/scripts/wechat-reader.sh "$@"
    ;;
  
  *)
    echo "📖 OpenClaw 管理工具"
    echo ""
    echo "使用方法:"
    echo "  $0 <命令> [参数]"
    echo ""
    echo "可用命令:"
    echo "  dashboard-status   - 查看 Dashboard 状态"
    echo "  dashboard-start    - 启动 Dashboard"
    echo "  dashboard-stop     - 停止 Dashboard"
    echo "  dashboard-restart  - 重启 Dashboard"
    echo "  logs               - 查看 Dashboard 日志"
    echo "  analyze-logs       - 分析日志"
    echo "  evolution          - 运行进化学习"
    echo "  health             - 系统健康检查"
    echo "  wechat <URL>       - 读取微信文章"
    echo ""
    echo "示例:"
    echo "  $0 dashboard-status"
    echo "  $0 wechat https://mp.weixin.qq.com/s/XXXXX"
    echo ""
    ;;
esac
