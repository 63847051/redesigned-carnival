"""
记忆管理器模块

提供基于 OpenClaw ContextEngine 接口的记忆管理系统
集成飞书 Bitable 进行云端持久化存储
"""

import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .context_engine import (
    ContextEngine,
    ImportanceLevel,
    LegacyContextEngine,
    MemoryEntry,
    MemoryType,
    Message,
    TokenBudget,
    Turn,
)

logger = logging.getLogger(__name__)


class MemoryManagerError(Exception):
    """记忆管理器基础异常"""

    pass


class MemoryStorageError(MemoryManagerError):
    """存储异常"""

    pass


class MemoryRetrievalError(MemoryManagerError):
    """检索异常"""

    pass


class FeishuMemoryBitable:
    """
    飞书记忆多维表格管理器

    用于存储和管理长期记忆的飞书多维表格
    """

    BASE_URL = "https://open.feishu.cn/open-apis/bitable/v1"

    # 字段映射
    FIELD_CONTENT = "内容"
    FIELD_TYPE = "类型"
    FIELD_IMPORTANCE = "重要性"
    FIELD_TAGS = "标签"
    FIELD_SOURCE = "来源"
    FIELD_CREATED = "创建时间"
    FIELD_ACCESSED = "最后访问"
    FIELD_ACCESS_COUNT = "访问次数"

    # 记忆类型映射
    MEMORY_TYPE_MAP = {
        "短期记忆": MemoryType.SHORT_TERM,
        "长期记忆": MemoryType.LONG_TERM,
        "情景记忆": MemoryType.EPISODIC,
        "程序记忆": MemoryType.PROCEDURAL,
    }

    IMPORTANCE_MAP = {
        "关键": ImportanceLevel.CRITICAL,
        "高": ImportanceLevel.HIGH,
        "中": ImportanceLevel.MEDIUM,
        "低": ImportanceLevel.LOW,
        "最小": ImportanceLevel.MINIMAL,
    }

    def __init__(
        self,
        app_token: Optional[str] = None,
        table_id: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        """
        初始化飞书记忆管理器

        参数:
            app_token: Bitable app token
            table_id: Table ID
            access_token: 飞书访问令牌
        """
        self.app_token = app_token or os.getenv("FEISHU_APP_TOKEN")
        self.table_id = table_id or os.getenv("FEISHU_MEMORY_TABLE_ID")
        self._access_token = access_token or os.getenv("FEISHU_ACCESS_TOKEN")
        self._bitable_manager = None

        if self.app_token and self.table_id:
            self._init_bitable_manager()

    def _init_bitable_manager(self) -> None:
        """初始化飞书多维表格管理器"""
        try:
            # 延迟导入避免循环依赖
            import sys
            from pathlib import Path

            # 尝试从多个路径导入
            possible_paths = [
                Path("/root/.openclaw/workspace/skills/feishu-worklog"),
                Path("/root/.openclaw/workspace"),
            ]

            for path in possible_paths:
                bitable_path = path / "bitable_manager.py"
                if bitable_path.exists():
                    sys.path.insert(0, str(path))
                    from bitable_manager import BitableManager

                    self._bitable_manager = BitableManager(
                        self.app_token, self.table_id
                    )
                    if self._access_token:
                        self._bitable_manager.set_access_token(self._access_token)
                    logger.info(
                        f"FeishuMemoryBitable initialized with app_token={self._mask(self.app_token)}"
                    )
                    return

            logger.warning("bitable_manager.py not found, feishu integration disabled")

        except ImportError as e:
            logger.warning(f"Failed to import bitable_manager: {e}")
        except Exception as e:
            logger.warning(f"Failed to initialize bitable manager: {e}")

    def _mask(self, token: str) -> str:
        if len(token) <= 8:
            return "***"
        return f"{token[:4]}...{token[-4:]}"

    def is_available(self) -> bool:
        return self._bitable_manager is not None

    def add_memory(self, entry: MemoryEntry) -> bool:
        """
        添加记忆条目

        参数:
            entry: 记忆条目

        返回:
            bool: 是否成功
        """
        if not self.is_available():
            logger.debug("Feishu Bitable not available, skipping")
            return False

        try:
            fields = {
                self.FIELD_CONTENT: entry.content,
                self.FIELD_TYPE: self._get_type_name(entry.memory_type),
                self.FIELD_IMPORTANCE: self._get_importance_name(entry.importance),
                self.FIELD_TAGS: ",".join(entry.tags),
                self.FIELD_SOURCE: entry.source_turn_id or "",
                self.FIELD_CREATED: entry.created_at.isoformat(),
                self.FIELD_ACCESSED: entry.last_accessed.isoformat(),
                self.FIELD_ACCESS_COUNT: entry.access_count,
            }

            self._bitable_manager.add_record(
                content=entry.content,
                project_type=self._get_type_name(entry.memory_type),
                priority=self._get_importance_name(entry.importance),
                status="长期记忆",
                note=f"tags:{','.join(entry.tags)}",
            )

            logger.info(f"Memory entry added to feishu: {entry.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to add memory to feishu: {e}")
            return False

    def search_memories(
        self,
        keyword: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        importance: Optional[ImportanceLevel] = None,
        limit: int = 20,
    ) -> List[MemoryEntry]:
        """
        搜索记忆

        参数:
            keyword: 关键词
            memory_type: 记忆类型
            importance: 重要性
            limit: 返回数量限制

        返回:
            List[MemoryEntry]: 记忆条目列表
        """
        if not self.is_available():
            return []

        try:
            filters = {}
            if keyword:
                filters["keyword"] = keyword

            records = self._bitable_manager.query_records(filters=filters)

            results = []
            for record in records[:limit]:
                fields = record.get("fields", {})
                entry = self._record_to_entry(record)
                if entry:
                    results.append(entry)

            return results

        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []

    def update_access(self, entry_id: str) -> bool:
        """更新访问记录"""
        # 简化实现
        return True

    def _get_type_name(self, memory_type: MemoryType) -> str:
        type_names = {
            MemoryType.SHORT_TERM: "短期记忆",
            MemoryType.LONG_TERM: "长期记忆",
            MemoryType.EPISODIC: "情景记忆",
            MemoryType.PROCEDURAL: "程序记忆",
        }
        return type_names.get(memory_type, "长期记忆")

    def _get_importance_name(self, importance: ImportanceLevel) -> str:
        importance_names = {
            ImportanceLevel.CRITICAL: "关键",
            ImportanceLevel.HIGH: "高",
            ImportanceLevel.MEDIUM: "中",
            ImportanceLevel.LOW: "低",
            ImportanceLevel.MINIMAL: "最小",
        }
        return importance_names.get(importance, "中")

    def _record_to_entry(self, record: Dict) -> Optional[MemoryEntry]:
        """将飞书记录转换为记忆条目"""
        try:
            fields = record.get("fields", {})

            content = fields.get(self.FIELD_CONTENT, "")
            type_str = fields.get(self.FIELD_TYPE, "长期记忆")
            importance_str = fields.get(self.FIELD_IMPORTANCE, "中")

            memory_type = self.MEMORY_TYPE_MAP.get(type_str, MemoryType.LONG_TERM)
            importance = self.IMPORTANCE_MAP.get(importance_str, ImportanceLevel.MEDIUM)

            return MemoryEntry(
                id=record.get("record_id", str(uuid.uuid4())),
                content=content,
                memory_type=memory_type,
                importance=importance,
                tags=fields.get(self.FIELD_TAGS, "").split(","),
                created_at=datetime.now(),
                last_accessed=datetime.now(),
            )

        except Exception as e:
            logger.warning(f"Failed to convert record to entry: {e}")
            return None


class FileMemoryStorage:
    """
    文件记忆存储

    用于本地文件系统的记忆存储
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        初始化文件存储

        参数:
            storage_path: 存储路径
        """
        self.storage_path = Path(storage_path or "/root/.openclaw/workspace/memory")
        self.short_term_path = self.storage_path / "short-term"
        self.long_term_path = self.storage_path / "long-term"
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """确保目录存在"""
        self.short_term_path.mkdir(parents=True, exist_ok=True)
        self.long_term_path.mkdir(parents=True, exist_ok=True)

    def save_memory(self, entry: MemoryEntry) -> bool:
        """
        保存记忆条目

        参数:
            entry: 记忆条目

        返回:
            bool: 是否成功
        """
        try:
            if entry.memory_type == MemoryType.SHORT_TERM:
                file_path = self.short_term_path / f"{entry.id}.json"
            else:
                file_path = self.long_term_path / f"{entry.id}.json"

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(entry.to_dict(), f, ensure_ascii=False, indent=2)

            logger.debug(f"Memory saved: {entry.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save memory {entry.id}: {e}")
            return False

    def load_memory(
        self, memory_id: str, memory_type: MemoryType
    ) -> Optional[MemoryEntry]:
        """
        加载记忆条目

        参数:
            memory_id: 记忆ID
            memory_type: 记忆类型

        返回:
            Optional[MemoryEntry]: 记忆条目
        """
        try:
            if memory_type == MemoryType.SHORT_TERM:
                file_path = self.short_term_path / f"{memory_id}.json"
            else:
                file_path = self.long_term_path / f"{memory_id}.json"

            if not file_path.exists():
                return None

            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            return self._dict_to_entry(data)

        except Exception as e:
            logger.error(f"Failed to load memory {memory_id}: {e}")
            return None

    def search_memories(
        self,
        keyword: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        limit: int = 20,
    ) -> List[MemoryEntry]:
        """
        搜索记忆

        参数:
            keyword: 关键词
            memory_type: 记忆类型
            limit: 返回数量限制

        返回:
            List[MemoryEntry]: 记忆条目列表
        """
        results = []

        search_paths = []
        if memory_type == MemoryType.SHORT_TERM:
            search_paths.append(self.short_term_path)
        elif memory_type == MemoryType.LONG_TERM:
            search_paths.append(self.long_term_path)
        else:
            search_paths = [self.short_term_path, self.long_term_path]

        for search_path in search_paths:
            if not search_path.exists():
                continue

            for file_path in search_path.glob("*.json"):
                try:
                    with open(file_path, encoding="utf-8") as f:
                        data = json.load(f)

                    entry = self._dict_to_entry(data)
                    if entry:
                        if keyword and keyword.lower() not in entry.content.lower():
                            continue
                        results.append(entry)

                except Exception as e:
                    logger.warning(f"Failed to read {file_path}: {e}")

                if len(results) >= limit:
                    break

        results.sort(key=lambda x: x.last_accessed, reverse=True)
        return results[:limit]

    def delete_memory(self, memory_id: str, memory_type: MemoryType) -> bool:
        """
        删除记忆

        参数:
            memory_id: 记忆ID
            memory_type: 记忆类型

        返回:
            bool: 是否成功
        """
        try:
            if memory_type == MemoryType.SHORT_TERM:
                file_path = self.short_term_path / f"{memory_id}.json"
            else:
                file_path = self.long_term_path / f"{memory_id}.json"

            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Memory deleted: {memory_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False

    def list_memories(
        self,
        memory_type: Optional[MemoryType] = None,
        limit: int = 100,
    ) -> List[MemoryEntry]:
        """
        列出记忆

        参数:
            memory_type: 记忆类型
            limit: 返回数量限制

        返回:
            List[MemoryEntry]: 记忆条目列表
        """
        results = []

        search_paths = []
        if memory_type == MemoryType.SHORT_TERM:
            search_paths.append(self.short_term_path)
        elif memory_type == MemoryType.LONG_TERM:
            search_paths.append(self.long_term_path)
        else:
            search_paths = [self.short_term_path, self.long_term_path]

        for search_path in search_paths:
            if not search_path.exists():
                continue

            for file_path in sorted(
                search_path.glob("*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )[:limit]:
                try:
                    with open(file_path, encoding="utf-8") as f:
                        data = json.load(f)

                    entry = self._dict_to_entry(data)
                    if entry:
                        results.append(entry)

                except Exception as e:
                    logger.warning(f"Failed to read {file_path}: {e}")

        return results

    def _dict_to_entry(self, data: Dict) -> Optional[MemoryEntry]:
        """将字典转换为记忆条目"""
        try:
            return MemoryEntry(
                id=data["id"],
                content=data["content"],
                memory_type=MemoryType(data["memory_type"]),
                importance=ImportanceLevel(data["importance"]),
                tags=data.get("tags", []),
                source_turn_id=data.get("source_turn_id"),
                created_at=datetime.fromisoformat(data["created_at"]),
                last_accessed=datetime.fromisoformat(data["last_accessed"]),
                access_count=data.get("access_count", 0),
                metadata=data.get("metadata", {}),
            )
        except Exception as e:
            logger.warning(f"Failed to convert dict to entry: {e}")
            return None


class EnhancedContextEngine(ContextEngine):
    """
    增强型ContextEngine

    实现完整的ContextEngine接口并集成:
    - 本地文件存储
    - 飞书Bitable云端存储
    - 智能记忆管理
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

        # 存储
        self._file_storage = FileMemoryStorage(
            config.get("storage_path") if config else None
        )

        # 飞书集成
        self._feishu = (
            FeishuMemoryBitable(
                app_token=config.get("feishu_app_token") if config else None,
                table_id=config.get("feishu_table_id") if config else None,
                access_token=config.get("feishu_access_token") if config else None,
            )
            if config and config.get("enable_feishu")
            else None
        )

        # 内存缓存
        self._short_term_cache: List[MemoryEntry] = []
        self._message_history: List[Message] = []

        # 配置
        self._max_short_term = config.get("max_short_term", 100) if config else 100
        self._max_long_term = config.get("max_long_term", 1000) if config else 1000

        logger.info(
            f"EnhancedContextEngine initialized, "
            f"feishu_available={self._feishu.is_available() if self._feishu else False}"
        )

    async def _load_persisted_state(self) -> None:
        logger.info("EnhancedContextEngine: loading persisted state")

        # 从文件加载长期记忆
        long_term_memories = self._file_storage.list_memories(
            memory_type=MemoryType.LONG_TERM, limit=self._max_long_term
        )

        logger.info(f"Loaded {len(long_term_memories)} long-term memories")

    async def _connect_storage(self) -> None:
        logger.info("EnhancedContextEngine: connecting storage")

        if self._feishu and self._feishu.is_available():
            logger.info("Feishu Bitable connected")

    async def _restore_session_memory(self) -> None:
        logger.info("EnhancedContextEngine: restoring session memory")

        # 从飞书恢复最近的会话记忆
        if self._feishu and self._feishu.is_available():
            recent_memories = self._feishu.search_memories(
                memory_type=MemoryType.SHORT_TERM, limit=50
            )
            self._short_term_cache.extend(recent_memories)
            logger.info(f"Restored {len(recent_memories)} session memories from feishu")

    async def _preprocess_message(self, message: Message) -> None:
        self._message_history.append(message)

    async def _assess_importance(self, message: Message) -> ImportanceLevel:
        content = message.content.lower()

        # 关键规则相关
        if "确认" in content or "确认执行" in content:
            return ImportanceLevel.CRITICAL

        # 决策相关
        if any(kw in content for kw in ["记住", "不要忘记", "重要", "偏好", "决定"]):
            return ImportanceLevel.HIGH

        # 用户信息
        if message.role == "user":
            return ImportanceLevel.MEDIUM

        # 工具结果
        if message.role == "tool":
            if len(message.content) > 500:
                return ImportanceLevel.MEDIUM
            return ImportanceLevel.LOW

        return ImportanceLevel.LOW

    async def _store_message(
        self, message: Message, importance: ImportanceLevel
    ) -> None:
        entry = MemoryEntry(
            id=message.id or str(uuid.uuid4()),
            content=message.content,
            memory_type=MemoryType.SHORT_TERM,
            importance=importance,
            source_turn_id=self._session_id,
            tags=self._extract_tags(message.content),
        )

        # 添加到缓存
        self._short_term_cache.append(entry)

        # 持久化
        self._file_storage.save_memory(entry)

        # 同步到飞书（如果是重要记忆）
        if importance.value >= ImportanceLevel.HIGH.value:
            if self._feishu and self._feishu.is_available():
                self._feishu.add_memory(entry)

    def _extract_tags(self, content: str) -> List[str]:
        """提取内容标签"""
        tags = []

        keyword_tags = {
            "设计": ["设计"],
            "开发": ["技术", "开发"],
            "项目": ["项目"],
            "规则": ["规则", "关键规则"],
            "偏好": ["偏好", "喜欢"],
            "任务": ["任务", "待办"],
        }

        content_lower = content.lower()
        for keyword, tag_list in keyword_tags.items():
            if keyword in content_lower:
                tags.extend(tag_list)

        return list(set(tags))

    async def _build_system_context(self, budget: TokenBudget) -> str:
        # 构建系统提示
        soul_path = Path("/root/.openclaw/workspace/SOUL.md")
        if soul_path.exists():
            with open(soul_path, encoding="utf-8") as f:
                return f.read()[: int(budget.soft_limit * 0.1)]
        return ""

    async def _retrieve_relevant_memories(
        self, budget: TokenBudget
    ) -> List[MemoryEntry]:
        # 搜索相关记忆
        memories = self._file_storage.search_memories(
            memory_type=MemoryType.LONG_TERM, limit=10
        )

        # 更新访问记录
        for memory in memories:
            memory.access_count += 1
            memory.last_accessed = datetime.now()
            self._file_storage.save_memory(memory)

        return memories

    async def _get_conversation_history(self, budget: TokenBudget) -> List[Message]:
        # 保留最近的对话
        max_messages = min(len(self._message_history), 20)
        return self._message_history[-max_messages:]

    async def _compress_conversation_history(self) -> int:
        # 压缩旧对话
        if len(self._short_term_cache) > self._max_short_term // 2:
            # 将部分短期记忆转为长期记忆
            for entry in self._short_term_cache[:-10]:
                if entry.importance.value >= ImportanceLevel.MEDIUM.value:
                    long_term_entry = MemoryEntry(
                        id=str(uuid.uuid4()),
                        content=entry.content,
                        memory_type=MemoryType.LONG_TERM,
                        importance=entry.importance,
                        tags=entry.tags,
                        source_turn_id=entry.source_turn_id,
                    )
                    self._file_storage.save_memory(long_term_entry)

                    if self._feishu and self._feishu.is_available():
                        self._feishu.add_memory(long_term_entry)

            # 清理短期缓存
            self._short_term_cache = self._short_term_cache[-10:]

            return 2000

        return 0

    async def _cleanup_low_importance_memories(self) -> int:
        before = len(self._short_term_cache)

        # 删除访问次数低且不重要的记忆
        to_keep = []
        for entry in self._short_term_cache:
            if (
                entry.importance.value >= ImportanceLevel.LOW.value
                or entry.access_count > 5
            ):
                to_keep.append(entry)
            else:
                self._file_storage.delete_memory(entry.id, entry.memory_type)

        self._short_term_cache = to_keep
        return before - len(self._short_term_cache)

    async def _extract_learning(self, turn: Turn) -> None:
        # 从对话中提取学习内容
        user_content = turn.user_message.content

        # 简单的关键信息提取
        if any(kw in user_content for kw in ["记住", "不要忘记"]):
            entry = MemoryEntry(
                id=str(uuid.uuid4()),
                content=user_content,
                memory_type=MemoryType.LONG_TERM,
                importance=ImportanceLevel.HIGH,
                tags=["学习"],
                source_turn_id=turn.turn_id,
            )
            self._file_storage.save_memory(entry)

            if self._feishu and self._feishu.is_available():
                self._feishu.add_memory(entry)

    async def _persist_state(self) -> None:
        logger.debug("EnhancedContextEngine: persisting state")

        # 持久化所有缓存的记忆
        for entry in self._short_term_cache:
            self._file_storage.save_memory(entry)

    async def _update_memory_index(self, turn: Turn) -> None:
        # 更新索引
        pass

    async def _prepare_subagent_context(self, parent_context: Any) -> Dict[str, Any]:
        return {
            "memory": self._short_term_cache[-5:],
            "session_id": self._session_id,
        }

    async def _merge_subagent_result(self, result: Any) -> None:
        # 合并子Agent结果
        pass

    async def _close_storage(self) -> None:
        logger.info("EnhancedContextEngine: closing storage")

        # 确保状态已保存
        await self._persist_state()


def create_context_engine(
    config: Optional[Dict[str, Any]] = None,
    use_legacy: bool = False,
) -> ContextEngine:
    """
    创建ContextEngine实例

    参数:
        config: 配置字典
        use_legacy: 是否使用LegacyContextEngine

    返回:
        ContextEngine: ContextEngine实例
    """
    if use_legacy:
        logger.info("Using LegacyContextEngine")
        return LegacyContextEngine(config)

    logger.info("Using EnhancedContextEngine")
    return EnhancedContextEngine(config)


# 导出
__all__ = [
    "ContextEngine",
    "LegacyContextEngine",
    "EnhancedContextEngine",
    "MemoryManager",
    "MemoryEntry",
    "MemoryType",
    "ImportanceLevel",
    "Message",
    "Turn",
    "TokenBudget",
    "FeishuMemoryBitable",
    "FileMemoryStorage",
    "create_context_engine",
]


# 为向后兼容保留旧名称
MemoryManager = EnhancedContextEngine
