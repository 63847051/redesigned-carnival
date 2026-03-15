#!/usr/bin/env python3
"""
测试飞书表格连接
"""
import sys
import json

# 添加工作区路径
workspace_root = "/root/.openclaw/workspace"
sys.path.insert(0, workspace_root)

def test_solution_a():
    """测试方案 A：工作日志表格"""
    print("\n" + "="*60)
    print("测试方案 A：工作日志表格")
    print("="*60)
    
    # 导入工作日志技能
    from skills.feishu_worklog.bitable_manager import BitableManager
    
    app_token = "BISAbNgYXa7Do1sc36YcBChInnS"
    table_id = "tbl5s8TEZ0tKhEm7"
    
    try:
        manager = BitableManager(app_token, table_id)
        
        # 获取表格信息
        print("\n✅ 连接成功！")
        print(f"App Token: {app_token}")
        print(f"Table ID: {table_id}")
        
        # 尝试读取一些记录
        records = manager.query_records(limit=3)
        print(f"\n📊 找到 {len(records)} 条记录:")
        
        for i, record in enumerate(records[:3], 1):
            print(f"\n记录 {i}:")
            for key, value in record.items():
                if value:
                    print(f"  {key}: {str(value)[:50]}...")
        
        print("\n✅ 方案 A 测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 方案 A 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_solution_b():
    """测试方案 B：mem9 专用表格"""
    print("\n" + "="*60)
    print("测试方案 B：mem9 专用表格")
    print("="*60)
    
    from skills.feishu_worklog.bitable_manager import BitableManager
    
    app_token = "Vg0CbokIeaTUAqsjolVcH1Xpnlg"
    table_id = "tblfs59X2SkzHRwN"
    
    try:
        manager = BitableManager(app_token, table_id)
        
        print("\n✅ 连接成功！")
        print(f"App Token: {app_token}")
        print(f"Table ID: {table_id}")
        
        # 尝试读取记录
        records = manager.query_records(limit=3)
        print(f"\n📊 找到 {len(records)} 条记录")
        
        if records:
            # 显示第一条记录的字段
            first_record = records[0]
            print(f"\n📋 字段列表:")
            for key in first_record.keys():
                print(f"  - {key}")
        else:
            print("\n📋 表格为空，需要添加字段")
        
        print("\n✅ 方案 B 连接成功！")
        return True
        
    except Exception as e:
        print(f"\n❌ 方案 B 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n🚀 开始测试飞书表格连接...")
    
    # 测试方案 A
    result_a = test_solution_a()
    
    # 测试方案 B
    result_b = test_solution_b()
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    print(f"方案 A（工作日志）: {'✅ 可用' if result_a else '❌ 不可用'}")
    print(f"方案 B（mem9专用）: {'✅ 可用' if result_b else '❌ 不可用'}")
    
    if result_a:
        print("\n🎯 建议：使用方案 A（立即可用）")
    elif result_b:
        print("\n🎯 建议：使用方案 B（需要先添加字段）")
    else:
        print("\n⚠️ 警告：两个方案都不可用")

if __name__ == "__main__":
    main()
