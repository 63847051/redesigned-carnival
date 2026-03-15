#!/usr/bin/env python3
"""
飞书云端同步 - 测试脚本

演示如何启用和测试飞书云端同步功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from memory import (
    create_context_engine,
    Message,
    TokenBudget,
    Turn,
)


async def test_feishu_sync():
    """测试飞书云端同步"""
    print("=" * 60)
    print("飞书云端同步 - 测试")
    print("=" * 60 + "\n")

    # 创建引擎（启用飞书同步）
    print("⚙️  配置飞书同步...")
    engine = create_context_engine({
        "enable_feishu": True,
        "feishu_app_token": "BISAbNgYXa7Do1sc36YcBChInnS",
        "feishu_table_id": "tbl5s8TEZ0tKhEm7",
    })
    print("✅ 飞书同步已配置\n")

    # 初始化
    print("🚀 初始化记忆系统...")
    await engine.bootstrap()
    print("✅ 记忆系统已启动\n")

    # 测试 1: 同步用户偏好（HIGH 重要性）
    print("=" * 60)
    print("测试 1: 同步用户偏好（HIGH 重要性）")
    print("=" * 60)

    print("👤 用户: 我最喜欢使用 Python 编程，特别是 FastAPI")
    msg1 = Message(
        id="feishu_test_001",
        role="user",
        content="我最喜欢使用 Python 编程，特别是 FastAPI"
    )

    await engine.ingest(msg1)
    print("✅ 已记录用户偏好")
    print("📱 飞书: 应该已自动同步（HIGH 重要性）\n")

    # 测试 2: 同步重要规则（CRITICAL 重要性）
    print("=" * 60)
    print("测试 2: 同步重要规则（CRITICAL 重要性）")
    print("=" * 60)

    print("👤 用户: 记住：API Key 是 xxx，绝对不能泄露")
    msg2 = Message(
        id="feishu_test_002",
        role="user",
        content="记住：API Key 是 xxx，绝对不能泄露"
    )

    await engine.ingest(msg2)
    print("✅ 已记录重要规则")
    print("📱 飞书: 应该已自动同步（CRITICAL 重要性）\n")

    # 测试 3: 同步任务（HIGH 重要性）
    print("=" * 60)
    print("测试 3: 同步任务（HIGH 重要性）")
    print("=" * 60)

    print("👤 用户: 明天之前完成 mem9 升级的 Phase 4 测试")
    msg3 = Message(
        id="feishu_test_003",
        role="user",
        content="明天之前完成 mem9 升级的 Phase 4 测试"
    )

    await engine.ingest(msg3)
    print("✅ 已记录任务")
    print("📱 飞书: 应该已自动同步（HIGH 重要性）\n")

    # 测试 4: 不同步低重要性内容（LOW 重要性）
    print("=" * 60)
    print("测试 4: 不同步低重要性内容（LOW 重要性）")
    print("=" * 60)

    print("👤 用户: 今天天气很好")
    msg4 = Message(
        id="feishu_test_004",
        role="user",
        content="今天天气很好"
    )

    await engine.ingest(msg4)
    print("✅ 已记录临时对话")
    print("📱 飞书: 不会同步（LOW 重要性）\n")

    # 查看同步统计
    print("=" * 60)
    print("同步总结")
    print("=" * 60)

    print(f"✅ 已添加 4 条记忆")
    print(f"📱 飞书应该有 3 条记录（HIGH + CRITICAL + HIGH）")
    print(f"❌ 飞书不应该有 1 条记录（LOW）\n")

    print("📱 请检查飞书多维表格:")
    print("   1. 打开飞书")
    print("   2. 找到对应的多维表格")
    print("   3. 应该能看到 3 条新记录:")
    print("      - 我最喜欢使用 Python 编程，特别是 FastAPI")
    print("      - 记住：API Key 是 xxx，绝对不能泄露")
    print("      - 明天之前完成 mem9 升级的 Phase 4 测试")
    print("   4. 不应该看到:")
    print("      - 今天天气很好\n")

    print("=" * 60)
    print("✅ 飞书云端同步测试完成！")
    print("=" * 60 + "\n")

    print("💡 下一步:")
    print("1. 检查飞书多维表格，验证同步结果")
    print("2. 尝试添加更多记忆，观察自动同步")
    print("3. 调整同步阈值和间隔")
    print("4. 查看 FEISHU_SETUP.md 了解更多配置")


async def main():
    """主函数"""
    try:
        await test_feishu_sync()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n🔧 故障排查:")
        print("1. 检查 app_token 和 table_id 是否正确")
        print("2. 确保有权限访问飞书表格")
        print("3. 检查网络连接")
        print("4. 查看 FEISHU_SETUP.md 的故障排查章节")


if __name__ == "__main__":
    asyncio.run(main())
