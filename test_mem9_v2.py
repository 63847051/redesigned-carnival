#!/usr/bin/env python3
# 测试 mem9 记忆系统与飞书集成（v2 - 使用正确的 API）

import asyncio
import sys
sys.path.append('/root/.openclaw/workspace')

from memory import create_context_engine, Message

async def test_mem9():
    print("🧪 测试 mem9 记忆系统与飞书集成（v2）\n")
    print("=" * 60)
    
    # 使用你的专属 mem9 表格
    config = {
        "enable_feishu": True,
        "feishu_app_token": "Vg0CbokIeaTUAqsjolcH1Xpnlg",
        "feishu_table_id": "tblfs59X2SkzHRwN",
    }
    
    print(f"📋 配置:")
    print(f"  - app_token: {config['feishu_app_token']}")
    print(f"  - table_id: {config['feishu_table_id']}")
    print()
    
    try:
        # 创建上下文引擎
        print("🚀 创建上下文引擎...")
        engine = create_context_engine(config)
        print("✅ 上下文引擎创建成功")
        
        # 启动系统
        print("\n🔄 启动系统（bootstrap）...")
        await engine.bootstrap()
        print("✅ 系统启动成功")
        
        # 测试添加记忆（使用 ingest API）
        test_message = Message(
            id="test_001",
            role="user",
            content="测试：幸运小行星今天完成了系统备份和版本升级到 v5.16.0，mem9 记忆系统运行正常！"
        )
        
        print(f"\n📝 测试添加记忆（ingest）:")
        print(f"  ID: {test_message.id}")
        print(f"  角色: {test_message.role}")
        print(f"  内容: {test_message.content}")
        
        # 使用 ingest 方法
        await engine.ingest(test_message)
        print("✅ 记忆添加成功（通过 ingest）")
        
        # 测试检索（使用 assemble API）
        print(f"\n🔍 测试检索（assemble）...")
        
        from memory import TokenBudget
        budget = TokenBudget(hard_limit=100000, soft_limit=80000)
        
        context = await engine.assemble(budget)
        print(f"✅ 检索成功！")
        print(f"  - Token 使用: {context.stats.tokens_used}")
        print(f"  - 记忆条目数: {len(context.memories)}")
        
        # 显示检索到的记忆
        if context.memories:
            print(f"\n📚 检索到的记忆:")
            for i, memory in enumerate(context.memories[:5], 1):
                print(f"\n  {i}. {memory.get('content', 'N/A')[:80]}...")
                if 'tags' in memory:
                    print(f"     标签: {', '.join(memory['tags'])}")
                if 'importance' in memory:
                    print(f"     重要性: {memory['importance']}")
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！mem9 系统运行正常！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mem9())
