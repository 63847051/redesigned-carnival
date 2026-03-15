"""
飞书工作日志表格 - 字段映射测试
"""

import sys
from pathlib import Path

# 添加工作区路径
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

from skills.feishu_worklog.bitable_manager import BitableManager


def main():
    """测试函数"""
    
    print("=" * 60)
    print("飞书工作日志表格 - 字段映射测试")
    print("=" * 60)
    print()
    
    # 你的工作日志表格配置
    app_token = "BISAbNgYXa7Do1sc36YcBChInnS"
    table_id = "tbl5s8TEZ0tKhEm7"
    
    print(f"📱 App Token: {app_token}")
    print(f"📊 Table ID: {table_id}")
    print()
    
    # 创建管理器
    print("✅ 创建 BitableManager...")
    manager = BitableManager(app_token, table_id)
    print()
    
    print("💡 mem9 字段映射:")
    print()
    print("mem9 字段          -> 工作日志字段")
    print("-" * 60)
    print("content           -> 内容")
    print("importance        -> 优先级别 (第一优先/重要/普通/中/高)")
    print("memory_type       -> 项目状态 (待确认/待完成/已完成)")
    print("extraction_type   -> 项目类型 (现场/设计/施工/机电)")
    print("created_at        -> 创建日期")
    print("source_turn_id    -> 附件 (存储 ID)")
    print("tags              -> 备注")
    print()
    
    print("💡 重要性映射:")
    print()
    print("CRITICAL (0.8+)   -> 第一优先")
    print("HIGH (0.6+)       -> 重要")
    print("MEDIUM (0.4+)     -> 普通")
    print("LOW (0.2+)        -> 中")
    print("MINIMAL (<0.2)    -> 普通")
    print()
    
    print("💡 记忆类型映射:")
    print()
    print("SHORT_TERM        -> 待确认")
    print("LONG_TERM         -> 待完成")
    print()
    
    print("💡 提取类型映射:")
    print()
    print("PREFERENCE        -> 设计")
    print("RULE              -> 施工")
    print("TASK              -> 机电")
    print("PROJECT           -> 现场")
    print("IDENTITY          -> 设计")
    print("MANUAL            -> 现场")
    print()
    
    print("=" * 60)
    print("✅ 字段映射说明完成！")
    print("=" * 60)
    print()
    
    print("🎯 下一步:")
    print("1. 适配器已准备就绪")
    print("2. 可以开始添加记忆到飞书")
    print("3. 所有记忆将存储在工作日志表格中")
    print()


if __name__ == "__main__":
    main()
