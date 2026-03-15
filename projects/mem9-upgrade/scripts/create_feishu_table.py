#!/usr/bin/env python3
"""
飞书多维表格 - 自动创建脚本

自动创建符合 mem9 记忆系统要求的飞书多维表格
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace')

from skills.feishu_worklog.bitable_manager import BitableManager
import json


def create_mem9_table():
    """创建 mem9 记忆系统表格"""
    print("=" * 60)
    print("飞书多维表格 - 自动创建")
    print("=" * 60 + "\n")

    # 凭证
    app_token = "BISAbNgYXa7Do1sc36YcBChInnS"
    table_id = "tbl5s8TEZ0tKhEm7"

    print(f"📱 App Token: {app_token}")
    print(f"📊 Table ID: {table_id}")
    print()

    # 创建管理器
    manager = BitableManager(app_token, table_id)

    # 测试连接
    print("🔍 测试连接...")
    try:
        records = manager.list_records()
        print(f"✅ 连接成功！当前表格有 {len(records)} 条记录\n")
    except Exception as e:
        print(f"❌ 连接失败: {e}\n")
        print("💡 可能的原因:")
        print("1. app_token 或 table_id 不正确")
        print("2. 没有权限访问表格")
        print("3. 表格不存在")
        print("\n🔧 解决方法:")
        print("1. 检查 app_token 和 table_id 是否正确")
        print("2. 确保有权限访问表格")
        print("3. 手动创建表格（见 FEISHU_QUICK_SETUP.md）")
        return

    # 检查表格结构
    print("🔍 检查表格结构...")
    try:
        fields = manager.get_fields()
        print(f"✅ 当前表格有 {len(fields)} 个字段:")
        for field in fields:
            print(f"   - {field['field_name']} ({field['type']})")
        print()
    except Exception as e:
        print(f"⚠️  无法获取字段信息: {e}\n")

    # 添加测试记录
    print("📝 添加测试记录...")
    test_record = {
        "content": "测试记录：用户喜欢使用 Python 编程",
        "importance": "HIGH",
        "memory_type": "LONG_TERM",
        "tags": ["python", "编程", "偏好"],
        "extraction_type": "PREFERENCE",
        "source_turn_id": "test_001",
    }

    try:
        result = manager.create_record(test_record)
        print(f"✅ 测试记录添加成功！")
        print(f"   Record ID: {result.get('record', {}).get('record_id')}\n")
    except Exception as e:
        print(f"❌ 添加记录失败: {e}\n")
        print("💡 可能的原因:")
        print("1. 字段名不匹配")
        print("2. 字段类型不正确")
        print("3. 单选/多选选项不匹配")
        print("\n🔧 解决方法:")
        print("1. 按照 FEISHU_QUICK_SETUP.md 重新创建表格")
        print("2. 确保字段名完全一致（区分大小写）")
        print("3. 确保单选选项完全一致（大写）")

    print("=" * 60)
    print("✅ 飞书表格检查完成！")
    print("=" * 60 + "\n")

    print("📱 请在飞书中查看:")
    print("1. 打开飞书")
    print("2. 找到对应的多维表格")
    print("3. 查看是否有测试记录")
    print("4. 如果没有，请按照 FEISHU_QUICK_SETUP.md 手动创建表格")


if __name__ == "__main__":
    create_mem9_table()
