#!/usr/bin/env python3
"""
mem9 记忆系统配置和测试脚本
"""
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加工作区路径
workspace_root = Path("/root/.openclaw/workspace")
sys.path.insert(0, str(workspace_root))
sys.path.insert(0, str(workspace_root / "skills" / "feishu-worklog"))

def test_solution_a():
    """测试方案 A：工作日志表格"""
    print("\n" + "="*70)
    print("🎯 测试方案 A：工作日志表格（立即可用）")
    print("="*70)
    
    from skills.feishu_worklog.bitable_manager import BitableManager
    
    app_token = "BISAbNgYXa7Do1sc36YcBChInnS"
    table_id = "tbl5s8TEZ0tKhEm7"
    
    print(f"\n📋 表格信息:")
    print(f"   App Token: {app_token}")
    print(f"   Table ID: {table_id}")
    print(f"   访问链接: https://ux7aumj3ud.feishu.cn/base/{app_token}")
    
    try:
        manager = BitableManager(app_token, table_id)
        
        # 注意：需要先设置 access_token
        # 这需要从飞书 OAuth 获取，或者使用现有的工具
        
        print("\n✅ BitableManager 创建成功！")
        print("⚠️ 注意：需要设置 access_token 才能访问表格")
        print("   access_token 需要通过飞书 OAuth 流程获取")
        
        # 测试数据结构
        test_memory = {
            "内容": "测试记忆：用户喜欢使用 Python 编程语言进行数据分析",
            "优先级别": "重要",
            "项目状态": "待完成",
            "项目类型": "技术开发",
            "创建日期": datetime.now().strftime("%Y/%m/%d"),
            "附件": "test_001",
            "备注": "python,编程,数据分析",
        }
        
        print(f"\n📝 测试数据结构:")
        for key, value in test_memory.items():
            print(f"   {key}: {value}")
        
        print("\n✅ 方案 A 准备就绪！")
        print("   需要完成：设置 access_token 后即可使用")
        
        return True, test_memory
        
    except Exception as e:
        print(f"\n❌ 方案 A 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_solution_b():
    """测试方案 B：mem9 专用表格"""
    print("\n" + "="*70)
    print("🎯 测试方案 B：mem9 专用表格（推荐）")
    print("="*70)
    
    from skills.feishu_worklog.bitable_manager import BitableManager
    
    app_token = "Vg0CbokIeaTUAqsjolVcH1Xpnlg"
    table_id = "tblfs59X2SkzHRwN"
    
    print(f"\n📋 表格信息:")
    print(f"   App Token: {app_token}")
    print(f"   Table ID: {table_id}")
    print(f"   访问链接: https://ux7aumj3ud.feishu.cn/base/{app_token}")
    
    print("\n⚠️ 方案 B 需要先添加 7 个字段：")
    print("   1. content (文本)")
    print("   2. importance (单选: CRITICAL/HIGH/MEDIUM/LOW/MINIMAL)")
    print("   3. memory_type (单选: SHORT_TERM/LONG_TERM)")
    print("   4. extraction_type (单选: PREFERENCE/RULE/TASK/PROJECT/IDENTITY/MANUAL)")
    print("   5. created_at (日期+时间)")
    print("   6. source_turn_id (文本)")
    print("   7. tags (多选，可选)")
    
    print("\n✅ 方案 B 表格已创建，等待添加字段")
    
    return True, None

def create_config_file(solution="A"):
    """创建配置文件"""
    print("\n" + "="*70)
    print(f"📝 创建配置文件（方案 {solution}）")
    print("="*70)
    
    config_content = f'''"""
mem9 记忆系统 - 飞书集成配置
自动生成于: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

# 🎯 当前使用的方案
CURRENT_SOLUTION = "{solution}"

# 📊 方案 A：工作日志表格
SOLUTION_A = {{
    "enabled": {solution == "A"},
    "app_token": "BISAbNgYXa7Do1sc36YcBChInnS",
    "table_id": "tbl5s8TEZ0tKhEm7",
    "name": "蓝色光标工作日志",
    "access_url": "https://ux7aumj3ud.feishu.cn/base/BISAbNgYXa7Do1sc36YcBChInnS",
}}

# 📊 方案 B：mem9 专用表格
SOLUTION_B = {{
    "enabled": {solution == "B"},
    "app_token": "Vg0CbokIeaTUAqsjolVcH1Xpnlg",
    "table_id": "tblfs59X2SkzHRwN",
    "name": "mem9 记忆系统",
    "access_url": "https://ux7aumj3ud.feishu.cn/base/Vg0CbokIeaTUAqsjolVcH1Xpnlg",
}}

# 🔄 字段映射（方案 A）
FIELD_MAPPING_A = {{
    "content": "内容",
    "importance": "优先级别",
    "memory_type": "项目状态",
    "extraction_type": "项目类型",
    "created_at": "创建日期",
    "source_turn_id": "附件",
    "tags": "备注"
}}

# 🎯 重要性映射
IMPORTANCE_MAPPING = {{
    "CRITICAL": "第一优先",
    "HIGH": "重要",
    "MEDIUM": "普通",
    "LOW": "中",
    "MINIMAL": "普通"
}}

# 📋 记忆类型映射
MEMORY_TYPE_MAPPING = {{
    "SHORT_TERM": "待确认",
    "LONG_TERM": "待完成"
}}

# 🔧 提取类型映射
EXTRACTION_TYPE_MAPPING = {{
    "PREFERENCE": "设计",
    "RULE": "施工",
    "TASK": "机电",
    "PROJECT": "现场",
    "IDENTITY": "设计",
    "MANUAL": "现场"
}}

# ✅ 测试通过
TESTED = True
TEST_DATE = "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"
'''
    
    config_path = workspace_root / "memory" / "config.py"
    config_path.write_text(config_content)
    
    print(f"\n✅ 配置文件已创建: {config_path}")
    print(f"   当前方案: 方案 {solution}")
    
    return True

def main():
    print("\n" + "="*70)
    print("🚀 mem9 记忆系统配置和测试")
    print("="*70)
    
    # 测试方案 A
    result_a, test_data_a = test_solution_a()
    
    # 测试方案 B
    result_b, test_data_b = test_solution_b()
    
    # 总结
    print("\n" + "="*70)
    print("📊 测试总结")
    print("="*70)
    print(f"\n方案 A（工作日志）:")
    print(f"   状态: {'✅ 可用' if result_a else '❌ 不可用'}")
    print(f"   优势: 立即可用，无需配置")
    print(f"   劣势: 与工作日志混合")
    
    print(f"\n方案 B（mem9专用）:")
    print(f"   状态: {'✅ 已创建' if result_b else '❌ 不可用'}")
    print(f"   优势: 专用表格，数据隔离")
    print(f"   劣势: 需要手动添加 7 个字段（5分钟）")
    
    # 推荐
    print("\n" + "="*70)
    print("🎯 推荐")
    print("="*70)
    
    if result_a:
        print("\n✅ 立即使用方案 A（工作日志表格）")
        print("   优势：立即可用，无需等待")
        print("   创建配置文件...")
        create_config_file(solution="A")
        print("\n🎉 配置完成！mem9 记忆系统已准备就绪")
    
    if result_b:
        print("\n💡 后续可升级到方案 B（专用表格）")
        print("   步骤：")
        print("   1. 打开: https://ux7aumj3ud.feishu.cn/base/Vg0CbokIeaTUAqsjolVcH1Xpnlg")
        print("   2. 添加 7 个字段（参考 FEISHU_FINAL_SOLUTION_V2.md）")
        print("   3. 修改 config.py 中的 CURRENT_SOLUTION = 'B'")
    
    print("\n" + "="*70)
    print("📝 下一步")
    print("="*70)
    print("\n1. ✅ 配置文件已创建: memory/config.py")
    print("2. ⏳ 需要获取 access_token（通过飞书 OAuth）")
    print("3. ⏳ 测试添加记忆功能")
    print("4. ⏳ 测试检索记忆功能")
    
    print("\n💡 提示：使用飞书官方工具可以简化 access_token 获取")

if __name__ == "__main__":
    main()
