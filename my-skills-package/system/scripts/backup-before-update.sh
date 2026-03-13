#!/bin/bash
# OpenClaw 快速备份脚本
# 在升级或重装前运行此脚本备份重要文件

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📦 开始备份 OpenClaw 配置...${NC}"

# 创建备份目录
BACKUP_DIR="/root/.openclaw/backups/manual_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo -e "${GREEN}✓ 备份目录: $BACKUP_DIR${NC}"

# 1. 备份主配置文件
if [ -f "/root/.openclaw/openclaw.json" ]; then
    cp /root/.openclaw/openclaw.json "$BACKUP_DIR/"
    echo -e "${GREEN}✓ 已备份: openclaw.json${NC}"
else
    echo -e "${YELLOW}⚠ openclaw.json 不存在${NC}"
fi

# 2. 备份凭证目录
if [ -d "/root/.openclaw/credentials" ]; then
    cp -r /root/.openclaw/credentials "$BACKUP_DIR/"
    echo -e "${GREEN}✓ 已备份: credentials/ 目录${NC}"

    # 特别提示飞书配对
    if [ -f "/root/.openclaw/credentials/feishu-pairing.json" ]; then
        echo -e "${GREEN}  ⭐ 飞书配对文件已备份（最重要！）${NC}"
    fi
else
    echo -e "${YELLOW}⚠ credentials/ 目录不存在${NC}"
fi

# 3. 备份工作区
if [ -d "/root/.openclaw/workspace" ]; then
    cp -r /root/.openclaw/workspace "$BACKUP_DIR/workspace_backup"
    echo -e "${GREEN}✓ 已备份: workspace/ 目录${NC}"
else
    echo -e "${YELLOW}⚠ workspace/ 目录不存在${NC}"
fi

# 4. 备份已安装技能列表
if command -v clawhub &> /dev/null; then
    clawhub list > "$BACKUP_DIR/skills_list.txt" 2>/dev/null || echo "clawhub 不可用" > "$BACKUP_DIR/skills_list.txt"
    echo -e "${GREEN}✓ 已备份: 已安装技能列表${NC}"
else
    echo "clawhub 未安装" > "$BACKUP_DIR/skills_list.txt"
    echo -e "${YELLOW}⚠ clawhub 未安装${NC}"
fi

# 5. 记录当前版本
if command -v openclaw &> /dev/null; then
    openclaw --version > "$BACKUP_DIR/version.txt" 2>&1
    echo -e "${GREEN}✓ 已记录: 当前版本${NC}"
else
    echo "openclaw 命令不可用" > "$BACKUP_DIR/version.txt"
fi

# 6. 记录 git commit（如果是通过 npm 安装在 nvm 中）
if [ -d "/root/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/.git" ]; then
    cd /root/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw
    git rev-parse HEAD > "$BACKUP_DIR/git_commit.txt" 2>/dev/null || echo "无法获取 git commit" > "$BACKUP_DIR/git_commit.txt"
    echo -e "${GREEN}✓ 已记录: Git commit${NC}"
fi

# 7. 创建备份清单
cat > "$BACKUP_DIR/backup_manifest.txt" << EOF
备份时间: $(date)
备份目录: $BACKUP_DIR
备份内容:
  - openclaw.json
  - credentials/
  - workspace/
  - skills_list.txt
  - version.txt
  - git_commit.txt (如果可用)
EOF

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ 备份完成！${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "备份位置: $BACKUP_DIR"
echo ""
echo -e "${YELLOW}重要提示:${NC}"
echo "1. 请妥善保管此备份目录"
echo "2. 特别注意 credentials/feishu-pairing.json 文件"
echo "3. 恢复时请参考 BACKUP-GUIDE.md"
echo ""
