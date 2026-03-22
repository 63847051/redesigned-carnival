# Web UI 可视化监控 - 使用指南

## 📋 目录
- [快速开始](#快速开始)
- [界面说明](#界面说明)
- [功能详解](#功能详解)
- [配置说明](#配置说明)
- [故障排除](#故障排除)
- [API 文档](#api-文档)
- [最佳实践](#最佳实践)

## 🚀 快速开始

### 1. 环境要求
- Node.js >= 16.0.0
- npm >= 8.0.0
- 现代浏览器 (Chrome 80+, Firefox 75+, Safari 13+)

### 2. 启动服务
```bash
cd /root/.openclaw/workspace/webui-monitoring
chmod +x start-monitoring.sh
./start-monitoring.sh
```

### 3. 访问界面
打开浏览器访问: `http://localhost:8080`

## 🖥️ 界面说明

### 1. 系统状态栏
- **位置**: 页面顶部
- **功能**: 显示系统整体运行状态
- **指示器**:
  - 🟢 绿色: 系统正常运行
  - 🟡 黄色: 系统待命状态
  - 🔴 红色: 系统错误状态

### 2. Agent 状态面板
- **位置**: 左上角卡片
- **功能**: 显示所有 Agent 的实时状态
- **信息项**:
  - Agent 名称和头像
  - 运行状态 (运行中/待命/错误)
  - 当前任务数量
  - Agent ID

### 3. 任务队列监控
- **位置**: 左上角第二个卡片
- **功能**: 统计任务执行情况
- **指标**:
  - 待处理任务数量
  - 进行中任务数量
  - 已完成任务数量

### 4. 性能指标
- **位置**: 右上角卡片
- **功能**: 展示系统性能数据
- **指标**:
  - 效率提升百分比
  - 任务完成率
  - 并发利用率

### 5. 效率趋势图
- **位置**: 右上角第二个卡片
- **功能**: 显示效率变化趋势
- **特点**:
  - 实时更新的柱状图
  - 显示最近 10 个时间点
  - 自动缩放和动画效果

### 6. 实时日志流
- **位置**: 底部横跨卡片
- **功能**: 显示 Agent 输出的实时日志
- **特性**:
  - 不同类型日志的颜色区分
  - 自动滚动到最新日志
  - 时间戳和 Agent 信息
  - 支持手动清空日志

## 🔧 功能详解

### 1. 实时数据更新
- **更新频率**: 2秒
- **数据源**: 并行执行系统 (Phase 1)
- **推送方式**: WebSocket 实时推送
- **数据类型**:
  - Agent 状态数据
  - 任务统计数据
  - 性能指标数据
  - 日志流数据

### 2. 连接管理
- **自动重连**: 网络断开后自动重连
- **心跳检测**: 30秒间隔心跳包
- **连接状态**: 实时显示连接状态
- **离线模式**: 支持离线浏览历史数据

### 3. 数据缓存
- **日志缓存**: 最多保留 100 条日志
- **图表缓存**: 保留最近 10 个数据点
- **性能优化**: 虚拟滚动处理大量数据

### 4. 响应式设计
- **桌面端**: 多列网格布局
- **移动端**: 单列堆叠布局
- **断点**: 768px 自动切换
- **适配**: 支持各种屏幕尺寸

## ⚙️ 配置说明

### 1. 环境变量
```bash
# 端口号 (默认: 8080)
export PORT=8081

# 更新间隔 (默认: 2000ms)
export UPDATE_INTERVAL=1000

# 最大客户端数 (默认: 100)
export MAX_CLIENTS=50

# 心跳间隔 (默认: 30000ms)
export HEARTBEAT_INTERVAL=60000
```

### 2. 服务器配置
```javascript
// config.js
module.exports = {
    port: 8080,
    updateInterval: 2000,
    maxLogEntries: 100,
    maxClients: 100,
    heartbeatInterval: 30000,
    enableMockData: true
};
```

### 3. 启动参数
```bash
# 使用默认配置
node server.js

# 指定端口
node server.js --port 8081

# 完整配置
node server.js --port 8081 --updateInterval 1000 --maxClients 50
```

## 🔍 故障排除

### 1. 常见问题

#### 问题 1: 端口被占用
**现象**: 启动失败，提示端口已占用
**解决**:
```bash
# 查看端口占用
lsof -i :8080

# 杀死占用进程
kill -9 <PID>

# 或者使用其他端口
export PORT=8081
./start-monitoring.sh
```

#### 问题 2: WebSocket 连接失败
**现象**: 页面显示连接断开
**解决**:
```bash
# 检查服务器状态
curl http://localhost:8080/health

# 重启服务
./start-monitoring.sh

# 检查防火墙设置
sudo ufw status
```

#### 问题 3: 数据不更新
**现象**: 界面数据长时间不更新
**解决**:
```bash
# 检查浏览器控制台
# 打开开发者工具 (F12) 查看错误信息

# 刷新页面
Ctrl+F5

# 清除浏览器缓存
```

#### 问题 4: 内存使用过高
**现象**: 服务器内存占用过高
**解决**:
```bash
# 检查内存使用
ps aux | grep node

# 重启服务
./start-monitoring.sh

# 调整配置中的 maxLogEntries
```

### 2. 日志查看
```bash
# 查看启动日志
tail -f logs/monitoring-$(date +%Y%m%d).log

# 查看实时日志
./start-monitoring.sh

# 查看系统日志
journalctl -u monitoring.service
```

### 3. 性能监控
```bash
# 查看服务器资源使用
htop

# 查看网络连接
netstat -tulpn | grep :8080

# 查看 WebSocket 连接
curl http://localhost:8080/config.js
```

## 📋 API 文档

### 1. WebSocket 接口

#### 客户端 → 服务器
```javascript
// 心跳包
{
    type: 'ping',
    timestamp: '2026-03-22T10:00:00Z'
}

// 订阅频道
{
    type: 'subscribe',
    channel: 'agent_status'
}

// 请求数据
{
    type: 'get_data',
    request: 'agents'
}

// 执行命令
{
    type: 'command',
    command: 'clear_logs'
}
```

#### 服务器 → 客户端
```javascript
// 连接成功
{
    type: 'welcome',
    clientId: 'client-123456789',
    message: 'Welcome to Web UI Monitoring System',
    timestamp: '2026-03-22T10:00:00Z'
}

// 数据更新
{
    type: 'update',
    data: {
        agents: [...],
        tasks: {...},
        performance: {...},
        logs: [...]
    },
    timestamp: '2026-03-22T10:00:00Z'
}

// 状态通知
{
    type: 'status',
    server: {
        status: 'running',
        uptime: '2h 34m'
    },
    timestamp: '2026-03-22T10:00:00Z'
}
```

### 2. HTTP 接口

#### 健康检查
```
GET /health
```

**响应**:
```json
{
    "status": "healthy",
    "timestamp": "2026-03-22T10:00:00Z",
    "uptime": "86400000",
    "activeConnections": 5,
    "server": {
        "status": "running",
        "version": "v5.23"
    }
}
```

#### 配置信息
```
GET /config.js
```

**响应**:
```json
{
    "server": {
        "port": 8080,
        "version": "v5.23",
        "uptime": "3600s"
    },
    "websocket": {
        "updateInterval": 2000,
        "maxClients": 100
    },
    "metrics": {
        "activeConnections": 5,
        "totalConnections": 10,
        "totalMessages": 1000
    },
    "data": {
        "agentsCount": 4,
        "tasksPending": 5,
        "efficiencyGain": "400%"
    }
}
```

## 🎯 最佳实践

### 1. 部署建议
- **生产环境**: 使用 Nginx 反向代理
- **开发环境**: 直接启动，启用调试模式
- **容器化**: 使用 Docker 容器部署
- **负载均衡**: 多实例部署时使用负载均衡

### 2. 性能优化
- **客户端**: 启用数据压缩，减少带宽使用
- **服务器**: 调整更新频率，避免过于频繁的推送
- **数据库**: 优化数据查询，使用索引
- **缓存**: 使用 Redis 缓存热点数据

### 3. 安全配置
- **认证**: 在生产环境中启用身份验证
- **HTTPS**: 使用 HTTPS 加密通信
- **防火墙**: 只开放必要端口
- **日志**: 定期审计访问日志

### 4. 监控和维护
- **健康检查**: 定期检查系统健康状态
- **日志轮转**: 配置日志轮转，避免磁盘空间不足
- **备份**: 定期备份数据
- **更新**: 定期更新依赖和安全补丁

### 5. 扩展开发
- **自定义插件**: 开发自定义监控插件
- **数据集成**: 集成其他系统的数据
- **界面定制**: 根据需求定制界面
- **API 扩展**: 扩展 API 接口

## 🔗 相关资源
- [Phase 1 实施报告](../parallel-execution-phase1.md)
- [系统架构文档](../../SOUL.md)
- [Agent 团队配置](../../IDENTITY.md)
- [GitHub 仓库](https://github.com/638470151/redesigned-carnival)

---

**文档版本**: v1.0  
**最后更新**: 2026-03-22  
**作者**: 大领导系统团队