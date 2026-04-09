#!/usr/bin/env python3
"""
知识图谱实现 - 时序实体关系
使用 SQLite 实现类似 MemPalace 的知识图谱
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

KG_DB_PATH = Path("/root/.openclaw/workspace/data/knowledge-graph.db")


class KnowledgeGraph:
    """知识图谱 - 时序实体关系"""

    def __init__(self, db_path: Path = KG_DB_PATH):
        self.db_path = db_path
        self.conn = None
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()

    def _create_tables(self):
        """创建表"""
        cursor = self.conn.cursor()

        # 创建三元组表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS triples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                predicate TEXT NOT NULL,
                object TEXT NOT NULL,
                valid_from TEXT,
                valid_until TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_subject
            ON triples(subject)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_object
            ON triples(object)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_validity
            ON triples(valid_from, valid_until)
        """)

        self.conn.commit()

    def add_triple(
        self,
        subject: str,
        predicate: str,
        obj: str,
        valid_from: Optional[str] = None,
        valid_until: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """添加三元组"""
        if valid_from is None:
            valid_from = datetime.now().isoformat()

        metadata_json = json.dumps(metadata) if metadata else None

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO triples (subject, predicate, object, valid_from, valid_until, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (subject, predicate, obj, valid_from, valid_until, metadata_json))

        self.conn.commit()
        print(f"✅ 添加三元组: {subject} → {predicate} → {obj}")

    def invalidate(
        self,
        subject: str,
        predicate: str,
        obj: str,
        ended: Optional[str] = None
    ):
        """使三元组失效"""
        if ended is None:
            ended = datetime.now().isoformat()

        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE triples
            SET valid_until = ?
            WHERE subject = ? AND predicate = ? AND object = ?
            AND valid_until IS NULL
        """, (ended, subject, predicate, obj))

        self.conn.commit()
        print(f"🔒 失效三元组: {subject} → {predicate} → {obj}")

    def query_entity(self, entity: str, as_of: Optional[str] = None) -> List[Dict]:
        """查询实体"""
        cursor = self.conn.cursor()

        if as_of:
            # 查询特定时间点的有效三元组
            cursor.execute("""
                SELECT subject, predicate, object, valid_from, valid_until
                FROM triples
                WHERE (subject = ? OR object = ?)
                AND valid_from <= ?
                AND (valid_until IS NULL OR valid_until > ?)
            """, (entity, entity, as_of, as_of))
        else:
            # 查询当前有效的三元组
            cursor.execute("""
                SELECT subject, predicate, object, valid_from, valid_until
                FROM triples
                WHERE (subject = ? OR object = ?)
                AND (valid_until IS NULL OR valid_until > datetime('now'))
            """, (entity, entity))

        results = []
        for row in cursor.fetchall():
            results.append({
                "subject": row[0],
                "predicate": row[1],
                "object": row[2],
                "valid_from": row[3],
                "valid_until": row[4]
            })

        return results

    def timeline(self, entity: str) -> List[Dict]:
        """获取实体时间线"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT subject, predicate, object, valid_from, valid_until
            FROM triples
            WHERE subject = ? OR object = ?
            ORDER BY valid_from ASC
        """, (entity, entity))

        results = []
        for row in cursor.fetchall():
            results.append({
                "subject": row[0],
                "predicate": row[1],
                "object": row[2],
                "valid_from": row[3],
                "valid_until": row[4]
            })

        return results

    def get_stats(self) -> Dict:
        """获取统计信息"""
        cursor = self.conn.cursor()

        # 总三元组数
        cursor.execute("SELECT COUNT(*) FROM triples")
        total = cursor.fetchone()[0]

        # 当前有效的三元组数
        cursor.execute("""
            SELECT COUNT(*) FROM triples
            WHERE valid_until IS NULL OR valid_until > datetime('now')
        """)
        active = cursor.fetchone()[0]

        # 唯一实体数
        cursor.execute("""
            SELECT COUNT(DISTINCT subject) FROM triples
            UNION
            SELECT COUNT(DISTINCT object) FROM triples
        """)
        entities = sum(row[0] for row in cursor.fetchall())

        return {
            "total_triples": total,
            "active_triples": active,
            "unique_entities": entities
        }

    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()


def demo():
    """演示知识图谱功能"""
    print("=" * 50)
    print("🕸️  知识图谱演示")
    print("=" * 50)

    kg = KnowledgeGraph()

    # 添加示例三元组
    print("\n📝 添加示例三元组...")

    kg.add_triple("幸运小行星", "使用", "OpenClaw", valid_from="2026-03-01")
    kg.add_triple("幸运小行星", "完成", "FinanceDatabase 集成", valid_from="2026-04-08")
    kg.add_triple("幸运小行星", "完成", "Golutra 并行执行", valid_from="2026-04-08")
    kg.add_triple("幸运小行星", "完成", "ECC 安全增强 Phase 1", valid_from="2026-04-08")
    kg.add_triple("小新", "负责", "技术任务", valid_from="2026-03-22")
    kg.add_triple("小蓝", "负责", "日志任务", valid_from="2026-03-22")
    kg.add_triple("设计专家", "负责", "设计任务", valid_from="2026-03-22")

    # 查询实体
    print("\n🔍 查询幸运小行星:")
    results = kg.query_entity("幸运小行星")
    for r in results:
        print(f"  - {r['subject']} → {r['predicate']} → {r['object']}")
        print(f"    有效期: {r['valid_from']} 至 {r['valid_until'] or '现在'}")

    # 时间线
    print("\n📅 幸运小行星时间线:")
    timeline = kg.timeline("幸运小行星")
    for event in timeline:
        print(f"  {event['valid_from']}: {event['predicate']} {event['object']}")

    # 统计
    print("\n📊 统计:")
    stats = kg.get_stats()
    print(f"  - 总三元组: {stats['total_triples']}")
    print(f"  - 有效三元组: {stats['active_triples']}")
    print(f"  - 唯一实体: {stats['unique_entities']}")

    kg.close()

    print("\n✅ 知识图谱演示完成！")
    print(f"📁 数据库: {KG_DB_PATH}")


if __name__ == "__main__":
    import json
    demo()
