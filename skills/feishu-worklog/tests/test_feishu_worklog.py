"""
飞书工作日志模块单元测试

测试 bitable_manager.py, intent_analyzer.py, worklog_assistant.py 的核心功能
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bitable_manager import (
    BitableManager,
    BitableManagerError,
    BitableValidationError,
    BitableAPIError,
)
from intent_analyzer import IntentAnalyzer, IntentResult, IntentAnalyzerError
from worklog_assistant import WorklogAssistant, WorklogAssistantError


class TestBitableManager(unittest.TestCase):
    """测试 BitableManager 核心功能"""

    def setUp(self):
        self.app_token = "BISAbNgYXa7Do1sc36YcBChInnS"
        self.table_id = "tbl5s8TEZ0tKhEm7"

    def test_init_valid_params(self):
        """测试正常初始化"""
        manager = BitableManager(self.app_token, self.table_id)
        self.assertEqual(manager.app_token, self.app_token)
        self.assertEqual(manager.table_id, self.table_id)

    def test_init_invalid_app_token(self):
        """测试无效 app_token"""
        with self.assertRaises(BitableValidationError):
            BitableManager("", self.table_id)
        with self.assertRaises(BitableValidationError):
            BitableManager("   ", self.table_id)

    def test_init_invalid_table_id(self):
        """测试无效 table_id"""
        with self.assertRaises(BitableValidationError):
            BitableManager(self.app_token, "")

    def test_mask_token(self):
        """测试 token 脱敏"""
        manager = BitableManager(self.app_token, self.table_id)
        self.assertEqual(manager._mask_token("short"), "***")
        self.assertEqual(manager._mask_token("abcdefgh"), "***")
        self.assertEqual(manager._mask_token("abcdefghij"), "abcd...ghij")

    def test_set_access_token(self):
        """测试设置 access_token"""
        manager = BitableManager(self.app_token, self.table_id)
        manager.set_access_token("test_token_123")
        self.assertEqual(manager._access_token, "test_token_123")

    def test_set_access_token_invalid(self):
        """测试无效 access_token"""
        manager = BitableManager(self.app_token, self.table_id)
        with self.assertRaises(BitableValidationError):
            manager.set_access_token("")
        with self.assertRaises(BitableValidationError):
            manager.set_access_token("   ")

    def test_get_headers(self):
        """测试请求头构建"""
        manager = BitableManager(self.app_token, self.table_id)
        headers = manager._get_headers()
        self.assertIn("Content-Type", headers)
        self.assertEqual(headers["Content-Type"], "application/json")

        manager.set_access_token("test_token")
        headers = manager._get_headers()
        self.assertIn("Authorization", headers)
        self.assertTrue(headers["Authorization"].startswith("Bearer "))

    @patch("requests.request")
    def test_add_record_success(self, mock_request):
        """测试添加记录成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {"record": {"record_id": "rec123456"}}
        }
        mock_request.return_value = mock_response

        manager = BitableManager(self.app_token, self.table_id)
        manager.set_access_token("test_token")

        result = manager.add_record(
            content="测试任务",
            project_type="技术开发",
            priority="高",
            status="进行中",
            note="测试备注",
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["record_id"], "rec123456")
        self.assertEqual(result["content"], "测试任务")
        self.assertEqual(result["project_type"], "技术开发")

    def test_add_record_empty_content(self):
        """测试空内容验证"""
        manager = BitableManager(self.app_token, self.table_id)
        with self.assertRaises(BitableValidationError):
            manager.add_record("")
        with self.assertRaises(BitableValidationError):
            manager.add_record("   ")

    def test_normalize_project_type(self):
        """测试项目类型标准化"""
        manager = BitableManager(self.app_token, self.table_id)
        self.assertEqual(manager._normalize_project_type("室内设计"), "室内设计")
        self.assertEqual(manager._normalize_project_type("技术开发"), "技术开发")
        self.assertEqual(manager._normalize_project_type("设计"), "设计")
        self.assertEqual(manager._normalize_project_type("未知类型"), "技术开发")

    def test_normalize_priority(self):
        """测试优先级标准化"""
        manager = BitableManager(self.app_token, self.table_id)
        self.assertEqual(manager._normalize_priority("高"), "高")
        self.assertEqual(manager._normalize_priority("第一优先"), "高")
        self.assertEqual(manager._normalize_priority("重要"), "高")
        self.assertEqual(manager._normalize_priority("中"), "中")
        self.assertEqual(manager._normalize_priority("普通重要"), "中")
        self.assertEqual(manager._normalize_priority("低"), "低")

    def test_normalize_status(self):
        """测试状态标准化"""
        manager = BitableManager(self.app_token, self.table_id)
        self.assertEqual(manager._normalize_status("待确认"), "待确认")
        self.assertEqual(manager._normalize_status("进行中"), "进行中")
        self.assertEqual(manager._normalize_status("已完成"), "已完成")
        self.assertEqual(manager._normalize_status("待完成"), "进行中")

    @patch("requests.request")
    def test_query_records_success(self, mock_request):
        """测试查询记录成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "items": [
                    {
                        "record_id": "rec1",
                        "fields": {"内容": "任务1", "项目状态": "已完成"},
                    },
                    {
                        "record_id": "rec2",
                        "fields": {"内容": "任务2", "项目状态": "进行中"},
                    },
                ]
            }
        }
        mock_request.return_value = mock_response

        manager = BitableManager(self.app_token, self.table_id)
        manager.set_access_token("test_token")

        records = manager.query_records()
        self.assertEqual(len(records), 2)

    @patch("requests.request")
    def test_query_records_with_filters(self, mock_request):
        """测试带过滤条件的查询"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"items": []}}
        mock_request.return_value = mock_response

        manager = BitableManager(self.app_token, self.table_id)
        manager.set_access_token("test_token")

        filters = {"status": "已完成", "project_type": "技术开发", "keyword": "测试"}
        records = manager.query_records(filters=filters)
        self.assertEqual(len(records), 0)

    @patch("requests.request")
    def test_update_status_success(self, mock_request):
        """测试更新状态成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {}}
        mock_request.return_value = mock_response

        manager = BitableManager(self.app_token, self.table_id)
        manager.set_access_token("test_token")

        result = manager.update_status("rec123", "已完成")
        self.assertTrue(result)

    def test_update_status_empty_record_id(self):
        """测试空 record_id 更新"""
        manager = BitableManager(self.app_token, self.table_id)
        with self.assertRaises(BitableValidationError):
            manager.update_status("", "已完成")

    @patch("requests.request")
    def test_get_statistics_success(self, mock_request):
        """测试获取统计信息成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "items": [
                    {"fields": {"项目状态": "已完成"}},
                    {"fields": {"项目状态": "已完成"}},
                    {"fields": {"项目状态": "进行中"}},
                    {"fields": {"项目状态": "待确认"}},
                ]
            }
        }
        mock_request.return_value = mock_response

        manager = BitableManager(self.app_token, self.table_id)
        manager.set_access_token("test_token")

        stats = manager.get_statistics()
        self.assertEqual(stats["total"], 4)
        self.assertEqual(stats["completed"], 2)
        self.assertEqual(stats["in_progress"], 1)
        self.assertEqual(stats["pending"], 1)
        self.assertEqual(stats["completion_rate"], 50.0)

    @patch("requests.request")
    def test_get_statistics_empty(self, mock_request):
        """测试空统计"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"items": []}}
        mock_request.return_value = mock_response

        manager = BitableManager(self.app_token, self.table_id)
        manager.set_access_token("test_token")

        stats = manager.get_statistics()
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["completion_rate"], 0.0)


class TestIntentAnalyzer(unittest.TestCase):
    """测试 IntentAnalyzer 意图识别"""

    def setUp(self):
        self.analyzer = IntentAnalyzer()

    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.analyzer)
        self.assertIsNotNone(self.analyzer._intent_patterns)

    def test_analyze_empty_text(self):
        """测试空文本分析"""
        with self.assertRaises(IntentAnalyzerError):
            self.analyzer.analyze("")
        with self.assertRaises(IntentAnalyzerError):
            self.analyzer.analyze("   ")

    def test_detect_intent_record(self):
        """测试记录意图识别"""
        result = self.analyzer.analyze("记录一下：完成了任务")
        self.assertEqual(result.intent, "record")

        result = self.analyzer.analyze("添加一个新任务")
        self.assertEqual(result.intent, "record")

        result = self.analyzer.analyze("新建任务")
        self.assertEqual(result.intent, "record")

    def test_detect_intent_query(self):
        """测试查询意图识别"""
        result = self.analyzer.analyze("查询今天完成的任务")
        self.assertEqual(result.intent, "query")

        result = self.analyzer.analyze("看看有哪些任务")
        self.assertEqual(result.intent, "query")

    def test_detect_intent_update(self):
        """测试更新意图识别"""
        result = self.analyzer.analyze("更新任务状态")
        self.assertEqual(result.intent, "update")

        result = self.analyzer.analyze("把第一个任务标记为完成")
        self.assertEqual(result.intent, "update")

    def test_detect_intent_delete(self):
        """测试删除意图识别"""
        result = self.analyzer.analyze("把这条内容移除")
        self.assertEqual(result.intent, "delete")

    def test_detect_project_type_indoor_design(self):
        """测试室内设计类型识别"""
        result = self.analyzer.analyze("完成了3F会议室平面图设计")
        self.assertEqual(result.project_type, "室内设计")

        result = self.analyzer.analyze("画一张效果图")
        self.assertEqual(result.project_type, "室内设计")

    def test_detect_project_type_tech_dev(self):
        """测试技术开发类型识别"""
        result = self.analyzer.analyze("写了一个爬虫脚本")
        self.assertEqual(result.project_type, "技术开发")

        result = self.analyzer.analyze("修复了一个bug")
        self.assertEqual(result.project_type, "技术开发")

    def test_detect_project_type_doc(self):
        """测试文档编写类型识别"""
        result = self.analyzer.analyze("编写了技术手册")
        self.assertEqual(result.project_type, "文档编写")

    def test_detect_project_type_default(self):
        """测试默认项目类型"""
        result = self.analyzer.analyze("做了一些事情")
        self.assertEqual(result.project_type, self.analyzer.DEFAULT_PROJECT_TYPE)

    def test_detect_priority_high(self):
        """测试高优先级识别"""
        result = self.analyzer.analyze("紧急任务需要处理")
        self.assertEqual(result.priority, "高")

        result = self.analyzer.analyze("重要的工作")
        self.assertEqual(result.priority, "高")

    def test_detect_priority_low(self):
        """测试低优先级识别"""
        result = self.analyzer.analyze("稍后处理的任务")
        self.assertEqual(result.priority, "低")

    def test_detect_priority_default(self):
        """测试默认优先级"""
        result = self.analyzer.analyze("普通任务")
        self.assertEqual(result.priority, self.analyzer.DEFAULT_PRIORITY)

    def test_detect_status_completed(self):
        """测试已完成状态识别"""
        result = self.analyzer.analyze("任务已经完成了")
        self.assertEqual(result.status, "已完成")

    def test_detect_status_in_progress(self):
        """测试进行中状态识别"""
        result = self.analyzer.analyze("正在处理中")
        self.assertEqual(result.status, "进行中")

    def test_detect_status_default(self):
        """测试默认状态"""
        result = self.analyzer.analyze("记录一下任务")
        self.assertEqual(result.status, self.analyzer.DEFAULT_STATUS)

    def test_extract_content(self):
        """测试内容提取"""
        result = self.analyzer.analyze("记录一下：完成了任务")
        self.assertIn("任务", result.content)

        result = self.analyzer.analyze("提交一个任务")
        self.assertIn("任务", result.content)

    def test_extract_note(self):
        """测试备注提取"""
        result = self.analyzer.analyze("完成任务（需要复查）")
        self.assertEqual(result.note, "需要复查")

        result = self.analyzer.analyze("记录任务备注：这是备注")
        self.assertEqual(result.note, "这是备注")

    def test_calculate_confidence(self):
        """测试可信度计算"""
        result = self.analyzer.analyze("记录一下：紧急的重要任务完成了")
        self.assertGreater(result.confidence, 0.5)

        result = self.analyzer.analyze("记录任务")
        self.assertLessEqual(result.confidence, 1.0)

    def test_get_intent_description(self):
        """测试获取意图描述"""
        self.assertEqual(self.analyzer.get_intent_description("record"), "记录任务")
        self.assertEqual(self.analyzer.get_intent_description("query"), "查询任务")
        self.assertEqual(self.analyzer.get_intent_description("update"), "更新任务")
        self.assertEqual(self.analyzer.get_intent_description("delete"), "删除任务")
        self.assertEqual(self.analyzer.get_intent_description("unknown"), "未知意图")

    def test_validate_params(self):
        """测试参数验证"""
        valid_params = {
            "project_type": "技术开发",
            "priority": "高",
            "status": "已完成",
        }
        is_valid, error = self.analyzer.validate_params(valid_params)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

        invalid_params = {"project_type": "无效类型"}
        is_valid, error = self.analyzer.validate_params(invalid_params)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)


class TestWorklogAssistant(unittest.TestCase):
    """测试 WorklogAssistant 端到端流程"""

    def setUp(self):
        self.app_token = "BISAbNgYXa7Do1sc36YcBChInnS"
        self.table_id = "tbl5s8TEZ0tKhEm7"

    @patch("worklog_assistant.BitableManager")
    def test_init(self, mock_bitable):
        """测试初始化"""
        assistant = WorklogAssistant(self.app_token, self.table_id)
        self.assertIsNotNone(assistant.bitable_manager)
        self.assertIsNotNone(assistant.intent_analyzer)

    def test_process_empty_input(self):
        """测试空输入处理"""
        assistant = WorklogAssistant(self.app_token, self.table_id)
        with patch.object(assistant.intent_analyzer, "analyze") as mock_analyze:
            with self.assertRaises(WorklogAssistantError):
                assistant.process("")

    @patch("worklog_assistant.BitableManager")
    def test_process_record_intent(self, mock_bitable_class):
        """测试记录意图处理"""
        mock_bitable = Mock()
        mock_bitable_class.return_value = mock_bitable

        mock_bitable.add_record.return_value = {
            "success": True,
            "record_id": "rec123",
            "content": "测试任务",
            "project_type": "技术开发",
            "priority": "中",
            "status": "待确认",
        }

        assistant = WorklogAssistant(self.app_token, self.table_id)
        result = assistant.process("记录一下：测试任务")

        self.assertIn("记录创建成功", result)
        self.assertIn("测试任务", result)
        mock_bitable.add_record.assert_called_once()

    @patch("worklog_assistant.BitableManager")
    def test_process_query_intent(self, mock_bitable_class):
        """测试查询意图处理"""
        mock_bitable = Mock()
        mock_bitable_class.return_value = mock_bitable

        mock_bitable.query_records.return_value = [
            {
                "record_id": "rec1",
                "fields": {
                    "内容": "任务1",
                    "项目状态": "已完成",
                    "项目类型": "技术开发",
                },
            }
        ]

        assistant = WorklogAssistant(self.app_token, self.table_id)
        result = assistant.process("查询今天的任务")

        self.assertIn("查询结果", result)
        mock_bitable.query_records.assert_called_once()

    @patch("worklog_assistant.BitableManager")
    def test_process_query_empty_result(self, mock_bitable_class):
        """测试查询空结果"""
        mock_bitable = Mock()
        mock_bitable_class.return_value = mock_bitable
        mock_bitable.query_records.return_value = []

        assistant = WorklogAssistant(self.app_token, self.table_id)
        result = assistant.process("查询不存在的任务")

        self.assertIn("没有找到", result)

    @patch("worklog_assistant.BitableManager")
    def test_process_update_intent(self, mock_bitable_class):
        """测试更新意图处理"""
        mock_bitable = Mock()
        mock_bitable_class.return_value = mock_bitable
        mock_bitable.update_status.return_value = True

        assistant = WorklogAssistant(self.app_token, self.table_id)
        result = assistant.process("更新record_id=rec123状态为完成")

        self.assertIn("更新成功", result)
        mock_bitable.update_status.assert_called_once()

    @patch("worklog_assistant.BitableManager")
    def test_process_delete_intent(self, mock_bitable_class):
        """测试删除意图处理"""
        mock_bitable = Mock()
        mock_bitable_class.return_value = mock_bitable
        mock_bitable.delete_record.return_value = True

        assistant = WorklogAssistant(self.app_token, self.table_id)

        original_analyze = assistant.intent_analyzer.analyze

        class MockIntentResult:
            intent = "delete"
            content = "ID=rec123"
            project_type = "技术开发"
            priority = "中"
            status = "待确认"
            note = ""
            confidence = 0.9

        assistant.intent_analyzer.analyze = lambda x: MockIntentResult()

        try:
            result = assistant.process("删除记录")
            self.assertIn("删除成功", result)
            mock_bitable.delete_record.assert_called_once()
        finally:
            assistant.intent_analyzer.analyze = original_analyze

    @patch("worklog_assistant.BitableManager")
    def test_get_statistics(self, mock_bitable_class):
        """测试获取统计信息"""
        mock_bitable = Mock()
        mock_bitable_class.return_value = mock_bitable
        mock_bitable.get_statistics.return_value = {
            "total": 10,
            "completed": 5,
            "in_progress": 3,
            "pending": 2,
            "completion_rate": 50.0,
        }

        assistant = WorklogAssistant(self.app_token, self.table_id)
        result = assistant.get_statistics()

        self.assertIn("工作日志统计", result)
        self.assertIn("10", result)

    @patch("worklog_assistant.BitableManager")
    def test_get_today_summary(self, mock_bitable_class):
        """测试获取今日摘要"""
        mock_bitable = Mock()
        mock_bitable_class.return_value = mock_bitable
        mock_bitable.get_today_statistics.return_value = {
            "date": "2026-03-15",
            "total": 5,
            "completed": 3,
            "in_progress": 2,
        }

        assistant = WorklogAssistant(self.app_token, self.table_id)
        result = assistant.get_today_summary()

        self.assertIn("今日工作摘要", result)

    @patch("worklog_assistant.BitableManager")
    def test_set_access_token(self, mock_bitable_class):
        """测试设置 access_token"""
        mock_bitable = Mock()
        mock_bitable_class.return_value = mock_bitable

        assistant = WorklogAssistant(self.app_token, self.table_id)
        assistant.set_access_token("test_token_123")

        mock_bitable.set_access_token.assert_called_once_with("test_token_123")


class TestIntegration(unittest.TestCase):
    """集成测试 - 端到端流程"""

    def setUp(self):
        self.app_token = "BISAbNgYXa7Do1sc36YcBChInnS"
        self.table_id = "tbl5s8TEZ0tKhEm7"

    @patch("worklog_assistant.BitableManager")
    def test_full_workflow(self, mock_bitable_class):
        """测试完整工作流"""
        mock_bitable = Mock()
        mock_bitable_class.return_value = mock_bitable

        mock_bitable.add_record.return_value = {
            "success": True,
            "record_id": "rec123",
            "content": "完成设计图",
            "project_type": "室内设计",
            "priority": "高",
            "status": "已完成",
        }

        mock_bitable.query_records.return_value = [
            {
                "record_id": "rec123",
                "fields": {
                    "内容": "完成设计图",
                    "项目状态": "已完成",
                    "项目类型": "室内设计",
                },
            }
        ]

        mock_bitable.get_statistics.return_value = {
            "total": 1,
            "completed": 1,
            "in_progress": 0,
            "pending": 0,
            "completion_rate": 100.0,
        }

        assistant = WorklogAssistant(self.app_token, self.table_id)

        result1 = assistant.process("记录一下：紧急任务，完成设计图")
        self.assertIn("记录创建成功", result1)

        result2 = assistant.process("查询已完成的任务")
        self.assertIn("查询结果", result2)

        result3 = assistant.get_statistics()
        self.assertIn("工作日志统计", result3)


if __name__ == "__main__":
    unittest.main()
