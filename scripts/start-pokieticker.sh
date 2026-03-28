#!/bin/bash
# PokieTicker 启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  📊 PokieTicker 股票新闻分析工具${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 进入项目目录
cd /root/.openclaw/workspace/PokieTicker

# 检查后端环境
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ 后端虚拟环境不存在${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 后端虚拟环境存在${NC}"

# 检查前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${RED}❌ 前端依赖未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 前端依赖已安装${NC}"
echo ""

# 启动后端
echo -e "${BLUE}🚀 启动后端服务...${NC}"
source venv/bin/activate
nohup uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/pokie-backend-server.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✅ 后端服务已启动 (PID: $BACKEND_PID)${NC}"
echo ""

# 等待后端启动
echo -e "${YELLOW}⏳ 等待后端服务启动...${NC}"
sleep 5

# 检查后端是否启动成功
if ! curl -s http://localhost:8000/docs >/dev/null; then
    echo -e "${RED}❌ 后端服务启动失败${NC}"
    echo "请检查日志: cat /tmp/pokie-backend-server.log"
    exit 1
fi

echo -e "${GREEN}✅ 后端服务启动成功${NC}"
echo ""

# 启动前端
echo -e "${BLUE}🚀 启动前端服务...${NC}"
cd frontend
nohup npm run dev -- --host 0.0.0.0 --port 7777 > /tmp/pokie-frontend-server.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✅ 前端服务已启动 (PID: $FRONTEND_PID)${NC}"
echo ""

# 等待前端启动
echo -e "${YELLOW}⏳ 等待前端服务启动...${NC}"
sleep 10

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🎉 PokieTicker 启动成功！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}访问地址:${NC}"
echo -e "  📊 前端界面: ${GREEN}http://43.134.63.176:7777/PokieTicker/${NC}"
echo -e "  🔧 后端 API: ${GREEN}http://43.134.63.176:8000/docs${NC}"
echo ""
echo -e "${YELLOW}进程信息:${NC}"
echo -e "  后端 PID: $BACKEND_PID"
echo -e "  前端 PID: $FRONTEND_PID"
echo ""
echo -e "${YELLOW}日志文件:${NC}"
echo -e "  后端: /tmp/pokie-backend-server.log"
echo -e "  前端: /tmp/pokie-frontend-server.log"
echo ""
echo -e "${YELLOW}停止服务:${NC}"
echo -e "  kill $BACKEND_PID  # 停止后端"
echo -e "  kill $FRONTEND_PID  # 停止前端"
echo ""
