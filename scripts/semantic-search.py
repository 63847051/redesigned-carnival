#!/usr/bin/env python3
"""
语义搜索记忆系统
支持中文和英文的语义搜索
"""

import os
import sys
import json
import glob
from pathlib import Path
from datetime import datetime

# 检查依赖
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    import numpy as np
except ImportError as e:
    print(f"❌ 缺少依赖: {e}")
    print("请安装: pip3 install sentence-transformers faiss-cpu numpy")
    sys.exit(1)

# 配置
MEMORY_DIR = Path("/root/.openclaw/workspace/memory")
INDEX_DIR = MEMORY_DIR / "indexes"
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'  # 支持中文和英文

class SemanticMemorySearch:
    """语义搜索记忆系统"""

    def __init__(self, model_name=MODEL_NAME):
        """初始化"""
        print("🧠 加载语义搜索模型...")
        self.model = SentenceTransformer(model_name)
        self.index_dir = INDEX_DIR
        self.memory_dir = MEMORY_DIR

        # 确保索引目录存在
        self.index_dir.mkdir(parents=True, exist_ok=True)

    def load_documents(self):
        """加载所有记忆文档"""
        documents = []
        metadata = []

        # 遍历所有 .md 文件
        for md_file in self.memory_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 提取元数据
                relative_path = md_file.relative_to(self.memory_dir)
                doc_id = str(relative_path)

                documents.append(content)
                metadata.append({
                    'id': doc_id,
                    'path': str(md_file),
                    'relative_path': str(relative_path),
                    'size': len(content)
                })
            except Exception as e:
                print(f"⚠️  读取文件失败 {md_file}: {e}")

        print(f"📚 已加载 {len(documents)} 个文档")
        return documents, metadata

    def build_index(self, force_rebuild=False):
        """建立索引"""
        index_path = self.index_dir / "knowledge.idx"
        metadata_path = self.index_dir / "knowledge_metadata.json"

        # 检查是否已存在索引
        if index_path.exists() and not force_rebuild:
            print(f"✅ 索引已存在: {index_path}")
            return

        print("🔨 建立语义索引...")
        documents, metadata = self.load_documents()

        if not documents:
            print("❌ 没有找到文档")
            return

        # 生成嵌入向量
        print("📊 生成嵌入向量...")
        embeddings = self.model.encode(documents, show_progress_bar=True)

        # 创建 FAISS 索引
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings.astype('float32'))

        # 保存索引
        faiss.write_index(index, str(index_path))

        # 保存元数据
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"✅ 索引已保存: {index_path}")
        print(f"📝 元数据已保存: {metadata_path}")
        print(f"📊 索引大小: {index.ntotal} 个向量")

    def load_index(self):
        """加载索引"""
        index_path = self.index_dir / "knowledge.idx"
        metadata_path = self.index_dir / "knowledge_metadata.json"

        if not index_path.exists():
            print("❌ 索引不存在，请先运行 build_index()")
            return None, None

        # 加载索引
        index = faiss.read_index(str(index_path))

        # 加载元数据
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        return index, metadata

    def search(self, query, top_k=5):
        """搜索"""
        # 加载索引
        index, metadata = self.load_index()
        if index is None:
            return

        # 编码查询
        query_vector = self.model.encode([query])

        # 搜索
        distances, indices = index.search(query_vector.astype('float32'), top_k)

        # 返回结果
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(metadata):
                result = {
                    'rank': i + 1,
                    'distance': float(dist),
                    'metadata': metadata[idx]
                }
                results.append(result)

        return results

    def display_results(self, query, results):
        """显示搜索结果"""
        print(f"\n🔍 查询: {query}")
        print(f"📊 找到 {len(results)} 个结果\n")

        for result in results:
            print(f"--- [排名 {result['rank']}] ---")
            print(f"📄 文件: {result['metadata']['relative_path']}")
            print(f"📏 相似度: {1/(1+result['distance']):.2f}")

            # 读取文档片段
            try:
                with open(result['metadata']['path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 显示前 200 个字符
                    preview = content[:200].replace('\n', ' ')
                    print(f"📝 预览: {preview}...")
            except:
                pass

            print()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='语义搜索记忆系统')
    parser.add_argument('action', choices=['build', 'search', 'rebuild'],
                       help='操作: build(建立索引), search(搜索), rebuild(重建索引)')
    parser.add_argument('--query', '-q', help='搜索查询')
    parser.add_argument('--top-k', '-k', type=int, default=5,
                       help='返回结果数量 (默认: 5)')

    args = parser.parse_args()

    # 创建搜索实例
    searcher = SemanticMemorySearch()

    if args.action == 'build':
        searcher.build_index()

    elif args.action == 'rebuild':
        searcher.build_index(force_rebuild=True)

    elif args.action == 'search':
        if not args.query:
            print("❌ 请提供搜索查询: --query <查询内容>")
            sys.exit(1)

        results = searcher.search(args.query, args.top_k)
        if results:
            searcher.display_results(args.query, results)
        else:
            print("❌ 搜索失败")


if __name__ == '__main__':
    main()
