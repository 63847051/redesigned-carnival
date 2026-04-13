"""
LLM 摘要生成器

使用 LLM 对搜索结果进行总结
生成更人性化的会话摘要
"""

import os
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SummaryResult:
    """摘要结果"""

    summary: str
    key_topics: List[str]
    relevant_sessions: List[Dict]
    confidence: float
    generated_at: str


class LLMSummarizer:
    """
    LLM 摘要生成器

    对搜索结果进行语义摘要
    """

    DEFAULT_PROMPT = """请总结以下搜索结果，找出最相关的会话。

搜索查询: {query}

会话列表:
{sessions}

请返回 JSON 格式的摘要:
{{
    "summary": "简短总结（50字以内）",
    "key_topics": ["主题1", "主题2", "主题3"],
    "relevant_sessions": [{{"session_id": "xxx", "reason": "为什么相关"}}]
}}
"""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = (
            api_key or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        )
        self.model = model or "gpt-4o-mini"
        self._client = None

    def _get_client(self):
        """获取 LLM 客户端"""
        if self._client is None:
            if "OPENAI" in (os.getenv("OPENAI_API_KEY") or ""):
                from openai import OpenAI

                self._client = OpenAI(api_key=self.api_key)
            elif "ANTHROPIC" in (os.getenv("ANTHROPIC_API_KEY") or ""):
                import anthropic

                self._client = anthropic.Anthropic(api_key=self.api_key)
        return self._client

    def summarize(
        self, query: str, sessions: List[Dict], force: bool = False
    ) -> SummaryResult:
        """
        生成摘要

        Args:
            query: 搜索查询
            sessions: 会话列表
            force: 强制使用 LLM（忽略阈值）

        Returns:
            摘要结果
        """
        if not sessions:
            return SummaryResult(
                summary="没有找到相关会话",
                key_topics=[],
                relevant_sessions=[],
                confidence=0.0,
                generated_at=datetime.now().isoformat(),
            )

        if not force and len(sessions) <= 2:
            session_str = "\n".join(
                [
                    f"- {s.get('title', 'Untitled')}: {s.get('snippet', '')[:100]}"
                    for s in sessions
                ]
            )
            session_ids = [
                s.get("session_id", f"session_{i}") for i, s in enumerate(sessions)
            ]
            return SummaryResult(
                summary=f"找到 {len(sessions)} 个相关会话",
                key_topics=self._extract_topics_simple(sessions),
                relevant_sessions=[
                    {"session_id": sid, "reason": "直接匹配"} for sid in session_ids
                ],
                confidence=0.8,
                generated_at=datetime.now().isoformat(),
            )
            return SummaryResult(
                summary=f"找到 {len(sessions)} 个相关会话",
                key_topics=self._extract_topics_simple(sessions),
                relevant_sessions=[
                    {"session_id": s["session_id"], "reason": "直接匹配"}
                    for s in sessions
                ],
                confidence=0.8,
                generated_at=datetime.now().isoformat(),
            )

        return self._summarize_with_llm(query, sessions)

    def _summarize_with_llm(self, query: str, sessions: List[Dict]) -> SummaryResult:
        """使用 LLM 生成摘要"""
        try:
            client = self._get_client()

            session_texts = []
            for i, s in enumerate(sessions, 1):
                session_texts.append(
                    f"{i}. {s.get('title', 'Untitled')}\n"
                    f"   {s.get('snippet', '')[:200]}"
                )

            sessions_str = "\n".join(session_texts)
            prompt = self.DEFAULT_PROMPT.format(query=query, sessions=sessions_str)

            if hasattr(client, "chat") and hasattr(client.chat, "completions"):
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=500,
                )
                result_text = response.choices[0].message.content
            else:
                response = client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}],
                )
                result_text = response.content[0].text

            result = json.loads(result_text)

            return SummaryResult(
                summary=result.get("summary", ""),
                key_topics=result.get("key_topics", []),
                relevant_sessions=result.get("relevant_sessions", []),
                confidence=0.9,
                generated_at=datetime.now().isoformat(),
            )
        except Exception as e:
            return SummaryResult(
                summary=f"摘要生成失败: {str(e)[:50]}",
                key_topics=self._extract_topics_simple(sessions),
                relevant_sessions=[
                    {"session_id": s["session_id"], "reason": "直接匹配"}
                    for s in sessions
                ],
                confidence=0.5,
                generated_at=datetime.now().isoformat(),
            )

    def _extract_topics_simple(self, sessions: List[Dict]) -> List[str]:
        """简单提取主题"""
        topics = set()
        for s in sessions:
            title = s.get("title", "")
            snippet = s.get("snippet", "")

            words = (title + " " + snippet).lower().split()
            for word in words:
                if len(word) > 4 and word not in {
                    "this",
                    "that",
                    "with",
                    "from",
                    "have",
                    "been",
                }:
                    topics.add(word)

        return list(topics)[:5]

    def summarize_conversation(self, messages: List[Dict]) -> str:
        """总结单个对话"""
        if not messages:
            return "空对话"

        user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
        if not user_msgs:
            return "无用户消息"

        return f"对话包含 {len(user_msgs)} 条用户消息"

    def extract_insights(self, sessions: List[Dict]) -> List[str]:
        """从会话中提取洞察"""
        insights = []

        for s in sessions:
            title = s.get("title", "")
            if title:
                insights.append(f"相关主题: {title}")

        return insights[:5]


_summarizer_instance: Optional[LLMSummarizer] = None


def get_llm_summarizer() -> LLMSummarizer:
    """获取全局摘要生成器"""
    global _summarizer_instance
    if _summarizer_instance is None:
        _summarizer_instance = LLMSummarizer()
    return _summarizer_instance


def summarize_search_results(query: str, sessions: List[Dict]) -> SummaryResult:
    """便捷函数：总结搜索结果"""
    summarizer = get_llm_summarizer()
    return summarizer.summarize(query, sessions)
