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
