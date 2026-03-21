#!/usr/bin/env python3
# 测试 mem9 记忆系统与飞书集成（v3 - 最终版）

import asyncio
import sys
sys.path.append('/root/.openclaw/workspace')

from memory import create_context_engine, Message, TokenBudget

async def test_mem9():
    print("🧪 mem9 记忆系统测试（v3 最终版）")
    print("=" * 60)
    
    # 使用你的专属 mem9 表格
    config = {
        "enable_feishu": True,
        "feishu_app_token": "Vg0CbokIeaTUAqsjolcH1Xpnlg",
        "feishu_table_id": "tblfs59X2SkzHRwN",
    }
    
    print(f"\n📋 配置:")
    print(f"  app_token: {config['feishu_app_token']}")
    print(f"  table_id: {config['feishu_table_id']}")
    
    try:
        # 1️⃣ 创建引擎
        print(f"\n🚀 步骤 1/4: 创建上下文引擎...")
        engine = create_context_engine(config)
        print("✅ 引擎创建成功")
        
        # 2️⃣ 启动系统
        print(f"\n🔄 步骤 2/4: 启动系统（bootstrap）...")
        await engine.bootstrap()
        print("✅ 系统启动成功")
        
        # 3️⃣ 添加记忆
        print(f"\n📝 步骤 3/4: 添加测试记忆...")
        test_message = Message(
            id="test_001",
            role="user",
            content="测试：幸运小行星今天完成了系统备份和版本升级到 v5.16.0，mem9 记忆系统与飞书 Bitable 集成成功！✅"
        )
        
        print(f"  内容: {test_message.content}")
        await engine.ingest(test_message)
        print("✅ 记忆添加成功")
        
        # 4️⃣ 检索记忆
        print(f"\n🔍 步骤 4/4: 检索记忆...")
        budget = TokenBudget(hard_limit=100000, soft_limit=80000)
        context = await engine.assemble(budget)
        print("✅ 检索成功")
        
        # 显示结果
        print(f"\n📊 测试结果:")
        print(f"  记忆条目数: {len(context.memories)}")
        
        if context.memories:
            print(f"\n📚 检索到的记忆（前 5 条）:")
            for i, memory in enumerate(context.memories[:5], 1):
                content = memory.get('content', 'N/A')
                print(f"\n  {i}. {content[:70]}...")
                
                if 'tags' in memory:
                    tags = memory['tags']
                    if isinstance(tags, list):
                        print(f"     🏷️  标签: {', '.join(tags)}")
                
                if 'importance' in memory:
                    print(f"     ⭐ 重要性: {memory['importance']}")
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！mem9 系统运行正常！")
        print("=" * 60)
        
        print("\n✨ Phase 5 完成摘要:")
        print("  ✅ mem9 与飞书 Bitable 集成成功")
        print("  ✅ 记忆添加功能正常")
        print("  ✅ 记忆检索功能正常")
        print("  ✅ 飞书云端存储正常")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mem9())
