#!/usr/bin/env python3
"""
记忆优化脚本

用于优化和管理记忆系统:
- 清理低价值记忆
- 压缩历史对话
- 同步到飞书
- 生成统计报告
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory import (
    EnhancedContextEngine,
    FileMemoryStorage,
    FeishuMemoryBitable,
    ImportanceLevel,
    MemoryType,
    create_context_engine,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MemoryOptimizer:
    """记忆优化器"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path) if config_path else {}
        self.storage = FileMemoryStorage()
        self.feishu = FeishuMemoryBitable(
            app_token=self.config.get("feishu_app_token"),
            table_id=self.config.get("feishu_table_id"),
            access_token=self.config.get("feishu_access_token"),
        )

    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        try:
            with open(config_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")
            return {}

    async def run(self, action: str) -> None:
        """运行优化任务

        参数:
            action: 操作类型 (clean, sync, stats, all)
        """
        actions = {
            "clean": self.cleanup,
            "sync": self.sync_to_feishu,
            "stats": self.show_statistics,
            "all": self.full_optimization,
        }

        action_func = actions.get(action)
        if not action_func:
            logger.error(f"Unknown action: {action}")
            return

        logger.info(f"Running action: {action}")
        await action_func()
        logger.info(f"Action {action} completed")

    async def cleanup(self) -> None:
        """清理低价值记忆"""
        logger.info("Starting memory cleanup...")

        short_term = self.storage.list_memories(MemoryType.SHORT_TERM, limit=1000)
        long_term = self.storage.list_memories(MemoryType.LONG_TERM, limit=1000)

        cleaned_short = 0
        cleaned_long = 0

        # 清理短期记忆
        for entry in short_term:
            if entry.importance == ImportanceLevel.MINIMAL and entry.access_count == 0:
                self.storage.delete_memory(entry.id, MemoryType.SHORT_TERM)
                cleaned_short += 1

        # 清理长期记忆（保留关键和高重要性）
        for entry in long_term:
            days_old = (datetime.now() - entry.created_at).days
            if (
                entry.importance == ImportanceLevel.MINIMAL
                and days_old > 30
                and entry.access_count < 3
            ):
                self.storage.delete_memory(entry.id, MemoryType.LONG_TERM)
                cleaned_long += 1

        logger.info(
            f"Cleanup complete: {cleaned_short} short-term, {cleaned_long} long-term"
        )

    async def sync_to_feishu(self) -> None:
        """同步到飞书"""
        if not self.feishu.is_available():
            logger.warning("Feishu not available, skipping sync")
            return

        logger.info("Syncing memories to Feishu...")

        long_term = self.storage.list_memories(MemoryType.LONG_TERM, limit=100)
        synced = 0

        for entry in long_term:
            if self.feishu.add_memory(entry):
                synced += 1

        logger.info(f"Synced {synced} memories to Feishu")

    async def show_statistics(self) -> None:
        """显示统计信息"""
        short_term = self.storage.list_memories(MemoryType.SHORT_TERM, limit=1000)
        long_term = self.storage.list_memories(MemoryType.LONG_TERM, limit=1000)

        # 按重要性分组
        importance_counts = {level: 0 for level in ImportanceLevel}
        for entry in long_term:
            importance_counts[entry.importance] += 1

        print("\n" + "=" * 50)
        print("Memory Statistics")
        print("=" * 50)
        print(f"Short-term memories: {len(short_term)}")
        print(f"Long-term memories: {len(long_term)}")
        print("\nLong-term by importance:")
        for level, count in importance_counts.items():
            print(f"  {level.name}: {count}")
        print("=" * 50)

    async def full_optimization(self) -> None:
        """完整优化"""
        logger.info("Starting full optimization...")

        await self.cleanup()
        await self.sync_to_feishu()
        await self.show_statistics()

        logger.info("Full optimization completed")


async def main():
    parser = argparse.ArgumentParser(description="Memory Optimizer")
    parser.add_argument(
        "action",
        choices=["clean", "sync", "stats", "all"],
        default="all",
        help="Action to perform",
    )
    parser.add_argument("--config", help="Path to config file")

    args = parser.parse_args()

    optimizer = MemoryOptimizer(args.config)
    await optimizer.run(args.action)


if __name__ == "__main__":
    asyncio.run(main())
