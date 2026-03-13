#!/bin/bash
# OpenClaw 恢复飞书配对脚本
# 用于重装后恢复飞书连接

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🔄 OpenClaw 飞书配对恢复脚本${NC}"
echo ""

# 检查备份目录参数
if [ -z "$1" ]; then
    echo -e "${RED}❌ 请指定备份目录${NC}"
    echo ""
    echo "用法: $0 <备份目录>"
    echo ""
    echo "示例:"
    echo "  $0 /root/.openclaw/backups/manual_20260302_120000"
    echo ""
    echo "可用备份:"
    ls -td /root/.openclaw/backups/manual_* 2>/dev/null || echo "  无备份目录"
    exit 1
fi

BACKUP_DIR="$1"

# 检查备份目录是否存在
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}❌ 备份目录不存在: $BACKUP_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 备份目录: $BACKUP_DIR${NC}"
echo ""

# 检查飞书配对文件
PAIRING_FILE="$BACKUP_DIR/credentials/feishu-pairing.json"
if [ ! -f "$PAIRING_FILE" ]; then
    echo -e "${RED}❌ 飞书配对文件不存在${NC}"
    echo "期望路径: $PAIRING_FILE"
    exit 1
fi

echo -e "${GREEN}✓ 找到飞书配对文件${NC}"
echo ""

# 确保目标目录存在
mkdir -p /root/.openclaw/credentials

# 停止 Gateway
echo -e "${YELLOW}⏹ 停止 Gateway...${NC}"
if systemctl --user is-active --quiet openclaw-gateway; then
    systemctl --user stop openclaw-gateway
    echo -e "${GREEN}✓ Gateway 已停止${NC}"
else
    echo -e "${YELLOW}⚠ Gateway 未运行${NC}"
fi
echo ""

# 恢复飞书配对
echo -e "${YELLOW}📋 恢复飞书配对...${NC}"
cp "$PAIRING_FILE" /root/.openclaw/credentials/feishu-pairing.json
echo -e "${GREEN}✓ 飞书配对已恢复${NC}"
echo ""

# 启动 Gateway
echo -e "${YELLOW}▶️ 启动 Gateway...${NC}"
systemctl --user start openclaw-gateway
sleep 3

if systemctl --user is-active --quiet openclaw-gateway; then
    echo -e "${GREEN}✓ Gateway 已启动${NC}"
else
    echo -e "${RED}❌ Gateway 启动失败${NC}"
    echo "请运行: systemctl --user status openclaw-gateway"
    exit 1
fi
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ 飞书配对恢复完成！${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}建议测试:${NC}"
echo "发送测试消息到飞书验证连接"
echo ""
