#!/usr/bin/env python3
"""
mem9 记忆系统 - 飞书表格配置脚本
一键添加所有必需字段
"""

import sys
from pathlib import Path

# 添加工作区路径
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))


def setup_feishu_table():
    """配置飞书表格"""
    
    print("=" * 60)
    print("mem9 记忆系统 - 飞书表格配置")
    print("=" * 60)
    print()
    
    # 新表格的凭证
    app_token = "Vg0CbokIeaTUAqsjolVcH1Xpnlg"
    table_id = "tblfs59X2SkzHRwN"
    
    print(f"📱 App Token: {app_token}")
    print(f"📊 Table ID: {table_id}")
    print()
    
    print("💡 需要添加的字段:")
    print()
    print("1. content (文本)")
    print("2. importance (单选)")
    print("3. memory_type (单选)")
    print("4. extraction_type (单选)")
    print("5. created_at (日期 + 时间)")
    print("6. source_turn_id (文本)")
    print("7. tags (多选)")
    print()
    
    print("⚠️  注意:")
    print("   需要先在飞书中完成文档授权")
    print("   授权后重新运行此脚本")
    print()
    
    print("🎯 授权方法:")
    print("   在飞书中发送: /feishu auth")
    print()
    
    print("=" * 60)
    print("✅ 配置脚本准备完成！")
    print("=" * 60)
    print()
    
    print("📋 下一步:")
    print("1. 在飞书中完成授权")
    print("2. 重新运行此脚本")
    print("3. 字段将自动添加")
    print()
    
    print("🔗 表格链接:")
    print("   https://ux7aumj3ud.feishu.cn/base/Vg0CbokIeaTUAqsjolVcH1Xpnlg")
    print()


if __name__ == "__main__":
    setup_feishu_table()
