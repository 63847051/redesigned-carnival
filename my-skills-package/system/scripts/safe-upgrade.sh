#!/bin/bash
# OpenClaw 安全升级脚本
# 自动执行：备份 -> 升级 -> 恢复配置 -> 验证

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🚀 OpenClaw 安全升级脚本${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 检查是否有备份脚本
BACKUP_SCRIPT="/root/.openclaw/workspace/scripts/backup-before-update.sh"
if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo -e "${RED}❌ 备份脚本不存在: $BACKUP_SCRIPT${NC}"
    exit 1
fi

# 步骤 1: 备份
echo -e "${YELLOW}📦 步骤 1/6: 执行备份...${NC}"
bash "$BACKUP_SCRIPT"
BACKUP_EXIT_CODE=$?

if [ $BACKUP_EXIT_CODE -ne 0 ]; then
    echo -e "${RED}❌ 备份失败，中止升级${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ 备份完成${NC}"
echo ""

# 步骤 2: 获取最新备份目录
LATEST_BACKUP=$(ls -td /root/.openclaw/backups/manual_* | head -1)
if [ -z "$LATEST_BACKUP" ]; then
    echo -e "${RED}❌ 无法找到备份目录${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 最新备份: $LATEST_BACKUP${NC}"
echo ""

# 步骤 3: 停止 Gateway
echo -e "${YELLOW}⏹ 步骤 2/6: 停止 Gateway...${NC}"
if systemctl --user is-active --quiet openclaw-gateway; then
    systemctl --user stop openclaw-gateway
    echo -e "${GREEN}✓ Gateway 已停止${NC}"
else
    echo -e "${YELLOW}⚠ Gateway 未运行${NC}"
fi
echo ""

# 步骤 4: 执行升级
echo -e "${YELLOW}⬆️ 步骤 3/6: 升级 OpenClaw...${NC}"
echo "执行: npm install -g openclaw"

# 询问用户确认
read -p "是否继续升级? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚠ 升级已取消${NC}"
    echo "可以稍后手动运行: npm install -g openclaw"
    exit 0
fi

if npm install -g openclaw; then
    echo -e "${GREEN}✓ 升级完成${NC}"
else
    echo -e "${RED}❌ 升级失败${NC}"
    echo "请不要担心，配置已安全备份"
    exit 1
fi
echo ""

# 步骤 5: 恢复配置
echo -e "${YELLOW}🔄 步骤 4/6: 恢复配置...${NC}"

# 恢复主配置
if [ -f "$LATEST_BACKUP/openclaw.json" ]; then
    cp "$LATEST_BACKUP/openclaw.json" /root/.openclaw/
    echo -e "${GREEN}✓ 已恢复: openclaw.json${NC}"
fi

# 恢复凭证
if [ -d "$LATEST_BACKUP/credentials" ]; then
    cp -r "$LATEST_BACKUP/credentials"/* /root/.openclaw/credentials/
    echo -e "${GREEN}✓ 已恢复: credentials/${NC}"

    # 特别提示飞书配对
    if [ -f "$LATEST_BACKUP/credentials/feishu-pairing.json" ]; then
        echo -e "${GREEN}  ⭐ 飞书配对已恢复${NC}"
    fi
fi

# 恢复工作区（可选，询问用户）
if [ -d "$LATEST_BACKUP/workspace_backup" ]; then
    read -p "是否恢复工作区? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp -r "$LATEST_BACKUP/workspace_backup"/* /root/.openclaw/workspace/
        echo -e "${GREEN}✓ 已恢复: workspace/${NC}"
    else
        echo -e "${YELLOW}⚠ 跳过工作区恢复${NC}"
    fi
fi
echo ""

# 步骤 6: 启动 Gateway
echo -e "${YELLOW}▶️ 步骤 5/6: 启动 Gateway...${NC}"
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

# 步骤 7: 验证
echo -e "${YELLOW}🔍 步骤 6/6: 验证状态...${NC}"
echo ""

# 显示版本
echo -e "${BLUE}当前版本:${NC}"
if command -v openclaw &> /dev/null; then
    openclaw --version
else
    echo "无法获取版本信息"
fi
echo ""

# 显示 Gateway 状态
echo -e "${BLUE}Gateway 状态:${NC}"
systemctl --user status openclaw-gateway --no-pager | head -n 5
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ 升级完成！${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}建议测试:${NC}"
echo "1. 发送测试消息到飞书"
echo "2. 检查工作区文件是否正常"
echo "3. 运行: openclaw status"
echo ""
