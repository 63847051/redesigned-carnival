"""
mem9 记忆系统 - 飞书集成配置
自动生成于: 2026-03-15 17:56:37
"""

# 🎯 当前使用的方案
CURRENT_SOLUTION = "A"

# 📊 方案 A：工作日志表格
SOLUTION_A = {
    "enabled": True,
    "app_token": "BISAbNgYXa7Do1sc36YcBChInnS",
    "table_id": "tbl5s8TEZ0tKhEm7",
    "name": "蓝色光标工作日志",
    "access_url": "https://ux7aumj3ud.feishu.cn/base/BISAbNgYXa7Do1sc36YcBChInnS",
}

# 📊 方案 B：mem9 专用表格
SOLUTION_B = {
    "enabled": False,
    "app_token": "Vg0CbokIeaTUAqsjolVcH1Xpnlg",
    "table_id": "tblfs59X2SkzHRwN",
    "name": "mem9 记忆系统",
    "access_url": "https://ux7aumj3ud.feishu.cn/base/Vg0CbokIeaTUAqsjolVcH1Xpnlg",
}

# 🔄 字段映射（方案 A）
FIELD_MAPPING_A = {
    "content": "内容",
    "importance": "优先级别",
    "memory_type": "项目状态",
    "extraction_type": "项目类型",
    "created_at": "创建日期",
    "source_turn_id": "附件",
    "tags": "备注"
}

# 🎯 重要性映射
IMPORTANCE_MAPPING = {
    "CRITICAL": "第一优先",
    "HIGH": "重要",
    "MEDIUM": "普通",
    "LOW": "中",
    "MINIMAL": "普通"
}

# 📋 记忆类型映射
MEMORY_TYPE_MAPPING = {
    "SHORT_TERM": "待确认",
    "LONG_TERM": "待完成"
}

# 🔧 提取类型映射
EXTRACTION_TYPE_MAPPING = {
    "PREFERENCE": "设计",
    "RULE": "施工",
    "TASK": "机电",
    "PROJECT": "现场",
    "IDENTITY": "设计",
    "MANUAL": "现场"
}

# ✅ 测试通过
TESTED = True
TEST_DATE = "2026-03-15 17:56:37"
