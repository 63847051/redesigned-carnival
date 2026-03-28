#!/bin/bash
# 快速恢复脚本 - OpenClaw 工作区完整备份恢复
# 使用方法: bash quick-restore.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  OpenClaw 工作区快速恢复脚本${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# 检查 Git 是否安装
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git 未安装${NC}"
    echo "请先安装 Git: yum install git -y"
    exit 1
fi

# 检查 Node.js 是否安装
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js 未安装${NC}"
    echo "请先安装 Node.js"
    exit 1
fi

# 仓库地址
REPO_URL="https://github.com/63847051/redesigned-carnival.git"
BACKUP_DIR="/root/.openclaw/workspace-backup"
WORKSPACE_DIR="/root/.openclaw/workspace"

echo -e "${YELLOW}📋 恢复步骤${NC}"
echo ""

# Step 1: 备份现有配置（如果存在）
echo -e "${BLUE}[1/5] 检查现有配置...${NC}"
if [ -d "$WORKSPACE_DIR" ]; then
    echo -e "${YELLOW}发现现有工作区，备份到: $BACKUP_DIR${NC}"
    mv "$WORKSPACE_DIR" "$BACKUP_DIR" || true
fi
echo -e "${GREEN}✅ 完成${NC}"
echo ""

# Step 2: 克隆仓库
echo -e "${BLUE}[2/5] 克隆备份仓库...${NC}"
git clone "$REPO_URL" "$WORKSPACE_DIR"
echo -e "${GREEN}✅ 完成${NC}"
echo ""

# Step 3: 恢复 OpenClaw 配置（如果存在）
echo -e "${BLUE}[3/5] 恢复 OpenClaw 配置...${NC}"
if [ -f "$BACKUP_DIR/../openclaw.json" ]; then
    cp "$BACKUP_DIR/../openclaw.json" "/root/.openclaw/openclaw.json"
    echo -e "${GREEN}✅ 配置已恢复${NC}"
else
    echo -e "${YELLOW}⚠️  未找到配置文件，需要手动配置${NC}"
fi
echo ""

# Step 4: 设置权限
echo -e "${BLUE}[4/5] 设置脚本执行权限...${NC}"
find "$WORKSPACE_DIR/scripts" -name "*.sh" -type f -exec chmod +x {} \;
echo -e "${GREEN}✅ 完成${NC}"
echo ""

# Step 5: 验证核心文件
echo -e "${BLUE}[5/5] 验证核心文件...${NC}"
CORE_FILES=(
    "$WORKSPACE_DIR/SOUL.md"
    "$WORKSPACE_DIR/IDENTITY.md"
    "$WORKSPACE_DIR/MEMORY.md"
    "$WORKSPACE_DIR/AGENTS.md"
)

ALL_OK=true
for file in "${CORE_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $(basename $file)${NC}"
    else
        echo -e "${RED}❌ $(basename $file) 缺失${NC}"
        ALL_OK=false
    fi
done
echo ""

# 完成
if [ "$ALL_OK" = true ]; then
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}  ✅ 恢复完成！${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo ""
    echo -e "${BLUE}工作区位置: $WORKSPACE_DIR${NC}"
    echo -e "${BLUE}版本信息: $(git -C $WORKSPACE_DIR log -1 --format='%h - %s')${NC}"
    echo ""
    echo -e "${YELLOW}下一步:${NC}"
    echo "1. 启动 OpenClaw Gateway"
    echo "2. 验证系统状态"
    echo "3. 开始使用"
    echo ""
else
    echo -e "${RED}======================================${NC}"
    echo -e "${RED}  ❌ 恢复失败！${NC}"
    echo -e "${RED}======================================${NC}"
    echo ""
    echo -e "${YELLOW}请检查:${NC}"
    echo "1. 网络连接"
    echo "2. GitHub 访问"
    echo "3. 磁盘空间"
    echo ""
    exit 1
fi
