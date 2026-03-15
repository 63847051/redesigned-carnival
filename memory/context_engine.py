"""
OpenClaw ContextEngine 接口实现

基于 OpenClaw 3.7+ 的 ContextEngine 插件接口
提供完整的生命周期管理：bootstrap, ingest, assemble, compact, afterTurn

参考文档:
- https://www.shareuhack.com/en/posts/openclaw-v2026-3-7-contextengine-guide
- https://openclaws.io/blog/openclaw-contextengine-deep-dive/
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """记忆类型枚举"""

    SHORT_TERM = "short_term"  # 短期记忆 - 当前会话
    LONG_TERM = "long_term"  # 长期记忆 - 持久化
    EPISODIC = "episodic"  # 情景记忆 - 事件序列
    PROCEDURAL = "procedural"  # 程序记忆 - 技能/习惯


class ImportanceLevel(Enum):
    """重要性级别"""

    CRITICAL = 5  # 关键信息 - 决策/偏好/规则
    HIGH = 4  # 高重要性 - 项目/任务
    MEDIUM = 3  # 中等重要性 - 常规信息
    LOW = 2  # 低重要性 - 闲聊/临时
    MINIMAL = 1  # 最小重要性 - 可遗忘


@dataclass
class TokenBudget:
    """Token预算"""

    hard_limit: int  # 硬性限制
    soft_limit: int  # 软性限制（建议值）
    current_usage: int = 0  # 当前使用量

    @property
    def remaining(self) -> int:
        return self.hard_limit - self.current_usage

    @property
    def usage_ratio(self) -> float:
        if self.hard_limit == 0:
            return 0.0
        return self.current_usage / self.hard_limit


@dataclass
class Message:
    """消息结构"""

    id: str
    role: str  # user/assistant/system/tool
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class Turn:
    """对话轮次"""

    turn_id: str
    user_message: Message
    assistant_message: Optional[Message] = None
    tool_results: List[Message] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AssembledContext:
    """组装后的上下文"""

    system: str = ""
    messages: List[Message] = field(default_factory=list)
    token_estimate: int = 0
    memory_injected: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryEntry:
    """记忆条目"""

    id: str
    content: str
    memory_type: MemoryType
    importance: ImportanceLevel
    tags: List[str] = field(default_factory=list)
    source_turn_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "importance": self.importance.value,
            "tags": self.tags,
            "source_turn_id": self.source_turn_id,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "metadata": self.metadata,
        }


@runtime_checkable
class ContextEngineConfig(Protocol):
    """ContextEngine配置协议"""

    app_token: Optional[str]
    table_id: Optional[str]
    enable_feishu: bool
    max_short_term: int
    max_long_term: int
    compaction_threshold: float
    persistence_interval: int


class ContextEngine(ABC):
    """
    ContextEngine 抽象基类

    实现 OpenClaw 3.7+ 的 ContextEngine 插件接口
    提供完整的生命周期管理
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化ContextEngine

        参数:
            config: 配置字典
        """
        self.config = config or {}
        self._initialized = False
        self._session_id: Optional[str] = None
        self._message_count = 0

        logger.info(f"ContextEngine initialized with config: {self.config}")

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    async def bootstrap(self) -> None:
        """
        Bootstrap: Engine初始化

        在引擎启动时调用：
        - 加载持久化状态
        - 建立数据库连接
        - 恢复会话记忆

        OpenClaw调用时机: Gateway启动时
        """
        logger.info("ContextEngine: bootstrap started")
        try:
            await self._load_persisted_state()
            await self._connect_storage()
            await self._restore_session_memory()
            self._initialized = True
            logger.info("ContextEngine: bootstrap completed successfully")
        except Exception as e:
            logger.error(f"ContextEngine: bootstrap failed: {str(e)}")
            raise

    async def ingest(self, message: Message) -> None:
        """
        Ingest: 新消息到达

        当新消息到达时调用：
        - 预处理消息
        - 分类/标记重要性
        - 决定是否需要记忆

        参数:
            message: 新到达的消息

        OpenClaw调用时机: 每次新消息时
        """
        if not self._initialized:
            logger.warning(
                "ContextEngine: ingest called before bootstrap, initializing now"
            )
            await self.bootstrap()

        self._message_count += 1
        logger.debug(
            f"ContextEngine: ingesting message {message.id}, role={message.role}"
        )

        try:
            await self._preprocess_message(message)
            importance = await self._assess_importance(message)
            await self._store_message(message, importance)
        except Exception as e:
            logger.error(
                f"ContextEngine: ingest failed for message {message.id}: {str(e)}"
            )
            raise

    async def assemble(self, budget: TokenBudget) -> AssembledContext:
        """
        Assemble: 上下文组装

        在每次模型调用前调用：
        - 决定哪些内容进入最终prompt
        - 检索相关记忆
        - 构建系统提示

        参数:
            budget: Token预算

        返回:
            AssembledContext: 组装后的上下文

        OpenClaw调用时机: 每次模型调用前
        """
        if not self._initialized:
            logger.warning(
                "ContextEngine: assemble called before bootstrap, initializing now"
            )
            await self.bootstrap()

        logger.debug(
            f"ContextEngine: assembling context, "
            f"budget={budget.hard_limit}, current={budget.current_usage}"
        )

        try:
            system_context = await self._build_system_context(budget)
            relevant_memories = await self._retrieve_relevant_memories(budget)
            conversation_history = await self._get_conversation_history(budget)

            assembled = AssembledContext(
                system=system_context,
                messages=conversation_history,
                token_estimate=budget.current_usage,
                memory_injected=[m.id for m in relevant_memories],
            )

            logger.debug(
                f"ContextEngine: assembled context with "
                f"{len(conversation_history)} messages, {len(relevant_memories)} memories"
            )

            return assembled

        except Exception as e:
            logger.error(f"ContextEngine: assemble failed: {str(e)}")
            raise

    async def compact(self) -> int:
        """
        Compact: 上下文压缩

        当Token接近限制时调用：
        - 压缩/摘要旧对话
        - 清理不重要记忆
        - 释放Token空间

        返回:
            int: 压缩后释放的Token数

        OpenClaw调用时机: Token超过阈值时
        """
        if not self._initialized:
            logger.warning("ContextEngine: compact called before bootstrap")
            return 0

        logger.info("ContextEngine: compact started")

        try:
            compacted_count = await self._compress_conversation_history()
            cleaned_count = await self._cleanup_low_importance_memories()
            total_freed = compacted_count + cleaned_count

            logger.info(
                f"ContextEngine: compact completed, "
                f"freed approximately {total_freed} tokens"
            )

            return total_freed

        except Exception as e:
            logger.error(f"ContextEngine: compact failed: {str(e)}")
            raise

    async def afterTurn(self, turn: Turn) -> None:
        """
        AfterTurn: 轮次后处理

        在每个对话轮次完成后调用：
        - 持久化状态
        - 更新索引
        - 提取重要信息到长期记忆

        参数:
            turn: 完成的对话轮次

        OpenClaw调用时机: 每个对话轮次完成后
        """
        if not self._initialized:
            logger.warning("ContextEngine: afterTurn called before bootstrap")
            return

        logger.debug(f"ContextEngine: afterTurn for turn {turn.turn_id}")

        try:
            await self._extract_learning(turn)
            await self._persist_state()
            await self._update_memory_index(turn)
        except Exception as e:
            logger.error(
                f"ContextEngine: afterTurn failed for turn {turn.turn_id}: {str(e)}"
            )
            raise

    async def prepareSubagentSpawn(self, parent_context: Any) -> Dict[str, Any]:
        """
        PrepareSubagentSpawn: 子Agent生成前

        在创建子Agent前调用：
        - 准备隔离的上下文范围
        - 决定子Agent能看到什么

        参数:
            parent_context: 父上下文

        返回:
            Dict: 子Agent的上下文配置

        OpenClaw调用时机: 子Agent生成前
        """
        logger.debug("ContextEngine: prepareSubagentSpawn")

        try:
            subagent_config = await self._prepare_subagent_context(parent_context)
            return subagent_config
        except Exception as e:
            logger.error(f"ContextEngine: prepareSubagentSpawn failed: {str(e)}")
            raise

    async def onSubagentEnded(self, result: Any) -> None:
        """
        OnSubagentEnded: 子Agent结束后

        在子Agent完成后调用：
        - 收集子Agent输出
        - 合并回主上下文

        参数:
            result: 子Agent执行结果

        OpenClaw调用时机: 子Agent完成后
        """
        logger.debug("ContextEngine: onSubagentEnded")

        try:
            await self._merge_subagent_result(result)
        except Exception as e:
            logger.error(f"ContextEngine: onSubagentEnded failed: {str(e)}")
            raise

    async def shutdown(self) -> None:
        """
        关闭引擎

        在引擎关闭时调用：
        - 保存最终状态
        - 关闭连接
        - 清理资源
        """
        logger.info("ContextEngine: shutdown started")

        try:
            await self._persist_state()
            await self._close_storage()
            self._initialized = False
            logger.info("ContextEngine: shutdown completed")
        except Exception as e:
            logger.error(f"ContextEngine: shutdown failed: {str(e)}")
            raise

    # ========== 抽象方法 ==========

    @abstractmethod
    async def _load_persisted_state(self) -> None:
        """加载持久化状态"""
        pass

    @abstractmethod
    async def _connect_storage(self) -> None:
        """连接存储"""
        pass

    @abstractmethod
    async def _restore_session_memory(self) -> None:
        """恢复会话记忆"""
        pass

    @abstractmethod
    async def _preprocess_message(self, message: Message) -> None:
        """预处理消息"""
        pass

    @abstractmethod
    async def _assess_importance(self, message: Message) -> ImportanceLevel:
        """评估消息重要性"""
        pass

    @abstractmethod
    async def _store_message(
        self, message: Message, importance: ImportanceLevel
    ) -> None:
        """存储消息"""
        pass

    @abstractmethod
    async def _build_system_context(self, budget: TokenBudget) -> str:
        """构建系统上下文"""
        pass

    @abstractmethod
    async def _retrieve_relevant_memories(
        self, budget: TokenBudget
    ) -> List[MemoryEntry]:
        """检索相关记忆"""
        pass

    @abstractmethod
    async def _get_conversation_history(self, budget: TokenBudget) -> List[Message]:
        """获取对话历史"""
        pass

    @abstractmethod
    async def _compress_conversation_history(self) -> int:
        """压缩对话历史"""
        pass

    @abstractmethod
    async def _cleanup_low_importance_memories(self) -> int:
        """清理低重要性记忆"""
        pass

    @abstractmethod
    async def _extract_learning(self, turn: Turn) -> None:
        """提取学习内容"""
        pass

    @abstractmethod
    async def _persist_state(self) -> None:
        """持久化状态"""
        pass

    @abstractmethod
    async def _update_memory_index(self, turn: Turn) -> None:
        """更新记忆索引"""
        pass

    @abstractmethod
    async def _prepare_subagent_context(self, parent_context: Any) -> Dict[str, Any]:
        """准备子Agent上下文"""
        pass

    @abstractmethod
    async def _merge_subagent_result(self, result: Any) -> None:
        """合并子Agent结果"""
        pass

    @abstractmethod
    async def _close_storage(self) -> None:
        """关闭存储"""
        pass


class LegacyContextEngine(ContextEngine):
    """
    LegacyContextEngine - 保留原有行为的ContextEngine

    作为默认引擎，保持与之前版本相同的压缩行为
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._short_term_messages: List[Message] = []
        self._long_term_memories: List[MemoryEntry] = []
        self._compressed_summaries: List[str] = []

    async def _load_persisted_state(self) -> None:
        logger.info("LegacyContextEngine: loading persisted state")
        # 加载持久化的记忆
        pass

    async def _connect_storage(self) -> None:
        logger.info("LegacyContextEngine: connecting storage")
        pass

    async def _restore_session_memory(self) -> None:
        logger.info("LegacyContextEngine: restoring session memory")
        pass

    async def _preprocess_message(self, message: Message) -> None:
        self._short_term_messages.append(message)

    async def _assess_importance(self, message: Message) -> ImportanceLevel:
        # 简单的重要性评估
        if message.role == "system":
            return ImportanceLevel.CRITICAL
        elif message.role == "user":
            content_lower = message.content.lower()
            if any(
                kw in content_lower for kw in ["记住", "不要忘记", "重要", "记住这个"]
            ):
                return ImportanceLevel.HIGH
            return ImportanceLevel.MEDIUM
        return ImportanceLevel.LOW

    async def _store_message(
        self, message: Message, importance: ImportanceLevel
    ) -> None:
        # 存储到对应类型的记忆中
        if importance.value >= ImportanceLevel.HIGH.value:
            entry = MemoryEntry(
                id=message.id,
                content=message.content,
                memory_type=MemoryType.LONG_TERM,
                importance=importance,
            )
            self._long_term_memories.append(entry)

    async def _build_system_context(self, budget: TokenBudget) -> str:
        return ""

    async def _retrieve_relevant_memories(
        self, budget: TokenBudget
    ) -> List[MemoryEntry]:
        return []

    async def _get_conversation_history(self, budget: TokenBudget) -> List[Message]:
        return self._short_term_messages[-20:]  # 保留最近20条

    async def _compress_conversation_history(self) -> int:
        # 简单的摘要压缩
        if len(self._short_term_messages) > 10:
            summary = f"[{len(self._short_term_messages)}条消息已压缩]"
            self._compressed_summaries.append(summary)
            self._short_term_messages = self._short_term_messages[-10:]
            return 1000
        return 0

    async def _cleanup_low_importance_memories(self) -> int:
        before = len(self._long_term_memories)
        self._long_term_memories = [
            m
            for m in self._long_term_memories
            if m.importance.value >= ImportanceLevel.LOW.value
        ]
        return before - len(self._long_term_memories)

    async def _extract_learning(self, turn: Turn) -> None:
        pass

    async def _persist_state(self) -> None:
        logger.debug("LegacyContextEngine: persisting state")

    async def _update_memory_index(self, turn: Turn) -> None:
        pass

    async def _prepare_subagent_context(self, parent_context: Any) -> Dict[str, Any]:
        return {"memory": self._short_term_messages[-5:]}

    async def _merge_subagent_result(self, result: Any) -> None:
        pass

    async def _close_storage(self) -> None:
        logger.info("LegacyContextEngine: closing storage")
