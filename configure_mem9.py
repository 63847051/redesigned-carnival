#!/usr/bin/env python3
"""配置 mem9 记忆系统 - 使用方案 A（现有工作日志表格）"""

import asyncio
import sys
from pathlib import Path

# 添加工作区路径
workspace_root = Path("/root/.openclaw/workspace")
sys.path.insert(0, str(workspace_root))

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from projects.mem9_upgrade.feishu_adapter_bitable import FeishuMemoryBitable

async def main():
    print("🚀 小新（opencode）配置 mem9 记忆系统...")
    print()
    
    # 配置：方案 A - 使用现有工作日志表格
    app_token = "BISAbNgYXa7Do1sc36YcBChInS"
    table_id = "tbl5s8TEZ0tKhEm7"
    
    print("📋 配置信息:")
    print(f"  - 方案: A（现有工作日志表格）")
    print(f"  - app_token: {app_token}")
    print(f"  - table_id: {table_id}")
    print()
    
    try:
        # 创建适配器
        print("1️⃣ 创建飞书适配器...")
        adapter = FeishuMemoryBitable(app_token, table_id)
        print("   ✅ 适配器已创建")
        
        # 测试连接
        print("2️⃣ 测试连接...")
        result = await adapter.search("测试")
        print(f"   ✅ 连接成功，找到 {len(result)} 条记录")
        
        print()
        print("🎉 mem9 记忆系统配置完成！")
        print("📋 记忆将存储到飞书工作日志表格")
        print()
        print("💡 说明:")
        print("   - 重要信息会自动提取")
        print("   - 可以搜索历史记忆")
        print("   - 支持中英文检索")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    print()
    if result:
        print("✅ mem9 配置成功！")
    else:
        print("❌ mem9 配置失败")
