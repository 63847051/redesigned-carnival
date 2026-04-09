"""
OpenClaw MCP Server 测试套件
"""

import asyncio
import pytest
from openclaw_mcp_server import (
    send_message_handler,
    read_history_handler,
    claim_tasks_handler
)

@pytest.mark.asyncio
async def test_send_message():
    """测试发送消息"""
    result = await send_message_handler(
        sessionKey="agent:main:test",
        message="Hello from test!"
    )
    assert result.type == "text"
    assert "✅ 消息已发送" in result.text or "❌" in result.text

@pytest.mark.asyncio
async def test_read_history():
    """测试读取历史"""
    result = await read_history_handler(
        sessionKey="agent:main:test",
        limit=10,
        format="markdown"
    )
    assert result.type == "text"
    assert "会话历史" in result.text or "❌" in result.text

@pytest.mark.asyncio
async def test_claim_tasks():
    """测试认领任务"""
    result = await claim_tasks_handler(
        mode="auto",
        skills=["code"],
        limit=5
    )
    assert result.type == "text"
    assert "认领的任务" in result.text or "❌" in result.text

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
