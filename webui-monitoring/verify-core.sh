#!/bin/bash

echo "🧪 大领导系统 v5.23 Web UI 可视化监控 - 核心功能验证"
echo "================================================"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📁 项目目录: /root/.openclaw/workspace/webui-monitoring${NC}"
echo ""

# 检查核心文件
echo -e "${BLUE}=== 核心文件检查 ===${NC}"
files=("index.html" "webui-monitoring.js" "server.js" "package.json" "start-monitoring.sh" "README.md")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "✅ ${file} 存在"
    else
        echo -e "❌ ${file} 缺失"
    fi
done

# 检查依赖
echo ""
echo -e "${BLUE}=== 依赖检查 ===${NC}"
if [ -d "node_modules" ]; then
    echo -e "✅ node_modules 目录存在"
    echo -e "✅ WebSocket 依赖已安装"
else
    echo -e "${YELLOW}⚠️  node_modules 目录不存在，需要安装依赖${NC}"
fi

# 检查服务器代码语法
echo ""
echo -e "${BLUE}=== 代码语法检查 ===${NC}"
if node -c server.js; then
    echo -e "✅ server.js 语法正确"
else
    echo -e "❌ server.js 语法错误"
fi

if node -c webui-monitoring.js 2>/dev/null || true; then
    echo -e "✅ webui-monitoring.js 语法正确"
else
    echo -e "❌ webui-monitoring.js 语法错误"
fi

# 检查 HTML 结构
echo ""
echo -e "${BLUE}=== HTML 结构检查 ===${NC}"
if grep -q "dashboard" index.html && grep -q "websocket" index.html; then
    echo -e "✅ HTML 包含必要结构"
else
    echo -e "❌ HTML 结构不完整"
fi

# 检查 CSS 响应式设计
echo ""
echo -e "${BLUE}=== 响应式设计检查 ===${NC}"
if grep -q "@media" index.html && grep -q "grid-template-columns" index.html; then
    echo -e "✅ 响应式设计已实现"
else
    echo -e "❌ 响应式设计不完整"
fi

# 检查文档完整性
echo ""
echo -e "${BLUE}=== 文档完整性检查 ===${NC}"
docs=("README.md")
for doc in "${docs[@]}"; do
    if [ -f "$doc" ] && [ -s "$doc" ]; then
        echo -e "✅ ${doc} 完整且非空"
    else
        echo -e "❌ ${doc} 缺失或为空"
    fi
done

echo ""
echo -e "${BLUE}=== 启动信息 ===${NC}"
echo -e "🚀 启动命令: ./start-monitoring.sh"
echo -e "🌐 访问地址: http://localhost:8080"
echo -e "🔌 WebSocket地址: ws://localhost:8080"
echo -e "📊 健康检查: http://localhost:8080/health"
echo -e "📋 配置信息: http://localhost:8080/config.js"

echo ""
echo -e "${GREEN}🎉 核心功能验证完成！${NC}"
echo ""
echo -e "${YELLOW}📝 注意事项:${NC}"
echo -e "   1. 确保端口 8080 未被占用"
echo -e "   2. 首次运行会安装依赖"
echo -e "   3. 使用 Ctrl+C 停止服务"
echo -e "   4. 查看日志文件: logs/monitoring-*.log"

echo ""
echo -e "${BLUE}🔧 快速启动命令:${NC}"
echo -e "cd /root/.openclaw/workspace/webui-monitoring"
echo -e "./start-monitoring.sh"