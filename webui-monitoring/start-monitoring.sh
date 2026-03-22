#!/bin/bash

echo "🚀 启动大领导系统 v5.23 Web UI 可视化监控..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查 Node.js 环境
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 Node.js 环境${NC}"
    echo "请先安装 Node.js: https://nodejs.org/"
    exit 1
fi

echo -e "${GREEN}✅ Node.js 版本: $(node --version)${NC}"

# 检查 npm 环境
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 npm 环境${NC}"
    echo "请先安装 npm"
    exit 1
fi

echo -e "${GREEN}✅ npm 版本: $(npm --version)${NC}"

# 检查是否在正确的目录
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ 错误: 未找到 package.json 文件${NC}"
    echo "请在 webui-monitoring 目录中运行此脚本"
    exit 1
fi

echo -e "${BLUE}📁 当前目录: $(pwd)${NC}"

# 检查是否存在 node_modules
if [ ! -d "node_modules" ];  then
    echo -e "${YELLOW}📦 正在安装依赖...${NC}"
    npm install
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 依赖安装失败${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 依赖安装完成${NC}"
else
    echo -e "${GREEN}✅ 依赖已安装${NC}"
fi

# 检查端口占用
function check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}⚠️  端口 $port 已被占用${NC}"
        return 1
    else
        echo -e "${GREEN}✅ 端口 $port 可用${NC}"
        return 0
    fi
}

# 尝试可用端口
PORT=8080
if check_port $PORT; then
    echo -e "${BLUE}🎯 使用端口: $PORT${NC}"
else
    for ((i=8081; i<=8090; i++)); do
        if check_port $i; then
            PORT=$i
            echo -e "${BLUE}🎯 使用端口: $PORT${NC}"
            break
        fi
    done
    
    if [ "$PORT" = "8080" ]; then
        echo -e "${RED}❌ 错误: 找不到可用端口 (8080-8090)${NC}"
        exit 1
    fi
fi

# 创建启动日志目录
mkdir -p logs
LOG_FILE="logs/monitoring-$(date +%Y%m%d-%H%M%S).log"

# 显示启动信息
echo ""
echo -e "${BLUE}===========================================${NC}"
echo -e "${BLUE}    大领导系统 v5.23 Web UI 监控启动      ${NC}"
echo -e "${BLUE}===========================================${NC}"
echo ""
echo -e "${GREEN}🌐 访问地址: http://localhost:$PORT${NC}"
echo -e "${GREEN}🔌 WebSocket地址: ws://localhost:$PORT${NC}"
echo -e "${GREEN}📊 健康检查: http://localhost:$PORT/health${NC}"
echo -e "${GREEN}📋 配置信息: http://localhost:$PORT/config.js${NC}"
echo ""
echo -e "${YELLOW}⏹️  按 Ctrl+C 停止服务${NC}"
echo ""

# 设置日志输出
exec > >(tee -a "$LOG_FILE")
exec 2>&1

# 启动服务器
echo -e "${BLUE}🚀 启动监控服务器...${NC}"
echo "启动时间: $(date)"
echo "日志文件: $LOG_FILE"

# 检查环境变量
if [ ! -z "$NODE_ENV" ]; then
    echo -e "${YELLOW}🌍 环境变量: NODE_ENV=$NODE_ENV${NC}"
fi

if [ ! -z "$PORT" ]; then
    echo -e "${YELLOW}🎯 端口配置: PORT=$PORT${NC}"
fi

# 启动服务器
node server.js --port $PORT

# 如果服务器异常退出，显示错误信息
echo -e "${RED}❌ 服务器异常退出${NC}"
echo "请检查日志文件: $LOG_FILE"
exit 1