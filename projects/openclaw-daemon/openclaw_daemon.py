#!/usr/bin/env python3
"""
OpenClaw Daemon v1.2 - 增强版 Driver 适配器
实现 Subagent、ACP、OpenCode 完整驱动

v1.2 新增：
- 自动重启优化
- 消息队列持久化
- 错误恢复机制
- 健康检查
- 性能监控
"""

import asyncio
import json
import logging
import subprocess
import os
import signal
import sys
import time
import threading
from typing import Dict, Optional, Any, List
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod
from collections import deque

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# 配置
# =============================================================================

GATEWAY_URL = "ws://localhost:18789"
GATEWAY_API_URL = "http://localhost:18789"
WORKSPACE = "/root/.openclaw/workspace"
STATE_FILE = "/root/.openclaw/workspace/.openclaw-daemon-state.json"
MESSAGE_QUEUE_FILE = "/root/.openclaw/workspace/.openclaw-daemon-queue.json"
HEALTH_CHECK_INTERVAL = 30  # 秒
MAX_RESTART_ATTEMPTS = 3
RESTART_DELAY = 5  # 秒

# =============================================================================
# 枚举定义
# =============================================================================

class AgentState(Enum):
    """Agent 状态"""
    COLD_START = "cold_start"
    RUNNING = "running"
    IDLE = "idle"
    SLEEP = "sleep"
    WAKE_UP = "wake_up"
    STOPPED = "stopped"
    ERROR = "error"

class DriverType(Enum):
    """驱动类型"""
    SUBAGENT = "subagent"
    ACP = "acp"
    OPENCODE = "opencode"

# =============================================================================
# 核心数据结构
# =============================================================================

class AgentInfo:
    """Agent 信息（v1.2 增强）"""
    
    def __init__(self, agent_id: str, driver_type: DriverType):
        self.agent_id = agent_id
        self.driver_type = driver_type
        self.state = AgentState.COLD_START
        self.session_key = None
        self.process = None
        self.config = {}
        self.last_activity = None
        self.message_queue = deque(maxlen=1000)  # 消息队列（持久化）
        self.restart_count = 0  # 重启次数
        self.created_at = datetime.now()  # 创建时间
        self.health_status = "unknown"  # 健康状态
        
    def update_state(self, new_state: AgentState):
        """更新状态"""
        old_state = self.state
        self.state = new_state
        self.last_activity = datetime.now()
        
        logger.info(f"Agent {self.agent_id}: {old_state.value} → {new_state.value}")
    
    def add_message(self, message: str):
        """添加消息到队列"""
        self.message_queue.append({
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_pending_messages(self) -> List[str]:
        """获取待处理消息"""
        messages = [item["message"] for item in list(self.message_queue)]
        self.message_queue.clear()
        return messages
    
    def increment_restart_count(self):
        """增加重启计数"""
        self.restart_count += 1
        logger.warning(f"Agent {self.agent_id} 重启次数: {self.restart_count}")
    
    def should_restart(self) -> bool:
        """判断是否应该重启"""
        return self.restart_count < MAX_RESTART_ATTEMPTS

# =============================================================================
# 性能监控器（v1.2 新增）
# =============================================================================

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {}
        self.lock = threading.Lock()
    
    def record_spawn(self, agent_id: str, duration: float):
        """记录启动时间"""
        with self.lock:
            if agent_id not in self.metrics:
                self.metrics[agent_id] = {
                    "spawn_count": 0,
                    "total_spawn_time": 0,
                    "avg_spawn_time": 0,
                    "restart_count": 0
                }
            
            self.metrics[agent_id]["spawn_count"] += 1
            self.metrics[agent_id]["total_spawn_time"] += duration
            self.metrics[agent_id]["avg_spawn_time"] = \
                self.metrics[agent_id]["total_spawn_time"] / self.metrics[agent_id]["spawn_count"]
    
    def record_restart(self, agent_id: str):
        """记录重启"""
        with self.lock:
            if agent_id not in self.metrics:
                self.metrics[agent_id] = {"restart_count": 0}
            
            self.metrics[agent_id]["restart_count"] += 1
    
    def get_report(self) -> str:
        """获取性能报告"""
        with self.lock:
            report = "## 性能监控报告\n\n"
            
            for agent_id, metrics in self.metrics.items():
                report += f"### {agent_id}\n"
                report += f"- 启动次数: {metrics.get('spawn_count', 0)}\n"
                report += f"- 平均启动时间: {metrics.get('avg_spawn_time', 0):.3f}s\n"
                report += f"- 重启次数: {metrics.get('restart_count', 0)}\n\n"
            
            return report

# 全局性能监控器
perf_monitor = PerformanceMonitor()

# =============================================================================
# Driver 适配器基类（v1.2 增强）
# =============================================================================

class DriverAdapter(ABC):
    """驱动适配器基类（v1.2 增强）"""
    
    def __init__(self, agent_info: AgentInfo):
        self.agent_info = agent_info
        self.health_check_interval = HEALTH_CHECK_INTERVAL
        self.last_health_check = None
    
    @abstractmethod
    async def spawn(self) -> subprocess.Popen:
        """启动 Agent"""
        pass
    
    @abstractmethod
    async def send_message(self, message: str):
        """发送消息"""
        pass
    
    @abstractmethod
    def supports_stdin_injection(self) -> bool:
        """是否支持 stdin 注入"""
        pass
    
    @abstractmethod
    async def stop(self):
        """停止 Agent"""
        pass
    
    @abstractmethod
    async def restart(self):
        """重启 Agent"""
        pass
    
    async def health_check(self) -> bool:
        """健康检查（v1.2 新增）"""
        if not self.agent_info.process:
            return False
        
        # 检查进程是否还在运行
        poll_result = self.agent_info.process.poll()
        
        if poll_result is not None:
            # 进程已退出
            logger.warning(f"Agent {self.agent_info.agent_id} 进程已退出（退出码: {poll_result}）")
            self.agent_info.health_status = "unhealthy"
            return False
        
        self.agent_info.health_status = "healthy"
        self.last_health_check = datetime.now()
        return True

# =============================================================================
# Subagent Driver
# =============================================================================

class SubagentDriver(DriverAdapter):
    """Subagent 驱动 - 重启模式（v1.2 增强）"""
    
    def __init__(self, agent_info: AgentInfo):
        super().__init__(agent_info)
        logger.info(f"初始化 Subagent 驱动: {agent_info.agent_id}")
    
    async def spawn(self) -> subprocess.Popen:
        """启动 Subagent（v1.2 增强）"""
        start_time = time.time()
        model = self.agent_info.config.get("model", "glmcode/glm-4.7")
        
        cmd = [
            "openclaw",
            "sessions",
            "spawn",
            "--runtime", "subagent",
            "--model", model,
            "--thread"
        ]
        
        logger.info(f"启动 Subagent: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=WORKSPACE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            
            self.agent_info.process = process
            self.agent_info.update_state(AgentState.RUNNING)
            
            # 记录性能
            duration = time.time() - start_time
            perf_monitor.record_spawn(self.agent_info.agent_id, duration)
            
            return process
            
        except Exception as e:
            logger.error(f"启动 Subagent 失败: {e}")
            self.agent_info.update_state(AgentState.ERROR)
            raise
    
    async def send_message(self, message: str):
        """发送消息（通过重启，v1.2 增强）"""
        logger.info(f"Subagent 发送消息（通过重启）")
        
        # 将消息加入队列
        self.agent_info.add_message(message)
        
        # 检查是否应该重启
        if self.agent_info.should_restart():
            # Subagent 不支持 stdin 注入，需要重启
            await self.restart()
        else:
            logger.error(f"Agent {self.agent_info.agent_id} 超过最大重启次数")
            self.agent_info.update_state(AgentState.ERROR)
    
    def supports_stdin_injection(self) -> bool:
        """Subagent 不支持 stdin 注入"""
        return False
    
    async def stop(self):
        """停止 Agent（v1.2 增强）"""
        if self.agent_info.process:
            self.agent_info.process.terminate()
            try:
                self.agent_info.process.wait(timeout=5)
                logger.info(f"Subagent {self.agent_info.agent_id} 已停止")
            except subprocess.TimeoutExpired:
                self.agent_info.process.kill()
                logger.warning(f"Subagent {self.agent_info.agent_id} 强制停止")
            
            self.agent_info.update_state(AgentState.STOPPED)
    
    async def restart(self):
        """重启 Agent（v1.2 增强）"""
        logger.info(f"重启 Subagent {self.agent_info.agent_id}")
        
        # 增加重启计数
        self.agent_info.increment_restart_count()
        perf_monitor.record_restart(self.agent_info.agent_id)
        
        # 停止当前进程
        await self.stop()
        
        # 等待一段时间再重启
        await asyncio.sleep(RESTART_DELAY)
        
        # 获取待处理消息
        pending_messages = self.agent_info.get_pending_messages()
        
        # 重新启动
        await self.spawn()
        
        # 处理积压的消息
        for msg in pending_messages:
            logger.info(f"处理积压消息: {msg[:50]}...")
            # Subagent 无法注入，只能通过其他方式处理

# =============================================================================
# ACP Driver
# =============================================================================

class ACPDriver(DriverAdapter):
    """ACP 驱动 - 注入模式"""
    
    def __init__(self, agent_info: AgentInfo):
        super().__init__(agent_info)
        logger.info(f"初始化 ACP 驱动: {agent_info.agent_id}")
    
    async def spawn(self) -> subprocess.Popen:
        """启动 ACP Agent"""
        agent_id = self.agent_info.config.get("agentId", "claude-code")
        model = self.agent_info.config.get("model", "anthropic/claude-sonnet-4")
        
        cmd = [
            "sessions_spawn",
            "--runtime", "acp",
            "--agentId", agent_id,
            "--model", model,
            "--thread"
        ]
        
        logger.info(f"启动 ACP Agent: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            cwd=WORKSPACE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        
        self.agent_info.process = process
        self.agent_info.update_state(AgentState.RUNNING)
        
        return process
    
    async def send_message(self, message: str):
        """发送消息（通过 stdin 注入）"""
        logger.info(f"ACP 发送消息（通过 stdin 注入）")
        
        if self.agent_info.process and self.agent_info.process.stdin:
            try:
                # 尝试直接注入
                self.agent_info.process.stdin.write(message.encode() + b"\n")
                self.agent_info.process.stdin.flush()
                logger.info(f"✅ 消息已注入到 ACP Agent")
                self.agent_info.update_state(AgentState.RUNNING)
            except Exception as e:
                logger.error(f"❌ 注入消息失败: {e}")
                # 降级到重启
                await self.restart_with_message(message)
        else:
            await self.restart_with_message(message)
    
    def supports_stdin_injection(self) -> bool:
        """ACP 支持 stdin 注入"""
        return True
    
    async def stop(self):
        """停止 Agent"""
        if self.agent_info.process:
            self.agent_info.process.terminate()
            try:
                self.agent_info.process.wait(timeout=5)
                logger.info(f"ACP Agent {self.agent_info.agent_id} 已停止")
            except subprocess.TimeoutExpired:
                self.agent_info.process.kill()
                logger.warning(f"ACP Agent {self.agent_info.agent_id} 强制停止")
            
            self.agent_info.update_state(AgentState.STOPPED)
    
    async def restart(self):
        """重启 Agent"""
        logger.info(f"重启 ACP Agent {self.agent_info.agent_id}")
        
        # 停止当前进程
        await self.stop()
        
        # 重新启动
        await self.spawn()
    
    async def restart_with_message(self, message: str):
        """带消息重启"""
        logger.info(f"重启 ACP Agent 并发送消息")
        
        # 停止当前进程
        await self.stop()
        
        # 将消息加入队列
        self.agent_info.add_message(message)
        
        # 重新启动
        await self.spawn()
        
        # 尝试注入积压的消息
        pending_messages = self.agent_info.get_pending_messages()
        if pending_messages and self.agent_info.process:
            for msg in pending_messages:
                try:
                    self.agent_info.process.stdin.write(msg.encode() + b"\n")
                    self.agent_info.process.stdin.flush()
                    logger.info(f"✅ 积压消息已注入")
                except Exception as e:
                    logger.error(f"❌ 注入积压消息失败: {e}")

# =============================================================================
# OpenCode Driver
# =============================================================================

class OpenCodeDriver(DriverAdapter):
    """OpenCode 驱动 - 混合模式"""
    
    def __init__(self, agent_info: AgentInfo):
        super().__init__(agent_info)
        logger.info(f"初始化 OpenCode 驱动: {agent_info.agent_id}")
    
    async def spawn(self) -> subprocess.Popen:
        """启动 OpenCode Agent"""
        model = self.agent_info.config.get("model", "opencode/minimax-m2.5-free")
        
        # OpenCode 使用独立的 CLI
        cmd = [
            "opencode",
            "-m", model,
            "run",
            "OpenCode Agent 已启动"
        ]
        
        logger.info(f"启动 OpenCode Agent: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            cwd=WORKSPACE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        
        self.agent_info.process = process
        self.agent_info.update_state(AgentState.RUNNING)
        
        return process
    
    async def send_message(self, message: str):
        """发送消息（通过 CLI）"""
        logger.info(f"OpenCode 发送消息（通过 CLI）")
        
        # OpenCode 需要通过 CLI 调用
        model = self.agent_info.config.get("model", "opencode/minimax-m2.5-free")
        
        cmd = [
            "opencode",
            "-m", model,
            "run",
            message
        ]
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            cwd=WORKSPACE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate(timeout=30)
        
        if process.returncode == 0:
            logger.info(f"✅ OpenCode 消息已发送")
            return True
        else:
            logger.error(f"❌ OpenCode 消息发送失败: {stderr}")
            return False
    
    def supports_stdin_injection(self) -> bool:
        """OpenCode 不支持 stdin 注入"""
        return False
    
    async def stop(self):
        """停止 Agent"""
        if self.agent_info.process:
            self.agent_info.process.terminate()
            try:
                self.agent_info.process.wait(timeout=5)
                logger.info(f"OpenCode Agent {self.agent_info.agent_id} 已停止")
            except subprocess.TimeoutExpired:
                self.agent_info.process.kill()
                logger.warning(f"OpenCode Agent {self.agent_info.agent_id} 强制停止")
            
            self.agent_info.update_state(AgentState.STOPPED)
    
    async def restart(self):
        """重启 Agent"""
        logger.info(f"重启 OpenCode Agent {self.agent_info.agent_id}")
        
        # 停止当前进程
        await self.stop()
        
        # 重新启动
        await self.spawn()

# =============================================================================
# Driver 工厂
# =============================================================================

class DriverFactory:
    """驱动工厂"""
    
    @staticmethod
    def create_driver(agent_info: AgentInfo) -> DriverAdapter:
        """创建驱动"""
        driver_type = agent_info.driver_type
        
        if driver_type == DriverType.SUBAGENT:
            return SubagentDriver(agent_info)
        elif driver_type == DriverType.ACP:
            return ACPDriver(agent_info)
        elif driver_type == DriverType.OPENCODE:
            return OpenCodeDriver(agent_info)
        else:
            raise ValueError(f"不支持的驱动类型: {driver_type}")

# =============================================================================
# Daemon 核心类（增强版）
# =============================================================================

class OpenClawDaemon:
    """OpenClaw Daemon 核心类（v1.2 增强）"""
    
    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
        self.running = False
        self.websocket = None
        self.session_file = STATE_FILE
        self.queue_file = MESSAGE_QUEUE_FILE
        self.health_check_task = None
    
    async def start(self):
        """启动 Daemon（v1.2 增强）"""
        logger.info("🚀 OpenClaw Daemon v1.2 启动中...")
        
        self.running = True
        
        # 加载状态
        await self.load_state()
        
        # 加载消息队列
        await self.load_message_queue()
        
        # 启动心跳
        asyncio.create_task(self.heartbeat_loop())
        
        # 启动健康检查（v1.2 新增）
        self.health_check_task = asyncio.create_task(self.health_check_loop())
        
        logger.info("✅ OpenClaw Daemon v1.2 已启动")
        logger.info(f"支持驱动: Subagent, ACP, OpenCode")
        logger.info(f"新增功能: 自动重启优化、消息队列持久化、错误恢复、健康检查")
    
    async def stop(self):
        """停止 Daemon（v1.2 增强）"""
        logger.info("🛑 停止 OpenClaw Daemon...")
        
        self.running = False
        
        # 停止健康检查（v1.2 新增）
        if self.health_check_task:
            self.health_check_task.cancel()
        
        # 停止所有 Agent
        for agent_id, agent_info in self.agents.items():
            driver = DriverFactory.create_driver(agent_info)
            await driver.stop()
        
        # 保存状态
        await self.save_state()
        
        # 保存消息队列（v1.2 新增）
        await self.save_message_queue()
        
        logger.info("✅ OpenClaw Daemon 已停止")
    
    async def load_state(self):
        """加载状态"""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    state = json.load(f)
                
                logger.info(f"加载状态: {len(state.get('agents', {}))} 个 Agent")
                
                # 恢复 Agent 信息
                for agent_id, agent_data in state.get('agents', {}).items():
                    driver_type = DriverType(agent_data.get('driver_type'))
                    agent_info = AgentInfo(agent_id, driver_type)
                    agent_info.state = AgentState(agent_data.get('state', 'stopped'))
                    agent_info.config = agent_data.get('config', {})
                    
                    self.agents[agent_id] = agent_info
                    
            except Exception as e:
                logger.error(f"加载状态失败: {e}")
    
    async def save_state(self):
        """保存状态"""
        state = {
            "agents": {},
            "last_updated": datetime.now().isoformat()
        }
        
        for agent_id, agent_info in self.agents.items():
            state["agents"][agent_id] = {
                "driver_type": agent_info.driver_type.value,
                "state": agent_info.state.value,
                "config": agent_info.config
            }
        
        with open(self.session_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info("状态已保存")
    
    async def spawn_agent(self, agent_id: str, driver_type: DriverType, config: dict = None) -> AgentInfo:
        """启动 Agent"""
        if agent_id in self.agents:
            logger.warning(f"Agent {agent_id} 已存在")
            return self.agents[agent_id]
        
        # 创建 Agent 信息
        agent_info = AgentInfo(agent_id, driver_type)
        agent_info.config = config or {}
        
        # 创建驱动
        driver = DriverFactory.create_driver(agent_info)
        
        # 启动 Agent
        await driver.spawn()
        
        # 保存到缓存
        self.agents[agent_id] = agent_info
        
        # 保存状态
        await self.save_state()
        
        logger.info(f"✅ Agent {agent_id} 已启动（驱动: {driver_type.value}）")
        
        return agent_info
    
    async def send_message_to_agent(self, agent_id: str, message: str):
        """发送消息到 Agent"""
        if agent_id not in self.agents:
            logger.error(f"Agent {agent_id} 不存在")
            return False
        
        agent_info = self.agents[agent_id]
        
        # 创建驱动
        driver = DriverFactory.create_driver(agent_info)
        
        # 发送消息
        await driver.send_message(message)
        
        return True
    
    async def heartbeat_loop(self):
        """心跳循环"""
        while self.running:
            try:
                # 每 30 秒一次心跳
                await asyncio.sleep(30)
                
                # 检查 Agent 状态
                await self.check_agents()
                
            except Exception as e:
                logger.error(f"心跳异常: {e}")
    
    async def check_agents(self):
        """检查 Agent 状态（v1.2 增强）"""
        for agent_id, agent_info in self.agents.items():
            if agent_info.process:
                # 检查进程是否还在运行
                poll_result = agent_info.process.poll()
                
                if poll_result is not None:
                    # 进程已退出
                    logger.warning(f"Agent {agent_id} 进程已退出（退出码: {poll_result}）")
                    agent_info.update_state(AgentState.ERROR)
                    
                    # 尝试自动重启（v1.2 增强）
                    if agent_info.should_restart() and agent_info.config.get("auto_restart", True):
                        logger.info(f"尝试自动重启 Agent {agent_id}")
                        driver = DriverFactory.create_driver(agent_info)
                        try:
                            await driver.restart()
                        except Exception as e:
                            logger.error(f"自动重启失败: {e}")
                            agent_info.update_state(AgentState.ERROR)
    
    async def health_check_loop(self):
        """健康检查循环（v1.2 新增）"""
        while self.running:
            try:
                await asyncio.sleep(HEALTH_CHECK_INTERVAL)
                
                # 对所有 Agent 进行健康检查
                for agent_id, agent_info in self.agents.items():
                    if agent_info.state == AgentState.RUNNING:
                        driver = DriverFactory.create_driver(agent_info)
                        is_healthy = await driver.health_check()
                        
                        if not is_healthy:
                            logger.warning(f"Agent {agent_id} 健康检查失败")
                            agent_info.update_state(AgentState.ERROR)
                            
                            # 尝试恢复
                            if agent_info.should_restart():
                                logger.info(f"尝试恢复 Agent {agent_id}")
                                try:
                                    await driver.restart()
                                except Exception as e:
                                    logger.error(f"恢复失败: {e}")
            
            except Exception as e:
                logger.error(f"健康检查异常: {e}")
    
    async def save_message_queue(self):
        """保存消息队列（v1.2 新增）"""
        try:
            queue_data = {}
            
            for agent_id, agent_info in self.agents.items():
                if agent_info.message_queue:
                    queue_data[agent_id] = list(agent_info.message_queue)
            
            with open(self.queue_file, 'w') as f:
                json.dump(queue_data, f, indent=2)
            
            logger.info("消息队列已保存")
        except Exception as e:
            logger.error(f"保存消息队列失败: {e}")
    
    async def load_message_queue(self):
        """加载消息队列（v1.2 新增）"""
        try:
            if os.path.exists(self.queue_file):
                with open(self.queue_file, 'r') as f:
                    queue_data = json.load(f)
                
                for agent_id, messages in queue_data.items():
                    if agent_id in self.agents:
                        self.agents[agent_id].message_queue.extend(messages)
                
                logger.info(f"消息队列已加载: {len(queue_data)} 个 Agent")
        except Exception as e:
            logger.error(f"加载消息队列失败: {e}")

# =============================================================================
# 主入口
# =============================================================================

async def main():
    """主入口"""
    daemon = OpenClawDaemon()
    
    # 信号处理
    loop = asyncio.get_event_loop()
    
    def signal_handler():
        logger.info("收到停止信号")
        asyncio.create_task(daemon.stop())
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: signal_handler())
    
    # 启动 Daemon
    await daemon.start()
    
    # 保持运行
    try:
        while daemon.running:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("收到中断信号")
    finally:
        await daemon.stop()

if __name__ == "__main__":
    asyncio.run(main())
