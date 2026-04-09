#!/usr/bin/env python3
"""
高级筛选器 - 多维度记忆检索
基于 FinanceDatabase 的 Equities 筛选逻辑
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

MEMORY_DIR = Path("/root/.openclaw/memory")
SCENE_BLOCKS_DIR = Path("/root/.openclaw/memory-tdai/scene_blocks")
WORKSPACE_DIR = Path("/root/.openclaw/workspace")


class AdvancedMemoryFilter:
    """高级记忆筛选器"""

    def __init__(self):
        self.memory_index = self._build_index()

    def _build_index(self) -> Dict[str, Any]:
        """构建记忆索引"""
        index = {
            "memories": [],
            "scenes": [],
            "tags": set(),
            "categories": set(),
        }

        # 索引场景块
        if SCENE_BLOCKS_DIR.exists():
            for scene_file in SCENE_BLOCKS_DIR.glob("*.md"):
                try:
                    scene_data = self._parse_scene_file(scene_file)
                    if scene_data:
                        index["scenes"].append(scene_data)
                        index["tags"].update(scene_data.get("tags", []))
                        index["categories"].add(scene_data.get("category", ""))
                except Exception as e:
                    pass

        # 索引记忆文件
        if MEMORY_DIR.exists():
            for memory_file in MEMORY_DIR.glob("*.md"):
                try:
                    memory_data = self._parse_memory_file(memory_file)
                    if memory_data:
                        index["memories"].append(memory_data)
                        index["tags"].update(memory_data.get("tags", []))
                except Exception as e:
                    pass

        return index

    def _parse_scene_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """解析场景文件"""
        try:
            content = file_path.read_text(encoding="utf-8")
            # 提取元数据
            metadata = {}
            if "热度:" in content:
                match = re.search(r"热度:\s*(\d+)", content)
                if match:
                    metadata["popularity"] = int(match.group(1))
            if "更新:" in content:
                match = re.search(r"更新:\s*([^\n]+)", content)
                if match:
                    metadata["updated"] = match.group(1)
            if "Summary:" in content:
                match = re.search(r"Summary:\s*([^\n]+)", content)
                if match:
                    metadata["summary"] = match.group(1)

            return {
                "path": str(file_path.relative_to(SCENE_BLOCKS_DIR)),
                "type": "scene",
                "category": file_path.stem.split("-")[0] if "-" in file_path.stem else "general",
                "tags": self._extract_tags(content),
                **metadata,
            }
        except Exception:
            return None

    def _parse_memory_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """解析记忆文件"""
        try:
            content = file_path.read_text(encoding="utf-8")
            return {
                "path": str(file_path.relative_to(MEMORY_DIR)),
                "type": "memory",
                "date": file_path.stem,
                "tags": self._extract_tags(content),
                "size": len(content),
            }
        except Exception:
            return None

    def _extract_tags(self, content: str) -> List[str]:
        """提取标签"""
        tags = []
        # 查找 #tag 格式
        tags.extend(re.findall(r"#(\w+)", content))
        # 查找 ⭐ 格式
        if "⭐" in content:
            tags.append("important")
        if "🚨" in content:
            tags.append("urgent")
        if "✅" in content:
            tags.append("completed")
        return tags

    def select(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_popularity: Optional[int] = None,
        keyword: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        多维度筛选

        参数:
            category: 分类（如 "技术支持"、"AI交互"）
            tags: 标签列表（如 ["important", "urgent"]）
            min_popularity: 最低热度
            keyword: 关键词搜索

        返回:
            匹配的记忆列表
        """
        results = []

        # 筛选场景
        for scene in self.memory_index["scenes"]:
            if self._match_filter(scene, category, tags, min_popularity, keyword):
                results.append(scene)

        # 筛选记忆
        for memory in self.memory_index["memories"]:
            if self._match_filter(memory, category, tags, None, keyword):
                results.append(memory)

        # 按热度/日期排序
        results.sort(key=lambda x: x.get("popularity", 0), reverse=True)

        return results

    def _match_filter(
        self,
        item: Dict[str, Any],
        category: Optional[str],
        tags: Optional[List[str]],
        min_popularity: Optional[int],
        keyword: Optional[str],
    ) -> bool:
        """检查是否匹配筛选条件"""
        # 分类筛选
        if category and item.get("category") != category:
            return False

        # 标签筛选
        if tags:
            item_tags = set(item.get("tags", []))
            if not set(tags).issubset(item_tags):
                return False

        # 热度筛选
        if min_popularity and item.get("popularity", 0) < min_popularity:
            return False

        # 关键词搜索
        if keyword:
            summary = item.get("summary", "")
            if keyword.lower() not in summary.lower():
                return False

        return True

    def search(self, query: str, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        模糊搜索

        参数:
            query: 搜索查询
            fields: 搜索字段（默认搜索所有）

        返回:
            匹配的记忆列表
        """
        results = []
        query_lower = query.lower()

        # 搜索场景
        for scene in self.memory_index["scenes"]:
            if self._match_search(scene, query_lower, fields):
                results.append(scene)

        # 搜索记忆
        for memory in self.memory_index["memories"]:
            if self._match_search(memory, query_lower, fields):
                results.append(memory)

        return results

    def _match_search(self, item: Dict[str, Any], query: str, fields: Optional[List[str]]) -> bool:
        """检查是否匹配搜索查询"""
        if not fields:
            # 搜索所有文本字段
            for value in item.values():
                if isinstance(value, str) and query in value.lower():
                    return True
            return False

        # 搜索指定字段
        for field in fields:
            if field in item:
                value = item[field]
                if isinstance(value, str) and query in value.lower():
                    return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_scenes": len(self.memory_index["scenes"]),
            "total_memories": len(self.memory_index["memories"]),
            "unique_tags": len(self.memory_index["tags"]),
            "unique_categories": len(self.memory_index["categories"]),
            "top_categories": self._get_top_categories(),
        }

    def _get_top_categories(self) -> List[Dict[str, int]]:
        """获取热门分类"""
        category_count = {}
        for scene in self.memory_index["scenes"]:
            category = scene.get("category", "unknown")
            category_count[category] = category_count.get(category, 0) + 1

        return [
            {"category": cat, "count": count}
            for cat, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True)
        ]


def main():
    """主函数 - 演示用法"""
    filter = AdvancedMemoryFilter()

    print("=" * 50)
    print("高级筛选器演示")
    print("=" * 50)

    # 统计信息
    stats = filter.get_statistics()
    print(f"\n📊 统计信息:")
    print(f"  - 场景数量: {stats['total_scenes']}")
    print(f"  - 记忆数量: {stats['total_memories']}")
    print(f"  - 标签数量: {stats['unique_tags']}")
    print(f"  - 分类数量: {stats['unique_categories']}")

    # 示例 1: 按分类筛选
    print(f"\n🔍 示例 1: 筛选'技术支持'场景")
    results = filter.select(category="技术支持")
    for result in results[:3]:
        print(f"  - {result['path']}: {result.get('summary', 'N/A')[:50]}...")

    # 示例 2: 按标签筛选
    print(f"\n🔍 示例 2: 筛选'重要'项目")
    results = filter.select(tags=["important"])
    for result in results[:3]:
        print(f"  - {result['path']}: {result.get('summary', 'N/A')[:50]}...")

    # 示例 3: 关键词搜索
    print(f"\n🔍 示例 3: 搜索'系统'")
    results = filter.search("系统")
    print(f"  找到 {len(results)} 个结果")

    # 保存索引
    index_path = WORKSPACE_DIR / "data" / "memory-index.json"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump({
            "scenes": filter.memory_index["scenes"],
            "memories": filter.memory_index["memories"],
            "statistics": stats,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 索引已保存到: {index_path}")


if __name__ == "__main__":
    main()
