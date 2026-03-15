"""
记忆可视化仪表板模块

提供记忆记录的增删改查、统计和可视化功能
"""

import logging
import sys
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """记忆类型枚举"""

    LEARNING = "学习"
    IDEA = "想法"
    DECISION = "决策"
    KNOWLEDGE = "知识"
    TASK = "任务"
    MEETING = "会议"
    PROJECT = "项目"
    OTHER = "其他"


class ImportanceLevel(Enum):
    """重要性级别枚举"""

    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    MINIMAL = 1


class MemoryDashboardError(Exception):
    """记忆仪表板基础异常"""

    pass


class MemoryValidationError(MemoryDashboardError):
    """数据验证异常"""

    pass


class MemoryAPIError(MemoryDashboardError):
    """API调用异常"""

    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(message)
        self.code = code


class MemoryDashboard:
    """记忆可视化仪表板

    提供记忆记录的自动化管理和统计功能
    """

    # 默认飞书Bitable配置
    DEFAULT_APP_TOKEN = "BISAbNgYXa7Do1sc36YcBChInnS"

    # 记录表和统计表的table_id（需要用户创建后配置）
    RECORD_TABLE_ID = "tbl_memory_records"
    STATS_TABLE_ID = "tbl_memory_stats"

    def __init__(
        self,
        app_token: str = DEFAULT_APP_TOKEN,
        record_table_id: Optional[str] = None,
        stats_table_id: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        """初始化记忆仪表板

        参数:
            app_token: 飞书Bitable app token
            record_table_id: 记录表table_id
            stats_table_id: 统计表table_id
            access_token: 飞书访问令牌
        """
        self.app_token = app_token
        self.record_table_id = record_table_id or self.RECORD_TABLE_ID
        self.stats_table_id = stats_table_id or self.STATS_TABLE_ID

        # 延迟导入bitable_manager，避免循环依赖
        BitableManager = None

        # 尝试多个可能的导入路径
        import_paths = [
            "skills.feishu_worklog.bitable_manager",
            "bitable_manager",
            "/root/.openclaw/workspace/skills/feishu-worklog/bitable_manager",
        ]

        for path in import_paths:
            try:
                if path.startswith("/"):
                    import importlib.util

                    spec = importlib.util.spec_from_file_location(
                        "bitable_manager", path + ".py"
                    )
                    if spec and spec.loader:
                        BitableManager = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(BitableManager)
                        BitableManager = BitableManager.BitableManager
                        break
                else:
                    from importlib import import_module

                    module = import_module(path)
                    BitableManager = module.BitableManager
                    break
            except (ImportError, AttributeError):
                continue

        if BitableManager is None:
            raise ImportError("Cannot import BitableManager from any known path")

        self._BitableManager = BitableManager

        self._record_manager: Optional[Any] = None
        self._stats_manager: Optional[Any] = None

        if access_token:
            self.set_access_token(access_token)

        logger.info(
            f"MemoryDashboard initialized: app_token={self._mask_token(app_token)}"
        )

    def _mask_token(self, token: str) -> str:
        """脱敏处理token"""
        if len(token) <= 8:
            return "***"
        return f"{token[:4]}...{token[-4:]}"

    @property
    def record_manager(self) -> Any:
        """获取记录表管理器"""
        if self._record_manager is None:
            self._record_manager = self._BitableManager(
                self.app_token, self.record_table_id
            )
            if self._access_token:
                self._record_manager.set_access_token(self._access_token)
        return self._record_manager

    @property
    def stats_manager(self) -> Any:
        """获取统计表管理器"""
        if self._stats_manager is None:
            self._stats_manager = self._BitableManager(
                self.app_token, self.stats_table_id
            )
            if self._access_token:
                self._stats_manager.set_access_token(self._access_token)
        return self._stats_manager

    def set_access_token(self, access_token: str) -> None:
        """设置访问令牌

        参数:
            access_token: 飞书访问令牌
        """
        self._access_token = access_token
        # 清除现有管理器，强制重新创建
        self._record_manager = None
        self._stats_manager = None
        logger.info("Access token set successfully")

    def _normalize_memory_type(self, memory_type: str) -> str:
        """标准化记忆类型"""
        type_mapping = {
            "学习": MemoryType.LEARNING.value,
            "想法": MemoryType.IDEA.value,
            "决策": MemoryType.DECISION.value,
            "知识": MemoryType.KNOWLEDGE.value,
            "任务": MemoryType.TASK.value,
            "会议": MemoryType.MEETING.value,
            "项目": MemoryType.PROJECT.value,
            "其他": MemoryType.OTHER.value,
        }
        return type_mapping.get(memory_type, MemoryType.OTHER.value)

    def _normalize_importance(self, importance: Union[str, int]) -> int:
        """标准化重要性级别"""
        if isinstance(importance, int):
            if 1 <= importance <= 5:
                return importance
            return ImportanceLevel.MEDIUM.value

        importance_mapping = {
            "critical": ImportanceLevel.CRITICAL.value,
            "高": ImportanceLevel.HIGH.value,
            "中": ImportanceLevel.MEDIUM.value,
            "低": ImportanceLevel.LOW.value,
            "最低": ImportanceLevel.MINIMAL.value,
        }
        return importance_mapping.get(importance, ImportanceLevel.MEDIUM.value)

    def add_memory(
        self,
        content: str,
        memory_type: str = "学习",
        tags: Optional[List[str]] = None,
        importance: Union[str, int] = 3,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """添加记忆记录

        参数:
            content: 记忆内容
            memory_type: 记忆类型（学习/想法/决策/知识/任务/会议/项目/其他）
            tags: 标签列表
            importance: 重要性级别（1-5或描述性文字）
            metadata: 额外元数据

        返回:
            Dict: 创建的记录信息

        异常:
            MemoryValidationError: 当参数验证失败时
            MemoryAPIError: 当API调用失败时
        """
        if not content or not content.strip():
            raise MemoryValidationError("记忆内容不能为空")

        content = content.strip()
        memory_type = self._normalize_memory_type(memory_type)
        importance = self._normalize_importance(importance)
        tags = tags or []

        fields = {
            "内容": content,
            "类型": memory_type,
            "重要性": importance,
            "创建时间": datetime.now().isoformat(),
        }

        if tags:
            fields["标签"] = ",".join(tags)

        if metadata:
            fields["元数据"] = str(metadata)

        logger.info(
            f"Adding memory: type={memory_type}, importance={importance}, "
            f"content={content[:50]}..."
        )

        try:
            result = self.record_manager.add_record(
                content=content,
                project_type=memory_type,
                priority=str(importance),
                status="已完成",
                note=",".join(tags) if tags else "",
            )

            # 尝试添加到统计表
            try:
                self._update_daily_stats()
            except Exception as e:
                logger.warning(f"Failed to update daily stats: {e}")

            return {
                "success": True,
                "record_id": result.get("record_id"),
                "content": content,
                "memory_type": memory_type,
                "tags": tags,
                "importance": importance,
                "created_at": fields["创建时间"],
            }

        except Exception as e:
            logger.error(f"Failed to add memory: {str(e)}")
            raise MemoryAPIError(f"添加记忆失败: {str(e)}")

    def query_memories(
        self,
        memory_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        importance_min: Optional[int] = None,
        date_range: Optional[Dict[str, str]] = None,
        keyword: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """查询记忆记录

        参数:
            memory_type: 按类型筛选
            tags: 按标签筛选
            importance_min: 最低重要性筛选
            date_range: 日期范围 {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
            keyword: 关键词搜索
            limit: 返回数量限制

        返回:
            List[Dict]: 记忆记录列表
        """
        filters = {}

        if memory_type:
            filters["project_type"] = self._normalize_memory_type(memory_type)

        if keyword:
            filters["keyword"] = keyword

        if date_range:
            filters["date_range"] = date_range

        try:
            records = self.record_manager.query_records(filters=filters)

            # 客户端过滤（标签和重要性）
            filtered = []
            for record in records:
                fields = record.get("fields", {})

                # 标签过滤
                if tags:
                    record_tags = fields.get("标签", "").split(",")
                    if not any(tag in record_tags for tag in tags):
                        continue

                # 重要性过滤
                if importance_min is not None:
                    try:
                        record_importance = int(fields.get("优先级别", 0))
                        if record_importance < importance_min:
                            continue
                    except (ValueError, TypeError):
                        continue

                filtered.append(
                    {
                        "record_id": record.get("record_id"),
                        "content": fields.get("内容", ""),
                        "memory_type": fields.get("项目类型", ""),
                        "tags": fields.get("标签", "").split(",")
                        if fields.get("标签")
                        else [],
                        "importance": fields.get("优先级别", ""),
                        "status": fields.get("项目状态", ""),
                        "created_at": fields.get("创建日期", ""),
                    }
                )

            logger.info(f"Found {len(filtered)} memory records")
            return filtered[:limit]

        except Exception as e:
            logger.error(f"Failed to query memories: {str(e)}")
            raise MemoryAPIError(f"查询记忆失败: {str(e)}")

    def get_memory_by_id(self, record_id: str) -> Dict[str, Any]:
        """根据ID获取记忆记录

        参数:
            record_id: 记录ID

        返回:
            Dict: 记忆记录详情
        """
        try:
            record = self.record_manager.get_record_by_id(record_id)
            fields = record.get("fields", {})

            return {
                "record_id": record.get("record_id"),
                "content": fields.get("内容", ""),
                "memory_type": fields.get("项目类型", ""),
                "tags": fields.get("标签", "").split(",") if fields.get("标签") else [],
                "importance": fields.get("优先级别", ""),
                "status": fields.get("项目状态", ""),
                "created_at": fields.get("创建日期", ""),
                "note": fields.get("备注", ""),
            }

        except Exception as e:
            logger.error(f"Failed to get memory: {str(e)}")
            raise MemoryAPIError(f"获取记忆失败: {str(e)}")

    def update_memory(
        self,
        record_id: str,
        content: Optional[str] = None,
        memory_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        importance: Optional[Union[str, int]] = None,
    ) -> bool:
        """更新记忆记录

        参数:
            record_id: 记录ID
            content: 新内容
            memory_type: 新类型
            tags: 新标签
            importance: 新重要性

        返回:
            bool: 是否成功
        """
        update_fields = {}

        if content is not None:
            if not content.strip():
                raise MemoryValidationError("记忆内容不能为空")
            update_fields["content"] = content.strip()

        if memory_type is not None:
            update_fields["project_type"] = self._normalize_memory_type(memory_type)

        if tags is not None:
            update_fields["note"] = ",".join(tags)

        if importance is not None:
            update_fields["priority"] = str(self._normalize_importance(importance))

        try:
            return self.record_manager.update_record(record_id, **update_fields)
        except Exception as e:
            logger.error(f"Failed to update memory: {str(e)}")
            raise MemoryAPIError(f"更新记忆失败: {str(e)}")

    def delete_memory(self, record_id: str) -> bool:
        """删除记忆记录

        参数:
            record_id: 记录ID

        返回:
            bool: 是否成功
        """
        try:
            return self.record_manager.delete_record(record_id)
        except Exception as e:
            logger.error(f"Failed to delete memory: {str(e)}")
            raise MemoryAPIError(f"删除记忆失败: {str(e)}")

    def get_statistics(
        self,
        date_range: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """获取统计信息

        参数:
            date_range: 日期范围

        返回:
            Dict: 统计信息
        """
        filters = {}
        if date_range:
            filters["date_range"] = date_range

        try:
            records = self.record_manager.query_records(filters=filters)

            # 统计各类型数量
            type_counts: Dict[str, int] = {}
            importance_counts: Dict[int, int] = {}
            tag_counts: Dict[str, int] = {}
            total = len(records)

            for record in records:
                fields = record.get("fields", {})

                # 类型统计
                mem_type = fields.get("项目类型", "其他")
                type_counts[mem_type] = type_counts.get(mem_type, 0) + 1

                # 重要性统计
                try:
                    importance = int(fields.get("优先级别", 3))
                    importance_counts[importance] = (
                        importance_counts.get(importance, 0) + 1
                    )
                except (ValueError, TypeError):
                    pass

                # 标签统计
                tags = fields.get("标签", "").split(",")
                for tag in tags:
                    if tag:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1

            # 计算技能掌握度（基于重要性>=4的数量）
            skill_count = importance_counts.get(4, 0) + importance_counts.get(5, 0)
            mastery_rate = round(skill_count / total * 100, 1) if total > 0 else 0.0

            return {
                "total": total,
                "type_counts": type_counts,
                "importance_counts": importance_counts,
                "tag_counts": dict(
                    sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                ),
                "skill_count": skill_count,
                "mastery_rate": mastery_rate,
            }

        except Exception as e:
            logger.error(f"Failed to get statistics: {str(e)}")
            raise MemoryAPIError(f"获取统计失败: {str(e)}")

    def get_today_statistics(self) -> Dict[str, Any]:
        """获取今日统计信息

        返回:
            Dict: 今日统计
        """
        today = date.today().isoformat()
        return self.get_statistics(date_range={"start": today, "end": today})

    def get_weekly_statistics(self) -> Dict[str, Any]:
        """获取本周统计信息

        返回:
            Dict: 本周统计
        """
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        return self.get_statistics(
            date_range={"start": week_start.isoformat(), "end": today.isoformat()}
        )

    def _update_daily_stats(self) -> bool:
        """更新每日统计表"""
        try:
            today = date.today().isoformat()
            today_stats = self.get_today_statistics()

            # 尝试添加到统计表（如果存在）
            # 这里可以扩展为写入统计表
            logger.info(f"Daily stats updated for {today}: {today_stats}")
            return True

        except Exception as e:
            logger.warning(f"Failed to update daily stats: {e}")
            return False

    def generate_dashboard_report(self) -> str:
        """生成仪表板报告

        返回:
            str: 格式化的报告文本
        """
        stats = self.get_statistics()
        today_stats = self.get_today_statistics()

        report_lines = [
            "=" * 50,
            "📊 记忆可视化仪表板",
            "=" * 50,
            "",
            f"📈 总记忆数: {stats['total']}",
            f"🎯 技能掌握度: {stats['mastery_rate']}%",
            "",
            "--- 今日统计 ---",
            f"  今日新增: {today_stats['total']}",
            "",
            "--- 类型分布 ---",
        ]

        for mem_type, count in stats["type_counts"].items():
            report_lines.append(f"  {mem_type}: {count}")

        report_lines.extend(
            [
                "",
                "--- 热门标签 (Top 10) ---",
            ]
        )

        for tag, count in list(stats["tag_counts"].items())[:10]:
            report_lines.append(f"  #{tag}: {count}")

        report_lines.extend(
            [
                "",
                "--- 重要性分布 ---",
                f"  ⭐⭐⭐⭐⭐ (关键): {stats['importance_counts'].get(5, 0)}",
                f"  ⭐⭐⭐⭐ (高): {stats['importance_counts'].get(4, 0)}",
                f"  ⭐⭐⭐ (中): {stats['importance_counts'].get(3, 0)}",
                f"  ⭐⭐ (低): {stats['importance_counts'].get(2, 0)}",
                f"  ⭐ (最低): {stats['importance_counts'].get(1, 0)}",
                "",
                "=" * 50,
            ]
        )

        return "\n".join(report_lines)

    def search_memories(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索记忆

        参数:
            query: 搜索关键词
            limit: 返回数量限制

        返回:
            List[Dict]: 匹配的记录列表
        """
        return self.query_memories(keyword=query, limit=limit)

    def get_memories_by_tag(self, tag: str, limit: int = 100) -> List[Dict[str, Any]]:
        """按标签获取记忆

        参数:
            tag: 标签名称
            limit: 返回数量限制

        返回:
            List[Dict]: 匹配的记录列表
        """
        return self.query_memories(tags=[tag], limit=limit)

    def get_memories_by_type(
        self, memory_type: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """按类型获取记忆

        参数:
            memory_type: 记忆类型
            limit: 返回数量限制

        返回:
            List[Dict]: 匹配的记录列表
        """
        return self.query_memories(memory_type=memory_type, limit=limit)

    def get_important_memories(
        self, min_importance: int = 4, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取重要记忆

        参数:
            min_importance: 最低重要性
            limit: 返回数量限制

        返回:
            List[Dict]: 重要记录列表
        """
        return self.query_memories(importance_min=min_importance, limit=limit)


def create_dashboard(
    app_token: str = MemoryDashboard.DEFAULT_APP_TOKEN,
    record_table_id: Optional[str] = None,
    stats_table_id: Optional[str] = None,
) -> MemoryDashboard:
    """创建记忆仪表板实例的便捷函数

    参数:
        app_token: 飞书Bitable app token
        record_table_id: 记录表ID
        stats_table_id: 统计表ID

    返回:
        MemoryDashboard: 仪表板实例
    """
    return MemoryDashboard(
        app_token=app_token,
        record_table_id=record_table_id,
        stats_table_id=stats_table_id,
    )
