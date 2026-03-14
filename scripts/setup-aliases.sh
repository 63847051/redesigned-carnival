#!/bin/bash
# OpenClaw 快捷命令配置
# 添加到 ~/.bashrc

cat >> /root/.bashrc << 'EOF'

# ═══════════════════════════════════════════════════════════════
# OpenClaw 快捷命令
# ═══════════════════════════════════════════════════════════════

# 项目导航
alias ai-dashboard='cd /root/.openclaw/workspace/ai-team-dashboard/dashboard'
alias workspace='cd /root/.openclaw/workspace'

# 系统管理
alias evolution='bash /root/.openclaw/workspace/scripts/self-evolution-system.sh'
alias heartbeat='bash /root/.openclaw/workspace/scripts/heartbeat-evolution.sh'

# 微信文章读取
alias wechat='bash /root/.openclaw/workspace/scripts/wechat-reader.sh'

# Dashboard 日志
alias logs='cd /root/.openclaw/workspace/ai-team-dashboard/dashboard && ./monitor-logs.sh'
alias analyze-logs='cd /root/.openclaw/workspace/ai-team-dashboard/dashboard && ./analyze-logs.sh'

# 服务管理
alias dashboard-start='systemctl start ai-dashboard.service'
alias dashboard-stop='systemctl stop ai-dashboard.service'
alias dashboard-status='systemctl status ai-dashboard.service'
alias dashboard-restart='systemctl restart ai-dashboard.service'

# Git 快捷命令
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'

# 系统监控
alias mem='free -h'
alias disk='df -h'
alias psnode='ps aux | grep node'

# ═══════════════════════════════════════════════════════════════
EOF

echo "✅ 快捷命令已添加到 ~/.bashrc"
echo "💡 请运行以下命令使其生效："
echo "   source ~/.bashrc"
echo ""
echo "📝 可用的快捷命令："
echo "   ai-dashboard    - 进入 Dashboard 目录"
echo "   workspace       - 进入工作空间"
echo "   evolution       - 运行进化学习"
echo "   wechat          - 读取微信文章"
echo "   logs            - 查看 Dashboard 日志"
echo "   analyze-logs    - 分析日志"
echo "   dashboard-start - 启动 Dashboard"
echo "   dashboard-stop  - 停止 Dashboard"
echo "   dashboard-status - 查看 Dashboard 状态"
echo ""
