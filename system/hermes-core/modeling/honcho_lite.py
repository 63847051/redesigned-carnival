"""
Honcho 用户建模系统（简化版）

4层工具：
1. profile - 快速用户卡片
2. search - 语义搜索
3. context - 辩证推理
4. conclude - 持久化结论
"""

import json
import os
import sqlite3
import threading
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import hashlib


@dataclass
class UserProfile:
    """用户档案"""

    user_id: str
    name: str
    traits: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    interaction_count: int = 0
    last_seen: str = None
    created_at: str = None


@dataclass
class UserConclusion:
    """用户结论"""

    conclusion_id: str
    user_id: str
    statement: str
    confidence: float
    evidence: List[str] = field(default_factory=list)
    created_at: str = None


class HonchoLite:
    """
    Honcho 用户建模简化版

    提供用户画像、语义搜索、辩证推理、结论持久化功能
    """

    def __init__(self, db_path: str = None):
        self.db_path = (
            Path(db_path)
            if db_path
            else Path.home() / ".hermes" / "hermes-core" / "users.db"
        )
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._lock = threading.RLock()
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        """初始化数据库 schema"""
        with self._lock:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    name TEXT,
                    traits TEXT,
                    preferences TEXT,
                    interaction_count INTEGER DEFAULT 0,
                    last_seen REAL,
                    created_at REAL
                )
            """)

            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    content TEXT,
                    timestamp REAL,
                    metadata TEXT,
                    embedded_content TEXT
                )
            """)

            self._conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS interactions_fts USING fts5(
                    user_id,
                    content,
                    tokenize='porter unicode61'
                )
            """)

            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS conclusions (
                    conclusion_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    statement TEXT,
                    confidence REAL,
                    evidence TEXT,
                    created_at REAL
                )
            """)

            self._conn.commit()

    def profile(self, user_id: str, name: str = None) -> UserProfile:
        """
        快速用户卡片

        返回用户的基本信息
        """
        with self._lock:
            cursor = self._conn.execute(
                """
                SELECT * FROM users WHERE user_id = ?
            """,
                (user_id,),
            )

            row = cursor.fetchone()

            if row:
                profile = UserProfile(
                    user_id=row["user_id"],
                    name=row["name"],
                    traits=json.loads(row["traits"] or "[]"),
                    preferences=json.loads(row["preferences"] or "{}"),
                    interaction_count=row["interaction_count"],
                    last_seen=datetime.fromtimestamp(row["last_seen"]).isoformat()
                    if row["last_seen"]
                    else None,
                    created_at=datetime.fromtimestamp(row["created_at"]).isoformat()
                    if row["created_at"]
                    else None,
                )
            else:
                now = datetime.now().timestamp()
                profile = UserProfile(
                    user_id=user_id,
                    name=name or "Unknown",
                    traits=[],
                    preferences={},
                    interaction_count=0,
                    last_seen=datetime.fromtimestamp(now).isoformat(),
                    created_at=datetime.fromtimestamp(now).isoformat(),
                )

                self._conn.execute(
                    """
                    INSERT INTO users (user_id, name, traits, preferences, interaction_count, last_seen, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (user_id, name or "Unknown", "[]", "{}", 0, now, now),
                )
                self._conn.commit()

            return profile

    def search(self, user_id: str, query: str, limit: int = 10) -> List[Dict]:
        """
        语义搜索

        搜索用户的历史交互记录
        """
        with self._lock:
            cursor = self._conn.execute(
                """
                SELECT i.content, i.timestamp, i.metadata
                FROM interactions i
                JOIN interactions_fts fts ON i.content = fts.content AND i.user_id = fts.user_id
                WHERE i.user_id = ? AND interactions_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """,
                (user_id, query, limit),
            )

            results = []
            for row in cursor:
                results.append(
                    {
                        "content": row[0],
                        "timestamp": row[1],
                        "metadata": json.loads(row[2] or "{}"),
                    }
                )

            if not results:
                cursor = self._conn.execute(
                    """
                    SELECT content, timestamp, metadata
                    FROM interactions
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (user_id, limit),
                )

                for row in cursor:
                    results.append(
                        {
                            "content": row[0],
                            "timestamp": row[1],
                            "metadata": json.loads(row[2] or "{}"),
                        }
                    )

            return results

    def context(self, user_id: str, question: str) -> Dict[str, Any]:
        """
        辩证推理

        基于用户历史进行推理分析
        """
        with self._lock:
            cursor = self._conn.execute(
                """
                SELECT content, timestamp FROM interactions
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT 50
            """,
                (user_id,),
            )

            recent_interactions = [row[0] for row in cursor]

            conclusions = self._get_conclusions(user_id)

            profile = self.profile(user_id)

            reasoning = self._dialectical_reasoning(
                question, recent_interactions, conclusions, profile
            )

            return {
                "question": question,
                "reasoning": reasoning,
                "supporting_evidence": recent_interactions[:5],
                "conclusions": [c.statement for c in conclusions[:3]],
            }

    def _dialectical_reasoning(
        self,
        question: str,
        interactions: List[str],
        conclusions: List[UserConclusion],
        profile: UserProfile,
    ) -> str:
        """辩证推理"""
        return (
            f"基于对用户 {profile.name} 的 {len(interactions)} 次交互分析：{question}"
        )

    def conclude(
        self,
        user_id: str,
        statement: str,
        confidence: float,
        evidence: List[str] = None,
    ) -> UserConclusion:
        """
        持久化结论

        保存对用户的结论
        """
        conclusion_id = hashlib.sha256(f"{user_id}:{statement}".encode()).hexdigest()[
            :16
        ]

        now = datetime.now().timestamp()

        with self._lock:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO conclusions 
                (conclusion_id, user_id, statement, confidence, evidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    conclusion_id,
                    user_id,
                    statement,
                    confidence,
                    json.dumps(evidence or []),
                    now,
                ),
            )
            self._conn.commit()

        return UserConclusion(
            conclusion_id=conclusion_id,
            user_id=user_id,
            statement=statement,
            confidence=confidence,
            evidence=evidence or [],
            created_at=datetime.fromtimestamp(now).isoformat(),
        )

    def _get_conclusions(self, user_id: str) -> List[UserConclusion]:
        """获取用户结论"""
        with self._lock:
            cursor = self._conn.execute(
                """
                SELECT * FROM conclusions
                WHERE user_id = ?
                ORDER BY confidence DESC
                LIMIT 10
            """,
                (user_id,),
            )

            return [
                UserConclusion(
                    conclusion_id=row["conclusion_id"],
                    user_id=row["user_id"],
                    statement=row["statement"],
                    confidence=row["confidence"],
                    evidence=json.loads(row["evidence"] or "[]"),
                    created_at=datetime.fromtimestamp(row["created_at"]).isoformat()
                    if row["created_at"]
                    else None,
                )
                for row in cursor
            ]

    def record_interaction(
        self, user_id: str, content: str, metadata: Dict = None
    ) -> None:
        """记录用户交互"""
        now = datetime.now().timestamp()

        with self._lock:
            existing = self._conn.execute(
                "SELECT user_id FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()

            if not existing:
                self._conn.execute(
                    """
                    INSERT INTO users (user_id, name, traits, preferences, interaction_count, last_seen, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (user_id, "Unknown", "[]", "{}", 0, now, now),
                )

            self._conn.execute(
                """
                INSERT INTO interactions (user_id, content, timestamp, metadata)
                VALUES (?, ?, ?, ?)
            """,
                (user_id, content, now, json.dumps(metadata or {})),
            )

            self._conn.execute(
                """
                INSERT INTO interactions_fts (user_id, content)
                VALUES (?, ?)
            """,
                (user_id, content),
            )

            self._conn.execute(
                """
                UPDATE users SET interaction_count = interaction_count + 1, last_seen = ?
                WHERE user_id = ?
            """,
                (now, user_id),
            )

            self._conn.commit()

    def update_traits(self, user_id: str, traits: List[str]) -> None:
        """更新用户特征"""
        with self._lock:
            self._conn.execute(
                """
                UPDATE users SET traits = ? WHERE user_id = ?
            """,
                (json.dumps(traits), user_id),
            )
            self._conn.commit()

    def get_all_users(self) -> List[UserProfile]:
        """获取所有用户"""
        with self._lock:
            cursor = self._conn.execute("SELECT * FROM users")

            return [
                UserProfile(
                    user_id=row["user_id"],
                    name=row["name"],
                    traits=json.loads(row["traits"] or "[]"),
                    preferences=json.loads(row["preferences"] or "{}"),
                    interaction_count=row["interaction_count"],
                    last_seen=datetime.fromtimestamp(row["last_seen"]).isoformat()
                    if row["last_seen"]
                    else None,
                    created_at=datetime.fromtimestamp(row["created_at"]).isoformat()
                    if row["created_at"]
                    else None,
                )
                for row in cursor
            ]

    def close(self) -> None:
        """关闭连接"""
        with self._lock:
            self._conn.close()


_honcho_instance: Optional[HonchoLite] = None
_honcho_lock = threading.Lock()


def get_honcho() -> HonchoLite:
    """获取全局 Honcho 实例"""
    global _honcho_instance
    if _honcho_instance is None:
        with _honcho_lock:
            if _honcho_instance is None:
                _honcho_instance = HonchoLite()
    return _honcho_instance


def get_user_profile(user_id: str) -> UserProfile:
    """便捷函数：获取用户档案"""
    return get_honcho().profile(user_id)


def search_user_history(user_id: str, query: str) -> List[Dict]:
    """便捷函数：搜索用户历史"""
    return get_honcho().search(user_id, query)


def reason_about_user(user_id: str, question: str) -> Dict:
    """便捷函数：推理用户"""
    return get_honcho().context(user_id, question)


def save_user_conclusion(
    user_id: str, statement: str, confidence: float
) -> UserConclusion:
    """便捷函数：保存用户结论"""
    return get_honcho().conclude(user_id, statement, confidence)
