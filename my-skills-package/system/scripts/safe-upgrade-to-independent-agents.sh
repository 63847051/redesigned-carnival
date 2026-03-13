#!/bin/bash
# 🛡️  安全升级到独立 Agent v3.0
# 基于崩溃教训的完全安全方案
# 不修改配置文件，使用环境变量

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================"
echo "🛡️  安全升级到独立 Agent v3.0"
echo "========================================"
echo ""
echo "⚠️  重要提示："
echo "  - 本脚本不会修改 openclaw.json"
echo "  - 使用环境变量配置（避免配置键问题）"
echo "  - 每步都会验证，失败立即回滚"
echo ""

# Step 1: 备份
echo -e "${YELLOW}📦 Step 1: 备份当前配置${NC}"
BACKUP_DIR="/root/.openclaw/backups/safe-upgrade-$(date +%Y%m%d%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 备份服务文件
if [ -f /root/.config/systemd/user/openclaw-gateway.service ]; then
    cp /root/.config/systemd/user/openclaw-gateway.service "$BACKUP_DIR/"
    echo -e "${GREEN}✅ 服务文件已备份${NC}"
else
    echo -e "${YELLOW}⚠️  服务文件不存在，将创建新文件${NC}"
fi

# 记录当前 Gateway 状态
systemctl --user is-active openclaw-gateway > "$BACKUP_DIR/gateway-status.txt" 2>&1
echo -e "${GREEN}✅ Gateway 状态已记录${NC}"

echo ""
echo -e "${BLUE}📁 备份位置: $BACKUP_DIR${NC}"
echo ""

# Step 2: 检查当前服务文件
echo -e "${YELLOW}🔍 Step 2: 检查当前服务配置${NC}"

if systemctl --user is-active --quiet openclaw-gateway; then
    echo -e "${GREEN}✅ Gateway 当前运行中${NC}"
else
    echo -e "${RED}❌ Gateway 未运行，请先启动${NC}"
    exit 1
fi
echo ""

# Step 3: 创建环境变量文件
echo -e "${YELLOW}🔧 Step 3: 创建环境变量文件${NC}"

cat > /root/.openclaw/gateway.env << 'EOF'
# OpenClaw Gateway 环境变量
# 允许创建独立子 Agent

OPENCLAW_SESSIONS_SPAWN_ALLOW_ANY=true
OPENCLAW_SESSIONS_SPAWN_ALLOWED_AGENTS=*
EOF

echo -e "${GREEN}✅ 环境变量文件已创建: /root/.openclaw/gateway.env${NC}"
echo ""

# Step 4: 修改服务文件
echo -e "${YELLOW}🔄 Step 4: 修改 systemd 服务文件${NC}"

# 停止 Gateway
echo "正在停止 Gateway..."
systemctl --user stop openclaw-gateway
sleep 2

# 创建新服务文件
cat > /root/.config/systemd/user/openclaw-gateway.service << 'EOF'
[Unit]
Description=OpenClaw Gateway (v2026.2.26)
After=network.target

[Service]
EnvironmentFile=/root/.openclaw/gateway.env
ExecStart=/usr/bin/openclaw gateway --port 18789
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

echo -e "${GREEN}✅ 服务文件已更新${NC}"

# 重新加载 systemd
systemctl --user daemon-reload
echo -e "${GREEN}✅ systemd 已重新加载${NC}"
echo ""

# Step 5: 启动 Gateway
echo -e "${YELLOW}🚀 Step 5: 启动 Gateway${NC}"

systemctl --user start openclaw-gateway
echo "等待 Gateway 启动..."
sleep 8

# 检查是否成功启动
if systemctl --user is-active --quiet openclaw-gateway; then
    echo -e "${GREEN}✅ Gateway 启动成功${NC}"
else
    echo -e "${RED}❌ Gateway 启动失败，正在回滚...${NC}"

    # 回滚
    if [ -f "$BACKUP_DIR/openclaw-gateway.service" ]; then
        cp "$BACKUP_DIR/openclaw-gateway.service" /root/.config/systemd/user/
    else
        rm -f /root/.config/systemd/user/openclaw-gateway.service
    fi

    systemctl --user daemon-reload
    systemctl --user start openclaw-gateway

    echo -e "${RED}❌ 升级失败，已回滚${NC}"
    exit 1
fi
echo ""

# Step 6: 验证配置
echo -e "${YELLOW}🔍 Step 6: 验证配置${NC}"

# 检查环境变量文件
if [ -f /root/.openclaw/gateway.env ]; then
    echo -e "${GREEN}✅ 环境变量文件存在${NC}"
    cat /root/.openclaw/gateway.env
else
    echo -e "${RED}❌ 环境变量文件丢失${NC}"
    exit 1
fi
echo ""

# Step 7: 检查日志
echo -e "${YELLOW}📋 Step 7: 检查启动日志${NC}"

# 检查是否有错误
ERRORS=$(journalctl --user -u openclaw-gateway --since "1 minute ago" --no-pager | grep -i "error\|failed" | wc -l)

if [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}✅ 没有错误日志${NC}"
else
    echo -e "${YELLOW}⚠️  发现 $ERRORS 个错误，请检查：${NC}"
    echo "journalctl --user -u openclaw-gateway --since '1 minute ago' --no-pager"
fi
echo ""

# 完成
echo "========================================"
echo -e "${GREEN}🎉 升级完成！${NC}"
echo "========================================"
echo ""
echo "📋 下一步："
echo "  1. 在主控 Agent 中运行: agents_list"
echo "  2. 验证 allowAny 是否为 true"
echo "  3. 测试创建独立 Agent"
echo ""
echo "📁 备份位置: $BACKUP_DIR"
echo ""
echo "⚠️  如果出现问题，可以运行："
echo "   bash /root/.openclaw/workspace/scripts/rollback-safe-upgrade.sh $BACKUP_DIR"
echo ""

# 创建回滚脚本
cat > /root/.openclaw/workspace/scripts/rollback-safe-upgrade.sh << 'ROLLBACK_EOF'
#!/bin/bash
# 回滚安全升级

if [ -z "$1" ]; then
    echo "用法: $0 <backup_directory>"
    exit 1
fi

BACKUP_DIR="$1"

echo "正在回滚..."

# 恢复服务文件
if [ -f "$BACKUP_DIR/openclaw-gateway.service" ]; then
    cp "$BACKUP_DIR/openclaw-gateway.service" /root/.config/systemd/user/
else
    rm -f /root/.config/systemd/user/openclaw-gateway.service
fi

# 删除环境变量文件
rm -f /root/.openclaw/gateway.env

# 重新加载并重启
systemctl --user daemon-reload
systemctl --user restart openclaw-gateway

sleep 5

if systemctl --user is-active --quiet openclaw-gateway; then
    echo "✅ 回滚成功"
else
    echo "❌ 回滚后 Gateway 未能启动"
    exit 1
fi
ROLLBACK_EOF

chmod +x /root/.openclaw/workspace/scripts/rollback-safe-upgrade.sh
echo -e "${GREEN}✅ 回滚脚本已创建${NC}"
