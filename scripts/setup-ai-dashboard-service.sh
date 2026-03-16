#!/bin/bash
# AI Team Dashboard 系统服务配置脚本
# 作者: 大领导系统 v5.16.0
# 日期: 2026-03-16
#
# 功能：将 AI Team Dashboard 配置为系统服务，开机自动启动

set -e

echo "🔧 配置 AI Team Dashboard 系统服务..."

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，无法配置 AI Team Dashboard 服务"
    echo "💡 请先安装 Docker: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，无法配置 AI Team Dashboard 服务"
    echo "💡 请先安装 Docker Compose"
    exit 1
fi

# 创建 systemd 用户服务文件
cat > ~/.config/systemd/user/ai-team-dashboard.service << 'EOF'
[Unit]
Description=AI Team Dashboard
After=network.target docker.service

[Service]
Type=oneshot
RemainAfter=exit
WorkingDirectory=/root/.openclaw/workspace/ai-team-dashboard
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF

echo "✅ 服务文件已创建"

# 重新加载 systemd
systemctl --user daemon-reload

# 启用服务
systemctl --user enable ai-team-dashboard

echo "🚀 启动 AI Team Dashboard 服务..."
systemctl --user start ai-team-dashboard

# 等待启动
sleep 10

# 检查状态
if systemctl --user is-active ai-team-dashboard >/dev/null 2>&1; then
    echo "✅ AI Team Dashboard 服务启动成功"
    echo "📍 访问地址: http://43.134.63.176:3800"
    echo ""
    echo "📋 管理命令:"
    echo "  - 启动: systemctl --user start ai-team-dashboard"
    echo "  - 停止: systemctl --user stop ai-team-dashboard"
    echo "  - 重启: systemctl --user restart ai-team-dashboard"
    echo "  - 状态: systemctl --user status ai-team-dashboard"
    echo "  - 日志: journalctl --user -u ai-team-dashboard -f"
else
    echo "❌ AI Team Dashboard 服务启动失败"
    echo "📋 查看日志: journalctl --user -u ai-team-dashboard -n 50"
    exit 1
fi
