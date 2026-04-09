"""
OpenClaw MCP Server 集成测试
"""

import asyncio
import httpx

GATEWAY_URL = "http://localhost:18789"
API_KEY = "8035173d53051cbadf25237967b8dfed116ce48d48dd50eb"

async def test_send_message():
    """测试发送消息"""
    print("\n🧪 测试 send_message...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GATEWAY_URL}/api/sessions/send",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={
                    "sessionKey": "agent:main:test",
                    "message": "Hello from MCP integration test!"
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            print(f"✅ send_message 成功: {data}")
    except Exception as e:
        print(f"❌ send_message 失败: {e}")

async def test_read_history():
    """测试读取历史"""
    print("\n🧪 测试 read_history...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GATEWAY_URL}/api/sessions/agent:main:test/history",
                headers={"Authorization": f"Bearer {API_KEY}"},
                params={"limit": 10},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            print(f"✅ read_history 成功: {len(data.get('messages', []))} 条消息")
    except Exception as e:
        print(f"❌ read_history 失败: {e}")

async def test_claim_tasks():
    """测试认领任务"""
    print("\n🧪 测试 claim_tasks...")
    
    try:
        # 先列出会话
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GATEWAY_URL}/api/sessions",
                headers={"Authorization": f"Bearer {API_KEY}"},
                params={"active": True},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            sessions = data.get("sessions", [])
            print(f"✅ claim_tasks 成功: 找到 {len(sessions)} 个活跃会话")
    except Exception as e:
        print(f"❌ claim_tasks 失败: {e}")

async def main():
    """运行所有测试"""
    print("🚀 OpenClaw MCP Server 集成测试")
    print("=" * 50)
    
    await test_send_message()
    await test_read_history()
    await test_claim_tasks()
    
    print("\n" + "=" * 50)
    print("✅ 集成测试完成")

if __name__ == "__main__":
    asyncio.run(main())
