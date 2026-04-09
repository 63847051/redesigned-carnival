#!/usr/bin/env python3
"""
OpenClaw MCP Server v2.5 - 高级功能版
从 7 个工具扩展到 13 个工具
添加：broadcast, get_tasks, create_task, update_task, batch_operation, analytics
"""

import asyncio
import json
import logging
import subprocess
import os
import time
from typing import Any, Optional, Dict, List
from mcp.server import Server
from mcp.types import Tool, TextContent
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 MCP Server
app = Server("openclaw-mcp-server")

# =============================================================================
# 错误类型定义（复用 v2.4）
# =============================================================================

class ErrorCode(Enum):
    """错误代码"""
    UNKNOWN = "UNKNOWN"
    TIMEOUT = "TIMEOUT"
    NOT_FOUND = "NOT_FOUND"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    INVALID_INPUT = "INVALID_INPUT"
    RATE_LIMITED = "RATE_LIMITED"
    GATEWAY_ERROR = "GATEWAY_ERROR"
    CACHE_ERROR = "CACHE_ERROR"
    PARSE_ERROR = "PARSE_ERROR"

class OpenClawError(Exception):
    """OpenClaw 错误基类"""
    
    def __init__(self, message: str, code: ErrorCode, details: str = ""):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)

# =============================================================================
# 错误处理器（复用 v2.4）
# =============================================================================

class ErrorHandler:
    """错误处理器"""
    
    def __init__(self):
        self.error_counts = {}
        self.last_errors = {}
    
    def record_error(self, operation: str, error: Exception):
        """记录错误"""
        if operation not in self.error_counts:
            self.error_counts[operation] = 0
        
        self.error_counts[operation] += 1
        self.last_errors[operation] = {
            "error": str(error),
            "time": datetime.now().isoformat(),
            "type": type(error).__name__
        }
        
        logger.error(f"错误记录: {operation} - {error}")
    
    def get_error_report(self) -> str:
        """获取错误报告"""
        report = "## 错误报告\n\n"
        
        if not self.error_counts:
            report += "✅ 无错误记录\n\n"
        else:
            for operation, count in self.error_counts.items():
                last_error = self.last_errors.get(operation, {})
                report += f"### {operation}\n"
                report += f"- 错误次数: {count}\n"
                report += f"- 最后错误: {last_error.get('error', 'N/A')}\n"
                report += f"- 时间: {last_error.get('time', 'N/A')}\n"
                report += f"- 类型: {last_error.get('type', 'N/A')}\n\n"
        
        return report

# 全局错误处理器
error_handler = ErrorHandler()

# =============================================================================
# 性能监控（复用 v2.4）
# =============================================================================

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {}
    
    def record(self, operation: str, duration: float):
        """记录性能指标"""
        if operation not in self.metrics:
            self.metrics[operation] = {
                "count": 0,
                "total_time": 0,
                "avg_time": 0,
                "max_time": 0,
                "min_time": float('inf')
            }
        
        metrics = self.metrics[operation]
        metrics["count"] += 1
        metrics["total_time"] += duration
        metrics["avg_time"] = metrics["total_time"] / metrics["count"]
        metrics["max_time"] = max(metrics["max_time"], duration)
        metrics["min_time"] = min(metrics["min_time"], duration)
    
    def get_report(self) -> str:
        """获取性能报告"""
        report = "## 性能监控报告\n\n"
        
        for operation, metrics in self.metrics.items():
            report += f"### {operation}\n"
            report += f"- 调用次数: {metrics['count']}\n"
            report += f"- 平均时间: {metrics['avg_time']:.3f}s\n"
            report += f"- 最大时间: {metrics['max_time']:.3f}s\n"
            report += f"- 最小时间: {metrics['min_time']:.3f}s\n\n"
        
        return report

# 全局性能监控器
perf_monitor = PerformanceMonitor()

# =============================================================================
# 缓存管理（复用 v2.4）
# =============================================================================

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            
            if time.time() - timestamp < self.ttl:
                logger.debug(f"缓存命中: {key}")
                return data
            else:
                del self.cache[key]
                logger.debug(f"缓存过期: {key}")
        
        return None
    
    def set(self, key: str, value: Any):
        """设置缓存"""
        self.cache[key] = (value, time.time())
        logger.debug(f"缓存设置: {key}")
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        logger.info("缓存已清空")

# 全局缓存管理器
cache_manager = CacheManager(ttl=300)

# =============================================================================
# 任务管理系统（新增）
# =============================================================================

class TaskManager:
    """任务管理器"""
    
    def __init__(self):
        self.tasks = {}
        self.task_counter = 0
    
    def create_task(self, title: str, description: str, skills: List[str], 
                   priority: str = "normal", session_key: str = None) -> str:
        """创建任务"""
        self.task_counter += 1
        task_id = f"task_{self.task_counter}"
        
        task = {
            "task_id": task_id,
            "title": title,
            "description": description,
            "skills": skills,
            "priority": priority,
            "session_key": session_key,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.tasks[task_id] = task
        logger.info(f"任务已创建: {task_id}")
        
        return task_id
    
    def get_tasks(self, status: str = None, priority: str = None, 
                 skills: List[str] = None, limit: int = 10) -> List[Dict]:
        """获取任务列表"""
        tasks = list(self.tasks.values())
        
        # 过滤
        if status:
            tasks = [t for t in tasks if t["status"] == status]
        
        if priority:
            tasks = [t for t in tasks if t["priority"] == priority]
        
        if skills:
            tasks = [t for t in tasks if any(s in t["skills"] for s in skills)]
        
        # 排序（按优先级和时间）
        priority_order = {"urgent": 0, "high": 1, "normal": 2, "low": 3}
        tasks.sort(key=lambda t: (priority_order.get(t["priority"], 2), t["created_at"]))
        
        return tasks[:limit]
    
    def update_task(self, task_id: str, status: str = None, 
                   agent_id: str = None) -> bool:
        """更新任务状态"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        if status:
            task["status"] = status
            task["updated_at"] = datetime.now().isoformat()
            
            if status == "completed":
                task["completed_at"] = datetime.now().isoformat()
        
        if agent_id:
            task["agent_id"] = agent_id
            task["claimed_at"] = datetime.now().isoformat()
        
        logger.info(f"任务已更新: {task_id}")
        return True
    
    def get_stats(self) -> Dict:
        """获取任务统计"""
        total = len(self.tasks)
        pending = sum(1 for t in self.tasks.values() if t["status"] == "pending")
        in_progress = sum(1 for t in self.tasks.values() if t["status"] == "in_progress")
        completed = sum(1 for t in self.tasks.values() if t["status"] == "completed")
        
        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed
        }

# 全局任务管理器
task_manager = TaskManager()

# =============================================================================
# 数据分析系统（新增）
# =============================================================================

class AnalyticsEngine:
    """数据分析引擎"""
    
    def __init__(self):
        self.event_log = []
    
    def log_event(self, event_type: str, data: Dict):
        """记录事件"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.event_log.append(event)
        
        # 只保留最近 1000 条
        if len(self.event_log) > 1000:
            self.event_log = self.event_log[-1000:]
    
    def analyze(self) -> Dict:
        """分析数据"""
        # 事件统计
        event_counts = defaultdict(int)
        for event in self.event_log:
            event_counts[event["type"]] += 1
        
        # 时间分布（最近 24 小时）
        now = datetime.now()
        last_24h = [e for e in self.event_log 
                   if datetime.fromisoformat(e["timestamp"]) > now - timedelta(hours=24)]
        
        hourly_dist = defaultdict(int)
        for event in last_24h:
            hour = datetime.fromisoformat(event["timestamp"]).hour
            hourly_dist[hour] += 1
        
        return {
            "total_events": len(self.event_log),
            "event_counts": dict(event_counts),
            "last_24h": len(last_24h),
            "hourly_distribution": dict(hourly_dist),
            "top_events": sorted(event_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }

# 全局分析引擎
analytics_engine = AnalyticsEngine()

# =============================================================================
# 工具定义
# =============================================================================

TOOLS = [
    # ===== 原有工具（v2.4） =====
    Tool(
        name="list_sessions",
        description="列出所有 OpenClaw 会话",
        inputSchema={
            "type": "object",
            "properties": {
                "activeMinutes": {
                    "type": "integer",
                    "description": "只显示最近 N 分钟活跃的会话",
                    "default": 0
                }
            }
        }
    ),
    Tool(
        name="send_message",
        description="发送消息到指定会话",
        inputSchema={
            "type": "object",
            "properties": {
                "channel": {"type": "string", "description": "渠道标识"},
                "target": {"type": "string", "description": "目标标识"},
                "message": {"type": "string", "description": "消息内容"}
            },
            "required": ["channel", "target", "message"]
        }
    ),
    Tool(
        name="read_history",
        description="读取会话历史记录",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionKey": {"type": "string", "description": "会话标识"},
                "limit": {"type": "integer", "description": "返回条数限制", "default": 10}
            },
            "required": ["sessionKey"]
        }
    ),
    Tool(
        name="claim_tasks",
        description="认领待处理的任务",
        inputSchema={
            "type": "object",
            "properties": {
                "skills": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "技能标签",
                    "default": []
                },
                "limit": {"type": "integer", "description": "最多认领的任务数", "default": 5}
            }
        }
    ),
    Tool(
        name="get_status",
        description="获取 OpenClaw 系统状态",
        inputSchema={
            "type": "object",
            "properties": {
                "includePerformance": {"type": "boolean", "default": False},
                "includeErrors": {"type": "boolean", "default": False}
            }
        }
    ),
    Tool(
        name="clear_cache",
        description="清空所有缓存",
        inputSchema={"type": "object", "properties": {}}
    ),
    Tool(
        name="get_error_report",
        description="获取错误报告",
        inputSchema={
            "type": "object",
            "properties": {
                "reset": {"type": "boolean", "default": False}
            }
        }
    ),
    
    # ===== 新增工具（v2.5） =====
    Tool(
        name="broadcast",
        description="广播消息到多个会话",
        inputSchema={
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "要广播的消息内容"
                },
                "channels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "目标频道列表"
                },
                "delay": {
                    "type": "number",
                    "description": "每条消息之间的延迟（秒）",
                    "default": 0.5
                }
            },
            "required": ["message", "channels"]
        }
    ),
    Tool(
        name="get_tasks",
        description="获取所有任务",
        inputSchema={
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["pending", "in_progress", "completed", "all"],
                    "description": "任务状态过滤",
                    "default": "all"
                },
                "priority": {
                    "type": "string",
                    "enum": ["urgent", "high", "normal", "low", "all"],
                    "description": "优先级过滤",
                    "default": "all"
                },
                "skills": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "技能标签过滤",
                    "default": []
                },
                "limit": {
                    "type": "integer",
                    "description": "返回条数限制",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 100
                }
            }
        }
    ),
    Tool(
        name="create_task",
        description="创建新任务",
        inputSchema={
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "任务标题"
                },
                "description": {
                    "type": "string",
                    "description": "任务描述"
                },
                "skills": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "所需技能标签",
                    "default": []
                },
                "priority": {
                    "type": "string",
                    "enum": ["urgent", "high", "normal", "low"],
                    "description": "任务优先级",
                    "default": "normal"
                },
                "sessionKey": {
                    "type": "string",
                    "description": "关联的会话标识"
                }
            },
            "required": ["title", "description"]
        }
    ),
    Tool(
        name="update_task",
        description="更新任务状态",
        inputSchema={
            "type": "object",
            "properties": {
                "taskId": {
                    "type": "string",
                    "description": "任务ID"
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "in_progress", "completed", "failed"],
                    "description": "新状态"
                },
                "agentId": {
                    "type": "string",
                    "description": "处理Agent ID"
                }
            },
            "required": ["taskId"]
        }
    ),
    Tool(
        name="batch_operation",
        description="批量操作多个会话",
        inputSchema={
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["send_message", "read_history", "get_status"],
                    "description": "操作类型"
                },
                "targets": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "目标列表（会话标识）"
                },
                "params": {
                    "type": "object",
                    "description": "操作参数"
                },
                "concurrency": {
                    "type": "integer",
                    "description": "并发数",
                    "default": 3,
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "required": ["operation", "targets"]
        }
    ),
    Tool(
        name="analytics",
        description="数据分析和统计",
        inputSchema={
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["overview", "tasks", "sessions", "performance"],
                    "description": "分析类型",
                    "default": "overview"
                },
                "timeRange": {
                    "type": "string",
                    "enum": ["1h", "24h", "7d", "30d"],
                    "description": "时间范围",
                    "default": "24h"
                }
            }
        }
    )
]

# =============================================================================
# 工具实现
# =============================================================================

async def broadcast_handler(message: str, channels: List[str], delay: float = 0.5) -> TextContent:
    """广播消息到多个会话"""
    start_time = time.time()
    
    try:
        results = []
        
        for channel in channels:
            cmd = [
                "openclaw",
                "message",
                "send",
                "--channel", "feishu",
                "--target", channel,
                "--message", message
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            results.append({
                "channel": channel,
                "success": result.returncode == 0,
                "output": result.stdout if result.returncode == 0 else result.stderr
            })
            
            # 延迟
            if delay > 0:
                await asyncio.sleep(delay)
        
        # 统计
        success_count = sum(1 for r in results if r["success"])
        total_count = len(results)
        
        response_text = f"## 广播完成\n\n"
        response_text += f"- **总目标**: {total_count}\n"
        response_text += f"- **成功**: {success_count}\n"
        response_text += f"- **失败**: {total_count - success_count}\n"
        response_text += f"- **耗时**: {time.time() - start_time:.3f}s\n\n"
        
        response_text += "### 详细结果\n\n"
        for r in results:
            status = "✅" if r["success"] else "❌"
            response_text += f"{status} **{r['channel']}**: {r['output']}\n"
        
        # 记录事件
        analytics_engine.log_event("broadcast", {
            "channels": channels,
            "success": success_count,
            "total": total_count
        })
        
        duration = time.time() - start_time
        perf_monitor.record("broadcast", duration)
        
        return TextContent(type="text", text=response_text)
        
    except Exception as e:
        error_handler.record_error("broadcast", e)
        return TextContent(type="text", text=f"❌ 广播失败: {str(e)}")

async def get_tasks_handler(status: str = "all", priority: str = "all", 
                            skills: List[str] = None, limit: int = 20) -> TextContent:
    """获取所有任务"""
    start_time = time.time()
    
    try:
        # 过滤参数
        status_filter = None if status == "all" else status
        priority_filter = None if priority == "all" else priority
        skills_filter = skills if skills else None
        
        # 获取任务
        tasks = task_manager.get_tasks(
            status=status_filter,
            priority=priority_filter,
            skills=skills_filter,
            limit=limit
        )
        
        response_text = f"## 任务列表\n\n"
        response_text += f"找到 {len(tasks)} 个任务\n\n"
        
        if tasks:
            for task in tasks:
                response_text += f"### {task['task_id']}\n"
                response_text += f"- **标题**: {task['title']}\n"
                response_text += f"- **状态**: {task['status']}\n"
                response_text += f"- **优先级**: {task['priority']}\n"
                response_text += f"- **技能**: {', '.join(task['skills'])}\n"
                response_text += f"- **创建时间**: {task['created_at']}\n"
                response_text += f"- **描述**: {task['description'][:100]}...\n\n"
        
        # 添加统计
        stats = task_manager.get_stats()
        response_text += f"### 统计\n\n"
        response_text += f"- **总计**: {stats['total']}\n"
        response_text += f"- **待处理**: {stats['pending']}\n"
        response_text += f"- **进行中**: {stats['in_progress']}\n"
        response_text += f"- **已完成**: {stats['completed']}\n"
        
        duration = time.time() - start_time
        perf_monitor.record("get_tasks", duration)
        
        return TextContent(type="text", text=response_text)
        
    except Exception as e:
        error_handler.record_error("get_tasks", e)
        return TextContent(type="text", text=f"❌ 获取任务失败: {str(e)}")

async def create_task_handler(title: str, description: str, skills: List[str] = None,
                             priority: str = "normal", sessionKey: str = None) -> TextContent:
    """创建新任务"""
    try:
        task_id = task_manager.create_task(
            title=title,
            description=description,
            skills=skills or [],
            priority=priority,
            session_key=sessionKey
        )
        
        # 记录事件
        analytics_engine.log_event("create_task", {
            "task_id": task_id,
            "priority": priority,
            "skills": skills
        })
        
        response_text = f"## 任务创建成功\n\n"
        response_text += f"- **任务ID**: {task_id}\n"
        response_text += f"- **标题**: {title}\n"
        response_text += f"- **优先级**: {priority}\n"
        response_text += f"- **技能**: {', '.join(skills or [])}\n"
        
        return TextContent(type="text", text=response_text)
        
    except Exception as e:
        error_handler.record_error("create_task", e)
        return TextContent(type="text", text=f"❌ 创建任务失败: {str(e)}")

async def update_task_handler(taskId: str, status: str = None, agentId: str = None) -> TextContent:
    """更新任务状态"""
    try:
        success = task_manager.update_task(taskId, status=status, agent_id=agentId)
        
        if not success:
            return TextContent(type="text", text=f"❌ 任务不存在: {taskId}")
        
        # 记录事件
        analytics_engine.log_event("update_task", {
            "task_id": taskId,
            "status": status,
            "agent_id": agentId
        })
        
        response_text = f"## 任务更新成功\n\n"
        response_text += f"- **任务ID**: {taskId}\n"
        
        if status:
            response_text += f"- **新状态**: {status}\n"
        
        if agentId:
            response_text += f"- **处理Agent**: {agentId}\n"
        
        return TextContent(type="text", text=response_text)
        
    except Exception as e:
        error_handler.record_error("update_task", e)
        return TextContent(type="text", text=f"❌ 更新任务失败: {str(e)}")

async def batch_operation_handler(operation: str, targets: List[str], 
                                 params: Dict = None, concurrency: int = 3) -> TextContent:
    """批量操作多个会话"""
    start_time = time.time()
    
    try:
        # 创建信号量（控制并发）
        semaphore = asyncio.Semaphore(concurrency)
        
        async def process_target(target: str):
            async with semaphore:
                if operation == "send_message":
                    cmd = [
                        "openclaw",
                        "message",
                        "send",
                        "--channel", "feishu",
                        "--target", target,
                        "--message", params.get("message", "")
                    ]
                elif operation == "read_history":
                    cmd = ["openclaw", "sessions", "list", "--active", "1"]
                elif operation == "get_status":
                    cmd = ["openclaw", "status"]
                else:
                    return {"target": target, "error": "未知操作"}
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                return {
                    "target": target,
                    "success": result.returncode == 0,
                    "output": result.stdout if result.returncode == 0 else result.stderr
                }
        
        # 并发处理
        results = await asyncio.gather(*[process_target(t) for t in targets])
        
        # 统计
        success_count = sum(1 for r in results if r["success"])
        
        response_text = f"## 批量操作完成\n\n"
        response_text += f"- **操作**: {operation}\n"
        response_text += f"- **总目标**: {len(targets)}\n"
        response_text += f"- **成功**: {success_count}\n"
        response_text += f"- **失败**: {len(targets) - success_count}\n"
        response_text += f"- **并发数**: {concurrency}\n"
        response_text += f"- **耗时**: {time.time() - start_time:.3f}s\n\n"
        
        response_text += "### 详细结果\n\n"
        for r in results:
            status = "✅" if r["success"] else "❌"
            response_text += f"{status} **{r['target']}**: {r.get('output', 'N/A')}\n"
        
        # 记录事件
        analytics_engine.log_event("batch_operation", {
            "operation": operation,
            "targets": targets,
            "success": success_count,
            "total": len(targets)
        })
        
        duration = time.time() - start_time
        perf_monitor.record("batch_operation", duration)
        
        return TextContent(type="text", text=response_text)
        
    except Exception as e:
        error_handler.record_error("batch_operation", e)
        return TextContent(type="text", text=f"❌ 批量操作失败: {str(e)}")

async def analytics_handler(type: str = "overview", timeRange: str = "24h") -> TextContent:
    """数据分析和统计"""
    try:
        # 获取分析数据
        analysis = analytics_engine.analyze()
        
        response_text = f"## 数据分析报告\n\n"
        response_text += f"- **时间范围**: {timeRange}\n"
        response_text += f"- **分析类型**: {type}\n\n"
        
        # 总览
        if type == "overview" or type == "tasks":
            stats = task_manager.get_stats()
            response_text += f"### 任务统计\n\n"
            response_text += f"- **总计**: {stats['total']}\n"
            response_text += f"- **待处理**: {stats['pending']}\n"
            response_text += f"- **进行中**: {stats['in_progress']}\n"
            response_text += f"- **已完成**: {stats['completed']}\n\n"
        
        # 事件分析
        response_text += f"### 事件统计\n\n"
        response_text += f"- **总事件数**: {analysis['total_events']}\n"
        response_text += f"- **最近24小时**: {analysis['last_24h']}\n\n"
        
        response_text += f"### Top 5 事件\n\n"
        for event, count in analysis['top_events']:
            response_text += f"- **{event}**: {count} 次\n"
        
        # 性能分析
        if type == "overview" or type == "performance":
            response_text += f"\n{perf_monitor.get_report()}"
        
        return TextContent(type="text", text=response_text)
        
    except Exception as e:
        error_handler.record_error("analytics", e)
        return TextContent(type="text", text=f"❌ 数据分析失败: {str(e)}")

# =============================================================================
# MCP Server 生命周期
# =============================================================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用工具"""
    return TOOLS

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """调用工具"""
    logger.info(f"调用工具: {name} with {arguments}")
    
    try:
        if name == "broadcast":
            return [await broadcast_handler(
                message=arguments["message"],
                channels=arguments["channels"],
                delay=arguments.get("delay", 0.5)
            )]
        
        elif name == "get_tasks":
            return [await get_tasks_handler(
                status=arguments.get("status", "all"),
                priority=arguments.get("priority", "all"),
                skills=arguments.get("skills", []),
                limit=arguments.get("limit", 20)
            )]
        
        elif name == "create_task":
            return [await create_task_handler(
                title=arguments["title"],
                description=arguments["description"],
                skills=arguments.get("skills", []),
                priority=arguments.get("priority", "normal"),
                sessionKey=arguments.get("sessionKey")
            )]
        
        elif name == "update_task":
            return [await update_task_handler(
                taskId=arguments["taskId"],
                status=arguments.get("status"),
                agentId=arguments.get("agentId")
            )]
        
        elif name == "batch_operation":
            return [await batch_operation_handler(
                operation=arguments["operation"],
                targets=arguments["targets"],
                params=arguments.get("params", {}),
                concurrency=arguments.get("concurrency", 3)
            )]
        
        elif name == "analytics":
            return [await analytics_handler(
                type=arguments.get("type", "overview"),
                timeRange=arguments.get("timeRange", "24h")
            )]
        
        # ===== 原有工具（v2.4） =====
        
        elif name == "list_sessions":
            # 列出会话
            active_minutes = arguments.get("activeMinutes", 0)
            cache_key = f"sessions:{active_minutes}"
            
            cached = cache_manager.get(cache_key)
            if cached:
                return [TextContent(type="text", text=cached)]
            
            cmd = ["openclaw", "sessions", "list"]
            if active_minutes > 0:
                cmd.extend(["--active-minutes", str(active_minutes)])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                cache_manager.set(cache_key, result.stdout)
                return [TextContent(type="text", text=result.stdout)]
            else:
                return [TextContent(type="text", text=f"❌ 列出会话失败: {result.stderr}")]
        
        elif name == "send_message":
            # 发送消息
            cmd = [
                "openclaw",
                "message",
                "send",
                "--channel", arguments["channel"],
                "--target", arguments["target"],
                "--message", arguments["message"]
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return [TextContent(type="text", text=result.stdout)]
            else:
                return [TextContent(type="text", text=f"❌ 发送消息失败: {result.stderr}")]
        
        elif name == "read_history":
            # 读取历史
            session_key = arguments["sessionKey"]
            limit = arguments.get("limit", 10)
            
            cmd = [
                "openclaw",
                "sessions",
                "history",
                session_key,
                "--limit", str(limit)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return [TextContent(type="text", text=result.stdout)]
            else:
                return [TextContent(type="text", text=f"❌ 读取历史失败: {result.stderr}")]
        
        elif name == "claim_tasks":
            # 认领任务
            skills = arguments.get("skills", [])
            limit = arguments.get("limit", 5)
            
            # 获取匹配的任务
            tasks = task_manager.get_tasks(
                status="pending",
                skills=skills,
                limit=limit
            )
            
            # 更新状态
            claimed_tasks = []
            for task in tasks:
                task_manager.update_task(task["task_id"], status="in_progress")
                claimed_tasks.append(task)
            
            response_text = f"## 认领任务成功\n\n"
            response_text += f"认领了 {len(claimed_tasks)} 个任务\n\n"
            
            for task in claimed_tasks:
                response_text += f"### {task['task_id']}\n"
                response_text += f"- **标题**: {task['title']}\n"
                response_text += f"- **技能**: {', '.join(task['skills'])}\n\n"
            
            return [TextContent(type="text", text=response_text)]
        
        elif name == "get_status":
            # 获取状态
            include_perf = arguments.get("includePerformance", False)
            include_errors = arguments.get("includeErrors", False)
            
            cmd = ["openclaw", "status"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            response_text = "## OpenClaw 系统状态\n\n"
            
            if result.returncode == 0:
                response_text += result.stdout
            else:
                response_text += f"❌ 获取状态失败: {result.stderr}\n\n"
            
            # 添加性能监控
            if include_perf:
                response_text += f"\n{perf_monitor.get_report()}"
            
            # 添加错误报告
            if include_errors:
                response_text += f"\n{error_handler.get_error_report()}"
            
            return [TextContent(type="text", text=response_text)]
        
        elif name == "clear_cache":
            # 清空缓存
            cache_manager.clear()
            return [TextContent(type="text", text="✅ 缓存已清空")]
        
        elif name == "get_error_report":
            # 获取错误报告
            reset = arguments.get("reset", False)
            
            report = error_handler.get_error_report()
            
            if reset:
                error_handler.error_counts.clear()
                error_handler.last_errors.clear()
                report += "\n\n✅ 错误记录已重置"
            
            return [TextContent(type="text", text=report)]
        
        else:
            return [TextContent(type="text", text=f"❌ 未知工具: {name}")]
    
    except Exception as e:
        logger.error(f"工具调用异常: {e}")
        error_handler.record_error(name, e)
        return [TextContent(type="text", text=f"❌ 工具调用异常: {str(e)}")]

# =============================================================================
# 主入口
# =============================================================================

async def main():
    """启动 MCP Server"""
    from mcp.server.stdio import stdio_server
    
    logger.info("🚀 OpenClaw MCP Server v2.5 启动中...")
    logger.info(f"工具数: {len(TOOLS)}")
    logger.info("新增功能: broadcast, get_tasks, create_task, update_task, batch_operation, analytics")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
