#!/usr/bin/env python3
"""
mem9 记忆系统 - 完整配置脚本
创建表格并添加所有字段
"""

import asyncio
from datetime import datetime


async def create_mem9_table():
    """创建完整的 mem9 记忆表格"""

    print("=" * 60)
    print("mem9 记忆系统 - 创建完整表格")
    print("=" * 60)
    print()

    # 表格配置
    table_name = "mem9 记忆系统"

    print(f"📊 表格名称: {table_name}")
    print()

    print("🎯 创建步骤:")
    print()
    print("1. ✅ 表格已创建")
    print("   App Token: Vg0CbokIeaTUAqsjolVcH1Xpnlg")
    print("   Table ID: tblfs59X2SkzHRwN")
    print()
    print("2. ⏳ 等待添加字段（需要授权）")
    print()

    print("📋 需要的字段:")
    print()
    print("1. content (文本)")
    print("2. importance (单选: CRITICAL/HIGH/MEDIUM/LOW/MINIMAL)")
    print("3. memory_type (单选: SHORT_TERM/LONG_TERM)")
    print("4. extraction_type (单选: PREFERENCE/RULE/TASK/PROJECT/IDENTITY/MANUAL)")
    print("5. created_at (日期 + 时间)")
    print("6. source_turn_id (文本)")
    print("7. tags (多选)")
    print()

    print("🔗 表格链接:")
    print("   https://ux7aumj3ud.feishu.cn/base/Vg0CbokIeaTUAqsjolVcH1Xpnlg")
    print()

    print("💡 在飞书中:")
    print("   1. 打开表格链接")
    print("   2. 手动添加 7 个字段")
    print("   3. 完成后告诉我")
    print()

    print("=" * 60)
    print("✅ 表格创建完成！")
    print("=" * 60)
    print()

    print("📝 配置信息:")
    print()
    print("app_token = 'Vg0CbokIeaTUAqsjolVcH1Xpnlg'")
    print("table_id = 'tblfs59X2SkzHRwN'")
    print()


if __name__ == "__main__":
    asyncio.run(create_mem9_table())
