#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆加载优化系统
- 按需加载
- 智能缓存
- 预加载策略
"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
CACHE_DIR = WORKSPACE / ".cache" / "memory"
CACHE_META = CACHE_DIR / "meta.json"

# 缓存配置
CACHE_TTL = 3600  # 缓存有效期（秒）
MAX_CACHE_SIZE = 100  # 最大缓存条目数


class MemoryCache:
    """记忆缓存系统"""
    
    def __init__(self):
        self.cache_dir = CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.meta = self._load_meta()
    
    def _load_meta(self) -> Dict:
        """加载缓存元数据"""
        if CACHE_META.exists():
            try:
                with open(CACHE_META, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "entries": {},
            "last_cleanup": None
        }
    
    def _save_meta(self):
        """保存缓存元数据"""
        with open(CACHE_META, "w", encoding="utf-8") as f:
            json.dump(self.meta, f, indent=2, ensure_ascii=False)
    
    def _get_cache_key(self, file_path: Path) -> str:
        """生成缓存键"""
        # 使用文件路径和修改时间生成唯一键
        stat = file_path.stat()
        content = f"{file_path}:{stat.st_mtime}:{stat.st_size}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, file_path: Path) -> Optional[str]:
        """
        从缓存获取文件内容
        
        Returns:
            文件内容，如果缓存未命中则返回 None
        """
        cache_key = self._get_cache_key(file_path)
        
        # 检查缓存是否存在
        if cache_key not in self.meta["entries"]:
            return None
        
        entry = self.meta["entries"][cache_key]
        
        # 检查缓存是否过期
        cache_time = datetime.fromisoformat(entry["timestamp"])
        if datetime.now() - cache_time > timedelta(seconds=CACHE_TTL):
            # 缓存过期，删除
            del self.meta["entries"][cache_key]
            self._save_meta()
            return None
        
        # 从缓存文件读取
        cache_file = self.cache_dir / f"{cache_key}.txt"
        if cache_file.exists():
            with open(cache_file, "r", encoding="utf-8") as f:
                return f.read()
        
        return None
    
    def set(self, file_path: Path, content: str):
        """设置缓存"""
        cache_key = self._get_cache_key(file_path)
        
        # 保存到缓存文件
        cache_file = self.cache_dir / f"{cache_key}.txt"
        with open(cache_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        # 更新元数据
        self.meta["entries"][cache_key] = {
            "file_path": str(file_path),
            "timestamp": datetime.now().isoformat(),
            "size": len(content)
        }
        
        # 清理过期缓存
        self._cleanup()
        
        # 保存元数据
        self._save_meta()
    
    def _cleanup(self):
        """清理过期和过多的缓存"""
        now = datetime.now()
        entries_to_delete = []
        
        # 清理过期缓存
        for key, entry in self.meta["entries"].items():
            cache_time = datetime.fromisoformat(entry["timestamp"])
            if now - cache_time > timedelta(seconds=CACHE_TTL):
                entries_to_delete.append(key)
        
        # 如果缓存过多，删除最旧的
        if len(self.meta["entries"]) > MAX_CACHE_SIZE:
            # 按时间排序
            sorted_entries = sorted(
                self.meta["entries"].items(),
                key=lambda x: x[1]["timestamp"]
            )
            # 删除最旧的
            excess = len(self.meta["entries"]) - MAX_CACHE_SIZE
            for key, _ in sorted_entries[:excess]:
                entries_to_delete.append(key)
        
        # 删除条目和文件
        for key in entries_to_delete:
            if key in self.meta["entries"]:
                del self.meta["entries"][key]
            
            cache_file = self.cache_dir / f"{key}.txt"
            if cache_file.exists():
                cache_file.unlink()
        
        if entries_to_delete:
            self.meta["last_cleanup"] = now.isoformat()


# 全局缓存实例
_cache = None

def get_cache() -> MemoryCache:
    """获取全局缓存实例"""
    global _cache
    if _cache is None:
        _cache = MemoryCache()
    return _cache


def load_memory_file(file_path: Path, use_cache: bool = True) -> str:
    """
    加载记忆文件（带缓存）
    
    Args:
        file_path: 文件路径
        use_cache: 是否使用缓存
    
    Returns:
        文件内容
    """
    if use_cache:
        # 尝试从缓存获取
        cache = get_cache()
        content = cache.get(file_path)
        if content is not None:
            return content
    
    # 从文件读取
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if use_cache:
        # 保存到缓存
        cache = get_cache()
        cache.set(file_path, content)
    
    return content


def load_memory_files_on_demand(
    file_paths: list,
    use_cache: bool = True
) -> Dict[str, str]:
    """
    按需加载多个记忆文件
    
    Args:
        file_paths: 文件路径列表
        use_cache: 是否使用缓存
    
    Returns:
        {文件路径: 文件内容} 字典
    """
    results = {}
    
    for file_path in file_paths:
        try:
            content = load_memory_file(file_path, use_cache)
            results[str(file_path)] = content
        except Exception as e:
            # 记录错误，但继续加载其他文件
            print(f"加载文件失败: {file_path}, 错误: {e}")
    
    return results


# ============================================================================
# 测试
# ============================================================================

if __name__ == "__main__":
    import time
    
    print("="*60)
    print("记忆加载优化系统测试")
    print("="*60)
    
    # 测试文件
    test_file = MEMORY_DIR / "2026-03-29.md"
    
    if not test_file.exists():
        print(f"⚠️ 测试文件不存在: {test_file}")
        print("创建测试文件...")
        test_file.write_text("# 测试内容\n\n这是一个测试文件。")
    
    print(f"\n测试文件: {test_file}")
    
    # 第一次加载（从文件）
    print("\n第一次加载（从文件）:")
    start = time.time()
    content1 = load_memory_file(test_file, use_cache=True)
    time1 = time.time() - start
    print(f"✅ 加载完成，耗时: {time1*1000:.2f}ms")
    print(f"   内容长度: {len(content1)} 字符")
    
    # 第二次加载（从缓存）
    print("\n第二次加载（从缓存）:")
    start = time.time()
    content2 = load_memory_file(test_file, use_cache=True)
    time2 = time.time() - start
    print(f"✅ 加载完成，耗时: {time2*1000:.2f}ms")
    print(f"   内容长度: {len(content2)} 字符")
    
    # 性能提升
    if time1 > 0:
        speedup = time1 / time2 if time2 > 0 else float('inf')
        print(f"\n🚀 性能提升: {speedup:.1f}x")
    
    # 缓存统计
    cache = get_cache()
    print(f"\n📊 缓存统计:")
    print(f"   缓存条目数: {len(cache.meta['entries'])}")
    print(f"   缓存目录: {cache.cache_dir}")
    
    print("\n✅ 测试完成！")
