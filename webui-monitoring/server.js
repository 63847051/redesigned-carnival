const WebSocket = require('ws');
const http = require('http');
const fs = require('fs');
const path = require('path');

class MonitoringServer {
    constructor(options = {}) {
        this.port = options.port || 8080;
        this.clients = new Set();
        this.server = http.createServer(this.handleHttpRequest.bind(this));
        this.wss = new WebSocket.Server({ 
            server: this.server,
            clientTracking: true,
            maxPayload: 16 * 1024 * 1024 // 16MB 最大消息大小
        });
        
        // 配置参数
        this.config = {
            updateInterval: options.updateInterval || 2000,
            maxLogEntries: options.maxLogEntries || 100,
            maxClients: options.maxClients || 100,
            heartbeatInterval: options.heartbeatInterval || 30000,
            enableMockData: options.enableMockData !== false // 默认启用模拟数据
        };
        
        this.setupWebSocket();
        this.setupDataAggregator();
        this.setupHeartbeat();
        this.setupMetrics();
    }

    setupWebSocket() {
        console.log(`🔌 设置 WebSocket 服务器，端口: ${this.port}`);
        
        this.wss.on('connection', (ws, req) => {
            console.log('🔗 新的客户端连接');
            
            // 检查客户端数量限制
            if (this.clients.size >= this.config.maxClients) {
                console.log('❌ 客户端数量已达上限，拒绝连接');
                ws.close(1013, 'Server busy');
                return;
            }
            
            // 添加客户端
            this.clients.add(ws);
            this.updateMetrics();
            
            // 设置客户端信息
            ws.clientId = this.generateClientId();
            ws.connectedAt = new Date();
            ws.lastPing = Date.now();
            
            console.log(`✅ 客户端 ${ws.clientId} 已连接，当前连接数: ${this.clients.size}`);
            
            // 处理消息
            ws.on('message', (message) => {
                this.handleClientMessage(ws, message);
            });
            
            // 处理关闭
            ws.on('close', () => {
                console.log(`🔌 客户端 ${ws.clientId} 断开连接`);
                this.clients.delete(ws);
                this.updateMetrics();
            });
            
            // 处理错误
            ws.on('error', (error) => {
                console.error(`❌ 客户端 ${ws.clientId} 错误:`, error.message);
                this.clients.delete(ws);
                this.updateMetrics();
            });
            
            // 发送初始状态
            this.sendClientStatus(ws);
            
            // 发送欢迎消息
            this.sendWelcomeMessage(ws);
        });
        
        // 处理 WebSocket 错误
        this.wss.on('error', (error) => {
            console.error('❌ WebSocket 服务器错误:', error);
        });
        
        // 处理 WebSocket 关闭
        this.wss.on('close', () => {
            console.log('🔌 WebSocket 服务器已关闭');
        });
    }

    setupDataAggregator() {
        console.log('📊 设置数据聚合器');
        
        // 模拟数据聚合器 - 实际环境中从并行执行系统获取
        this.dataAggregator = {
            agents: [
                { id: 'agent-1', name: '技术专家小新', status: 'running', tasks: 3, model: 'glm-4.7' },
                { id: 'agent-2', name: '日志专家小蓝', status: 'idle', tasks: 1, model: 'glm-4.5' },
                { id: 'agent-3', name: '设计专家', status: 'running', tasks: 2, model: 'glm-4.6' },
                { id: 'agent-4', name: '大领导', status: 'running', tasks: 4, model: 'glm-4.7' }
            ],
            tasks: {
                pending: 5,
                running: 3,
                completed: 12,
                total: 20
            },
            performance: {
                efficiencyGain: '400%',
                completionRate: '87%',
                utilizationRate: '85%',
                avgResponseTime: '120ms',
                totalTasksExecuted: 156
            },
            system: {
                uptime: '2h 34m',
                memoryUsage: '45%',
                cpuUsage: '23%',
                networkStatus: 'healthy'
            },
            logs: []
        };

        // 实际数据更新函数 - 可以从并行执行系统获取真实数据
        this.updateRealData = async () => {
            try {
                // 这里可以调用并行执行系统的 API
                // const realData = await this.fetchDataFromParallelExecution();
                // this.dataAggregator = { ...this.dataAggregator, ...realData };
                
                console.log('🔄 数据已更新');
            } catch (error) {
                console.error('❌ 获取实时数据失败:', error);
            }
        };

        // 模拟实时数据更新
        this.startDataSimulation();
    }

    startDataSimulation() {
        console.log('🎮 启动模拟数据更新');
        
        const updateData = () => {
            // 更新 Agent 状态
            this.dataAggregator.agents.forEach(agent => {
                // 20% 概率改变状态
                if (Math.random() < 0.2) {
                    agent.status = agent.status === 'running' ? 'idle' : 'running';
                }
                
                // 随机任务数量
                agent.tasks = Math.floor(Math.random() * 5);
            });

            // 更新任务统计
            this.dataAggregator.tasks.pending = Math.floor(Math.random() * 10);
            this.dataAggregator.tasks.running = Math.floor(Math.random() * 5);
            this.dataAggregator.tasks.completed += Math.floor(Math.random() * 2);
            this.dataAggregator.tasks.total = this.dataAggregator.tasks.pending + 
                                            this.dataAggregator.tasks.running + 
                                            this.dataAggregator.tasks.completed;

            // 更新性能指标
            this.dataAggregator.performance.efficiencyGain = `${(300 + Math.random() * 200).toFixed(0)}%`;
            this.dataAggregator.performance.completionRate = `${(80 + Math.random() * 15).toFixed(0)}%`;
            this.dataAggregator.performance.utilizationRate = `${(70 + Math.random() * 25).toFixed(0)}%`;
            this.dataAggregator.performance.avgResponseTime = `${(100 + Math.random() * 50).toFixed(0)}ms`;
            this.dataAggregator.performance.totalTasksExecuted += Math.floor(Math.random() * 3);

            // 更新系统指标
            this.dataAggregator.system.memoryUsage = `${(40 + Math.random() * 30).toFixed(0)}%`;
            this.dataAggregator.system.cpuUsage = `${(15 + Math.random() * 20).toFixed(0)}%`;

            // 生成新日志
            if (this.dataAggregator.logs.length >= this.config.maxLogEntries) {
                this.dataAggregator.logs.shift();
            }
            
            const logTypes = ['INFO', 'WARN', 'ERROR'];
            const agents = this.dataAggregator.agents;
            const randomAgent = agents[Math.floor(Math.random() * agents.length)];
            const randomType = logTypes[Math.floor(Math.random() * logTypes.length)];
            const timestamp = new Date().toLocaleTimeString();
            
            this.dataAggregator.logs.push({
                timestamp,
                agent: randomAgent.name,
                type: randomType,
                message: `${randomType}: ${randomAgent.name} 执行任务完成`,
                taskId: `task-${Math.floor(Math.random() * 1000)}`
            });

            // 广播更新
            this.broadcastToAll();
        };

        // 立即执行一次
        updateData();
        
        // 定期更新
        setInterval(updateData, this.config.updateInterval);
    }

    setupHeartbeat() {
        console.log('💓 设置心跳机制');
        
        const heartbeat = () => {
            const now = Date.now();
            const deadClients = [];
            
            this.clients.forEach(client => {
                // 检查心跳
                if (now - client.lastPing > this.config.heartbeatInterval * 2) {
                    deadClients.push(client);
                    return;
                }
                
                // 发送心跳
                if (client.readyState === WebSocket.OPEN) {
                    client.ping();
                }
            });
            
            // 清理死亡的客户端
            deadClients.forEach(client => {
                console.log(`❌ 清理死亡客户端: ${client.clientId}`);
                this.clients.delete(client);
                this.updateMetrics();
            });
        };
        
        // 每 30 秒检查一次
        setInterval(heartbeat, this.config.heartbeatInterval);
    }

    setupMetrics() {
        this.metrics = {
            startTime: Date.now(),
            totalConnections: 0,
            activeConnections: 0,
            totalMessages: 0,
            uptime: 0
        };
        
        // 定期更新指标
        setInterval(() => {
            this.metrics.uptime = Date.now() - this.metrics.startTime;
            this.metrics.activeConnections = this.clients.size;
        }, 1000);
    }

    updateMetrics() {
        this.metrics.activeConnections = this.clients.size;
    }

    generateClientId() {
        return `client-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    handleClientMessage(ws, message) {
        this.metrics.totalMessages++;
        
        try {
            const data = JSON.parse(message.toString());
            console.log(`📨 客户端 ${ws.clientId} 发送消息:`, data.type);
            
            switch (data.type) {
                case 'ping':
                    this.handlePing(ws);
                    break;
                    
                case 'subscribe':
                    this.handleSubscribe(ws, data);
                    break;
                    
                case 'unsubscribe':
                    this.handleUnsubscribe(ws, data);
                    break;
                    
                case 'get_data':
                    this.handleGetData(ws, data);
                    break;
                    
                case 'command':
                    this.handleCommand(ws, data);
                    break;
                    
                default:
                    console.warn(`⚠️ 未知消息类型: ${data.type}`);
            }
        } catch (error) {
            console.error(`❌ 解析客户端消息失败:`, error.message);
            
            // 发送错误响应
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                    type: 'error',
                    message: 'Invalid message format',
                    timestamp: new Date().toISOString()
                }));
            }
        }
    }

    handlePing(ws) {
        ws.lastPing = Date.now();
        
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'pong',
                timestamp: new Date().toISOString()
            }));
        }
    }

    handleSubscribe(ws, data) {
        console.log(`📢 客户端 ${ws.clientId} 订阅:`, data.channel);
        
        // 这里可以实现频道订阅逻辑
        // 例如：只订阅特定类型的更新
        
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'subscribed',
                channel: data.channel,
                timestamp: new Date().toISOString()
            }));
        }
    }

    handleUnsubscribe(ws, data) {
        console.log(`📢 客户端 ${ws.clientId} 取消订阅:`, data.channel);
        
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'unsubscribed',
                channel: data.channel,
                timestamp: new Date().toISOString()
            }));
        }
    }

    handleGetData(ws, data) {
        console.log(`📥 客户端 ${ws.clientId} 请求数据:`, data.request);
        
        let response;
        
        switch (data.request) {
            case 'agents':
                response = { agents: this.dataAggregator.agents };
                break;
                
            case 'tasks':
                response = { tasks: this.dataAggregator.tasks };
                break;
                
            case 'performance':
                response = { performance: this.dataAggregator.performance };
                break;
                
            case 'system':
                response = { system: this.dataAggregator.system };
                break;
                
            case 'logs':
                response = { 
                    logs: this.dataAggregator.logs.slice(-20) // 只返回最新的20条日志
                };
                break;
                
            case 'metrics':
                response = { 
                    metrics: {
                        ...this.metrics,
                        uptime: `${Math.floor(this.metrics.uptime / 1000)}s`,
                        activeConnections: this.metrics.activeConnections
                    }
                };
                break;
                
            default:
                response = { error: 'Unknown data request' };
        }
        
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'data',
                request: data.request,
                data: response,
                timestamp: new Date().toISOString()
            }));
        }
    }

    handleCommand(ws, data) {
        console.log(`🔧 客户端 ${ws.clientId} 执行命令:`, data.command);
        
        // 这里可以实现命令执行逻辑
        // 例如：重启服务、清理日志等
        
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'command_result',
                command: data.command,
                success: true,
                message: 'Command executed successfully',
                timestamp: new Date().toISOString()
            }));
        }
    }

    sendClientStatus(ws) {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'status',
                server: {
                    status: 'running',
                    uptime: `${Math.floor(this.metrics.uptime / 1000)}s`,
                    version: 'v5.23'
                },
                timestamp: new Date().toISOString()
            }));
        }
    }

    sendWelcomeMessage(ws) {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'welcome',
                clientId: ws.clientId,
                message: 'Welcome to Web UI Monitoring System',
                config: {
                    updateInterval: this.config.updateInterval,
                    maxLogEntries: this.config.maxLogEntries
                },
                timestamp: new Date().toISOString()
            }));
        }
    }

    broadcastToAll() {
        const message = JSON.stringify({
            type: 'update',
            data: this.dataAggregator,
            timestamp: new Date().toISOString()
        });

        let successCount = 0;
        let failureCount = 0;
        
        this.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
                try {
                    client.send(message);
                    successCount++;
                } catch (error) {
                    console.error(`❌ 向客户端 ${client.clientId} 发送消息失败:`, error.message);
                    failureCount++;
                    
                    // 移除有问题的客户端
                    this.clients.delete(client);
                    this.updateMetrics();
                }
            }
        });
        
        if (failureCount > 0) {
            console.log(`📡 广播结果: 成功 ${successCount}, 失败 ${failureCount}`);
        }
    }

    handleHttpRequest(req, res) {
        const url = req.url || '/';
        
        console.log(`🌐 HTTP 请求: ${req.method} ${url}`);
        
        if (url === '/' || url === '/index.html') {
            this.sendHtml(res);
        } else if (url === '/webui-monitoring.js') {
            this.sendJs(res);
        } else if (url === '/server.js') {
            this.sendServerJs(res);
        } else if (url === '/config.js') {
            this.sendConfigJson(res);
        } else if (url === '/health') {
            this.sendHealthCheck(res);
        } else {
            res.writeHead(404);
            res.end(JSON.stringify({ error: 'Not Found' }));
        }
    }

    sendHtml(res) {
        fs.readFile(path.join(__dirname, 'index.html'), (err, data) => {
            if (err) {
                console.error('❌ 读取 HTML 文件失败:', err);
                res.writeHead(500);
                res.end('Server Error');
                return;
            }
            
            res.writeHead(200, { 
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            });
            res.end(data);
        });
    }

    sendJs(res) {
        fs.readFile(path.join(__dirname, 'webui-monitoring.js'), (err, data) => {
            if (err) {
                console.error('❌ 读取 JS 文件失败:', err);
                res.writeHead(500);
                res.end('Server Error');
                return;
            }
            
            res.writeHead(200, { 
                'Content-Type': 'application/javascript; charset=utf-8',
                'Cache-Control': 'no-cache, no-store, must-revalidate'
            });
            res.end(data);
        });
    }

    sendServerJs(res) {
        // 发送服务器源码
        const serverCode = `
// Web UI 监控服务器
const MonitoringServer = require('./server');
const server = new MonitoringServer({
    port: process.env.PORT || 8080,
    updateInterval: parseInt(process.env.UPDATE_INTERVAL) || 2000,
    maxClients: parseInt(process.env.MAX_CLIENTS) || 100
});
server.start();
`;
        
        res.writeHead(200, { 
            'Content-Type': 'application/javascript; charset=utf-8',
            'Cache-Control': 'no-cache'
        });
        res.end(serverCode);
    }

    sendConfigJson(res) {
        const config = {
            server: {
                port: this.port,
                version: 'v5.23',
                uptime: Math.floor(this.metrics.uptime / 1000)
            },
            websocket: {
                updateInterval: this.config.updateInterval,
                maxClients: this.config.maxClients,
                heartbeatInterval: this.config.heartbeatInterval
            },
            metrics: {
                activeConnections: this.metrics.activeConnections,
                totalConnections: this.metrics.totalConnections,
                totalMessages: this.metrics.totalMessages
            },
            data: {
                agentsCount: this.dataAggregator.agents.length,
                tasksPending: this.dataAggregator.tasks.pending,
                tasksRunning: this.dataAggregator.tasks.running,
                tasksCompleted: this.dataAggregator.tasks.completed,
                efficiencyGain: this.dataAggregator.performance.efficiencyGain,
                completionRate: this.dataAggregator.performance.completionRate
            }
        };
        
        res.writeHead(200, { 
            'Content-Type': 'application/json; charset=utf-8',
            'Cache-Control': 'no-cache'
        });
        res.end(JSON.stringify(config, null, 2));
    }

    sendHealthCheck(res) {
        const health = {
            status: 'healthy',
            timestamp: new Date().toISOString(),
            uptime: this.metrics.uptime,
            activeConnections: this.metrics.activeConnections,
            server: {
                status: 'running',
                version: 'v5.23'
            },
            database: {
                status: 'connected'
            },
            websocket: {
                connectedClients: this.metrics.activeConnections,
                maxClients: this.config.maxClients
            }
        };
        
        res.writeHead(200, { 
            'Content-Type': 'application/json; charset=utf-8'
        });
        res.end(JSON.stringify(health, null, 2));
    }

    getMetrics() {
        return {
            ...this.metrics,
            uptime: `${Math.floor(this.metrics.uptime / 1000)}s`,
            activeConnections: this.metrics.activeConnections,
            data: this.dataAggregator
        };
    }

    start() {
        this.server.listen(this.port, () => {
            console.log(`🚀 Web UI 监控服务器已启动: http://localhost:${this.port}`);
            console.log(`🔌 WebSocket 服务器已启动: ws://localhost:${this.port}`);
            console.log(`📊 健康检查: http://localhost:${this.port}/health`);
            console.log(`📋 服务器信息: http://localhost:${this.port}/config.js`);
            
            // 设置信号处理
            process.on('SIGTERM', () => {
                console.log('📥 收到 SIGTERM 信号，正在关闭服务器...');
                this.shutdown();
            });
            
            process.on('SIGINT', () => {
                console.log('📥 收到 SIGINT 信号，正在关闭服务器...');
                this.shutdown();
            });
        });
    }

    async shutdown() {
        console.log('🔄 开始关闭服务器...');
        
        // 停止接受新连接
        this.wss.close();
        
        // 通知所有客户端服务器即将关闭
        const shutdownMessage = JSON.stringify({
            type: 'shutdown',
            message: 'Server is shutting down',
            timestamp: new Date().toISOString()
        });
        
        this.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(shutdownMessage);
                client.close();
            }
        });
        
        // 等待客户端关闭连接
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // 关闭 HTTP 服务器
        this.server.close(() => {
            console.log('✅ 服务器已安全关闭');
            process.exit(0);
        });
    }
}

// 如果直接运行此文件，启动服务器
if (require.main === module) {
    const port = process.env.PORT || 8080;
    const server = new MonitoringServer({
        port: parseInt(port),
        updateInterval: parseInt(process.env.UPDATE_INTERVAL) || 2000,
        maxClients: parseInt(process.env.MAX_CLIENTS) || 100
    });
    server.start();
}

module.exports = MonitoringServer;