"""
Knowledge Persistence System - 知识持久化系统

基于 Hermes Agent 的知识持久化机制实现
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


@dataclass
class KnowledgeItem:
    """知识条目"""
    id: Optional[int]
    key: str
    value: Any
    category: str
    source: str
    created_at: str
    updated_at: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


class KnowledgeDatabase:
    """知识数据库"""
    
    def __init__(self, db_path: str = "/root/.openclaw/workspace/data/knowledge.db"):
        """初始化数据库"""
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                category TEXT NOT NULL,
                source TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_key ON knowledge(key)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category ON knowledge(category)
        """)
        
        conn.commit()
        conn.close()
        
    def store(self, key: str, value: Any, category: str = "general", 
              source: str = "system", metadata: Dict[str, Any] = None) -> bool:
        """存储知识"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            value_json = json.dumps(value, ensure_ascii=False)
            metadata_json = json.dumps(metadata or {}, ensure_ascii=False)
            
            cursor.execute("""
                INSERT OR REPLACE INTO knowledge 
                (key, value, category, source, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, 
                    COALESCE((SELECT created_at FROM knowledge WHERE key = ?), ?),
                    ?, ?)
            """, (key, value_json, category, source, key, now, now, metadata_json))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ 存储失败: {e}")
            return False
    
    def retrieve(self, key: str) -> Optional[KnowledgeItem]:
        """检索知识"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, key, value, category, source, created_at, updated_at, metadata
                FROM knowledge WHERE key = ?
            """, (key,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return KnowledgeItem(
                    id=row[0],
                    key=row[1],
                    value=json.loads(row[2]),
                    category=row[3],
                    source=row[4],
                    created_at=row[5],
                    updated_at=row[6],
                    metadata=json.loads(row[7]) if row[7] else {}
                )
            return None
            
        except Exception as e:
            print(f"❌ 检索失败: {e}")
            return None
    
    def search(self, query: str, category: str = None, limit: int = 10) -> List[KnowledgeItem]:
        """搜索知识"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if category:
                cursor.execute("""
                    SELECT id, key, value, category, source, created_at, updated_at, metadata
                    FROM knowledge 
                    WHERE key LIKE ? AND category = ?
                    ORDER BY updated_at DESC
                    LIMIT ?
                """, (f"%{query}%", category, limit))
            else:
                cursor.execute("""
                    SELECT id, key, value, category, source, created_at, updated_at, metadata
                    FROM knowledge 
                    WHERE key LIKE ? OR value LIKE ?
                    ORDER BY updated_at DESC
                    LIMIT ?
                """, (f"%{query}%", f"%{query}%", limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                KnowledgeItem(
                    id=row[0],
                    key=row[1],
                    value=json.loads(row[2]),
                    category=row[3],
                    source=row[4],
                    created_at=row[5],
                    updated_at=row[6],
                    metadata=json.loads(row[7]) if row[7] else {}
                )
                for row in rows
            ]
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []
    
    def delete(self, key: str) -> bool:
        """删除知识"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM knowledge WHERE key = ?", (key,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ 删除失败: {e}")
            return False
    
    def list_categories(self) -> List[str]:
        """列出所有分类"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT category FROM knowledge ORDER BY category
            """)
            
            categories = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return categories
            
        except Exception as e:
            print(f"❌ 列出分类失败: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM knowledge")
            total = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT category, COUNT(*) as count 
                FROM knowledge 
                GROUP BY category 
                ORDER BY count DESC
            """)
            
            by_category = {row[0]: row[1] for row in cursor.fetchall()}
            
            conn.close()
            
            return {
                "total_items": total,
                "by_category": by_category,
                "categories_count": len(by_category)
            }
            
        except Exception as e:
            print(f"❌ 获取统计失败: {e}")
            return {}


class KnowledgePersistenceSystem:
    """知识持久化系统（主接口）"""
    
    def __init__(self, db_path: str = "/root/.openclaw/workspace/data/knowledge.db"):
        """初始化系统"""
        self.db = KnowledgeDatabase(db_path)
        
    def learn(self, key: str, value: Any, category: str = "general", 
              source: str = "system") -> bool:
        """学习新知识"""
        return self.db.store(key, value, category, source)
    
    def recall(self, key: str) -> Optional[Any]:
        """回忆知识"""
        item = self.db.retrieve(key)
        return item.value if item else None
    
    def search_knowledge(self, query: str, category: str = None) -> List[Dict]:
        """搜索知识"""
        items = self.db.search(query, category)
        return [item.to_dict() for item in items]
    
    def forget(self, key: str) -> bool:
        """忘记知识"""
        return self.db.delete(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.db.get_stats()


if __name__ == "__main__":
    system = KnowledgePersistenceSystem()
    
    # 测试
    system.learn("test_key", {"hello": "world"}, "test", "system")
    result = system.recall("test_key")
    print(f"✅ 知识持久化系统测试成功: {result}")
