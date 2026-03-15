"""
自动记录模块

监控对话内容，识别重要信息并自动记录到飞书Bitable
"""

import logging
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, field
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class ContentType(Enum):
    """内容类型枚举"""

    QUESTION = "问题"
    ANSWER = "回答"
    COMMAND = "命令"
    STATEMENT = "声明"
    DISCUSSION = "讨论"


class AutoRecordError(Exception):
    """自动记录基础异常"""

    pass


class AutoRecordConfigError(AutoRecordError):
    """配置异常"""

    pass


@dataclass
class MemoryPattern:
    """记忆识别模式"""

    name: str
    pattern: str
    memory_type: str
    importance_boost: int = 0
    tags: List[str] = field(default_factory=list)


@dataclass
class RecognizedMemory:
    """识别出的记忆"""

    content: str
    memory_type: str
    importance: int
    tags: List[str]
    reason: str
    confidence: float


class KeywordAnalyzer:
    """关键词分析器"""

    # 决策关键词
    DECISION_KEYWORDS = {
        "决定",
        "选择",
        "采纳",
        "确定",
        "批准",
        "认可",
        "就这样",
        "好吧",
        "可以",
        "没问题",
        "同意",
        "will",
        "decide",
        "choose",
        "agree",
        "accept",
    }

    # 学习关键词
    LEARNING_KEYWORDS = {
        "学习",
        "学会",
        "掌握",
        "了解",
        "理解",
        "知道",
        "教程",
        "文档",
        "例子",
        "演示",
        "讲解",
        "learn",
        "understand",
        "master",
        "tutorial",
    }

    # 技能关键词
    SKILL_KEYWORDS = {
        "技能",
        "技巧",
        "方法",
        "方案",
        "策略",
        "怎么",
        "如何",
        "怎样",
        "做",
        "实现",
        "skill",
        "technique",
        "method",
        "how to",
    }

    # 任务关键词
    TASK_KEYWORDS = {
        "任务",
        "待办",
        "todo",
        "完成",
        "执行",
        "做一下",
        "帮我",
        "请",
        "需要",
        "必须",
        "task",
        "todo",
        "must",
        "need to",
    }

    # 项目关键词
    PROJECT_KEYWORDS = {
        "项目",
        "产品",
        "系统",
        "平台",
        "应用",
        "开发",
        "设计",
        "架构",
        "构建",
        "project",
        "product",
        "system",
        "develop",
    }

    @classmethod
    def analyze_content(cls, text: str) -> Dict[str, Any]:
        """分析内容

        参数:
            text: 待分析文本

        返回:
            Dict: 分析结果
        """
        text_lower = text.lower()

        # 检测决策
        is_decision = any(kw in text for kw in cls.DECISION_KEYWORDS)

        # 检测学习
        is_learning = any(kw in text for kw in cls.LEARNING_KEYWORDS)

        # 检测技能
        is_skill = any(kw in text for kw in cls.SKILL_KEYWORDS)

        # 检测任务
        is_task = any(kw in text for kw in cls.TASK_KEYWORDS)

        # 检测项目
        is_project = any(kw in text for kw in cls.PROJECT_KEYWORDS)

        # 提取可能的技术术语
        tech_terms = cls._extract_tech_terms(text)

        # 提取标签
        tags = []
        if is_skill:
            tags.extend(["技巧", "方法"])
        if is_learning:
            tags.append("学习")
        if is_task:
            tags.append("任务")
        if is_project:
            tags.append("项目")
        tags.extend(tech_terms)

        # 确定类型
        memory_type = "其他"
        if is_decision:
            memory_type = "决策"
        elif is_task:
            memory_type = "任务"
        elif is_skill or is_learning:
            memory_type = "学习"
        elif is_project:
            memory_type = "项目"

        # 计算重要性分数
        importance = 3  # 默认中等

        if is_decision:
            importance += 2
        if is_skill and tech_terms:
            importance += 1
        if len(text) > 100:
            importance += 1

        importance = min(5, max(1, importance))

        return {
            "is_decision": is_decision,
            "is_learning": is_learning,
            "is_skill": is_skill,
            "is_task": is_task,
            "is_project": is_project,
            "memory_type": memory_type,
            "importance": importance,
            "tags": list(set(tags)),
            "tech_terms": tech_terms,
        }

    @classmethod
    def _extract_tech_terms(cls, text: str) -> List[str]:
        """提取技术术语"""
        tech_patterns = [
            r"\b(Python|JavaScript|React|Node\.js|TypeScript)\b",
            r"\b(API|SDK|CLI|REST|GraphQL)\b",
            r"\b(Docker|Kubernetes|K8s)\b",
            r"\b(Git|GitHub|Docker)\b",
            r"\b(pip|npm|yarn|conda)\b",
            r"\b(mongo|mysql|redis|postgresql)\b",
            r"\b(AI|ML|LLM|GPT)\b",
        ]

        terms = []
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms.extend([m.lower() for m in matches])

        return list(set(terms))


class ImportanceScorer:
    """重要性评分器"""

    # 基础分数
    BASE_SCORE = 3

    # 长度相关
    LENGTH_THRESHOLDS = [
        (50, 1),
        (200, 2),
        (500, 3),
        (1000, 4),
    ]

    # 加分模式
    BOOST_PATTERNS = [
        (r"记住|记住这个|保存|记录", 2, "用户要求记忆"),
        (r"重要|关键|核心|必须", 1, "明确重要性"),
        (r"以后|将来|未来|下次", 1, "未来参考"),
        (r"配置|设置|安装|部署", 1, "配置类"),
        (r"错误|bug|问题|修复", 1, "问题解决"),
        (r"api|接口|函数|方法", 1, "技术内容"),
    ]

    # 减分模式
    REDUCE_PATTERNS = [
        (r"哈哈|呵呵|哦|嗯", -1, "语气词"),
        (r"你好| hi | hello", -1, "问候"),
    ]

    @classmethod
    def calculate_score(
        cls,
        text: str,
        content_type: ContentType = ContentType.STATEMENT,
        user_specified_importance: Optional[int] = None,
    ) -> int:
        """计算重要性分数

        参数:
            text: 文本内容
            content_type: 内容类型
            user_specified_importance: 用户指定的重要性

        返回:
            int: 重要性分数 (1-5)
        """
        if user_specified_importance is not None:
            return min(5, max(1, user_specified_importance))

        score = cls.BASE_SCORE

        # 长度加分
        text_length = len(text)
        for threshold, bonus in cls.LENGTH_THRESHOLDS:
            if text_length >= threshold:
                score += bonus

        # 内容类型加分
        if content_type == ContentType.STATEMENT:
            score += 2
        elif content_type == ContentType.ANSWER:
            score += 1

        # 模式加分
        for pattern, boost, reason in cls.BOOST_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                score += boost

        # 模式减分
        for pattern, reduce, reason in cls.REDUCE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                score += reduce

        # 限制范围
        return min(5, max(1, score))

    @classmethod
    def should_auto_record(cls, text: str) -> bool:
        """判断是否应该自动记录

        参数:
            text: 文本内容

        返回:
            bool: 是否应该自动记录
        """
        score = cls.calculate_score(text)
        return score >= 4


class AutoRecord:
    """自动记录器

    监控对话内容，识别重要信息并自动记录
    """

    def __init__(
        self,
        dashboard: Any = None,
        auto_save: bool = False,
        min_importance_threshold: int = 4,
    ):
        """初始化自动记录器

        参数:
            dashboard: 记忆仪表板实例
            auto_save: 是否自动保存到飞书
            min_importance_threshold: 自动记录的最低重要性阈值
        """
        self.dashboard = dashboard
        self.auto_save = auto_save
        self.min_importance_threshold = min_importance_threshold

        self.keyword_analyzer = KeywordAnalyzer()
        self.importance_scorer = ImportanceScorer()

        # 记忆模式
        self.patterns: List[MemoryPattern] = []
        self._init_default_patterns()

        # 记录历史
        self.recognized_memories: List[RecognizedMemory] = []

        # 回调函数
        self.on_memory_recognized: Optional[Callable] = None

        logger.info(
            f"AutoRecord initialized: auto_save={auto_save}, "
            f"min_threshold={min_importance_threshold}"
        )

    def _init_default_patterns(self) -> None:
        """初始化默认模式"""
        self.patterns = [
            MemoryPattern(
                name="记住这个",
                pattern=r"记住|保存|记录",
                memory_type="知识",
                importance_boost=2,
                tags=["用户请求"],
            ),
            MemoryPattern(
                name="配置信息",
                pattern=r"(配置|设置|环境).*[:：]",
                memory_type="知识",
                importance_boost=1,
                tags=["配置"],
            ),
            MemoryPattern(
                name="技术要点",
                pattern=r"(def|class|function|import|api|api)",
                memory_type="学习",
                importance_boost=1,
                tags=["代码", "技术"],
            ),
            MemoryPattern(
                name="决策声明",
                pattern=r"(决定|选择|采纳|就这样)",
                memory_type="决策",
                importance_boost=2,
                tags=["决策"],
            ),
            MemoryPattern(
                name="任务分配",
                pattern=r"(帮我|请|需要|必须).*(做|完成)",
                memory_type="任务",
                importance_boost=1,
                tags=["任务"],
            ),
        ]

    def analyze_message(
        self,
        text: str,
        content_type: ContentType = ContentType.STATEMENT,
        sender: str = "user",
    ) -> RecognizedMemory:
        """分析消息并识别记忆

        参数:
            text: 消息文本
            content_type: 内容类型
            sender: 发送者 (user/assistant)

        返回:
            RecognizedMemory: 识别出的记忆
        """
        # 关键词分析
        keyword_result = self.keyword_analyzer.analyze_content(text)

        # 重要性评分
        importance = self.importance_scorer.calculate_score(text, content_type)

        # 模式匹配
        matched_patterns = []
        for pattern in self.patterns:
            if re.search(pattern.pattern, text, re.IGNORECASE):
                matched_patterns.append(pattern.name)
                importance += pattern.importance_boost

        importance = min(5, max(1, importance))

        # 构建标签
        tags = list(set(keyword_result["tags"]))
        for pattern_name in matched_patterns:
            pattern = next((p for p in self.patterns if p.name == pattern_name), None)
            if pattern and pattern.tags:
                tags.extend(pattern.tags)

        tags = list(set(tags))

        # 确定记忆类型
        memory_type = keyword_result["memory_type"]
        if matched_patterns:
            first_match = next(
                (p for p in self.patterns if p.name == matched_patterns[0]), None
            )
            if first_match:
                memory_type = first_match.memory_type

        # 生成原因
        reasons = []
        if keyword_result["is_decision"]:
            reasons.append("包含决策内容")
        if keyword_result["is_skill"]:
            reasons.append("包含技能/方法")
        if keyword_result["is_learning"]:
            reasons.append("包含学习内容")
        if matched_patterns:
            reasons.append(f"匹配模式: {', '.join(matched_patterns)}")

        reason = "; ".join(reasons) if reasons else "一般内容"

        memory = RecognizedMemory(
            content=text,
            memory_type=memory_type,
            importance=importance,
            tags=tags,
            reason=reason,
            confidence=min(1.0, importance / 5.0),
        )

        self.recognized_memories.append(memory)

        logger.debug(
            f"Recognized memory: type={memory_type}, "
            f"importance={importance}, tags={tags}"
        )

        # 触发回调
        if self.on_memory_recognized:
            try:
                self.on_memory_recognized(memory)
            except Exception as e:
                logger.warning(f"Callback error: {e}")

        return memory

    def should_record(self, memory: RecognizedMemory) -> bool:
        """判断是否应该记录

        参数:
            memory: 识别出的记忆

        返回:
            bool: 是否应该记录
        """
        # 检查重要性阈值
        if memory.importance < self.min_importance_threshold:
            return False

        # 检查是否包含有效内容
        if len(memory.content.strip()) < 10:
            return False

        return True

    def record_memory(
        self,
        content: str,
        memory_type: str = "学习",
        tags: Optional[List[str]] = None,
        importance: int = 3,
    ) -> Dict[str, Any]:
        """记录记忆到仪表板

        参数:
            content: 记忆内容
            memory_type: 记忆类型
            tags: 标签列表
            importance: 重要性

        返回:
            Dict: 记录结果
        """
        if not self.dashboard:
            logger.warning("No dashboard configured, skipping save")
            return {"success": False, "reason": "no_dashboard"}

        if not self.auto_save:
            logger.info(f"Auto-save disabled, would record: {content[:50]}...")
            return {"success": False, "reason": "auto_save_disabled"}

        try:
            result = self.dashboard.add_memory(
                content=content,
                memory_type=memory_type,
                tags=tags,
                importance=importance,
            )
            logger.info(f"Memory recorded successfully: {result.get('record_id')}")
            return result
        except Exception as e:
            logger.error(f"Failed to record memory: {str(e)}")
            return {"success": False, "error": str(e)}

    def process_conversation(
        self,
        messages: List[Dict[str, Any]],
    ) -> List[RecognizedMemory]:
        """处理对话历史

        参数:
            messages: 消息列表 [{"role": "user"/"assistant", "content": "..."}]

        返回:
            List[RecognizedMemory]: 识别出的记忆列表
        """
        recognized = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if not content:
                continue

            # 确定内容类型
            content_type = (
                ContentType.ANSWER if role == "assistant" else ContentType.QUESTION
            )

            # 分析消息
            memory = self.analyze_message(content, content_type, role)

            # 检查是否应该记录
            if self.should_record(memory):
                recognized.append(memory)

                # 自动记录（如果启用）
                if self.auto_save and self.dashboard:
                    self.record_memory(
                        content=memory.content,
                        memory_type=memory.memory_type,
                        tags=memory.tags,
                        importance=memory.importance,
                    )

        logger.info(
            f"Processed {len(messages)} messages, recognized {len(recognized)} memories"
        )
        return recognized

    def get_recent_memories(
        self,
        limit: int = 20,
        min_importance: Optional[int] = None,
    ) -> List[RecognizedMemory]:
        """获取最近识别出的记忆

        参数:
            limit: 返回数量限制
            min_importance: 最低重要性筛选

        返回:
            List[RecognizedMemory]: 记忆列表
        """
        memories = self.recognized_memories[-limit:]

        if min_importance is not None:
            memories = [m for m in memories if m.importance >= min_importance]

        return memories

    def clear_history(self) -> None:
        """清除识别历史"""
        self.recognized_memories.clear()
        logger.info("Memory history cleared")


def create_auto_record(
    dashboard: Any = None,
    access_token: Optional[str] = None,
    auto_save: bool = False,
) -> AutoRecord:
    """创建自动记录器实例

    参数:
        dashboard: 记忆仪表板实例
        access_token: 飞书访问令牌
        auto_save: 是否自动保存

    返回:
        AutoRecord: 自动记录器实例
    """
    from memory_dashboard import MemoryDashboard

    if dashboard is None and access_token:
        dashboard = MemoryDashboard(access_token=access_token)

    return AutoRecord(
        dashboard=dashboard,
        auto_save=auto_save,
    )
