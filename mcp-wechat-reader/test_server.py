#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '/root/.openclaw/workspace/mcp-wechat-reader')

from server import mcp

async def test_server_info():
    """测试服务器信息"""
    print("=" * 50)
    print("🧪 测试 1: 服务器信息")
    print("=" * 50)
    
    try:
        result = await mcp.call_tool("get_server_info")
        print("✅ 服务器信息:")
        print(f"  名称: {result.get('name')}")
        print(f"  版本: {result.get('version')}")
        print(f"  状态: {result.get('status')}")
        print(f"  功能: {', '.join(result.get('features', []))}")
    except Exception as e:
        print(f"❌ 错误: {e}")
    print()

async def test_read_article(url):
    """测试读取文章"""
    print("=" * 50)
    print("🧪 测试 2: 读取文章")
    print("=" * 50)
    
    try:
        result = await mcp.call_tool("read_wechat_article", url=url)
        print("✅ 读取结果:")
        print(f"  标题: {result.get('title')}")
        print(f"  作者: {result.get('author')}")
        print(f"  公众号: {result.get('account')}")
        print(f"  字数: {len(result.get('content', ''))}")
        print(f"  摘要: {result.get('summary', '')[:100]}...")
    except Exception as e:
        print(f"❌ 错误: {e}")
    print()

# 测试用的示例 URL（需要替换为真实链接）
TEST_URL = "https://mp.weixin.qq.com/s/example"

async def main():
    print("\n📋 开始测试...\n")
    
    # 测试 1: 服务器信息
    await test_server_info()
    
    # 测试 2: 读取文章（需要真实 URL）
    print("⚠️  注意: 需要提供真实的微信文章 URL 进行测试")
    print(f"   示例: python3 test_server.py <真实微信文章URL>")
    print()
    
    print("==================================================")
    print("✅ 测试完成！")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
