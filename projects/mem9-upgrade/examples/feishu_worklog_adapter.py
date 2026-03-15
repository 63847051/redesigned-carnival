"""
使用现有工作日志表格作为 mem9 记忆存储
完整示例
"""

import asyncio
import sys
from pathlib import Path

# 添加工作区路径
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

from datetime import datetime
from projects.mem9_upgrade.feishu_adapter_bitable import FeishuMemoryBitable


async def main():
    """主函数"""
    
    print("=" * 60)
    print("mem9 记忆系统 - 飞书工作日志适配器")
    print("=" * 60)
    print()
    
    # 配置（使用你的工作日志表格）
    app_token = "BISAbNgYXa7Do1sc36YcBChInnS"
    table_id = "tbl5s8TEZ0tKhEm7"
    
    # 创建适配器
    print("📱 创建飞书适配器...")
    adapter = FeishuMemoryBitable(app_token, table_id)
    
    # 注意：需要设置 access_token
    # 这个令牌通常由 OpenClaw 自动注入
    # adapter.set_access_token("your_access_token")
    
    print("✅ 适配器已创建")
    print()
    
    # 测试 1: 添加记忆
    print("=" * 60)
    print("测试 1: 添加记忆")
    print("=" * 60)
    print()
    
    test_memories = [
        {
            "content": "用户喜欢使用 Python 编程，特别是 FastAPI",
            "importance": "HIGH",
            "memory_type": "LONG_TERM",
            "extraction_type": "PREFERENCE",
            "created_at": datetime.now(),
            "source_turn_id": "mem_001",
            "tags": ["python", "fastapi", "编程"],
        },
        {
            "content": "Git 推送前必须等待用户确认",
            "importance": "CRITICAL",
            "memory_type": "LONG_TERM",
            "extraction_type": "RULE",
            "created_at": datetime.now(),
            "source_turn_id": "mem_002",
            "tags": ["git", "规则", "重要"],
        },
        {
            "content": "明天之前完成 mem9 测试",
            "importance": "MEDIUM",
            "memory_type": "SHORT_TERM",
            "extraction_type": "TASK",
            "created_at": datetime.now(),
            "source_turn_id": "mem_003",
            "tags": ["任务", "测试"],
        },
    ]
    
    print(f"📝 准备添加 {len(test_memories)} 条记忆...")
    print()
    
    for i, memory in enumerate(test_memories, 1):
        print(f"{i}. {memory['content'][:40]}...")
        print(f"   重要性: {memory['importance']}")
        print(f"   类型: {memory['extraction_type']}")
        print()
    
    # 注意：实际使用时需要先设置 access_token
    print("⚠️  注意：")
    print("   实际使用时需要设置 access_token")
    print("   OpenClaw 会自动注入此令牌")
    print()
    
    # 取消注释以实际测试
    # for memory in test_memories:
    #     adapter.add_memory(memory)
    
    # 测试 2: 查询记忆
    print("=" * 60)
    print("测试 2: 查询记忆")
    print("=" * 60)
    print()
    
    print("🔍 查询所有记忆...")
    
    # 取消注释以实际查询
    # memories = adapter.query_memories(limit=10)
    # print(f"✅ 找到 {len(memories)} 条记忆:")
    # 
    # for i, memory in enumerate(memories, 1):
    #     print(f"\n{i}. {memory['content']}")
    #     print(f"   重要性: {memory['importance']}")
    #     print(f"   类型: {memory['memory_type']}")
    #     print(f"   标签: {', '.join(memory['tags'])}")
    
    print()
    print("💡 字段映射说明:")
    print()
    print("mem9 字段 -> 工作日志字段:")
    print("  content      -> 内容")
    print("  importance   -> 优先级别")
    print("  memory_type  -> 项目状态")
    print("  extraction_type -> 项目类型")
    print("  created_at   -> 创建日期")
    print("  source_turn_id -> 附件（存储 ID）")
    print("  tags         -> 备注")
    print()
    
    print("💡 重要性映射:")
    print("  CRITICAL -> 第一优先")
    print("  HIGH     -> 重要")
    print("  MEDIUM   -> 普通")
    print("  LOW      -> 中")
    print("  MINIMAL  -> 普通")
    print()
    
    print("💡 记忆类型映射:")
    print("  SHORT_TERM -> 待确认")
    print("  LONG_TERM  -> 待完成")
    print()
    
    print("💡 提取类型映射:")
    print("  PREFERENCE -> 设计")
    print("  RULE       -> 施工")
    print("  TASK       -> 机电")
    print("  PROJECT    -> 现场")
    print()
    
    print("=" * 60)
    print("✅ 示例完成！")
    print("=" * 60)
    print()
    
    print("🎯 下一步:")
    print("1. 在 OpenClaw 中运行此脚本")
    print("2. access_token 会自动注入")
    print("3. 记忆将自动同步到飞书工作日志表格")
    print()


if __name__ == "__main__":
    asyncio.run(main())
