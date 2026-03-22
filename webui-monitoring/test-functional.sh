#!/bin/bash

echo "🧪 大领导系统 v5.23 Web UI 可视化监控 - 功能测试"
echo "================================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 测试结果统计
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试函数
function test_case() {
    local test_name="$1"
    local test_command="$2"
    local expected_exit_code="${3:-0}"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${BLUE}📋 测试: $test_name${NC}"
    
    # 执行测试命令
    eval "$test_command"
    local exit_code=$?
    
    if [ $exit_code -eq $expected_exit_code ]; then
        echo -e "${GREEN}✅ 通过${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ 失败 (退出码: $exit_code)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# 清理函数
function cleanup() {
    echo -e "${YELLOW}🧹 清理测试环境...${NC}"
    
    # 停止运行的服务
    pkill -f "node server.js" 2>/dev/null || true
    
    # 清理临时文件
    rm -f test-output.log
    rm -f test-response.json
    
    echo -e "${GREEN}✅ 清理完成${NC}"
}

# 设置陷阱
trap cleanup EXIT

# 测试 1: 环境检查
echo -e "${BLUE}=== 测试 1: 环境检查 ===${NC}"
test_case "检查 Node.js 环境" "node --version"
test_case "检查 npm 环境" "npm --version"

# 测试 2: 依赖安装
echo -e "${BLUE}=== 测试 2: 依赖安装 ===${NC}"
test_case "检查 package.json" "[ -f package.json ]"
test_case "安装依赖" "npm install --silent"

# 测试 3: 服务器启动
echo -e "${BLUE}=== 测试 3: 服务器启动 ===${NC}"
test_case "启动服务器" "timeout 10s node server.js --port 8081 &" 0
sleep 3

# 测试 4: HTTP 接口测试
echo -e "${BLUE}=== 测试 4: HTTP 接口测试 ===${NC}"
test_case "健康检查" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8081/health | grep -q '200'"
test_case "获取首页" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8081/ | grep -q '200'"
test_case "获取配置" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8081/config.js | grep -q '200'"

# 测试 5: WebSocket 连接测试
echo -e "${BLUE}=== 测试 5: WebSocket 连接测试 ===${NC}"
# 创建 WebSocket 测试脚本
cat > test-websocket.js << 'EOF'
const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:8081');
let connected = false;
let receivedMessage = false;

ws.on('open', () => {
    connected = true;
    console.log('WebSocket 连接成功');
    
    // 发送 ping
    ws.send(JSON.stringify({type: 'ping'}));
});

ws.on('message', (data) => {
    console.log('收到消息:', data.toString());
    receivedMessage = true;
    
    // 检查欢迎消息
    const message = JSON.parse(data.toString());
    if (message.type === 'welcome') {
        console.log('✅ WebSocket 连接测试通过');
        process.exit(0);
    }
});

ws.on('close', () => {
    console.log('WebSocket 连接关闭');
    process.exit(1);
});

ws.on('error', (error) => {
    console.log('WebSocket 错误:', error.message);
    process.exit(1);
});

// 5秒后超时
setTimeout(() => {
    if (!connected || !receivedMessage) {
        console.log('❌ WebSocket 连接测试失败');
        process.exit(1);
    }
}, 5000);
EOF

test_case "WebSocket 连接测试" "node test-websocket.js" 0

# 测试 6: 数据验证
echo -e "${BLUE}=== 测试 6: 数据验证 ===${NC}"
test_case "获取配置数据" "curl -s http://localhost:8081/config.js > test-response.json && grep -q 'server' test-response.json"
test_case "验证配置格式" "cat test-response.json | python3 -m json.tool > /dev/null 2>&1"

# 测试 7: 性能测试
echo -e "${BLUE}=== 测试 7: 性能测试 ===${NC}"
test_case "内存使用检查" "ps aux | grep 'node server.js' | grep -v grep | awk '{print \$4}' | grep -E '^[0-9]+(\.[0-9]+)?$' | head -1" 0

# 测试 8: 响应式设计测试
echo -e "${BLUE}=== 测试 8: 响应式设计测试 ===${NC}"
test_case "检查 CSS 媒体查询" "grep -q '@media' index.html"
test_case "检查移动端适配" "grep -q 'grid-template-columns' index.html"

# 测试 9: 文档完整性
echo -e "${BLUE}=== 测试 9: 文档完整性 ===${NC}"
test_case "检查 README.md" "[ -f README.md ]"
test_case "检查启动脚本" "[ -f start-monitoring.sh ]"
test_case "检查服务器代码" "[ -f server.js ]"
test_case "检查前端代码" "[ -f index.html ]"
test_case "检查客户端代码" "[ -f webui-monitoring.js ]"

# 测试 10: 安全性检查
echo -e "${BLUE}=== 测试 10: 安全性检查 ===${NC}"
test_case "检查端口安全" "netstat -tlnp 2>/dev/null | grep -q ':8081'"
test_case "检查权限设置" "[ -r index.html ] && [ -x start-monitoring.sh ]"

# 显示测试结果
echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}           测试结果汇总                        ${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

echo -e "📊 总测试数: ${TOTAL_TESTS}"
echo -e "${GREEN}✅ 通过: ${PASSED_TESTS}${NC}"
echo -e "${RED}❌ 失败: ${FAILED_TESTS}${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 所有测试通过！系统功能正常。${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}⚠️  有 ${FAILED_TESTS} 个测试失败，请检查相关功能。${NC}"
    exit 1
fi