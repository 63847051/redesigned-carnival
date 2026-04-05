#!/usr/bin/env python3
"""
缓存管理器
参考 Claude Code 的缓存优化策略
"""

import os
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, workspace: Optional[str] = None):
        """
        初始化缓存管理器
        
        Args:
            workspace: 工作区路径
        """
        if workspace is None:
            workspace = os.environ.get('OPENCLAW_WORKSPACE', '/root/.openclaw/workspace')
        
        self.workspace = Path(workspace)
        self.cache_dir = self.workspace / '.cache'
        self.tools_cache = self.cache_dir / 'tools'
        self.config_cache = self.cache_dir / 'config'
        
        # 创建缓存目录
        self.tools_cache.mkdir(parents=True, exist_ok=True)
        self.config_cache.mkdir(parents=True, exist_ok=True)
    
    def get_file_hash(self, filepath: Path) -> str:
        """
        计算文件内容哈希
        
        Args:
            filepath: 文件路径
        
        Returns:
            MD5 哈希值
        """
        content = filepath.read_bytes()
        return hashlib.md5(content).hexdigest()
    
    def cache_config_file(self, filepath: Path) -> Path:
        """
        缓存配置文件（使用内容哈希命名）
        
        Args:
            filepath: 配置文件路径
        
        Returns:
            缓存文件路径
        """
        hash_value = self.get_file_hash(filepath)
        filename = f"{filepath.name}.{hash_value}"
        return self.config_cache / filename
    
    def get_cached_tools(self) -> List[str]:
        """
        获取排序后的工具列表
        
        Returns:
            工具列表（按字母表排序）
        """
        tools_file = self.tools_cache / "tools_list.txt"
        
        if tools_file.exists():
            return tools_file.read_text().splitlines()
        
        # 生成工具列表
        scripts_dir = self.workspace / "scripts"
        tools = []
        
        # 获取所有 Shell 脚本
        tools.extend([str(f) for f in scripts_dir.glob("*.sh")])
        
        # 获取所有 Python 脚本
        tools.extend([str(f) for f in scripts_dir.glob("*.py")])
        
        # 按字母表排序
        tools.sort()
        
        # 缓存到文件
        tools_file.write_text("\n".join(tools))
        
        return tools
    
    def invalidate_cache(self, cache_type: str = "all") -> None:
        """
        使缓存失效
        
        Args:
            cache_type: 缓存类型 ("tools", "config", "all")
        """
        if cache_type in ("tools", "all"):
            # 清理工具缓存
            for file in self.tools_cache.glob("*"):
                file.unlink()
        
        if cache_type in ("config", "all"):
            # 清理配置缓存
            for file in self.config_cache.glob("*"):
                file.unlink()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        tools_files = list(self.tools_cache.glob("*"))
        config_files = list(self.config_cache.glob("*"))
        
        tools_size = sum(f.stat().st_size for f in tools_files)
        config_size = sum(f.stat().st_size for f in config_files)
        
        return {
            "tools": {
                "count": len(tools_files),
                "size_bytes": tools_size,
                "size_human": f"{tools_size / 1024:.1f}K"
            },
            "config": {
                "count": len(config_files),
                "size_bytes": config_size,
                "size_human": f"{config_size / 1024:.1f}K"
            },
            "total": {
                "count": len(tools_files) + len(config_files),
                "size_bytes": tools_size + config_size,
                "size_human": f"{(tools_size + config_size) / 1024:.1f}K"
            }
        }
    
    def optimize_config_files(self) -> List[Path]:
        """
        优化配置文件（使用内容哈希命名）
        
        Returns:
            优化后的配置文件列表
        """
        config_files = [
            "SOUL.md",
            "IDENTITY.md",
            "AGENTS.md",
            "MEMORY.md",
            "HEARTBEAT.md"
        ]
        
        optimized = []
        
        for filename in config_files:
            filepath = self.workspace / filename
            if filepath.exists():
                cached_path = self.cache_config_file(filepath)
                
                # 创建符号链接或复制
                if not cached_path.exists():
                    import shutil
                    shutil.copy2(filepath, cached_path)
                
                optimized.append(cached_path)
        
        return optimized
    
    def get_tool_index(self) -> str:
        """
        获取工具索引（Markdown 格式）
        
        Returns:
            工具索引内容
        """
        tools = self.get_cached_tools()
        
        lines = [
            "# 工具索引（按字母表排序）",
            f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"总计: {len(tools)} 个工具",
            ""
        ]
        
        # 分类统计
        shell_tools = [t for t in tools if t.endswith('.sh')]
        python_tools = [t for t in tools if t.endswith('.py')]
        
        lines.append("## Shell 脚本")
        lines.append(f"（{len(shell_tools)} 个）")
        lines.append("")
        for tool in shell_tools:
            lines.append(f"- {Path(tool).name}")
        
        lines.append("")
        lines.append("## Python 脚本")
        lines.append(f"（{len(python_tools)} 个）")
        lines.append("")
        for tool in python_tools:
            lines.append(f"- {Path(tool).name}")
        
        return "\n".join(lines)
    
    def save_tool_index(self) -> Path:
        """
        保存工具索引
        
        Returns:
            索引文件路径
        """
        index_path = self.tools_cache / "tools_index.md"
        index_path.write_text(self.get_tool_index())
        return index_path


# 便捷函数
def optimize_cache() -> Dict[str, Any]:
    """
    优化缓存
    
    Returns:
        缓存统计信息
    """
    manager = CacheManager()
    
    # 优化工具排序
    tools = manager.get_cached_tools()
    
    # 优化配置文件
    manager.optimize_config_files()
    
    # 保存工具索引
    manager.save_tool_index()
    
    return manager.get_cache_stats()


if __name__ == '__main__':
    print("=" * 60)
    print("缓存管理器测试")
    print("=" * 60)
    
    # 创建缓存管理器
    manager = CacheManager()
    
    # 优化缓存
    print("\n📊 优化缓存...")
    stats = optimize_cache()
    
    # 显示统计
    print("\n✅ 缓存优化完成！")
    print(f"\n📈 统计信息:")
    print(f"  工具缓存: {stats['tools']['count']} 个文件, {stats['tools']['size_human']}")
    print(f"  配置缓存: {stats['config']['count']} 个文件, {stats['config']['size_human']}")
    print(f"  总计: {stats['total']['count']} 个文件, {stats['total']['size_human']}")
