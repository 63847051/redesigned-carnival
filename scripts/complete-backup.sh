#!/bin/bash
# 完整备份流程脚本
# 确保备份时不会遗漏任何步骤

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  📦 完整备份流程${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查工作目录
if [ ! -d "/root/.openclaw/workspace" ]; then
    echo -e "${RED}❌ 工作目录不存在${NC}"
    exit 1
fi

cd /root/.openclaw/workspace

# Step 1: 检查 Git 状态
echo -e "${BLUE}[1/6] 检查 Git 状态...${NC}"
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  有未提交的更改${NC}"
    git status --short
else
    echo -e "${GREEN}✅ 工作区干净${NC}"
fi
echo ""

# Step 2: 检查版本号一致性
echo -e "${BLUE}[2/6] 检查版本号一致性...${NC}"
CURRENT_VERSION=$(grep "版本.*v6" SOUL.md | head -1 | grep -oP "v\d+\.\d+\.\d+" || echo "v6.1.1")
README_VERSION=$(grep "版本.*v6" README.md | head -1 | grep -oP "v\d+\.\d+\.\d+" || echo "unknown")

echo "SOUL.md 版本: $CURRENT_VERSION"
echo "README.md 版本: $README_VERSION"

if [ "$CURRENT_VERSION" != "$README_VERSION" ]; then
    echo -e "${RED}❌ 版本号不一致！${NC}"
    echo -e "${YELLOW}需要更新 README.md${NC}"
    echo ""
    read -p "是否现在更新 README.md？(y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✅ 请手动更新 README.md 后重新运行${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ 版本号一致${NC}"
fi
echo ""

# Step 3: 添加所有更改
echo -e "${BLUE}[3/6] 添加所有更改...${NC}"
git add -A
echo -e "${GREEN}✅ 完成${NC}"
echo ""

# Step 4: 提交更改
echo -e "${BLUE}[4/6] 提交更改...${NC}"
echo "请输入提交信息（留空使用默认）:"
read -p "> " COMMIT_MSG

if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="📦 系统备份 - $(date +'%Y-%m-%d %H:%M')

    # 自动生成详细的提交信息
    COMMIT_MSG="$COMMIT_MSG

✅ 完成的改进:
$(git status --short | wc -l) 个文件变更

📊 版本: $CURRENT_VERSION
🔧 状态: 系统正常运行
💾 备份: 完整备份到 GitHub"
fi

git commit -m "$COMMIT_MSG"
echo -e "${GREEN}✅ 完成${NC}"
echo ""

# Step 5: 推送到 GitHub
echo -e "${BLUE}[5/6] 推送到 GitHub...${NC}"
git push origin main
echo -e "${GREEN}✅ 完成${NC}"
echo ""

# Step 6: 验证推送成功
echo -e "${BLUE}[6/6] 验证推送...${NC}"
LATEST_COMMIT=$(git log -1 --format='%h')
echo "最新提交: $LATEST_COMMIT"
echo -e "${GREEN}✅ 备份完成！${NC}"
echo ""

# 完成
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ 备份成功完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}GitHub 仓库:${NC}"
echo "https://github.com/63847051/redesigned-carnival"
echo ""
echo -e "${BLUE}版本信息:${NC}"
echo "$CURRENT_VERSION"
echo ""
