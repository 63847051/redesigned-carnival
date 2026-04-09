#!/usr/bin/env python3
"""
宫殿架构升级 - Wing/Room/Hall/Tunnel 实现
将现有的 Scene Blocks 升级为宫殿式结构
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

SCENE_BLOCKS_DIR = Path("/root/.openclaw/memory-tdai/scene_blocks")
PALACE_DATA_PATH = Path("/root/.openclaw/workspace/data/palace-structure.json")


class PalaceArchitect:
    """宫殿架构构建器"""

    def __init__(self):
        self.wings = {}
        self.rooms = {}
        self.halls = {
            "hall_facts": "决策和事实",
            "hall_events": "事件和里程碑",
            "hall_discoveries": "发现和洞察",
            "hall_preferences": "偏好和习惯",
            "hall_advice": "建议和方案"
        }
        self.tunnels = defaultdict(set)  # room -> set of wings
        self.room_to_wing = {}  # room -> wing

    def analyze_scene_blocks(self) -> Dict:
        """分析现有 Scene Blocks"""
        print("🔍 分析 Scene Blocks...")

        scene_files = list(SCENE_BLOCKS_DIR.glob("*.md"))
        print(f"找到 {len(scene_files)} 个场景文件")

        # 提取 Wing 分类
        for scene_file in scene_files:
            self._extract_wing_and_room(scene_file)

        # 生成统计
        stats = {
            "total_wings": len(self.wings),
            "total_rooms": len(self.rooms),
            "wings": dict(self.wings),
            "rooms": dict(self.rooms),
            "tunnels": {k: list(v) for k, v in self.tunnels.items()}
        }

        return stats

    def _extract_wing_and_room(self, scene_file: Path):
        """从文件名提取 Wing 和 Room"""
        filename = scene_file.stem  # 如 "技术支持-系统使用咨询"
        parts = filename.split("-")

        if len(parts) >= 2:
            category = parts[0]  # "技术支持"
            topic = "-".join(parts[1:])  # "系统使用咨询"

            # 创建 Wing
            wing_name = f"wing_{self._slugify(category)}"
            if wing_name not in self.wings:
                self.wings[wing_name] = {
                    "name": category,
                    "slug": wing_name,
                    "rooms": []
                }

            # 创建 Room
            room_slug = self._slugify(topic)
            room_name = f"room_{room_slug}"

            if room_name not in self.rooms:
                self.rooms[room_name] = {
                    "name": topic,
                    "slug": room_name,
                    "wing": wing_name,
                    "file": str(scene_file.name)
                }
                self.wings[wing_name]["rooms"].append(room_name)

            # 记录 Room 到 Wing 的映射
            self.room_to_wing[room_name] = wing_name

    def _slugify(self, text: str) -> str:
        """转换为 slug"""
        return re.sub(r"[^\w]", "_", text.lower())

    def detect_tunnels(self) -> Dict:
        """检测跨 Wing 的相同 Room（自动创建 Tunnel）"""
        print("🔗 检测 Tunnels...")

        # 统计每个 Room 出现在哪些 Wing
        room_wings = defaultdict(set)
        for room_name, room_data in self.rooms.items():
            room_wings[room_data["name"]].add(room_data["wing"])

        # 如果一个 Room 出现在多个 Wing，创建 Tunnel
        for room_name, wings in room_wings.items():
            if len(wings) > 1:
                room_slug = self._slugify(room_name)
                self.tunnels[room_slug] = list(wings)
                print(f"  🔗 Tunnel: {room_name} → {', '.join(wings)}")

        return {"tunnels": {k: list(v) for k, v in self.tunnels.items()}}

    def generate_structure(self) -> Dict:
        """生成完整的宫殿结构"""
        print("🏗️  生成宫殿结构...")

        structure = {
            "generated_at": datetime.now().isoformat(),
            "wings": self.wings,
            "rooms": self.rooms,
            "halls": self.halls,
            "tunnels": dict(self.tunnels),
            "statistics": {
                "total_wings": len(self.wings),
                "total_rooms": len(self.rooms),
                "total_tunnels": len(self.tunnels)
            }
        }

        return structure

    def save_structure(self, structure: Dict):
        """保存宫殿结构"""
        print("💾 保存宫殿结构...")

        PALACE_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(PALACE_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(structure, f, ensure_ascii=False, indent=2)

        print(f"✅ 宫殿结构已保存到: {PALACE_DATA_PATH}")

    def print_summary(self, structure: Dict):
        """打印摘要"""
        print("\n" + "=" * 50)
        print("🏰 宫殿结构摘要")
        print("=" * 50)

        stats = structure["statistics"]
        print(f"\n📊 统计:")
        print(f"  - Wings: {stats['total_wings']}")
        print(f"  - Rooms: {stats['total_rooms']}")
        print(f"  - Tunnels: {stats['total_tunnels']}")

        print(f"\n🏛️  Wings:")
        for wing_name, wing_data in structure["wings"].items():
            room_count = len(wing_data["rooms"])
            print(f"  - {wing_data['name']} ({wing_name}): {room_count} 个房间")

        if structure["tunnels"]:
            print(f"\n🔗 Tunnels:")
            for room_name, wings in structure["tunnels"].items():
                print(f"  - {room_name}: 连接 {len(wings)} 个 Wings")


def main():
    """主函数"""
    print("=" * 50)
    print("🏰 宫殿架构升级 - Phase 1")
    print("=" * 50)

    architect = PalaceArchitect()

    # 分析 Scene Blocks
    stats = architect.analyze_scene_blocks()

    # 检测 Tunnels
    architect.detect_tunnels()

    # 生成结构
    structure = architect.generate_structure()

    # 保存结构
    architect.save_structure(structure)

    # 打印摘要
    architect.print_summary(structure)

    print("\n✅ Phase 1 完成！")
    print(f"📁 数据已保存到: {PALACE_DATA_PATH}")


if __name__ == "__main__":
    main()
