#!/usr/bin/env python3
"""
角色池管理器 - Phase 2
实现动态角色创建和复用
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import asyncio


class RoleStatus(Enum):
    """角色状态"""
    IDLE = "idle"           # 空闲
    BUSY = "busy"           # 忙碌
    WARMING = "warming"     # 预热中
    TERMINATED = "terminated"  # 已终止


@dataclass
class RoleConfig:
    """角色配置"""
    role_id: str
    role_name: str
    agent_id: str
    model: str = "glmcode/glm-4.5-air"
    max_concurrent_tasks: int = 1
    warm_up: bool = False
    timeout_seconds: int = 300
    metadata: Dict = field(default_factory=dict)


@dataclass
class RoleInstance:
    """角色实例"""
    config: RoleConfig
    status: RoleStatus = RoleStatus.IDLE
    current_task: Optional[str] = None
    task_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)
    total_execution_time: float = 0.0

    @property
    def idle_time(self) -> timedelta:
        """空闲时间"""
        if self.status == RoleStatus.BUSY:
            return timedelta(0)
        return datetime.now() - self.last_used

    @property
    def is_expired(self) -> bool:
        """是否过期（超过 10 分钟未使用）"""
        return self.idle_time > timedelta(minutes=10)


class RolePool:
    """角色池 - 管理动态角色创建和复用"""

    def __init__(self, max_pool_size: int = 10):
        self.roles: Dict[str, RoleInstance] = {}
        self.max_pool_size = max_pool_size
        self.task_queue: List[str] = []
        self.role_assignment: Dict[str, str] = {}  # task_id -> role_id

    async def create_role(self, config: RoleConfig) -> bool:
        """
        创建新角色

        参数:
            config: 角色配置

        返回:
            是否创建成功
        """
        # 检查池是否已满
        if len(self.roles) >= self.max_pool_size:
            # 尝试清理过期角色
            await self._cleanup_expired_roles()
            if len(self.roles) >= self.max_pool_size:
                return False

        # 创建角色实例
        instance = RoleInstance(config=config)

        # 预热角色（如果需要）
        if config.warm_up:
            instance.status = RoleStatus.WARMING
            await self._warm_up_role(instance)

        self.roles[config.role_id] = instance
        return True

    async def _warm_up_role(self, instance: RoleInstance):
        """预热角色"""
        # 这里可以发送预热消息到 Agent
        await asyncio.sleep(0.5)  # 模拟预热
        instance.status = RoleStatus.IDLE

    async def acquire_role(self, task_id: str, required_role: str) -> Optional[str]:
        """
        获取角色（优先复用空闲角色）

        参数:
            task_id: 任务 ID
            required_role: 需要的角色类型

        返回:
            角色 ID，如果无可用角色则返回 None
        """
        # 查找空闲的匹配角色
        for role_id, instance in self.roles.items():
            if (instance.config.role_name == required_role and
                instance.status == RoleStatus.IDLE and
                not instance.is_expired):

                # 分配角色
                instance.status = RoleStatus.BUSY
                instance.current_task = task_id
                instance.last_used = datetime.now()
                self.role_assignment[task_id] = role_id

                return role_id

        # 没有可用角色
        return None

    async def release_role(self, task_id: str):
        """
        释放角色

        参数:
            task_id: 任务 ID
        """
        if task_id not in self.role_assignment:
            return

        role_id = self.role_assignment[task_id]
        instance = self.roles.get(role_id)

        if instance:
            instance.status = RoleStatus.IDLE
            instance.current_task = None
            instance.task_count += 1
            instance.last_used = datetime.now()

        del self.role_assignment[task_id]

    async def _cleanup_expired_roles(self):
        """清理过期角色"""
        expired_roles = [
            role_id for role_id, instance in self.roles.items()
            if instance.is_expired and instance.status == RoleStatus.IDLE
        ]

        for role_id in expired_roles:
            await self.terminate_role(role_id)

    async def terminate_role(self, role_id: str):
        """
        终止角色

        参数:
            role_id: 角色 ID
        """
        if role_id in self.roles:
            self.roles[role_id].status = RoleStatus.TERMINATED
            del self.roles[role_id]

    def get_role(self, role_id: str) -> Optional[RoleInstance]:
        """获取角色实例"""
        return self.roles.get(role_id)

    def get_all_roles(self) -> List[RoleInstance]:
        """获取所有角色"""
        return list(self.roles.values())

    def get_idle_roles(self, role_name: Optional[str] = None) -> List[RoleInstance]:
        """
        获取空闲角色

        参数:
            role_name: 角色名称过滤（可选）

        返回:
            空闲角色列表
        """
        idle_roles = [
            instance for instance in self.roles.values()
            if instance.status == RoleStatus.IDLE
        ]

        if role_name:
            idle_roles = [
                instance for instance in idle_roles
                if instance.config.role_name == role_name
            ]

        return idle_roles

    def get_pool_stats(self) -> Dict:
        """
        获取池统计信息

        返回:
            统计数据
        """
        total = len(self.roles)
        idle = sum(1 for r in self.roles.values() if r.status == RoleStatus.IDLE)
        busy = sum(1 for r in self.roles.values() if r.status == RoleStatus.BUSY)
        warming = sum(1 for r in self.roles.values() if r.status == RoleStatus.WARMING)

        total_tasks = sum(r.task_count for r in self.roles.values())
        total_execution_time = sum(r.total_execution_time for r in self.roles.values())

        # 计算复用率
        reuse_rate = total_tasks / total if total > 0 else 0

        return {
            "total_roles": total,
            "idle_roles": idle,
            "busy_roles": busy,
            "warming_roles": warming,
            "utilization_rate": busy / total if total > 0 else 0,
            "reuse_rate": reuse_rate,
            "total_tasks_processed": total_tasks,
            "total_execution_time": total_execution_time,
        }

    def visualize_pool(self) -> str:
        """
        可视化角色池

        返回:
            角色池的文本表示
        """
        lines = ["角色池状态:", "=" * 50]

        for role_id, instance in self.roles.items():
            status_emoji = {
                RoleStatus.IDLE: "💤",
                RoleStatus.BUSY: "🔥",
                RoleStatus.WARMING: "⏳",
                RoleStatus.TERMINATED: "❌",
            }.get(instance.status, "❓")

            lines.append(f"{status_emoji} {role_id} ({instance.config.role_name})")
            lines.append(f"   状态: {instance.status.value}")
            lines.append(f"   任务数: {instance.task_count}")
            lines.append(f"   Agent: {instance.config.agent_id}")
            if instance.current_task:
                lines.append(f"   当前任务: {instance.current_task}")
            lines.append("")

        return "\n".join(lines)


if __name__ == "__main__":
    # 测试角色池
    async def test():
        pool = RolePool(max_pool_size=5)

        # 创建角色
        config1 = RoleConfig("role1", "数据分析师", "opencode", warm_up=True)
        config2 = RoleConfig("role2", "数据分析师", "opencode")

        await pool.create_role(config1)
        await pool.create_role(config2)

        # 获取角色
        role_id = await pool.acquire_role("task1", "数据分析师")
        print(f"获取到角色: {role_id}")

        # 查看状态
        print(pool.visualize_pool())

        # 释放角色
        await pool.release_role("task1")
        print("释放后:")
        print(pool.visualize_pool())

    asyncio.run(test())
