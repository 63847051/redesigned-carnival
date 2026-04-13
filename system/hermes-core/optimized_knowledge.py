"""
Optimized Knowledge Persistence - 优化的知识持久化系统

新增功能：
- 查询缓存（LRU）
- 批量操作
- 索引优化
"""

import sqlite3
import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from functools import lru_cache
from collections import OrderedDict

# 导入原始系统
from knowledge_persistence import KnowledgeItem, KnowledgeDatabase


class LRUCache:
    """LRU 缓存实现"""
    
    def __init__(self, capacity: int = 100, ttl: int = 3600):
        """
        初始化 LRU 缓存
        
        Args:
            capacity: 缓存容量
            ttl: 生存时间（秒）
        """
        self.capacity = capacity
        self.ttl = ttl
        self.cache: OrderedDict[str, tuple] = OrderedDict()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key not in self.cache:
            return None
        
        value, timestamp = self.cache[key]
        
        # 检查是否过期
        if time.time() - timestamp > self.ttl:
            del self.cache[key]
            return None
        
        # 移到末尾（最近使用）
        self.cache.move_to_end(key)
        return value
    
    def put(self, key: str, value: Any):
        """设置缓存值"""
        # 移到末尾
        self.cache[key] = (value, time.time())
        self.cache.move_to_end(key)
        
        # 超出容量，删除最旧的
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
    
    def invalidate(self, key: str = None):
        """使缓存失效"""
        if key:
            self.cache.pop(key, None)
        else:
            self.cache.clear()
    
    def get_stats(self) -> Dict:
        """获取缓存统计"""
        return {
            "size": len(self.cache),
            "capacity": self.capacity,
            "ttl": self.ttl,
            "hit_rate": 0.0  # 需要额外跟踪
        }


class OptimizedKnowledgeDatabase(KnowledgeDatabase):
    """优化的知识数据库（继承自原始数据库）"""
    
    def __init__(self, db_path: str = "/root/.openclaw/workspace/data/knowledge.db",
                 cache_size: int = 100, cache_ttl: int = 3600):
        """
        初始化优化的知识数据库
        
        Args:
            db_path: 数据库路径
            cache_size: 缓存大小
            cache_ttl: 缓存生存时间（秒）
        """
        super().__init__(db_path)
        
        # 初始化缓存
        self.cache = LRUCache(capacity=cache_size, ttl=cache_ttl)
        
        # 优化索引
        self._optimize_indexes()
    
    def _optimize_indexes(self):
        """优化数据库索引"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建复合索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category_updated
            ON knowledge(category, updated_at DESC)
        """)
        
        # 创建全文搜索索引（如果支持 FTS5）
        try:
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts
                USING fts5(key, value, category, content=knowledge, content_rowid=id)
            """)
            
            # 触发器保持同步
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS knowledge_ai AFTER INSERT ON knowledge BEGIN
                    INSERT INTO knowledge_fts(rowid, key, value, category)
                    VALUES (new.id, new.key, new.value, new.category);
                END
            """)
            
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS knowledge_ad AFTER DELETE ON knowledge BEGIN
                    INSERT INTO knowledge_fts(knowledge_fts, rowid, key, value, category)
                    VALUES ('delete', old.id, old.key, old.value, old.category);
                END
            """)
            
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS knowledge_au AFTER UPDATE ON knowledge BEGIN
                    INSERT INTO knowledge_fts(knowledge_fts, rowid, key, value, category)
                    VALUES ('delete', old.id, old.key, old.value, old.category);
                    INSERT INTO knowledge_fts(rowid, key, value, category)
                    VALUES (new.id, new.key, new.value, new.category);
                END
            """)
        except Exception as e:
            print(f"⚠️ FTS5 不可用: {e}")
        
        conn.commit()
        conn.close()
    
    def retrieve(self, key: str) -> Optional[KnowledgeItem]:
        """检索知识（带缓存）"""
        # 先查缓存
        cached = self.cache.get(key)
        if cached:
            return cached
        
        # 查数据库
        item = super().retrieve(key)
        
        # 更新缓存
        if item:
            self.cache.put(key, item)
        
        return item
    
    def store(self, key: str, value: Any, category: str = "general",
              source: str = "system", metadata: Dict[str, Any] = None) -> bool:
        """存储知识（更新缓存）"""
        result = super().store(key, value, category, source, metadata)
        
        # 更新缓存
        if result:
            self.cache.invalidate(key)  # 使旧缓存失效
        
        return result
    
    def search(self, query: str, category: str = None, limit: int = 10) -> List[KnowledgeItem]:
        """搜索知识（使用 FTS5）"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 尝试使用 FTS5
            if category:
                cursor.execute("""
                    SELECT k.id, k.key, k.value, k.category, k.source, k.created_at, k.updated_at, k.metadata
                    FROM knowledge k
                    JOIN knowledge_fts fts ON k.id = fts.rowid
                    WHERE knowledge_fts MATCH ? AND k.category = ?
                    ORDER BY k.updated_at DESC
                    LIMIT ?
                """, (query, category, limit))
            else:
                cursor.execute("""
                    SELECT k.id, k.key, k.value, k.category, k.source, k.created_at, k.updated_at, k.metadata
                    FROM knowledge k
                    JOIN knowledge_fts fts ON k.id = fts.rowid
                    WHERE knowledge_fts MATCH ?
                    ORDER BY k.updated_at DESC
                    LIMIT ?
                """, (query, limit))
            
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
            
        except Exception:
            # FTS5 不可用，使用原始搜索
            return super().search(query, category, limit)
    
    def batch_store(self, items: List[Dict[str, Any]]) -> int:
        """批量存储知识"""
        success_count = 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 开始事务
            conn.execute("BEGIN TRANSACTION")
            
            now = datetime.now().isoformat()
            
            for item_data in items:
                key = item_data.get("key")
                value = item_data.get("value")
                category = item_data.get("category", "general")
                source = item_data.get("source", "system")
                metadata = item_data.get("metadata", {})
                
                value_json = json.dumps(value, ensure_ascii=False)
                metadata_json = json.dumps(metadata, ensure_ascii=False)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO knowledge 
                    (key, value, category, source, created_at, updated_at, metadata)
                    VALUES (?, ?, ?, ?, 
                        COALESCE((SELECT created_at FROM knowledge WHERE key = ?), ?),
                        ?, ?)
                """, (key, value_json, category, source, key, now, now, metadata_json))
                
                success_count += 1
            
            # 提交事务
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            print(f"❌ 批量存储失败: {e}")
        finally:
            conn.close()
        
        # 清空缓存
        self.cache.invalidate()
        
        return success_count
    
    def batch_retrieve(self, keys: List[str]) -> Dict[str, KnowledgeItem]:
        """批量检索知识"""
        result = {}
        
        # 先从缓存获取
        for key in keys:
            cached = self.cache.get(key)
            if cached:
                result[key] = cached
        
        # 剩余的从数据库获取
        remaining_keys = [k for k in keys if k not in result]
        
        if remaining_keys:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            placeholders = ','.join(['?'] * len(remaining_keys))
            cursor.execute(f"""
                SELECT id, key, value, category, source, created_at, updated_at, metadata
                FROM knowledge WHERE key IN ({placeholders})
            """, remaining_keys)
            
            for row in cursor.fetchall():
                item = KnowledgeItem(
                    id=row[0],
                    key=row[1],
                    value=json.loads(row[2]),
                    category=row[3],
                    source=row[4],
                    created_at=row[5],
                    updated_at=row[6],
                    metadata=json.loads(row[7]) if row[7] else {}
                )
                result[item.key] = item
                self.cache.put(item.key, item)
            
            conn.close()
        
        return result
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计"""
        return self.cache.get_stats()


class OptimizedKnowledgePersistenceSystem:
    """优化的知识持久化系统（主接口）"""
    
    def __init__(self, db_path: str = "/root/.openclaw/workspace/data/knowledge.db",
                 cache_size: int = 100, cache_ttl: int = 3600):
        """初始化系统"""
        self.db = OptimizedKnowledgeDatabase(db_path, cache_size, cache_ttl)
    
    def learn(self, key: str, value: Any, category: str = "general",
              source: str = "system") -> bool:
        """学习新知识"""
        return self.db.store(key, value, category, source)
    
    def learn_batch(self, items: List[Dict[str, Any]]) -> int:
        """批量学习"""
        return self.db.batch_store(items)
    
    def recall(self, key: str) -> Optional[Any]:
        """回忆知识"""
        item = self.db.retrieve(key)
        return item.value if item else None
    
    def recall_batch(self, keys: List[str]) -> Dict[str, Any]:
        """批量回忆"""
        items = self.db.batch_retrieve(keys)
        return {k: v.value for k, v in items.items()}
    
    def search_knowledge(self, query: str, category: str = None) -> List[Dict]:
        """搜索知识"""
        items = self.db.search(query, category)
        return [item.to_dict() for item in items]
    
    def forget(self, key: str) -> bool:
        """忘记知识"""
        return self.db.delete(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        base_stats = self.db.get_stats()
        cache_stats = self.db.get_cache_stats()
        
        return {
            **base_stats,
            "cache": cache_stats
        }


if __name__ == "__main__":
    # 测试
    system = OptimizedKnowledgePersistenceSystem()
    
    # 批量学习
    items = [
        {"key": "test_1", "value": {"data": 1}, "category": "test"},
        {"key": "test_2", "value": {"data": 2}, "category": "test"},
        {"key": "test_3", "value": {"data": 3}, "category": "test"},
    ]
    
    count = system.learn_batch(items)
    print(f"✅ 批量学习完成: {count} 条")
    
    # 批量回忆
    keys = ["test_1", "test_2", "test_3"]
    results = system.recall_batch(keys)
    print(f"✅ 批量回忆完成: {len(results)} 条")
    
    # 缓存统计
    stats = system.get_stats()
    print(f"✅ 缓存统计: {stats['cache']}")
