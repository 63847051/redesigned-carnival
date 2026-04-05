#!/usr/bin/env python3
"""
Agent 注册表
管理所有可用的 Agent
"""

from typing import Dict, Type, Optional, Any
from pathlib import Path


class AgentInfo:
    """Agent 信息"""

    def __init__(self, agent_class: Type, config: dict):
        """
        初始化 Agent 信息

        Args:
            agent_class: Agent 类
            config: Agent 配置
        """
        self.agent_class = agent_class
        self.config = config

    def __repr__(self):
        return f"AgentInfo(class={self.agent_class.__name__}, role={self.config.get('role')})"


class AgentRegistry:
    """Agent 注册表"""

    def __init__(self):
        """初始化 Agent 注册表"""
        self.agents: Dict[str, AgentInfo] = {}

    def register(self, name: str, agent_class: Type, config: dict):
        """
        注册新的 Agent

        Args:
            name: Agent 名称
            agent_class: Agent 类
            config: Agent 配置
        """
        self.agents[name] = AgentInfo(agent_class, config)

    def unregister(self, name: str):
        """
        注销 Agent

        Args:
            name: Agent 名称
        """
        if name in self.agents:
            del self.agents[name]

    def get(self, name: str) -> Optional[AgentInfo]:
        """
        获取 Agent 信息

        Args:
            name: Agent 名称

        Returns:
            AgentInfo 或 None
        """
        return self.agents.get(name)

    def get_agent_class(self, name: str) -> Optional[Type]:
        """
        获取 Agent 类

        Args:
            name: Agent 名称

        Returns:
            Agent 类或 None
        """
        info = self.get(name)
        return info.agent_class if info else None

    def get_agent_config(self, name: str) -> dict:
        """
        获取 Agent 配置

        Args:
            name: Agent 名称

        Returns:
            Agent 配置字典
        """
        info = self.get(name)
        return info.config if info else {}

    def list_agents(self) -> list:
        """
        列出所有已注册的 Agent

        Returns:
            list: Agent 名称列表
        """
        return list(self.agents.keys())

    def list_agent_info(self) -> list:
        """
        列出所有 Agent 的详细信息

        Returns:
            list: Agent 信息列表
        """
        return [
            {
                "name": name,
                "class": info.agent_class.__name__,
                "role": info.config.get("role"),
                "model": info.config.get("model"),
                "description": info.config.get("description")
            }
            for name, info in self.agents.items()
        ]

    def is_registered(self, name: str) -> bool:
        """
        检查 Agent 是否已注册

        Args:
            name: Agent 名称

        Returns:
            bool: 是否已注册
        """
        return name in self.agents

    def count(self) -> int:
        """
        获取已注册 Agent 的数量

        Returns:
            int: Agent 数量
        """
        return len(self.agents)

    def clear(self):
        """清空所有注册的 Agent"""
        self.agents.clear()


# 全局 Agent 注册表实例
_registry = None


def get_registry() -> AgentRegistry:
    """获取全局 Agent 注册表实例"""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry


def register_agent(name: str, agent_class: Type, config: dict):
    """
    快捷方法：注册 Agent

    Args:
        name: Agent 名称
        agent_class: Agent 类
        config: Agent 配置
    """
    get_registry().register(name, agent_class, config)


def get_agent(name: str) -> Optional[AgentInfo]:
    """
    快捷方法：获取 Agent

    Args:
        name: Agent 名称

    Returns:
        AgentInfo 或 None
    """
    return get_registry().get(name)


def list_agents() -> list:
    """
    快捷方法：列出所有 Agent

    Returns:
        list: Agent 名称列表
    """
    return get_registry().list_agents()


# 测试代码
if __name__ == "__main__":
    print("🧪 测试 Agent 注册表\n")

    registry = get_registry()

    # 创建测试 Agent 类
    class TestAgent:
        def __init__(self, name, model):
            self.name = name
            self.model = model

        def __repr__(self):
            return f"TestAgent(name={self.name}, model={self.model})"

    # 注册 Agent
    print("1. 注册 Agent...\n")
    registry.register("test1", TestAgent, {
        "model": "glm-4.7",
        "role": "测试 Agent",
        "description": "这是一个测试 Agent"
    })

    registry.register("test2", TestAgent, {
        "model": "glm-4.6",
        "role": "另一个测试 Agent",
        "description": "这是另一个测试 Agent"
    })

    # 列出 Agent
    print("2. 列出所有 Agent:\n")
    for info in registry.list_agent_info():
        print(f"  📦 {info['name']}")
        print(f"     类: {info['class']}")
        print(f"     角色: {info['role']}")
        print(f"     模型: {info['model']}")
        print(f"     描述: {info['description']}")
        print()

    # 获取 Agent
    print("3. 获取特定 Agent:\n")
    agent_info = registry.get("test1")
    if agent_info:
        print(f"  ✅ 找到 Agent: {agent_info}")
        print(f"  配置: {agent_info.config}")

    # 检查注册状态
    print(f"\n4. 检查注册状态:")
    print(f"  test1 已注册: {registry.is_registered('test1')}")
    print(f"  test3 已注册: {registry.is_registered('test3')}")

    # Agent 数量
    print(f"\n5. Agent 数量: {registry.count()}")

    # 注销 Agent
    print(f"\n6. 注销 test1...")
    registry.unregister("test1")
    print(f"  剩余 Agent: {registry.list_agents()}")
    print(f"  Agent 数量: {registry.count()}")
