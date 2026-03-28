#!/bin/bash
# OpenClaw Bot 监控仪表板启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  🤖 OpenClaw Bot 监控仪表板${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js 版本: $(node --version)${NC}"

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ npm 版本: $(npm --version)${NC}"
echo ""

# 进入项目目录
cd /root/.openclaw/workspace/OpenClaw-bot-review

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  依赖未安装，正在安装...${NC}"
    npm install
    echo -e "${GREEN}✅ 依赖安装完成${NC}"
    echo ""
fi

# 检查 OpenClaw 配置
if [ ! -f "$HOME/.openclaw/openclaw.json" ]; then
    echo -e "${RED}❌ OpenClaw 配置文件不存在${NC}"
    echo "请先安装和配置 OpenClaw"
    exit 1
fi

echo -e "${GREEN}✅ OpenClaw 配置文件存在${NC}"
echo ""

# 启动开发服务器
echo -e "${BLUE}🚀 启动监控仪表板...${NC}"
echo ""
echo -e "${YELLOW}访问地址:${NC}"
echo -e "  本地: ${GREEN}http://localhost:3000${NC}"
echo -e "  公网: ${GREEN}http://43.134.63.176:3000${NC}"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"
echo ""

# 启动服务
npm run start
