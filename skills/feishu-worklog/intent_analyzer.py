"""
飞书工作日志意图分析器模块

提供自然语言输入的智能意图识别和参数提取功能
"""

import re
import logging
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class IntentResult:
    """意图分析结果数据类"""

    intent: str
    content: str
    project_type: str
    priority: str
    status: str
    note: str
    confidence: float


class IntentAnalyzerError(Exception):
    """意图分析器基础异常"""

    pass


class IntentAnalyzer:
    """意图分析器

    通过关键词匹配和规则分析，识别用户输入的意图和相关参数
    """

    # 意图类型关键词映射
    INTENTS: Dict[str, List[str]] = {
        "record": ["记录", "添加", "新建", "创建", "写下", "写一下", "提交", "录入"],
        "query": ["查询", "查看", "显示", "统计", "多少", "看看", "有哪些", "列出"],
        "update": ["更新", "修改", "标记", "完成", "改一下", "变更", "调整"],
        "delete": ["删除", "移除", "去掉", "清掉"],
    }

    # 项目类型关键词映射
    PROJECT_KEYWORDS: Dict[str, List[str]] = {
        "室内设计": [
            "设计",
            "图纸",
            "平面图",
            "立面图",
            "天花",
            "排砖",
            "效果图",
            "CAD",
            "施工图",
        ],
        "技术开发": [
            "代码",
            "开发",
            "爬虫",
            "API",
            "脚本",
            "前端",
            "后端",
            "bug",
            "修复",
            "系统",
            "程序",
        ],
        "文档编写": ["文档", "手册", "说明", "报告", "方案", "总结", "记录"],
        "现场": ["现场", "工地", "施工", "验收", "巡查"],
        "机电": ["机电", "电气", "弱电", "智能化"],
    }

    # 优先级关键词映射
    PRIORITY_KEYWORDS: Dict[str, List[str]] = {
        "高": ["紧急", "重要", "优先", "高", "急", "加急", "马上", "立即", "第一时间"],
        "中": ["普通", "中", "正常", "常规", "日常"],
        "低": ["低", "不急", "稍后", "有空", "后面", "不着急"],
    }

    # 状态关键词映射
    STATUS_KEYWORDS: Dict[str, List[str]] = {
        "待确认": ["待确认", "待办", "todo", "未开始", "待处理", "新"],
        "进行中": ["进行中", "doing", "正在", "在做", "处理中", "进行", "开始", "着手"],
        "已完成": ["完成", "done", "已完成", "做好了", "结束", "完结", "结束", "做好"],
    }

    # 默认值
    DEFAULT_PROJECT_TYPE = "技术开发"
    DEFAULT_PRIORITY = "中"
    DEFAULT_STATUS = "待确认"

    def __init__(self) -> None:
        """初始化意图分析器"""
        logger.info("IntentAnalyzer initialized")
        self._build_patterns()

    def _build_patterns(self) -> None:
        """预编译正则表达式以提高匹配效率"""
        self._intent_patterns: Dict[str, re.Pattern] = {}
        for intent, keywords in self.INTENTS.items():
            pattern = "|".join(re.escape(kw) for kw in keywords)
            self._intent_patterns[intent] = re.compile(pattern)

    def analyze(self, text: str) -> IntentResult:
        """分析用户输入

        参数:
            text: 用户输入文本

        返回:
            IntentResult: 解析后的意图和参数

        异常:
            IntentAnalyzerError: 当输入文本无效时

        示例:
            >>> analyzer = IntentAnalyzer()
            >>> result = analyzer.analyze("记录一下：完成了3F会议室平面图设计")
            >>> print(result.intent)
            record
        """
        if not text or not text.strip():
            raise IntentAnalyzerError("输入文本不能为空")

        text = text.strip()
        logger.debug(f"Analyzing text: {text}")

        intent = self._detect_intent(text)
        content = self._extract_content(text)
        project_type = self._detect_project_type(text)
        priority = self._detect_priority(text)
        status = self._detect_status(text)
        note = self._extract_note(text)
        confidence = self._calculate_confidence(intent, project_type, priority, status)

        result = IntentResult(
            intent=intent,
            content=content,
            project_type=project_type,
            priority=priority,
            status=status,
            note=note,
            confidence=confidence,
        )

        logger.info(
            f"Analysis result: intent={intent}, project_type={project_type}, "
            f"priority={priority}, status={status}, confidence={confidence:.2f}"
        )

        return result

    def _detect_intent(self, text: str) -> str:
        """检测意图类型

        参数:
            text: 用户输入文本

        返回:
            str: 意图类型 (record/query/update/delete)
        """
        scores: Dict[str, float] = {intent: 0.0 for intent in self.INTENTS}

        for intent, pattern in self._intent_patterns.items():
            matches = pattern.findall(text)
            scores[intent] = float(len(matches))

        if not scores or max(scores.values()) == 0:
            logger.warning("No intent detected, defaulting to 'record'")
            return "record"

        detected_intent = max(scores, key=scores.get)
        logger.debug(f"Intent scores: {scores}, detected: {detected_intent}")

        return detected_intent

    def _extract_content(self, text: str) -> str:
        """提取任务内容

        处理掉意图关键词，保留核心内容

        参数:
            text: 用户输入文本

        返回:
            str: 任务内容
        """
        content = text

        # 移除常见前缀模式
        prefixes_to_remove = [
            r"^记录一下[：:]*",
            r"^添加[：:]*",
            r"^新建[：:]*",
            r"^创建[：:]*",
            r"^写一下[：:]*",
            r"^提交[：:]*",
            r"^录入[：:]*",
            r"^查询[：:]*",
            r"^查看[：:]*",
            r"^显示[：:]*",
            r"^更新[：:]*",
            r"^修改[：:]*",
            r"^标记[：:]*",
            r"^删除[：:]*",
        ]

        for prefix in prefixes_to_remove:
            content = re.sub(prefix, "", content, flags=re.IGNORECASE)

        # 移除第一个出现的意图关键词之前的内容
        all_keywords: List[str] = []
        for keywords in self.INTENTS.values():
            all_keywords.extend(keywords)

        for keyword in all_keywords:
            pattern = f"^{re.escape(keyword)}"
            content = re.sub(pattern, "", content, count=1)

        # 清理多余空白
        content = re.sub(r"\s+", " ", content).strip()

        if not content:
            content = text

        return content

    def _detect_project_type(self, text: str) -> str:
        """检测项目类型

        参数:
            text: 用户输入文本

        返回:
            str: 项目类型
        """
        scores: Dict[str, int] = {ptype: 0 for ptype in self.PROJECT_KEYWORDS}

        for ptype, keywords in self.PROJECT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    scores[ptype] += 1

        if max(scores.values()) == 0:
            logger.debug("No project type detected, using default")
            return self.DEFAULT_PROJECT_TYPE

        detected = max(scores, key=scores.get)
        logger.debug(f"Project type scores: {scores}, detected: {detected}")

        return detected

    def _detect_priority(self, text: str) -> str:
        """检测优先级

        参数:
            text: 用户输入文本

        返回:
            str: 优先级
        """
        scores: Dict[str, int] = {priority: 0 for priority in self.PRIORITY_KEYWORDS}

        for priority, keywords in self.PRIORITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    scores[priority] += 1

        if max(scores.values()) == 0:
            logger.debug("No priority detected, using default")
            return self.DEFAULT_PRIORITY

        detected = max(scores, key=scores.get)
        logger.debug(f"Priority scores: {scores}, detected: {detected}")

        return detected

    def _detect_status(self, text: str) -> str:
        """检测状态

        参数:
            text: 用户输入文本

        返回:
            str: 状态
        """
        scores: Dict[str, int] = {status: 0 for status in self.STATUS_KEYWORDS}

        for status, keywords in self.STATUS_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    scores[status] += 1

        if max(scores.values()) == 0:
            logger.debug("No status detected, using default")
            return self.DEFAULT_STATUS

        detected = max(scores, key=scores.get)
        logger.debug(f"Status scores: {scores}, detected: {detected}")

        return detected

    def _extract_note(self, text: str) -> str:
        """提取备注信息

        尝试从文本中提取备注内容，通常在括号或特定标记后

        参数:
            text: 用户输入文本

        返回:
            str: 备注内容
        """
        # 匹配括号内的内容作为备注
        bracket_patterns = [
            r"[（(]([^）)]+)[）)]",
            r"备注[:：]?\s*([^，,]+)?",
            r"说明[:：]?\s*([^，,]+)?",
        ]

        for pattern in bracket_patterns:
            match = re.search(pattern, text)
            if match:
                note = match.group(1).strip()
                if note:
                    return note

        return ""

    def _calculate_confidence(
        self,
        intent: str,
        project_type: str,
        priority: str,
        status: str,
    ) -> float:
        """计算解析结果的可信度

        参数:
            intent: 意图类型
            project_type: 项目类型
            priority: 优先级
            status: 状态

        返回:
            float: 可信度分数 (0-1)
        """
        score = 0.0

        # 意图检测有匹配
        if intent in self._intent_patterns:
            pattern = self._intent_patterns[intent]
            if pattern.search(f"记录查询修改删除添加新建"):
                score += 0.3

        # 非默认值被检测到
        if project_type != self.DEFAULT_PROJECT_TYPE:
            score += 0.2

        if priority != self.DEFAULT_PRIORITY:
            score += 0.2

        if status != self.DEFAULT_STATUS:
            score += 0.2

        # 内容非空
        score += 0.1

        return min(score, 1.0)

    def get_intent_description(self, intent: str) -> str:
        """获取意图的中文描述

        参数:
            intent: 意图类型

        返回:
            str: 中文描述
        """
        descriptions = {
            "record": "记录任务",
            "query": "查询任务",
            "update": "更新任务",
            "delete": "删除任务",
        }
        return descriptions.get(intent, "未知意图")

    def validate_params(self, params: Dict) -> Tuple[bool, Optional[str]]:
        """验证解析后的参数是否有效

        参数:
            params: 参数字典

        返回:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        valid_project_types = list(self.PROJECT_KEYWORDS.keys()) + [
            self.DEFAULT_PROJECT_TYPE
        ]
        valid_priorities = list(self.PRIORITY_KEYWORDS.keys()) + [self.DEFAULT_PRIORITY]
        valid_statuses = list(self.STATUS_KEYWORDS.keys()) + [self.DEFAULT_STATUS]

        if (
            params.get("project_type")
            and params["project_type"] not in valid_project_types
        ):
            return False, f"无效的项目类型: {params['project_type']}"

        if params.get("priority") and params["priority"] not in valid_priorities:
            return False, f"无效的优先级: {params['priority']}"

        if params.get("status") and params["status"] not in valid_statuses:
            return False, f"无效的状态: {params['status']}"

        return True, None
