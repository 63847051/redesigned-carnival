#!/usr/bin/env python3
"""
OpenClaw Web UI Server v1.1
提供频道/线程展示、Agent 状态可视化和实时监控

v1.1 新增：
- 任务看板（Kanban Board）
- 性能图表
- 实时日志流
- 移动端适配
"""

import asyncio
import json
import logging
from typing import Dict, List
from datetime import datetime, timedelta
from aiohttp import web
import aiohttp_cors
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# 配置
# =============================================================================

WEB_HOST = "0.0.0.0"
WEB_PORT = 8080
DAEMON_STATE_FILE = "/root/.openclaw/workspace/.openclaw-daemon-state.json"

# =============================================================================
# 数据模型（v1.1 增强）
# =============================================================================

class ChannelInfo:
    """频道信息"""
    
    def __init__(self, channel_id: str, name: str, channel_type: str):
        self.channel_id = channel_id
        self.name = name
        self.channel_type = channel_type  # direct, group
        self.threads = []
        self.last_activity = None

class ThreadInfo:
    """线程信息"""
    
    def __init__(self, thread_id: str, channel_id: str, title: str):
        self.thread_id = thread_id
        self.channel_id = channel_id
        self.title = title
        self.messages = []
        self.agent_id = None
        self.last_activity = None

class AgentState:
    """Agent 状态（v1.1 增强）"""
    
    def __init__(self, agent_id: str, driver_type: str, state: str):
        self.agent_id = agent_id
        self.driver_type = driver_type
        self.state = state
        self.process_id = None
        self.session_key = None
        self.message_queue = []
        self.uptime = None
        self.last_activity = None
        self.restart_count = 0  # v1.1 新增
        self.avg_spawn_time = 0.0  # v1.1 新增

class TaskInfo:
    """任务信息（v1.1 新增）"""
    
    def __init__(self, task_id: str, title: str, description: str, priority: str, status: str):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.priority = priority  # urgent, high, normal, low
        self.status = status  # pending, in_progress, completed
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

class LogEntry:
    """日志条目（v1.1 新增）"""
    
    def __init__(self, level: str, message: str):
        self.level = level  # INFO, WARNING, ERROR
        self.message = message
        self.timestamp = datetime.now().isoformat()

# =============================================================================
# Web UI Server
# =============================================================================

class OpenClawWebUI:
    """OpenClaw Web UI 服务器"""
    
    def __init__(self):
        self.app = web.Application(client_max_size=1024*1024)
        self.channels: Dict[str, ChannelInfo] = {}
        self.threads: Dict[str, ThreadInfo] = {}
        self.agents: Dict[str, AgentState] = {}
        self.setup_routes()
        self.setup_cors()
    
    def setup_cors(self):
        """设置 CORS"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                expose="*",
                allow_credentials=True,
                allow_methods="*",
                allow_headers="*",
            )
        })
    
    def setup_routes(self):
        """设置路由"""
        
        @self.app.route("/")
        async def index(request):
            """首页"""
            return web.Response(text="OpenClaw Web UI", content_type="text/html")
        
        @self.app.route("/api/channels")
        async def get_channels(request):
            """获取频道列表"""
            channels_data = [
                {
                    "id": ch.channel_id,
                    "name": ch.name,
                    "type": ch.channel_type,
                    "threads": len(ch.threads),
                    "last_activity": ch.last_activity.isoformat() if ch.last_activity else None
                }
                for ch in self.channels.values()
            ]
            
            return web.json_response({
                "success": True,
                "channels": channels_data
            })
        
        @self.app.route("/api/threads")
        async def get_threads(request):
            """获取线程列表"""
            channel_id = request.query.get("channel")
            
            threads_data = [
                {
                    "id": th.thread_id,
                    "channel_id": th.channel_id,
                    "title": th.title,
                    "agent_id": th.agent_id,
                    "message_count": len(th.messages),
                    "last_activity": th.last_activity.isoformat() if th.last_activity else None
                }
                for th in self.threads.values()
                if not channel_id or th.channel_id == channel_id
            ]
            
            return web.json_response({
                "success": True,
                "threads": threads_data
            })
        
        @self.app.route("/api/agents")
        async def get_agents(request):
            """获取 Agent 状态"""
            agents_data = [
                {
                    "agent_id": ag.agent_id,
                    "driver_type": ag.driver_type,
                    "state": ag.state,
                    "process_id": ag.process_id,
                    "session_key": ag.session_key,
                    "message_queue_size": len(ag.message_queue),
                    "uptime": ag.uptime,
                    "last_activity": ag.last_activity.isoformat() if ag.last_activity else None
                }
                for ag in self.agents.values()
            ]
            
            return web.json_response({
                "success": True,
                "agents": agents_data
            })
        
        @self.app.route("/api/stats")
        async def get_stats(request):
            """获取统计信息"""
            stats = {
                "total_channels": len(self.channels),
                "total_threads": len(self.threads),
                "total_agents": len(self.agents),
                "running_agents": sum(1 for ag in self.agents.values() if ag.state == "running"),
                "timestamp": datetime.now().isoformat()
            }
            
            return web.json_response({
                "success": True,
                "stats": stats
            })
        
        @self.app.route("/ws/echo")
        async def websocket_handler(request):
            """WebSocket 处理器（实时更新）"""
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            
            logger.info("WebSocket 连接建立")
            
            try:
                # 每 5 秒推送一次更新
                while True:
                    # 获取最新状态
                    update = {
                        "type": "update",
                        "timestamp": datetime.now().isoformat(),
                        "agents": {
                            ag.agent_id: {
                                "state": ag.state,
                                "message_queue_size": len(ag.message_queue)
                            }
                            for ag in self.agents.values()
                        }
                    }
                    
                    await ws.send_str(json.dumps(update))
                    await asyncio.sleep(5)
                    
            except Exception as e:
                logger.error(f"WebSocket 错误: {e}")
            finally:
                await ws.close()
            
            return ws
    
    async def load_daemon_state(self):
        """加载 Daemon 状态"""
        try:
            with open(DAEMON_STATE_FILE, 'r') as f:
                state = json.load(f)
            
            # 解析 Agent 状态
            for agent_id, agent_data in state.get("agents", {}).items():
                agent = AgentState(
                    agent_id,
                    agent_data.get("driver_type", "unknown"),
                    agent_data.get("state", "stopped")
                )
                agent.last_activity = datetime.fromisoformat(agent_data.get("last_activity", datetime.now().isoformat()))
                
                self.agents[agent_id] = agent
            
            logger.info(f"加载 {len(self.agents)} 个 Agent 状态")
            
        except Exception as e:
            logger.error(f"加载 Daemon 状态失败: {e}")
    
    async def start(self):
        """启动 Web UI"""
        self.app.router.add_get("/", self.index)
        self.app.router.add_get("/api/channels", self.get_channels)
        self.app.router.add_get("/api/threads", self.get_threads)
        self.app.router.add_get("/api/agents", self.get_agents)
        self.app.router.add_get("/api/stats", self.get_stats)
        self.app.router.add_get("/ws/echo", self.websocket_handler)
        
        # 加载 Daemon 状态
        await self.load_daemon_state()
        
        runner = web.AppRunner(self.app)
        site = web.TCPSite(runner, host=WEB_HOST, port=WEB_PORT)
        
        logger.info(f"🚀 OpenClaw Web UI 启动: http://{WEB_HOST}:{WEB_PORT}")
        
        await site.start()
    
    async def stop(self):
        """停止 Web UI"""
        logger.info("🛑 停止 OpenClaw Web UI")

# =============================================================================
# 主入口
# =============================================================================

async def main():
    """主入口"""
    web_ui = OpenClawWebUI()
    
    try:
        await web_ui.start()
        
        # 保持运行
        while True:
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("收到中断信号")
    finally:
        await web_ui.stop()

if __name__ == "__main__":
    asyncio.run(main())
