#!/usr/bin/env python3
"""
OpenClaw Slock Server - 持久化存储和 WebSocket 服务
基于 Slock 设计的完整实现
"""

import asyncio
import json
import logging
import sqlite3
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import web
import aiohttp_cors
from aiohttp import web

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# 配置
# =============================================================================

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 9000
DB_FILE = "/root/.openclaw/workspace/slock-server/slock.db"

# =============================================================================
# 数据库初始化
# =============================================================================

class SlockDatabase:
    """Slock 数据库"""
    
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.conn = None
        self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        # 创建目录
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        
        # 连接数据库
        self.conn = sqlite3.connect(self.db_file)
        
        # 创建表
        self.create_tables()
        
        logger.info(f"数据库已初始化: {self.db_file}")
    
    def create_tables(self):
        """创建表"""
        cursor = self.conn.cursor()
        
        # 消息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_key TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX(session_key),
                INDEX(timestamp)
            )
        """)
        
        # 任务表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                session_key TEXT NOT NULL,
                title TEXT,
                description TEXT,
                status TEXT DEFAULT 'pending',
                skills TEXT,
                priority TEXT DEFAULT 'normal',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX(session_key),
                INDEX(status)
            )
        """)
        
        # 会话表
        cursor.execute("""
            CREATE TABLE IFN NOT EXISTS sessions (
                session_key TEXT PRIMARY KEY,
                agent_id TEXT,
                state TEXT DEFAULT 'cold_start',
                driver_type TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 频道表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                channel_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 线程表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threads (
                thread_id TEXT PRIMARY KEY,
                channel_id TEXT NOT NULL,
                title TEXT,
                agent_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX(channel_id)
            )
        """)
        
        self.conn.commit()
        logger.info("数据库表已创建")
    
    def add_message(self, session_key: str, role: str, content: str):
        """添加消息"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO messages (session_key, role, content) VALUES (?, ?, ?)",
            (session_key, role, content)
        )
        self.conn.commit()
        
        logger.debug(f"消息已添加: {session_key}")
    
    def get_messages(self, session_key: str, limit: int = 10) -> List[Dict]:
        """获取消息"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT role, content, timestamp FROM messages WHERE session_key = ? ORDER BY timestamp DESC LIMIT ?",
            (session_key, limit)
        )
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "role": row[0],
                "content": row[1],
                "timestamp": row[2]
            })
        
        return messages
    
    def create_task(self, task_id: str, session_key: str, title: str, description: str, skills: List[str], priority: str):
        """创建任务"""
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO tasks (task_id, session_key, title, description, skills, priority)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (task_id, session_key, title, description, json.dumps(skills), priority)
        )
        self.conn.commit()
        
        logger.info(f"任务已创建: {task_id}")
    
    def claim_task(self, task_id: str, agent_id: str):
        """认领任务"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE tasks SET status = 'claimed', agent_id = ?, updated_at = CURRENT_TIMESTAMP WHERE task_id = ?",
            (agent_id, task_id)
        )
        self.conn.commit()
        
        logger.info(f"任务已认领: {task_id} by {agent_id}")
    
    def get_pending_tasks(self, skills: List[str] = None, limit: int = 10) -> List[Dict]:
        """获取待处理任务"""
        query = "SELECT * FROM tasks WHERE status = 'pending'"
        params = []
        
        if skills:
            query += " AND skills LIKE ?"
            params.append(f"%{skills[0]}%")
        
        query += " ORDER BY priority DESC, created_at ASC LIMIT ?"
        params.append(limit)
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                "id": row[0],
                "task_id": row[1],
                "session_key": row[2],
                "title": row[3],
                "description": row[4],
                "status": row[5],
                "skills": json.loads(row[6]) if row[6] else [],
                "priority": row[7],
                "created_at": row[8],
                "updated_at": row[9]
            })
        
        return tasks
    
    def update_session_state(self, session_key: str, state: str):
        """更新会话状态"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO sessions (session_key, state, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (session_key, state)
        )
        self.conn.commit()
        
        logger.debug(f"会话状态已更新: {session_key} -> {state}")
    
    def get_all_sessions(self) -> List[Dict]:
        """获取所有会话"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sessions ORDER BY updated_at DESC")
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                "session_key": row[0],
                "agent_id": row[1],
                "state": row[2],
                "driver_type": row[3],
                "created_at": row[4],
                "updated_at": row[5]
            })
        
        return sessions

# =============================================================================
# Slock Server
# =============================================================================

class SlockServer:
    """Slock Server 核心类"""
    
    def __init__(self):
        self.app = web.Application(client_max_size=1024*1024)
        self.db = SlockDatabase(DB_FILE)
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
        
        @self.app.route("/api/messages")
        async def add_message(request):
            """添加消息"""
            try:
                data = await request.json()
                
                self.db.add_message(
                    data["session_key"],
                    data["role"],
                    data["content"]
                )
                
                return web.json_response({
                    "success": True,
                    "message": "消息已添加"
                })
                
            except Exception as e:
                logger.error(f"添加消息失败: {e}")
                return web.json_response({
                    "success": False,
                    "error": str(e)
                })
        
        @self.app.route("/api/messages/{session_key}")
        async def get_messages(request):
            """获取消息"""
            try:
                session_key = request.match_info['session_key']
                limit = int(request.query.get("limit", 10))
                
                messages = self.db.get_messages(session_key, limit)
                
                return web.json_response({
                    "success": True,
                    "messages": messages
                })
                
            except Exception as e:
                logger.error(f"获取消息失败: {e}")
                return web.json_response({
                    "success": False,
                    "error": str(e)
                })
        
        @self.app.route("/api/tasks")
        async def create_task(request):
            """创建任务"""
            try:
                data = await request.json()
                
                self.db.create_task(
                    data["task_id"],
                    data["session_key"],
                    data.get("title", ""),
                    data.get("description", ""),
                    data.get("skills", []),
                    data.get("priority", "normal")
                )
                
                return web.json_response({
                    "success": True,
                    "message": "任务已创建"
                })
                
            except Exception as e:
                logger.error(f"创建任务失败: {e}")
                return web.json_response({
                    "success": False,
                    "error": str(e)
                })
        
        @self.app.route("/api/tasks/claim")
        async def claim_task(request):
            """认领任务"""
            try:
                data = await request.json()
                
                self.db.claim_task(
                    data["task_id"],
                    data["agent_id"]
                )
                
                return web.json_response({
                    "success": True,
                    "message": "任务已认领"
                })
                
            except Exception as e:
                logger.error(f"认领任务失败: {e}")
                return web.json_response({
                    "success": False,
                    "error": str(e)
                })
        
        @self.app.route("/api/tasks/pending")
        async def get_pending_tasks(request):
            """获取待处理任务"""
            try:
                skills = request.query.get("skills", "").split(",") if request.query.get("skills") else None
                limit = int(request.query.get("limit", 10))
                
                tasks = self.db.get_pending_tasks(skills, limit)
                
                return web.json_response({
                    "success": True,
                    "tasks": tasks
                })
                
            except Exception as e:
                logger.error(f"获取任务失败: {e}")
                return web.json_response({
                    "success": False,
                    "error": str(e)
                })
        
        @self.app.route("/api/sessions")
        async def get_sessions(request):
            """获取所有会话"""
            try:
                sessions = self.db.get_all_sessions()
                
                return web.json_response({
                    "success": True,
                    "sessions": sessions
                })
                
            except Exception as e:
                logger.error(f"获取会话失败: {e}")
                return web.json_response({
                    "success": False,
                    "error": str(e)
                })
    
    async def start(self):
        """启动 Slock Server"""
        self.app.router.add_get("/api/messages/{session_key}", self.get_messages)
        self.app.router.add_post("/api/messages", self.add_message)
        self.app.router.add_post("/api/tasks", self.create_task)
        self.app.router.add_post("/api/tasks/claim", self.claim_task)
        self.app.router.add_get("/api/tasks/pending", self.get_pending_tasks)
        self.app.router.add_get("/api/sessions", self.get_sessions)
        
        runner = web.AppRunner(self.app)
        site = web.TCPSite(runner, host=SERVER_HOST, port=SERVER_PORT)
        
        logger.info(f"🚀 Slock Server 启动: http://{SERVER_HOST}:{SERVER_PORT}")
        
        await site.start()
    
    async def stop(self):
        """停止 Slock Server"""
        logger.info("🛑 停止 Slock Server")

# =============================================================================
# 主入口
# =============================================================================

async def main():
    """主入口"""
    server = SlockServer()
    
    try:
        await server.start()
        
        # 保持运行
        while True:
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("收到中断信号")
    finally:
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
