#!/bin/bash
# Control Center 系统服务配置脚本
# 作者: 大领导系统 v5.16.0
# 日期: 2026-03-16
#
# 功能：将 Control Center 配置为系统服务，开机自动启动

set -e

echo "🔧 配置 Control Center 系统服务..."

# 创建 systemd 用户服务文件
cat > ~/.config/systemd/user/control-center.service << 'EOF'
[Unit]
Description=OpenClaw Control Center
After=network.target openclaw-gateway.service

[Service]
Type=simple
WorkingDirectory=/root/.openclaw/control-center
Environment="LOCAL_API_TOKEN=67b455b94ac842d4d3bfb8739d3b7fe16c8770d36d708adc57512a9ab79598cc"
ExecStart=/usr/bin/npm run dev
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
EOF

echo "✅ 服务文件已创建"

# 重新加载 systemd
systemctl --user daemon-reload

# 启用服务
systemctl --user enable control-center

echo "🚀 启动 Control Center 服务..."
systemctl --user start control-center

# 等待启动
sleep 5

# 检查状态
if systemctl --user is-active control-center >/dev/null 2>&1; then
    echo "✅ Control Center 服务启动成功"
    echo "📍 访问地址: http://43.134.63.176:4310"
    echo ""
    echo "📋 管理命令:"
    echo "  - 启动: systemctl --user start control-center"
    echo "  - 停止: systemctl --user stop control-center"
    echo "  - 重启: systemctl --user restart control-center"
    echo "  - 状态: systemctl --user status control-center"
    echo "  - 日志: journalctl --user -u control-center -f"
else
    echo "❌ Control Center 服务启动失败"
    echo "📋 查看日志: journalctl --user -u control-center -n 50"
    exit 1
fi
