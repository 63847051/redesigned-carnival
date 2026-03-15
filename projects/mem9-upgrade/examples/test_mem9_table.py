"""
测试 mem9 记忆表格连接
"""

import sys
from pathlib import Path

# 添加工作区路径
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

from skills.feishu_worklog.bitable_manager import BitableManager


def test_mem9_table():
    """测试新的 mem9 记忆表格"""
    
    print("=" * 60)
    print("mem9 记忆系统 - 表格连接测试")
    print("=" * 60)
    print()
    
    # 新表格凭证
    app_token = "Vg0CbokIeaTUAqsjolVcH1Xpnlg"
    table_id = "tblxw36mEv0dMyGH"
    
    print(f"📱 App Token: {app_token}")
    print(f"📊 Table ID: {table_id}")
    print()
    
    # 创建管理器
    print("✅ 创建 BitableManager...")
    manager = BitableManager(app_token, table_id)
    print()
    
    # 表格信息
    print("📋 表格信息:")
    print("   名称: mem9 记忆系统")
    print("   访问: https://ux7aumj3ud.feishu.cn/base/Vg0CbokIeaTUAqsjolVcH1Xpnlg")
    print()
    
    # 字段信息
    print("📝 当前字段:")
    print("   - 多行文本（主字段）")
    print()
    
    # 测试记录
    test_record = {
        "多行文本": "测试记忆：用户喜欢使用 Python 编程，特别是 FastAPI 框架。\n\n重要性: HIGH\n类型: PREFERENCE\n标签: python, fastapi, 编程"
    }
    
    print("🎯 准备添加测试记忆:")
    print(f"   内容: {test_record['多行文本'][:50]}...")
    print()
    
    print("⚠️  注意:")
    print("   需要先在飞书中完成表格授权")
    print("   授权后可以添加记录")
    print()
    
    print("🎯 使用方法:")
    print()
    print("   1. 在飞书中打开表格:")
    print("      https://ux7aumj3ud.feishu.cn/base/Vg0CbokIeaTUAqsjolVcH1Xpnlg")
    print()
    print("   2. 完成授权（如果需要）")
    print()
    print("   3. 使用以下代码添加记忆:")
    print()
    print("   ```python")
    print("   from memory import create_context_engine, Message")
    print()
    print("   engine = create_context_engine({")
    print("       'enable_feishu': True,")
    print("       'feishu_app_token': 'Vg0CbokIeaTUAqsjolVcH1Xpnlg',")
    print("       'feishu_table_id': 'tblxw36mEv0dMyGH',")
    print("   })")
    print()
    print("   await engine.bootstrap()")
    print()
    print("   msg = Message(")
    print("       id='mem_001',")
    print("       role='user',")
    print("       content='用户喜欢使用 Python 编程'")
    print("   )")
    print()
    print("   await engine.ingest(msg)")
    print("   ```")
    print()
    
    print("=" * 60)
    print("✅ 测试脚本准备完成！")
    print("=" * 60)
    print()


if __name__ == "__main__":
    test_mem9_table()
