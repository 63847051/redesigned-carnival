"""
FTS5 会话搜索系统

基于 SQLite FTS5 的全文搜索
支持会话检索和关键词匹配
"""

import sqlite3
import threading
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import json


class SessionSearch:
    """
    FTS5 会话搜索引擎

    提供全文搜索能力，快速检索历史会话
    """

    def __init__(self, db_path: str = None):
        self.db_path = (
            Path(db_path)
            if db_path
            else Path.home() / ".hermes" / "hermes-core" / "sessions.db"
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
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    title TEXT,
                    started_at REAL,
                    ended_at REAL,
                    message_count INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)

            self._conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS session_fts USING fts5(
                    session_id,
                    title,
                    content,
                    tokenize='porter unicode61'
                )
            """)

            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp REAL,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """)

            self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session 
                ON messages(session_id, timestamp)
            """)

            self._conn.commit()

    def index_session(
        self, session_id: str, title: str, messages: List[Dict], metadata: Dict = None
    ) -> None:
        """索引会话"""
        with self._lock:
            now = datetime.now().timestamp()

            content = " ".join(m.get("content", "") for m in messages)

            self._conn.execute(
                """
                INSERT OR REPLACE INTO sessions (id, title, started_at, ended_at, 
                                                message_count, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    session_id,
                    title,
                    now,
                    now,
                    len(messages),
                    json.dumps(metadata or {}),
                ),
            )

            self._conn.execute(
                """
                INSERT INTO session_fts (session_id, title, content)
                VALUES (?, ?, ?)
            """,
                (session_id, title, content),
            )

            for msg in messages:
                self._conn.execute(
                    """
                    INSERT INTO messages (session_id, role, content, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        session_id,
                        msg.get("role", "user"),
                        msg.get("content", ""),
                        msg.get("timestamp", now),
                        json.dumps(msg.get("metadata", {})),
                    ),
                )

            self._conn.commit()

    def search(
        self, query: str, limit: int = 10, session_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        搜索会话

        Args:
            query: 搜索关键词
            limit: 返回结果数量
            session_id: 可选，限定会话

        Returns:
            匹配结果列表
        """
        with self._lock:
            if session_id:
                cursor = self._conn.execute(
                    """
                    SELECT s.id, s.title, s.started_at, s.message_count,
                           snippet(session_fts, 2, '<mark>', '</mark>', '...', 20) as snippet
                    FROM session_fts fts
                    JOIN sessions s ON s.id = fts.session_id
                    WHERE session_fts MATCH ? AND s.id = ?
                    ORDER BY rank
                    LIMIT ?
                """,
                    (query, session_id, limit),
                )
            else:
                cursor = self._conn.execute(
                    """
                    SELECT s.id, s.title, s.started_at, s.message_count,
                           snippet(session_fts, 2, '<mark>', '</mark>', '...', 20) as snippet
                    FROM session_fts fts
                    JOIN sessions s ON s.id = fts.session_id
                    WHERE session_fts MATCH ?
                    ORDER BY rank
                    LIMIT ?
                """,
                    (query, limit),
                )

            results = []
            for row in cursor:
                results.append(
                    {
                        "session_id": row["id"],
                        "title": row["title"],
                        "started_at": row["started_at"],
                        "message_count": row["message_count"],
                        "snippet": row["snippet"],
                    }
                )

            return results

    def get_session_messages(self, session_id: str, limit: int = 100) -> List[Dict]:
        """获取会话消息"""
        with self._lock:
            cursor = self._conn.execute(
                """
                SELECT role, content, timestamp, metadata
                FROM messages
                WHERE session_id = ?
                ORDER BY timestamp
                LIMIT ?
            """,
                (session_id, limit),
            )

            messages = []
            for row in cursor:
                messages.append(
                    {
                        "role": row["role"],
                        "content": row["content"],
                        "timestamp": row["timestamp"],
                        "metadata": json.loads(row["metadata"] or "{}"),
                    }
                )

            return messages

    def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """获取最近会话"""
        with self._lock:
            cursor = self._conn.execute(
                """
                SELECT id, title, started_at, message_count
                FROM sessions
                ORDER BY started_at DESC
                LIMIT ?
            """,
                (limit,),
            )

            sessions = []
            for row in cursor:
                sessions.append(
                    {
                        "session_id": row["id"],
                        "title": row["title"],
                        "started_at": row["started_at"],
                        "message_count": row["message_count"],
                    }
                )

            return sessions

    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        with self._lock:
            self._conn.execute(
                "DELETE FROM messages WHERE session_id = ?", (session_id,)
            )
            self._conn.execute(
                "DELETE FROM session_fts WHERE session_id = ?", (session_id,)
            )
            self._conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            self._conn.commit()
            return True

    def get_stats(self) -> Dict:
        """获取搜索统计"""
        with self._lock:
            session_count = self._conn.execute(
                "SELECT COUNT(*) FROM sessions"
            ).fetchone()[0]

            message_count = self._conn.execute(
                "SELECT COUNT(*) FROM messages"
            ).fetchone()[0]

            return {"session_count": session_count, "message_count": message_count}

    def close(self) -> None:
        """关闭连接"""
        with self._lock:
            self._conn.close()


_search_instance: Optional[SessionSearch] = None
_search_lock = threading.Lock()


def get_session_search() -> SessionSearch:
    """获取全局搜索实例"""
    global _search_instance
    if _search_instance is None:
        with _search_lock:
            if _search_instance is None:
                _search_instance = SessionSearch()
    return _search_instance


def search_sessions(query: str, limit: int = 10) -> List[Dict]:
    """便捷搜索函数"""
    search = get_session_search()
    return search.search(query, limit)


def index_session(session_id: str, title: str, messages: List[Dict]) -> None:
    """便捷索引函数"""
    search = get_session_search()
    search.index_session(session_id, title, messages)
