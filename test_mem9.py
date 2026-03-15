#!/usr/bin/env python3
# 测试 mem9 记忆系统与飞书集成

import asyncio
import sys
sys.path.append('/root/.openclaw/workspace')

from memory import create_context_engine

async def test_mem9():
    print("🧪 测试 mem9 记忆系统与飞书集成\n")
    
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
        engine = create_context_engine(config)
        print("✅ 上下文引擎创建成功")
        
        # 启动系统
        await engine.bootstrap()
        print("✅ 系统启动成功")
        
        # 测试添加记忆
        from memory.auto_tagger import extract_tags
        from memory.importance_scorer import score_importance
        
        test_memory = {
            "content": "测试：幸运小行星今天完成了系统备份和版本升级到 v5.12.0",
            "importance": "HIGH",
            "memory_type": "LONG_TERM",
            "extraction_type": "PROJECT",
            "tags": ["系统升级", "GitHub备份"],
        }
        
        print(f"\n📝 测试添加记忆: {test_memory['content']}")
        await engine.add_memory(test_memory)
        print("✅ 记忆添加成功")
        
        # 测试检索
        print(f"\n🔍 测试检索: GitHub备份")
        results = await engine.search("GitHub备份", limit=3)
        print(f"✅ 检索成功，找到 {len(results)} 条结果")
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.get('content', 'N/A')[:50]}...")
        
        print("\n✅ 所有测试通过！")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mem9())
