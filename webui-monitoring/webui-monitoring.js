class MonitoringUI {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.updateInterval = 2000;
        this.efficiencyData = [];
        this.init();
    }

    init() {
        this.setupWebSocket();
        this.setupEventListeners();
        this.startAutoRefresh();
        this.initializeEfficiencyChart();
    }

    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}`;
        
        console.log('尝试连接 WebSocket:', wsUrl);
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('✅ WebSocket 连接已建立');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.updateConnectionStatus('connected');
            this.updateSystemStatus('connected');
        };
        
        this.ws.onmessage = (event) => {
            this.handleMessage(event.data);
        };
        
        this.ws.onclose = (event) => {
            console.log('🔌 WebSocket 连接已关闭:', event.code, event.reason);
            this.isConnected = false;
            this.updateConnectionStatus('disconnected');
            this.updateSystemStatus('disconnected');
            this.handleReconnection();
        };
        
        this.ws.onerror = (error) => {
            console.error('❌ WebSocket 错误:', error);
            this.isConnected = false;
            this.updateConnectionStatus('error');
            this.updateSystemStatus('error');
        };
    }

    handleMessage(data) {
        try {
            const message = JSON.parse(data);
            console.log('📨 收到消息:', message.type);
            
            switch (message.type) {
                case 'update':
                    this.updateDashboard(message.data);
                    this.updateEfficiencyChart(message.data);
                    break;
                case 'status':
                    this.updateSystemStatus(message.status);
                    break;
                case 'log':
                    this.addLogEntry(message.data);
                    break;
                default:
                    console.warn('⚠️ 未知消息类型:', message.type);
            }
        } catch (error) {
            console.error('❌ 解析消息失败:', error);
        }
    }

    updateDashboard(data) {
        // 更新 Agent 状态
        this.updateAgentStatus(data.agents || []);
        
        // 更新任务队列
        this.updateTaskQueue(data.tasks || {});
        
        // 更新性能指标
        this.updatePerformanceMetrics(data.performance || {});
        
        // 更新日志流
        if (data.logs && Array.isArray(data.logs)) {
            this.updateLogStream(data.logs);
        }
    }

    updateAgentStatus(agents) {
        const container = document.getElementById('agent-status');
        if (!container) return;
        
        if (agents.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 20px; color: #666;">
                    <div class="loading"></div>
                    <p>暂无 Agent 数据</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = agents.map(agent => {
            const statusClass = this.getStatusClass(agent.status);
            const statusText = this.getStatusText(agent.status);
            const avatar = this.getAgentAvatar(agent.name);
            
            return `
                <div class="agent-item">
                    <div class="agent-info">
                        <span class="status-indicator ${statusClass}"></span>
                        <strong>${avatar} ${agent.name}</strong>
                    </div>
                    <div class="agent-stats">
                        <span>状态: ${statusText}</span>
                        <span>任务: ${agent.tasks || 0}</span>
                        <span>ID: ${agent.id}</span>
                    </div>
                </div>
            `;
        }).join('');
    }

    updateTaskQueue(tasks) {
        const pendingTasks = tasks.pending || 0;
        const runningTasks = tasks.running || 0;
        const completedTasks = tasks.completed || 0;
        
        // 添加动画效果
        this.animateValue('pending-tasks', pendingTasks);
        this.animateValue('running-tasks', runningTasks);
        this.animateValue('completed-tasks', completedTasks);
    }

    updatePerformanceMetrics(metrics) {
        const efficiencyGain = metrics.efficiencyGain || '0%';
        const completionRate = metrics.completionRate || '0%';
        const utilizationRate = metrics.utilizationRate || '0%';
        
        // 添加动画效果
        this.animateValue('efficiency-gain', efficiencyGain, '%');
        this.animateValue('completion-rate', completionRate, '%');
        this.animateValue('utilization-rate', utilizationRate, '%');
    }

    updateLogStream(logs) {
        const container = document.getElementById('log-content');
        if (!container) return;
        
        // 只显示最新的 50 条日志
        const recentLogs = logs.slice(-50);
        
        const logHtml = recentLogs.map(log => `
            <div class="log-entry ${log.type.toLowerCase()}">
                <span class="log-time">${log.timestamp}</span>
                <span class="log-agent">${log.agent}</span>
                <span class="log-type">${log.type}</span>
                <span class="log-message">${log.message}</span>
            </div>
        `).join('');
        
        // 使用虚拟滚动优化性能
        if (recentLogs.length > 20) {
            const logsToShow = recentLogs.slice(-20);
            container.innerHTML = logsToShow.map(log => `
                <div class="log-entry ${log.type.toLowerCase()}">
                    <span class="log-time">${log.timestamp}</span>
                    <span class="log-agent">${log.agent}</span>
                    <span class="log-type">${log.type}</span>
                    <span class="log-message">${log.message}</span>
                </div>
            `).join('');
        } else {
            container.innerHTML = logHtml;
        }
        
        // 自动滚动到底部
        container.scrollTop = container.scrollHeight;
    }

    addLogEntry(log) {
        const container = document.getElementById('log-content');
        if (!container) return;
        
        // 限制日志数量
        const logEntries = container.querySelectorAll('.log-entry');
        if (logEntries.length > 50) {
            container.removeChild(logEntries[0]);
        }
        
        const logElement = document.createElement('div');
        logElement.className = `log-entry ${log.type.toLowerCase()}`;
        logElement.innerHTML = `
            <span class="log-time">${log.timestamp}</span>
            <span class="log-agent">${log.agent}</span>
            <span class="log-type">${log.type}</span>
            <span class="log-message">${log.message}</span>
        `;
        
        container.appendChild(logElement);
        container.scrollTop = container.scrollHeight;
    }

    updateSystemStatus(status) {
        const indicator = document.getElementById('system-status');
        const text = document.getElementById('system-status-text');
        
        switch (status) {
            case 'connected':
                indicator.className = 'status-indicator status-running';
                text.textContent = '系统正常';
                break;
            case 'disconnected':
                indicator.className = 'status-indicator status-idle';
                text.textContent = '连接断开';
                break;
            case 'error':
                indicator.className = 'status-indicator status-error';
                text.textContent = '连接错误';
                break;
            case 'maintenance':
                indicator.className = 'status-indicator status-idle';
                text.textContent = '维护模式';
                break;
            default:
                indicator.className = 'status-indicator status-idle';
                text.textContent = '系统状态未知';
        }
    }

    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        const indicator = document.getElementById('connection-indicator');
        const text = document.getElementById('connection-text');
        
        // 更新连接状态指示器
        statusElement.className = `connection-status ${status}`;
        
        switch (status) {
            case 'connected':
                indicator.className = 'status-indicator status-running';
                text.textContent = '已连接';
                break;
            case 'disconnected':
                indicator.className = 'status-indicator status-error';
                text.textContent = '连接断开';
                break;
            case 'reconnecting':
                indicator.className = 'status-indicator status-idle';
                text.textContent = '重新连接中...';
                break;
            case 'error':
                indicator.className = 'status-indicator status-error';
                text.textContent = '连接错误';
                break;
        }
        
        // 显示/隐藏离线警告
        const offlineWarning = document.getElementById('offline-warning');
        if (status === 'disconnected') {
            offlineWarning.style.display = 'block';
            offlineWarning.className = 'offline-banner reconnecting';
            offlineWarning.innerHTML = '<span>🔄 连接已断开，正在尝试重新连接...</span>';
        } else {
            offlineWarning.style.display = 'none';
        }
    }

    handleReconnection() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log('🔴 达到最大重连次数，停止重连');
            this.updateConnectionStatus('error');
            return;
        }
        
        this.reconnectAttempts++;
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000); // 指数退避
        
        console.log(`🔄 ${delay}ms 后尝试重连 (第 ${this.reconnectAttempts} 次)`);
        this.updateConnectionStatus('reconnecting');
        
        setTimeout(() => {
            console.log('🔌 尝试重新连接 WebSocket');
            this.setupWebSocket();
        }, delay);
    }

    setupEventListeners() {
        // 清空日志按钮
        const clearLogsBtn = document.getElementById('clear-logs');
        if (clearLogsBtn) {
            clearLogsBtn.addEventListener('click', () => {
                const logContent = document.getElementById('log-content');
                if (logContent) {
                    logContent.innerHTML = '<div style="text-align: center; padding: 50px; color: #95a5a6;"><p>日志已清空</p></div>';
                }
            });
        }

        // 窗口大小改变时重新计算布局
        window.addEventListener('resize', () => {
            this.handleResize();
        });

        // 页面可见性变化处理
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                console.log('📱 页面隐藏，暂停实时更新');
            } else {
                console.log('📱 页面可见，恢复实时更新');
            }
        });
    }

    handleResize() {
        const width = window.innerWidth;
        const dashboard = document.querySelector('.dashboard');
        
        if (width < 768) {
            // 移动端布局
            dashboard.style.gridTemplateColumns = '1fr';
            dashboard.classList.add('mobile-layout');
        } else {
            // 桌面端布局
            dashboard.style.gridTemplateColumns = 'repeat(auto-fit, minmax(350px, 1fr))';
            dashboard.classList.remove('mobile-layout');
        }
    }

    animateValue(elementId, value, suffix = '') {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const isPercentage = value.includes('%');
        const numericValue = parseFloat(value);
        
        if (!isNaN(numericValue)) {
            const duration = 1000; // 动画持续时间
            const start = parseFloat(element.textContent) || 0;
            const increment = (numericValue - start) / (duration / 16); // 60fps
            
            let current = start;
            const timer = setInterval(() => {
                current += increment;
                if ((increment > 0 && current >= numericValue) || (increment < 0 && current <= numericValue)) {
                    current = numericValue;
                    clearInterval(timer);
                }
                
                if (isPercentage) {
                    element.textContent = `${Math.round(current)}${suffix}`;
                } else {
                    element.textContent = Math.round(current) + suffix;
                }
            }, 16);
        } else {
            element.textContent = value + suffix;
        }
    }

    initializeEfficiencyChart() {
        const chartContainer = document.getElementById('efficiency-chart');
        if (!chartContainer) return;
        
        // 初始化空的数据点
        this.efficiencyData = Array(10).fill(0);
        
        // 创建初始的图表条
        chartContainer.innerHTML = this.efficiencyData.map((value, index) => `
            <div class="chart-bar" style="height: ${value}%">
                <span class="chart-value">${value}%</span>
                <span class="chart-label">T-${9 - index}</span>
            </div>
        `).join('');
    }

    updateEfficiencyChart(data) {
        const efficiencyGain = data.performance?.efficiencyGain || '0%';
        const efficiencyValue = parseInt(efficiencyGain) || 0;
        
        // 更新数据数组
        this.efficiencyData.shift();
        this.efficiencyData.push(efficiencyValue);
        
        // 更新图表
        const chartContainer = document.getElementById('efficiency-chart');
        if (!chartContainer) return;
        
        chartContainer.innerHTML = this.efficiencyData.map((value, index) => {
            const height = Math.min(value, 100); // 限制最大高度
            return `
                <div class="chart-bar" style="height: ${height}%">
                    <span class="chart-value">${value}%</span>
                    <span class="chart-label">T-${9 - index}</span>
                </div>
            `;
        }).join('');
    }

    getStatusClass(status) {
        const statusMap = {
            'running': 'status-running',
            'idle': 'status-idle',
            'error': 'status-error',
            'blocked': 'status-error',
            'waiting_approval': 'status-idle'
        };
        return statusMap[status] || 'status-idle';
    }

    getStatusText(status) {
        const statusMap = {
            'running': '运行中',
            'idle': '待命',
            'error': '错误',
            'blocked': '阻塞',
            'waiting_approval': '待审批'
        };
        return statusMap[status] || status;
    }

    getAgentAvatar(name) {
        const avatarMap = {
            '技术专家小新': '💻',
            '日志专家小蓝': '📋',
            '设计专家': '🎨',
            '大领导': '🎯'
        };
        
        // 如果有匹配的返回，否则返回默认
        for (const [key, avatar] of Object.entries(avatarMap)) {
            if (name.includes(key)) {
                return avatar;
            }
        }
        
        return '🤖';
    }

    startAutoRefresh() {
        // 每分钟检查一次连接状态
        setInterval(() => {
            if (!this.isConnected) {
                console.log('🔄 定时检查连接状态...');
                this.handleReconnection();
            }
        }, 60000);
    }

    // 模拟数据生成器（用于演示）
    generateMockData() {
        return {
            agents: [
                { id: 'agent-1', name: '技术专家小新', status: 'running', tasks: Math.floor(Math.random() * 5) },
                { id: 'agent-2', name: '日志专家小蓝', status: 'idle', tasks: Math.floor(Math.random() * 3) },
                { id: 'agent-3', name: '设计专家', status: 'running', tasks: Math.floor(Math.random() * 4) }
            ],
            tasks: {
                pending: Math.floor(Math.random() * 10),
                running: Math.floor(Math.random() * 5),
                completed: 12 + Math.floor(Math.random() * 10)
            },
            performance: {
                efficiencyGain: `${(300 + Math.random() * 200).toFixed(0)}%`,
                completionRate: `${(80 + Math.random() * 15).toFixed(0)}%`,
                utilizationRate: `${(70 + Math.random() * 25).toFixed(0)}%`
            },
            logs: []
        };
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    const ui = new MonitoringUI();
    
    // 开发模式下生成模拟数据
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log('🔧 开发模式：启用模拟数据');
        
        // 定期生成模拟数据（如果没有WebSocket连接）
        setInterval(() => {
            if (!ui.isConnected) {
                const mockData = ui.generateMockData();
                
                // 添加模拟日志
                const logTypes = ['INFO', 'WARN', 'ERROR'];
                const agents = mockData.agents;
                const randomAgent = agents[Math.floor(Math.random() * agents.length)];
                const randomType = logTypes[Math.floor(Math.random() * logTypes.length)];
                const timestamp = new Date().toLocaleTimeString();
                
                mockData.logs.push({
                    timestamp,
                    agent: randomAgent.name,
                    type: randomType,
                    message: `${randomType}: ${randomAgent.name} 执行任务完成`
                });
                
                ui.updateDashboard(mockData);
            }
        }, 3000);
    }
});

// 添加错误处理
window.addEventListener('error', (event) => {
    console.error('🔴 页面错误:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('🔴 未处理的 Promise 拒绝:', event.reason);
});