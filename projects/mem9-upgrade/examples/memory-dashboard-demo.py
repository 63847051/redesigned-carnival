"""
记忆仪表板使用示例

演示如何使用记忆可视化仪表板和自动记录功能
"""

import sys
import os

# 使用importlib动态加载模块
import importlib.util


def _load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# 加载模块
memory_dashboard = _load_module(
    "memory_dashboard",
    os.path.join(os.path.dirname(__file__), "..", "scripts", "memory-dashboard.py"),
)
auto_record = _load_module(
    "auto_record",
    os.path.join(os.path.dirname(__file__), "..", "scripts", "auto-record.py"),
)

# 导出类
MemoryDashboard = memory_dashboard.MemoryDashboard
MemoryType = memory_dashboard.MemoryType
ImportanceLevel = memory_dashboard.ImportanceLevel
AutoRecord = auto_record.AutoRecord
ContentType = auto_record.ContentType
create_auto_record = auto_record.create_auto_record


def demo_dashboard_basic_usage():
    """演示记忆仪表板基本用法"""
    print("\n" + "=" * 60)
    print("📊 记忆仪表板基本用法演示")
    print("=" * 60)

    # 创建仪表板实例（需要access_token才能实际调用飞书API）
    # 在实际使用时替换为真实的access_token
    dashboard = MemoryDashboard(
        app_token="BISAbNgYXa7Do1sc36YcBChInnS",
        record_table_id="tbl_memory_records",
        # stats_table_id="tbl_memory_stats",  # 可选
    )

    # 设置访问令牌（替换为真实token）
    # dashboard.set_access_token("your_real_access_token")

    print("\n✅ 仪表板创建成功")
    print(f"   App Token: {dashboard._mask_token(dashboard.app_token)}")
    print(f"   记录表ID: {dashboard.record_table_id}")

    # 演示添加记忆（模拟，不实际调用API）
    print("\n--- 添加记忆示例 ---")

    # 示例1: 添加学习内容
    print("\n1️⃣ 添加学习内容:")
    print("   dashboard.add_memory(")
    print('       content="学会了使用Python的async/await语法进行异步编程",')
    print('       memory_type="学习",')
    print('       tags=["Python", "异步编程"],')
    print("       importance=4")
    print("   )")

    # 示例2: 添加决策
    print("\n2️⃣ 添加决策:")
    print("   dashboard.add_memory(")
    print('       content="决定使用飞书Bitable作为记忆存储后端",')
    print('       memory_type="决策",')
    print('       tags=["架构", "存储"],')
    print("       importance=5")
    print("   )")

    # 示例3: 添加知识
    print("\n3️⃣ 添加知识:")
    print("   dashboard.add_memory(")
    print('       content="飞书API调用需要先获取app_access_token，')
    print('              然后使用该token访问Bitable API",')
    print('       memory_type="知识",')
    print('       tags=["飞书", "API"],')
    print("       importance=3")
    print("   )")

    return dashboard


def demo_query_operations(dashboard: MemoryDashboard):
    """演示查询操作"""
    print("\n" + "=" * 60)
    print("🔍 查询操作演示")
    print("=" * 60)

    # 按关键词搜索
    print("\n--- 关键词搜索 ---")
    print('dashboard.search_memories("Python")')
    print('dashboard.search_memories("异步")')

    # 按标签查询
    print("\n--- 按标签查询 ---")
    print('dashboard.get_memories_by_tag("Python")')
    print('dashboard.get_memories_by_tag("学习")')

    # 按类型查询
    print("\n--- 按类型查询 ---")
    print('dashboard.get_memories_by_type("学习")')
    print('dashboard.get_memories_by_type("决策")')

    # 按重要性查询
    print("\n--- 按重要性查询 ---")
    print("dashboard.get_important_memories(min_importance=4)")

    # 日期范围查询
    print("\n--- 日期范围查询 ---")
    print("dashboard.query_memories(date_range={")
    print('    "start": "2026-03-01",')
    print('    "end": "2026-03-15"')
    print("})")


def demo_statistics(dashboard: MemoryDashboard):
    """演示统计功能"""
    print("\n" + "=" * 60)
    print("📈 统计功能演示")
    print("=" * 60)

    # 总体统计
    print("\n--- 总体统计 ---")
    print("stats = dashboard.get_statistics()")
    print("print(stats)")
    print("""
    预期输出示例:
    {
        'total': 150,
        'type_counts': {'学习': 50, '决策': 20, '知识': 80},
        'importance_counts': {5: 10, 4: 30, 3: 80, 2: 20, 1: 10},
        'tag_counts': {'Python': 25, 'API': 20, '学习': 15},
        'skill_count': 40,
        'mastery_rate': 26.7
    }
    """)

    # 今日统计
    print("\n--- 今日统计 ---")
    print("today_stats = dashboard.get_today_statistics()")
    print("print(today_stats)")

    # 本周统计
    print("\n--- 本周统计 ---")
    print("weekly_stats = dashboard.get_weekly_statistics()")
    print("print(weekly_stats)")

    # 生成报告
    print("\n--- 生成仪表板报告 ---")
    print("report = dashboard.generate_dashboard_report()")
    print("print(report)")
    print("""
    预期输出示例:
    ==================================================
    📊 记忆可视化仪表板
    ==================================================
    
    📈 总记忆数: 150
    🎯 技能掌握度: 26.7%
    
    --- 今日统计 ---
      今日新增: 12
    
    --- 类型分布 ---
      学习: 50
      知识: 80
      决策: 20
      ...
    """)


def demo_auto_record():
    """演示自动记录功能"""
    print("\n" + "=" * 60)
    print("🤖 自动记录功能演示")
    print("=" * 60)

    # 创建自动记录器（不连接仪表板，只做演示）
    auto_recorder = AutoRecord(
        dashboard=None,
        auto_save=False,  # 演示模式，不自动保存
        min_importance_threshold=3,
    )

    print("\n✅ 自动记录器创建成功")
    print(f"   自动保存: {auto_recorder.auto_save}")
    print(f"   最低重要性阈值: {auto_recorder.min_importance_threshold}")

    # 模拟对话消息
    test_messages = [
        {
            "role": "user",
            "content": "请帮我记住这个Python技巧：使用list comprehension可以简化代码",
        },
        {
            "role": "assistant",
            "content": """好的，这里是一个示例：
squares = [x**2 for x in range(10)]
这比使用for循环更简洁高效。""",
        },
        {
            "role": "user",
            "content": "决定使用Docker来容器化我们的应用，这样可以在任何环境一致地运行",
        },
        {"role": "assistant", "content": "好的，我已经帮你记录了这个重要决策。"},
        {"role": "user", "content": "明天记得买咖啡"},
    ]

    # 处理对话
    print("\n--- 处理对话消息 ---")
    recognized = auto_recorder.process_conversation(test_messages)

    # 显示识别结果
    print(f"\n识别到 {len(recognized)} 条重要记忆:")
    for i, memory in enumerate(recognized, 1):
        print(f"\n  {i}. 类型: {memory.memory_type}")
        print(f"     重要性: {'⭐' * memory.importance} ({memory.importance})")
        print(f"     标签: {', '.join(memory.tags) if memory.tags else '无'}")
        print(f"     原因: {memory.reason}")
        print(f"     内容: {memory.content[:60]}...")

    # 显示最近记忆
    print("\n--- 最近重要记忆 (importance >= 4) ---")
    important = auto_recorder.get_recent_memories(min_importance=4)
    for memory in important:
        print(f"  • [{memory.memory_type}] {memory.content[:40]}...")

    return auto_recorder


def demo_auto_record_with_callback():
    """演示带回调的自动记录"""
    print("\n" + "=" * 60)
    print("🔔 带回调的自动记录演示")
    print("=" * 60)

    # 定义回调函数
    def on_memory_recognized(memory):
        print(f"\n  🎯 检测到重要记忆!")
        print(f"     类型: {memory.memory_type}")
        print(f"     重要性: {memory.importance}")
        print(f"     标签: {memory.tags}")

    # 创建带回调的自动记录器
    auto_recorder = AutoRecord(
        dashboard=None,
        auto_save=False,
        min_importance_threshold=3,
    )
    auto_recorder.on_memory_recognized = on_memory_recognized

    # 分析单条消息
    print("\n--- 分析消息 ---")
    test_content = "记住这个重要的配置：数据库连接使用SSL加密，端口是5432"

    memory = auto_recorder.analyze_message(
        test_content, content_type=ContentType.QUESTION, sender="user"
    )

    print(f"\n  内容: {test_content}")
    print(f"  识别结果: {memory.memory_type}, 重要性: {memory.importance}")
    print(f"  是否应记录: {auto_recorder.should_record(memory)}")


def demo_configuration():
    """演示配置说明"""
    print("\n" + "=" * 60)
    print("⚙️ 配置说明")
    print("=" * 60)

    print("""
1. 飞书多维表格配置:
   
   需要在飞书中创建两个表格:
   
   a) 记录表 (tbl_memory_records):
      - id: 自动生成
      - 内容: 单行文本
      - 项目类型: 单选(学习/想法/决策/知识/任务/会议/项目/其他)
      - 优先级别: 数字(1-5)
      - 项目状态: 单选
      - 标签: 多行文本
      - 创建日期: 日期时间
      - 备注: 多行文本
   
   b) 统计表 (tbl_memory_stats):
      - 日期: 日期
      - 学习次数: 数字
      - 记忆条数: 数字
      - 技能掌握度: 百分比
      - 技能列表: 多行文本

2. 获取Access Token:
   
   调用飞书API获取app_access_token:
   
   curl -X POST 'https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal' \\
        -H 'Content-Type: application/json' \\
        -d '{
            "app_id": "your_app_id",
            "app_secret": "your_app_secret"
        }'

3. 使用示例:
   
   from memory_dashboard import MemoryDashboard
   
   dashboard = MemoryDashboard(
       app_token="BISAbNgYXa7Do1sc36YcBChInnS",
       record_table_id="your_record_table_id"
   )
   dashboard.set_access_token("your_access_token")
   
   # 添加记忆
   dashboard.add_memory(
       content="学习Python的异步编程",
       memory_type="学习",
       tags=["Python", "异步"],
       importance=4
   )
   
   # 查询记忆
   memories = dashboard.search_memories("Python")
   
   # 获取统计
   stats = dashboard.get_statistics()
""")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🎓 记忆可视化仪表板 - 使用示例")
    print("=" * 60)

    # 1. 基本用法演示
    dashboard = demo_dashboard_basic_usage()

    # 2. 查询操作演示
    demo_query_operations(dashboard)

    # 3. 统计功能演示
    demo_statistics(dashboard)

    # 4. 自动记录演示
    auto_recorder = demo_auto_record()

    # 5. 回调演示
    demo_auto_record_with_callback()

    # 6. 配置说明
    demo_configuration()

    print("\n" + "=" * 60)
    print("✅ 演示完成!")
    print("=" * 60)
    print("""
📝 后续步骤:
   1. 在飞书中创建多维表格
   2. 获取飞书应用App ID和App Secret
   3. 配置table_id
   4. 运行脚本测试完整功能
""")


if __name__ == "__main__":
    main()
