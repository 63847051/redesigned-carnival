#!/usr/bin/env python3
"""
A 股 MCP 代理服务器
代理到 http://82.156.17.205/cnstock/mcp
"""

import httpx
from fastmcp import FastMCP

# 创建 MCP 服务器
mcp = FastMCP("A 股数据代理")

# 远程 MCP 服务地址
REMOTE_MCP_URL = "http://82.156.17.205/cnstock/mcp"


async def call_remote_mcp(tool: str, stock_code: str) -> dict:
    """
    调用远程 MCP 服务
    
    Args:
        tool: 工具名称 (brief/medium/full)
        stock_code: 股票代码
    
    Returns:
        dict: 股票数据
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 调用远程 MCP 服务
            response = await client.post(
                REMOTE_MCP_URL,
                json={
                    "tool": tool,
                    "stock_code": stock_code
                },
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": f"HTTP 请求失败: {str(e)}"}
        except Exception as e:
            return {"error": f"未知错误: {str(e)}"}


@mcp.tool()
async def brief(stock_code: str) -> dict:
    """
    获取股票基本信息和行情数据
    
    Args:
        stock_code: 股票代码，例如 "SH600000"（浦发银行）
    
    Returns:
        dict: 包含股票名称、所属板块、当前行情等基本信息
    """
    result = await call_remote_mcp("brief", stock_code)
    return result


@mcp.tool()
async def medium(stock_code: str) -> dict:
    """
    获取股票基本数据 + 财务数据
    
    Args:
        stock_code: 股票代码，例如 "SH600000"（浦发银行）
    
    Returns:
        dict: 包含基本信息和近年主要财务数据
    """
    result = await call_remote_mcp("medium", stock_code)
    return result


@mcp.tool()
async def full(stock_code: str) -> dict:
    """
    获取完整股票数据 + 技术指标
    
    Args:
        stock_code: 股票代码，例如 "SH600000"（浦发银行）
    
    Returns:
        dict: 包含所有数据和技术指标（KDJ、MACD、RSI、布林带等）
    """
    result = await call_remote_mcp("full", stock_code)
    return result


if __name__ == "__main__":
    # 运行 MCP 服务器
    mcp.run()
