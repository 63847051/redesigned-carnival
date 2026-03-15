"""
飞书工作日志智能助手模块

整合意图分析和Bitable管理功能，提供完整的日志管理能力
"""

import logging
from typing import Dict, Optional, List, Any
from datetime import datetime, date

from intent_analyzer import IntentAnalyzer, IntentResult, IntentAnalyzerError
from bitable_manager import (
    BitableManager,
    BitableManagerError,
    BitableValidationError,
    BitableAPIError,
)

logger = logging.getLogger(__name__)


class WorklogAssistantError(Exception):
    """工作日志助手基础异常"""

    pass


class WorklogAssistant:
    """工作日志智能助手

    整合意图分析和飞书Bitable管理，提供自然语言处理工作日志的能力
    """

    def __init__(self, app_token: str, table_id: str):
        """初始化工作日志助手

        参数:
            app_token: Bitable app token
            table_id: Table ID

        异常:
            BitableValidationError: 当app_token或table_id无效时
        """
        logger.info(
            f"Initializing WorklogAssistant with app_token={app_token[:4]}..., table_id={table_id}"
        )

        self.bitable_manager = BitableManager(app_token, table_id)
        self.intent_analyzer = IntentAnalyzer()

        logger.info("WorklogAssistant initialized successfully")

    def set_access_token(self, access_token: str) -> None:
        """设置飞书访问令牌

        参数:
            access_token: 飞书应用访问令牌
        """
        self.bitable_manager.set_access_token(access_token)
        logger.info("Access token set successfully")

    def process(self, user_input: str) -> str:
        """处理用户输入

        参数:
            user_input: 用户输入的自然语言文本

        返回:
            str: 处理结果描述

        异常:
            WorklogAssistantError: 当处理失败时
        """
        if not user_input or not user_input.strip():
            raise WorklogAssistantError("用户输入不能为空")

        user_input = user_input.strip()
        logger.info(f"Processing user input: {user_input[:50]}...")

        try:
            # 步骤1: 意图分析
            intent_result = self.intent_analyzer.analyze(user_input)
            logger.info(
                f"Intent detected: {intent_result.intent}, confidence: {intent_result.confidence:.2f}"
            )

            # 步骤2: 根据意图类型分发处理
            if intent_result.intent == "record":
                return self._handle_record(intent_result)
            elif intent_result.intent == "query":
                return self._handle_query(intent_result)
            elif intent_result.intent == "update":
                return self._handle_update(intent_result)
            elif intent_result.intent == "delete":
                return self._handle_delete(intent_result)
            else:
                return self._format_error(f"未知的意图类型: {intent_result.intent}")

        except IntentAnalyzerError as e:
            logger.error(f"Intent analysis failed: {str(e)}")
            return self._format_error(f"意图分析失败: {str(e)}")
        except BitableManagerError as e:
            logger.error(f"Bitable operation failed: {str(e)}")
            return self._format_error(f"数据操作失败: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return self._format_error(f"处理失败: {str(e)}")

    def _handle_record(self, params: IntentResult) -> str:
        """处理记录意图

        参数:
            params: 意图分析结果

        返回:
            str: 处理结果描述
        """
        logger.info(f"Handling record intent: content={params.content[:30]}...")

        try:
            result = self.bitable_manager.add_record(
                content=params.content,
                project_type=params.project_type,
                priority=params.priority,
                status=params.status,
                note=params.note,
            )

            return self._format_record_success(result)

        except BitableValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return self._format_error(f"数据验证失败: {str(e)}")
        except BitableAPIError as e:
            logger.error(f"API error: {str(e)}")
            return self._format_error(f"飞书API调用失败: {str(e)}")

    def _handle_query(self, params: IntentResult) -> str:
        """处理查询意图

        参数:
            params: 意图分析结果

        返回:
            str: 查询结果描述
        """
        logger.info("Handling query intent")

        # 构建查询过滤器
        filters = self._build_query_filters(params)

        try:
            records = self.bitable_manager.query_records(filters=filters)

            if not records:
                return self._format_empty_result("没有找到符合条件的记录")

            return self._format_query_result(records, params)

        except BitableAPIError as e:
            logger.error(f"API error: {str(e)}")
            return self._format_error(f"查询失败: {str(e)}")

    def _handle_update(self, params: IntentResult) -> str:
        """处理更新意图

        参数:
            params: 意图分析结果

        返回:
            str: 更新结果描述
        """
        logger.info("Handling update intent")

        # 从内容中提取记录ID或描述
        record_id = self._extract_record_id(params.content)

        if not record_id:
            return self._format_error("无法确定要更新的记录，请提供记录ID")

        try:
            # 如果内容中指定了新状态
            new_status = params.status if params.status != "待确认" else "已完成"

            success = self.bitable_manager.update_status(record_id, new_status)

            if success:
                return self._format_update_success(record_id, new_status)
            else:
                return self._format_error("更新失败")

        except BitableValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return self._format_error(f"数据验证失败: {str(e)}")
        except BitableAPIError as e:
            logger.error(f"API error: {str(e)}")
            return self._format_error(f"更新失败: {str(e)}")

    def _handle_delete(self, params: IntentResult) -> str:
        """处理删除意图

        参数:
            params: 意图分析结果

        返回:
            str: 删除结果描述
        """
        logger.info("Handling delete intent")

        # 从内容中提取记录ID
        record_id = self._extract_record_id(params.content)

        if not record_id:
            return self._format_error("无法确定要删除的记录，请提供记录ID")

        try:
            success = self.bitable_manager.delete_record(record_id)

            if success:
                return self._format_delete_success(record_id)
            else:
                return self._format_error("删除失败")

        except BitableValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return self._format_error(f"数据验证失败: {str(e)}")
        except BitableAPIError as e:
            logger.error(f"API error: {str(e)}")
            return self._format_error(f"删除失败: {str(e)}")

    def _build_query_filters(self, params: IntentResult) -> Dict:
        """构建查询过滤器

        参数:
            params: 意图分析结果

        返回:
            Dict: 过滤器配置
        """
        filters: Dict = {}

        # 状态过滤
        if params.status and params.status != "待确认":
            filters["status"] = params.status

        # 项目类型过滤
        if params.project_type and params.project_type != "技术开发":
            filters["project_type"] = params.project_type

        # 关键词搜索
        if params.content:
            filters["keyword"] = params.content

        # 日期范围
        date_range = self._extract_date_range(params.content)
        if date_range:
            filters["date_range"] = date_range

        logger.debug(f"Built filters: {filters}")
        return filters

    def _extract_record_id(self, content: str) -> Optional[str]:
        """从内容中提取记录ID

        参数:
            content: 内容文本

        返回:
            Optional[str]: 记录ID
        """
        import re

        # 匹配形如 "record_xxx" 或 "rec_xxx" 或纯数字ID
        patterns = [
            r"record[_-]?id[:\s=]+([a-zA-Z0-9_-]+)",
            r"ID[:\s=]+([a-zA-Z0-9_-]+)",
            r"编号[:\s=]+(\d+)",
            r"第(\d+)条",
            r"第\s*(\d+)\s*个",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _extract_date_range(self, content: str) -> Optional[Dict]:
        """从内容中提取日期范围

        参数:
            content: 内容文本

        返回:
            Optional[Dict]: 日期范围 {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
        """
        import re

        today = date.today()

        # 今天
        if "今天" in content or "今日" in content:
            return {"start": today.isoformat(), "end": today.isoformat()}

        # 昨天
        if "昨天" in content or "昨日" in content:
            from datetime import timedelta

            yesterday = today - timedelta(days=1)
            return {"start": yesterday.isoformat(), "end": yesterday.isoformat()}

        # 本周
        if "本周" in content:
            from datetime import timedelta

            week_start = today - timedelta(days=today.weekday())
            return {"start": week_start.isoformat(), "end": today.isoformat()}

        # 本月
        if "本月" in content:
            return {
                "start": f"{today.year}-{today.month:02d}-01",
                "end": today.isoformat(),
            }

        # 匹配日期范围格式 "2026-01-01 到 2026-01-31"
        range_pattern = r"(\d{4}-\d{2}-\d{2})\s*(?:到|至|-)\s*(\d{4}-\d{2}-\d{2})"
        match = re.search(range_pattern, content)
        if match:
            return {"start": match.group(1), "end": match.group(2)}

        return None

    def get_statistics(self) -> str:
        """获取统计信息

        返回:
            str: 统计信息描述
        """
        try:
            stats = self.bitable_manager.get_statistics()
            return self._format_statistics(stats)
        except BitableManagerError as e:
            logger.error(f"Failed to get statistics: {str(e)}")
            return self._format_error(f"获取统计信息失败: {str(e)}")

    def get_today_summary(self) -> str:
        """获取今日摘要

        返回:
            str: 今日摘要描述
        """
        try:
            stats = self.bitable_manager.get_today_statistics()
            return self._format_today_summary(stats)
        except BitableManagerError as e:
            logger.error(f"Failed to get today summary: {str(e)}")
            return self._format_error(f"获取今日摘要失败: {str(e)}")

    # ==================== 格式化输出 ====================

    def _format_record_success(self, result: Dict) -> str:
        """格式化记录成功的结果"""
        lines = [
            "=" * 40,
            "✅ 记录创建成功",
            "=" * 40,
            f"📝 内容: {result.get('content', 'N/A')}",
            f"📁 类型: {result.get('project_type', 'N/A')}",
            f"⭐ 优先级: {result.get('priority', 'N/A')}",
            f"📌 状态: {result.get('status', 'N/A')}",
            f"🆔 记录ID: {result.get('record_id', 'N/A')}",
        ]
        if result.get("note"):
            lines.append(f"📋 备注: {result['note']}")
        lines.append("=" * 40)
        return "\n".join(lines)

    def _format_query_result(self, records: List[Dict], params: IntentResult) -> str:
        """格式化查询结果"""
        lines = [
            "=" * 40,
            f"🔍 查询结果 (共 {len(records)} 条)",
            "=" * 40,
        ]

        for i, record in enumerate(records, 1):
            fields = record.get("fields", {})
            content = fields.get("内容", "N/A")
            status = fields.get("项目状态", "N/A")
            project_type = fields.get("项目类型", "N/A")
            record_id = record.get("record_id", "N/A")

            lines.append(f"\n[{i}] {content[:50]}")
            lines.append(f"    类型: {project_type} | 状态: {status} | ID: {record_id}")

        lines.append("\n" + "=" * 40)
        return "\n".join(lines)

    def _format_update_success(self, record_id: str, new_status: str) -> str:
        """格式化更新成功的结果"""
        return f"""{"=" * 40}
✅ 状态更新成功
{"=" * 40}
🆔 记录ID: {record_id}
📌 新状态: {new_status}
{"=" * 40}"""

    def _format_delete_success(self, record_id: str) -> str:
        """格式化删除成功的结果"""
        return f"""{"=" * 40}
✅ 记录删除成功
{"=" * 40}
🆔 记录ID: {record_id}
{"=" * 40}"""

    def _format_statistics(self, stats: Dict) -> str:
        """格式化统计信息"""
        return f"""{"=" * 40}
📊 工作日志统计
{"=" * 40}
📈 总任务数: {stats.get("total", 0)}
✅ 已完成: {stats.get("completed", 0)}
🔄 进行中: {stats.get("in_progress", 0)}
⏳ 待确认: {stats.get("pending", 0)}
📊 完成率: {stats.get("completion_rate", 0)}%
{"=" * 40}"""

    def _format_today_summary(self, stats: Dict) -> str:
        """格式化今日摘要"""
        return f"""{"=" * 40}
📅 今日工作摘要 ({stats.get("date", "N/A")})
{"=" * 40}
📝 今日任务: {stats.get("total", 0)}
✅ 已完成: {stats.get("completed", 0)}
🔄 进行中: {stats.get("in_progress", 0)}
{"=" * 40}"""

    def _format_empty_result(self, message: str) -> str:
        """格式化空结果"""
        return f"""{"=" * 40}
📭 {message}
{"=" * 40}"""

    def _format_error(self, message: str) -> str:
        """格式化错误信息"""
        return f"""{"=" * 40}
❌ 错误
{"=" * 40}
{message}
{"=" * 40}"""


def main() -> None:
    """演示入口"""
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # 示例用法
    app_token = "BISAbNgYXa7Do1sc36YcBChInnS"
    table_id = "tbl5s8TEZ0tKhEm7"

    assistant = WorklogAssistant(app_token, table_id)

    test_inputs = [
        "记录一下：完成了3F会议室平面图设计",
        "今天完成了多少任务？",
        "查看室内设计相关的任务",
        "统计本周的工作情况",
    ]

    print("飞书工作日志智能助手演示")
    print("=" * 50)

    for input_text in test_inputs:
        print(f"\n输入: {input_text}")
        print("-" * 50)
        result = assistant.process(input_text)
        print(result)
        print()


if __name__ == "__main__":
    main()
