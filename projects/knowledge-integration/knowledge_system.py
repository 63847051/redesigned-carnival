#!/usr/bin/env python3
"""
知识库集成系统 v1.0 - Karpathy 风格
实现自动知识提取、智能检索和知识进化
"""

import asyncio
import json
import logging
import os
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import subprocess

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# 数据模型
# =============================================================================

@dataclass
class KnowledgeChunk:
    """知识块"""
    id: str
    content: str
    source: str
    chunk_type: str  # concept, relation, conclusion, practice
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    quality_score: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class CompiledKnowledge:
    """编译后的知识"""
    source: str
    knowledge: List[KnowledgeChunk]
    embeddings: List[List[float]]
    checksum: str
    compiled_at: datetime = field(default_factory=datetime.now)

# =============================================================================
# 知识编译器
# =============================================================================

class KnowledgeCompiler:
    """知识编译器"""
    
    def __init__(self):
        self.parsers = {
            ".md": self._parse_markdown,
            ".txt": self._parse_text,
            ".json": self._parse_json
        }
    
    async def compile(self, source_path: str) -> CompiledKnowledge:
        """编译知识"""
        logger.info(f"编译知识: {source_path}")
        
        # 1. 读取文件
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 2. 计算校验和
        checksum = hashlib.md5(content.encode()).hexdigest()
        
        # 3. 解析内容
        ext = os.path.splitext(source_path)[1]
        parser = self.parsers.get(ext, self._parse_text)
        chunks = parser(content, source_path)
        
        # 4. 生成向量嵌入（简化版）
        embeddings = await self._generate_embeddings(chunks)
        
        # 5. 更新知识块
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding
        
        return CompiledKnowledge(
            source=source_path,
            knowledge=chunks,
            embeddings=embeddings,
            checksum=checksum
        )
    
    def _parse_markdown(self, content: str, source: str) -> List[KnowledgeChunk]:
        """解析 Markdown"""
        chunks = []
        
        # 简化版：按标题分割
        lines = content.split('\n')
        current_chunk = []
        chunk_id = 0
        
        for line in lines:
            if line.startswith('#'):
                # 遇到标题，保存当前块
                if current_chunk:
                    chunk_content = '\n'.join(current_chunk).strip()
                    if chunk_content:
                        chunks.append(KnowledgeChunk(
                            id=f"{source}_{chunk_id}",
                            content=chunk_content,
                            source=source,
                            chunk_type="concept",
                            metadata={"line_number": chunk_id}
                        ))
                        chunk_id += 1
                    current_chunk = []
            
            current_chunk.append(line)
        
        # 最后一个块
        if current_chunk:
            chunk_content = '\n'.join(current_chunk).strip()
            if chunk_content:
                chunks.append(KnowledgeChunk(
                    id=f"{source}_{chunk_id}",
                    content=chunk_content,
                    source=source,
                    chunk_type="concept",
                    metadata={"line_number": chunk_id}
                ))
        
        logger.info(f"解析 Markdown: {len(chunks)} 个知识块")
        return chunks
    
    def _parse_text(self, content: str, source: str) -> List[KnowledgeChunk]:
        """解析纯文本"""
        # 简化版：按段落分割
        paragraphs = content.split('\n\n')
        
        chunks = []
        for i, para in enumerate(paragraphs):
            if para.strip():
                chunks.append(KnowledgeChunk(
                    id=f"{source}_{i}",
                    content=para.strip(),
                    source=source,
                    chunk_type="concept",
                    metadata={"paragraph_number": i}
                ))
        
        logger.info(f"解析文本: {len(chunks)} 个知识块")
        return chunks
    
    def _parse_json(self, content: str, source: str) -> List[KnowledgeChunk]:
        """解析 JSON"""
        try:
            data = json.loads(content)
            
            # 简化版：每个顶层对象作为一个知识块
            chunks = []
            
            if isinstance(data, list):
                for i, item in enumerate(data):
                    chunks.append(KnowledgeChunk(
                        id=f"{source}_{i}",
                        content=json.dumps(item, ensure_ascii=False),
                        source=source,
                        chunk_type="concept",
                        metadata={"item_number": i}
                    ))
            elif isinstance(data, dict):
                chunks.append(KnowledgeChunk(
                    id=f"{source}_0",
                    content=json.dumps(data, ensure_ascii=False),
                    source=source,
                    chunk_type="concept",
                    metadata={}
                ))
            
            logger.info(f"解析 JSON: {len(chunks)} 个知识块")
            return chunks
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}")
            return self._parse_text(content, source)
    
    async def _generate_embeddings(self, chunks: List[KnowledgeChunk]) -> List[List[float]]:
        """生成向量嵌入（简化版）"""
        # 简化版：使用哈希值作为伪向量
        # 实际应该使用 embedding 模型
        
        embeddings = []
        
        for chunk in chunks:
            # 使用内容哈希生成伪向量
            hash_val = hashlib.sha256(chunk.content.encode()).hexdigest()
            
            # 将哈希值转换为 128 维向量
            vector = []
            for i in range(0, min(len(hash_val), 32), 2):
                hex_val = int(hash_val[i:i+2], 16)
                normalized = hex_val / 255.0
                vector.append(normalized)
            
            # 填充到 128 维
            while len(vector) < 128:
                vector.append(0.0)
            
            embeddings.append(vector[:128])
        
        return embeddings

# =============================================================================
# 智能检索
# =============================================================================

class SmartRetrieval:
    """智能检索"""
    
    def __init__(self):
        self.index = {}  # 简化版：内存索引
    
    async def index(self, compiled: CompiledKnowledge):
        """建立索引"""
        logger.info(f"建立索引: {compiled.source}")
        
        for chunk in compiled.knowledge:
            self.index[chunk.id] = chunk
    
    async def search(self, query: str, mode: str = "auto") -> List[KnowledgeChunk]:
        """智能搜索"""
        logger.info(f"搜索: {query} (模式: {mode})")
        
        # 简化版：基于关键词匹配
        results = []
        
        query_lower = query.lower()
        
        for chunk in self.index.values():
            content_lower = chunk.content.lower()
            
            # 关键词匹配
            if query_lower in content_lower:
                # 计算相关性分数
                score = self._calculate_relevance(query_lower, content_lower)
                chunk.quality_score = score
                results.append(chunk)
        
        # 按相关性排序
        results.sort(key=lambda c: c.quality_score, reverse=True)
        
        # 返回前 10 个结果
        return results[:10]
    
    def _calculate_relevance(self, query: str, content: str) -> float:
        """计算相关性"""
        # 简化版：基于关键词出现次数
        count = content.count(query)
        return min(count / 10.0, 1.0)

# =============================================================================
# 知识进化
# =============================================================================

class KnowledgeEvolution:
    """知识进化"""
    
    def __init__(self):
        self.last_evolution = None
    
    async def evolve(self, chunks: List[KnowledgeChunk]) -> Dict[str, Any]:
        """知识进化"""
        logger.info("开始知识进化")
        
        # 1. 评估质量
        quality_report = await self._assess_quality(chunks)
        
        # 2. 去重
        dedup_report = await self._deduplicate(chunks)
        
        # 3. 生成报告
        evolution_report = {
            "timestamp": datetime.now().isoformat(),
            "quality": quality_report,
            "deduplication": dedup_report,
            "total_chunks": len(chunks)
        }
        
        self.last_evolution = evolution_report
        
        return evolution_report
    
    async def _assess_quality(self, chunks: List[KnowledgeChunk]) -> Dict[str, Any]:
        """评估质量"""
        high_quality = 0
        low_quality = 0
        
        for chunk in chunks:
            # 简化版：基于内容长度评估
            if len(chunk.content) > 100:
                chunk.quality_score = 0.8
                high_quality += 1
            else:
                chunk.quality_score = 0.3
                low_quality += 1
        
        return {
            "high_quality": high_quality,
            "low_quality": low_quality,
            "avg_quality": sum(c.quality_score for c in chunks) / len(chunks)
        }
    
    async def _deduplicate(self, chunks: List[KnowledgeChunk]) -> Dict[str, Any]:
        """去重"""
        # 简化版：基于内容哈希去重
        seen = set()
        duplicates = 0
        
        for chunk in chunks:
            content_hash = hashlib.md5(chunk.content.encode()).hexdigest()
            
            if content_hash in seen:
                duplicates += 1
                chunk.quality_score = 0.0  # 标记为低质量
            
            seen.add(content_hash)
        
        return {
            "duplicates_found": duplicates,
            "unique_chunks": len(seen)
        }

# =============================================================================
# 主系统
# =============================================================================

class KnowledgeSystem:
    """知识系统"""
    
    def __init__(self, storage_path: str = "/tmp/knowledge"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        self.compiler = KnowledgeCompiler()
        self.retrieval = SmartRetrieval()
        self.evolution = KnowledgeEvolution()
        
        self.compiled_knowledge: Dict[str, CompiledKnowledge] = {}
    
    async def add_document(self, source_path: str) -> Dict[str, Any]:
        """添加文档"""
        logger.info(f"添加文档: {source_path}")
        
        # 1. 编译知识
        compiled = await self.compiler.compile(source_path)
        
        # 2. 建立索引
        await self.retrieval.index(compiled)
        
        # 3. 存储
        self.compiled_knowledge[source_path] = compiled
        
        return {
            "success": True,
            "source": source_path,
            "chunks": len(compiled.knowledge),
            "checksum": compiled.checksum
        }
    
    async def search(self, query: str, mode: str = "auto") -> List[Dict[str, Any]]:
        """搜索知识"""
        chunks = await self.retrieval.search(query, mode)
        
        return [
            {
                "id": chunk.id,
                "content": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                "source": chunk.source,
                "score": chunk.quality_score,
                "type": chunk.chunk_type
            }
            for chunk in chunks
        ]
    
    async def evolve(self) -> Dict[str, Any]:
        """知识进化"""
        all_chunks = []
        
        for compiled in self.compiled_knowledge.values():
            all_chunks.extend(compiled.knowledge)
        
        return await self.evolution.evolve(all_chunks)
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        total_chunks = sum(len(c.knowledge) for c in self.compiled_knowledge.values())
        
        return {
            "total_documents": len(self.compiled_knowledge),
            "total_chunks": total_chunks,
            "indexed_chunks": len(self.retrieval.index),
            "storage_path": self.storage_path
        }

# =============================================================================
# 主入口
# =============================================================================

async def main():
    """主入口"""
    system = KnowledgeSystem()
    
    # 示例：添加文档
    test_doc = "/tmp/test_knowledge.md"
    with open(test_doc, 'w') as f:
        f.write("""
# OpenClaw 系统架构

OpenClaw 是一个 AI 代理框架，支持多种运行时。

## 核心组件

1. **Gateway** - 网关服务
2. **Agent** - 代理执行
3. **MCP** - 模型上下文协议

## 使用方法

启动 Gateway：
```bash
openclaw gateway start
```

创建 Agent：
```bash
openclaw sessions spawn
```
""")
    
    # 添加文档
    result = await system.add_document(test_doc)
    print(f"添加文档: {result}")
    
    # 搜索
    search_results = await system.search("Gateway")
    print(f"\n搜索结果 ({len(search_results)}):")
    for r in search_results:
        print(f"- {r['id']}: {r['content']}")
    
    # 统计
    stats = await system.get_stats()
    print(f"\n统计: {stats}")
    
    # 进化
    evolution = await system.evolve()
    print(f"\n进化: {evolution}")

if __name__ == "__main__":
    asyncio.run(main())
