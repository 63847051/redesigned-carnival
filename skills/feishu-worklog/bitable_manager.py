"""
飞书多维表格管理器模块

提供对飞书多维表格的增删改查操作以及统计功能
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class BitableManagerError(Exception):
    """Bitable管理器基础异常"""

    pass


class BitableAPIError(BitableManagerError):
    """飞书API调用异常"""

    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(message)
        self.code = code


class BitableValidationError(BitableManagerError):
    """数据验证异常"""

    pass


class BitableManager:
    """飞书多维表格管理器

    提供对飞书多维表格的创建、查询、更新和统计等功能
    """

    # 支持的项目类型
    PROJECT_TYPES = ["室内设计", "技术开发", "文档编写", "现场", "设计", "施工", "机电"]

    # 支持的优先级
    PRIORITIES = ["高", "中", "低", "第一优先", "重要", "普通重要"]

    # 支持的状态
    STATUSES = ["待确认", "进行中", "已完成", "待完成"]

    # 飞书API基础URL
    BASE_URL = "https://open.feishu.cn/open-apis/bitable/v1"

    def __init__(self, app_token: str, table_id: str):
        """初始化飞书多维表格管理器

        参数:
            app_token: Bitable app token (例如: BISAbNgYXa7Do1sc36YcBChInnS)
            table_id: Table ID (例如: tbl5s8TEZ0tKhEm7)

        异常:
            BitableValidationError: 当app_token或table_id无效时
        """
        if not app_token or not app_token.strip():
            raise BitableValidationError("app_token不能为空")
        if not table_id or not table_id.strip():
            raise BitableValidationError("table_id不能为空")

        self.app_token = app_token.strip()
        self.table_id = table_id.strip()
        self._access_token: Optional[str] = None

        logger.info(
            f"BitableManager initialized with app_token={self._mask_token(self.app_token)}, table_id={self.table_id}"
        )

    @staticmethod
    def _mask_token(token: str) -> str:
        """脱敏处理token"""
        if len(token) <= 8:
            return "***"
        return f"{token[:4]}...{token[-4:]}"

    def set_access_token(self, access_token: str) -> None:
        """设置访问令牌

        参数:
            access_token: 飞书开放平台应用访问令牌
        """
        if not access_token or not access_token.strip():
            raise BitableValidationError("access_token不能为空")
        self._access_token = access_token.strip()
        logger.debug("Access token set successfully")

    def _get_headers(self) -> Dict[str, str]:
        """构建请求头"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._access_token}"
            if self._access_token
            else "",
        }
        return {k: v for k, v in headers.items() if v}

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """发起API请求

        参数:
            method: HTTP方法 (GET, POST, PUT, DELETE)
            endpoint: API端点路径
            params: URL查询参数
            data: 请求体数据

        返回:
            API响应数据

        异常:
            BitableAPIError: 当API调用失败时
        """
        import requests

        url = f"{self.BASE_URL}{endpoint}"
        headers = self._get_headers()

        logger.debug(f"Request: {method} {url}, params={params}, data={data}")

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=30,
            )

            result = response.json()

            if response.status_code >= 400:
                error_code = result.get("error", {}).get("code", response.status_code)
                error_msg = result.get("error", {}).get("message", "Unknown error")
                logger.error(f"API error: {error_code} - {error_msg}")
                raise BitableAPIError(f"API调用失败: {error_msg}", error_code)

            logger.debug(f"Response: {result}")
            return result

        except requests.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise BitableAPIError(f"网络请求失败: {str(e)}")

    def add_record(
        self,
        content: str,
        project_type: str = "技术开发",
        priority: str = "中",
        status: str = "待确认",
        note: str = "",
    ) -> Dict:
        """添加记录

        参数:
            content: 任务内容
            project_type: 项目类型（室内设计、技术开发、文档编写、现场、设计、施工、机电）
            priority: 优先级（高、中、低、第一优先、重要、普通重要）
            status: 状态（待确认、进行中、已完成、待完成）
            note: 备注（可选）

        返回:
            Dict: 创建的记录信息，包含record_id等

        异常:
            BitableValidationError: 当参数验证失败时
            BitableAPIError: 当API调用失败时
        """
        # 参数验证
        if not content or not content.strip():
            raise BitableValidationError("任务内容不能为空")

        content = content.strip()
        project_type = self._normalize_project_type(project_type)
        priority = self._normalize_priority(priority)
        status = self._normalize_status(status)
        note = note.strip() if note else ""

        # 构建字段数据
        fields = {
            "内容": content,
            "项目类型": project_type,
            "优先级别": priority,
            "项目状态": status,
        }

        if note:
            fields["备注"] = note

        # 添加创建时间
        fields["创建日期"] = datetime.now().isoformat()

        logger.info(
            f"Adding record: content={content[:50]}..., project_type={project_type}, priority={priority}, status={status}"
        )

        try:
            endpoint = f"/apps/{self.app_token}/tables/{self.table_id}/records"
            result = self._make_request("POST", endpoint, data={"fields": fields})

            record_id = result.get("data", {}).get("record", {}).get("record_id")
            logger.info(f"Record created successfully: {record_id}")

            return {
                "success": True,
                "record_id": record_id,
                "content": content,
                "project_type": project_type,
                "priority": priority,
                "status": status,
                "note": note,
                "created_at": fields["创建日期"],
            }

        except BitableAPIError:
            raise
        except Exception as e:
            logger.error(f"Failed to add record: {str(e)}")
            raise BitableManagerError(f"添加记录失败: {str(e)}")

    def _normalize_project_type(self, project_type: str) -> str:
        """标准化项目类型"""
        type_mapping = {
            "室内设计": "室内设计",
            "技术开发": "技术开发",
            "文档编写": "文档编写",
            "设计": "设计",
            "现场": "现场",
            "施工": "施工",
            "机电": "机电",
        }
        return type_mapping.get(project_type, "技术开发")

    def _normalize_priority(self, priority: str) -> str:
        """标准化优先级"""
        priority_mapping = {
            "高": "高",
            "中": "中",
            "低": "低",
            "第一优先": "高",
            "重要": "高",
            "普通重要": "中",
        }
        return priority_mapping.get(priority, "中")

    def _normalize_status(self, status: str) -> str:
        """标准化状态"""
        status_mapping = {
            "待确认": "待确认",
            "进行中": "进行中",
            "已完成": "已完成",
            "待完成": "进行中",
        }
        return status_mapping.get(status, "待确认")

    def query_records(self, filters: Optional[Dict] = None) -> List[Dict]:
        """查询记录

        参数:
            filters: 筛选条件，可包含:
                - status: 状态筛选
                - project_type: 项目类型筛选
                - date_range: 日期范围 {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
                - keyword: 关键词搜索

        返回:
            List[Dict]: 记录列表

        异常:
            BitableAPIError: 当API调用失败时
        """
        filters = filters or {}
        logger.info(f"Querying records with filters: {filters}")

        try:
            endpoint = f"/apps/{self.app_token}/tables/{self.table_id}/records"

            # 构建筛选条件
            filter_conditions = []

            if filters.get("status"):
                filter_conditions.append(
                    {
                        "field_name": "项目状态",
                        "operator": "equal",
                        "value": filters["status"],
                    }
                )

            if filters.get("project_type"):
                filter_conditions.append(
                    {
                        "field_name": "项目类型",
                        "operator": "equal",
                        "value": filters["project_type"],
                    }
                )

            if filters.get("keyword"):
                filter_conditions.append(
                    {
                        "field_name": "内容",
                        "operator": "contains",
                        "value": filters["keyword"],
                    }
                )

            params = {"page_size": 100}

            if filter_conditions:
                params["filter"] = {
                    "conjunction": "and",
                    "conditions": filter_conditions,
                }

            result = self._make_request("GET", endpoint, params=params)

            records = result.get("data", {}).get("items", [])

            # 日期范围过滤（如果需要）
            if filters.get("date_range"):
                records = self._filter_by_date_range(records, filters["date_range"])

            logger.info(f"Found {len(records)} records")
            return records

        except BitableAPIError:
            raise
        except Exception as e:
            logger.error(f"Failed to query records: {str(e)}")
            raise BitableManagerError(f"查询记录失败: {str(e)}")

    def _filter_by_date_range(
        self, records: List[Dict], date_range: Dict
    ) -> List[Dict]:
        """根据日期范围过滤记录"""
        start_date = date_range.get("start")
        end_date = date_range.get("end")

        if not start_date and not end_date:
            return records

        filtered = []
        for record in records:
            fields = record.get("fields", {})
            created_date = fields.get("创建日期", "")

            if not created_date:
                continue

            # 解析日期
            try:
                created_dt = datetime.fromisoformat(created_date.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                continue

            if start_date:
                start_dt = datetime.fromisoformat(start_date)
                if created_dt < start_dt:
                    continue

            if end_date:
                end_dt = datetime.fromisoformat(end_date)
                if created_dt > end_dt:
                    continue

            filtered.append(record)

        return filtered

    def get_record_by_id(self, record_id: str) -> Dict:
        """根据ID获取单条记录

        参数:
            record_id: 记录ID

        返回:
            Dict: 记录详情

        异常:
            BitableValidationError: 当record_id无效时
            BitableAPIError: 当API调用失败时
        """
        if not record_id or not record_id.strip():
            raise BitableValidationError("record_id不能为空")

        try:
            endpoint = (
                f"/apps/{self.app_token}/tables/{self.table_id}/records/{record_id}"
            )
            result = self._make_request("GET", endpoint)
            return result.get("data", {})

        except BitableAPIError:
            raise
        except Exception as e:
            logger.error(f"Failed to get record: {str(e)}")
            raise BitableManagerError(f"获取记录失败: {str(e)}")

    def update_status(self, record_id: str, status: str) -> bool:
        """更新记录状态

        参数:
            record_id: 记录ID
            status: 新状态（待确认、进行中、已完成、待完成）

        返回:
            bool: 是否成功

        异常:
            BitableValidationError: 当参数无效时
            BitableAPIError: 当API调用失败时
        """
        if not record_id or not record_id.strip():
            raise BitableValidationError("record_id不能为空")

        status = self._normalize_status(status)

        # 构建更新数据
        fields = {"项目状态": status}

        # 如果设置为完成，添加完成时间
        if status == "已完成":
            fields["完成时间"] = datetime.now().isoformat()

        logger.info(f"Updating record {record_id} status to {status}")

        try:
            endpoint = (
                f"/apps/{self.app_token}/tables/{self.table_id}/records/{record_id}"
            )
            self._make_request("PUT", endpoint, data={"fields": fields})

            logger.info(f"Record {record_id} status updated successfully")
            return True

        except BitableAPIError:
            raise
        except Exception as e:
            logger.error(f"Failed to update record: {str(e)}")
            raise BitableManagerError(f"更新记录失败: {str(e)}")

    def update_record(
        self,
        record_id: str,
        content: Optional[str] = None,
        project_type: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        note: Optional[str] = None,
    ) -> bool:
        """更新记录

        参数:
            record_id: 记录ID
            content: 任务内容（可选）
            project_type: 项目类型（可选）
            priority: 优先级（可选）
            status: 状态（可选）
            note: 备注（可选）

        返回:
            bool: 是否成功

        异常:
            BitableValidationError: 当参数无效时
            BitableAPIError: 当API调用失败时
        """
        if not record_id or not record_id.strip():
            raise BitableValidationError("record_id不能为空")

        fields = {}

        if content is not None:
            if not content.strip():
                raise BitableValidationError("任务内容不能为空")
            fields["内容"] = content.strip()

        if project_type is not None:
            fields["项目类型"] = self._normalize_project_type(project_type)

        if priority is not None:
            fields["优先级别"] = self._normalize_priority(priority)

        if status is not None:
            status_normalized = self._normalize_status(status)
            fields["项目状态"] = status_normalized
            if status_normalized == "已完成":
                fields["完成时间"] = datetime.now().isoformat()

        if note is not None:
            fields["备注"] = note.strip() if note.strip() else ""

        if not fields:
            raise BitableValidationError("没有需要更新的字段")

        logger.info(f"Updating record {record_id} with fields: {list(fields.keys())}")

        try:
            endpoint = (
                f"/apps/{self.app_token}/tables/{self.table_id}/records/{record_id}"
            )
            self._make_request("PUT", endpoint, data={"fields": fields})

            logger.info(f"Record {record_id} updated successfully")
            return True

        except BitableAPIError:
            raise
        except Exception as e:
            logger.error(f"Failed to update record: {str(e)}")
            raise BitableManagerError(f"更新记录失败: {str(e)}")

    def delete_record(self, record_id: str) -> bool:
        """删除记录

        参数:
            record_id: 记录ID

        返回:
            bool: 是否成功

        异常:
            BitableValidationError: 当record_id无效时
            BitableAPIError: 当API调用失败时
        """
        if not record_id or not record_id.strip():
            raise BitableValidationError("record_id不能为空")

        logger.warning(f"Deleting record {record_id}")

        try:
            endpoint = (
                f"/apps/{self.app_token}/tables/{self.table_id}/records/{record_id}"
            )
            self._make_request("DELETE", endpoint)

            logger.info(f"Record {record_id} deleted successfully")
            return True

        except BitableAPIError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete record: {str(e)}")
            raise BitableManagerError(f"删除记录失败: {str(e)}")

    def get_statistics(self) -> Dict:
        """获取统计信息

        返回:
            Dict: 统计信息，包含:
                - total: 总任务数
                - completed: 完成数
                - in_progress: 进行中数
                - pending: 待确认数
                - completion_rate: 完成率（百分比）

        异常:
            BitableAPIError: 当API调用失败时
        """
        logger.info("Getting statistics")

        try:
            # 获取所有记录
            all_records = self.query_records()

            total = len(all_records)
            completed = 0
            in_progress = 0
            pending = 0

            for record in all_records:
                fields = record.get("fields", {})
                status = fields.get("项目状态", "")

                if status == "已完成":
                    completed += 1
                elif status == "进行中":
                    in_progress += 1
                else:
                    pending += 1

            completion_rate = round((completed / total * 100), 1) if total > 0 else 0.0

            stats = {
                "total": total,
                "completed": completed,
                "in_progress": in_progress,
                "pending": pending,
                "completion_rate": completion_rate,
            }

            logger.info(f"Statistics: {stats}")
            return stats

        except BitableAPIError:
            raise
        except Exception as e:
            logger.error(f"Failed to get statistics: {str(e)}")
            raise BitableManagerError(f"获取统计信息失败: {str(e)}")

    def get_today_statistics(self) -> Dict:
        """获取今日统计信息

        返回:
            Dict: 今日统计信息
        """
        logger.info("Getting today's statistics")

        from datetime import date

        today = date.today().isoformat()
        date_range = {"start": today, "end": today}

        try:
            today_records = self.query_records(filters={"date_range": date_range})

            total = len(today_records)
            completed = 0

            for record in today_records:
                fields = record.get("fields", {})
                status = fields.get("项目状态", "")
                if status == "已完成":
                    completed += 1

            return {
                "date": today,
                "total": total,
                "completed": completed,
                "in_progress": total - completed,
            }

        except BitableAPIError:
            raise
        except Exception as e:
            logger.error(f"Failed to get today's statistics: {str(e)}")
            raise BitableManagerError(f"获取今日统计失败: {str(e)}")

    def list_fields(self) -> List[Dict]:
        """获取表格字段列表

        返回:
            List[Dict]: 字段列表

        异常:
            BitableAPIError: 当API调用失败时
        """
        logger.info("Listing fields")

        try:
            endpoint = f"/apps/{self.app_token}/tables/{self.table_id}/fields"
            result = self._make_request("GET", endpoint)

            fields = result.get("data", {}).get("items", [])
            logger.info(f"Found {len(fields)} fields")
            return fields

        except BitableAPIError:
            raise
        except Exception as e:
            logger.error(f"Failed to list fields: {str(e)}")
            raise BitableManagerError(f"获取字段列表失败: {str(e)}")
