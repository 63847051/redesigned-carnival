#!/usr/bin/env python3
"""
微信公众号文章阅读器 MCP 服务器
使用 FastMCP 构建
"""

from fastmcp import FastMCP
import httpx
from typing import Any
from bs4 import BeautifulSoup

# 创建 FastMCP 实例
mcp = FastMCP(
    name="wechat-article-reader",
    version="1.0.0"
)

# 工具 1: 读取微信公众号文章
@mcp.tool()
async def read_wechat_article(url: str) -> dict[str, Any]:
    """读取微信公众号文章"""
    try:
        if "mp.weixin.qq.com" not in url:
            return {
                "success": False,
                "error": "URL 不是微信公众号链接",
                "url": url
            }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.find('h1', class_='title')
            title_text = title.get_text().strip() if title else "未知标题"
            
            author = soup.find('a', class_='lnk_nc mb_lnk')
            author_text = author.get_text().strip() if author else "未知作者"
            
            content_div = soup.find('div', id='js_content')
            content_text = ""
            if content_div:
                for script in content_div.find_all(['script', 'style']):
                    script.decompose()
                content_text = content_div.get_text().strip()
            
            # 生成摘要
            summary = content_text[:200] + "..." if len(content_text) > 200 else content_text
            
            return {
                "success": True,
                "url": url,
                "title": title_text,
                "author": author_text,
                "content": content_text,
                "summary": summary
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url
        }

# 工具 2: 提取关键信息
@mcp.tool()
async def extract_article_info(url: str) -> dict[str, Any]:
    """提取文章关键信息"""
    result = await read_wechat_article(url)
    
    if not result.get("success"):
        return result
    
    content = result.get("content", "")
    word_count = len(content)
    
    summary = result.get("summary", "")
    
    return {
        "success": True,
        "url": url,
        "title": result.get("title"),
        "author": result.get("author"),
        "word_count": word_count,
        "summary": summary
    }

# 工具 3: 生成摘要
@mcp.tool()
async def summarize_article(url: str, max_length: int = 200) -> dict[str, Any]:
    """生成文章摘要"""
    result = await read_wechat_article(url)
    
    if not result.get("success"):
        return result
    
    content = result.get("content", "")
    
    if len(content) > max_length:
        summary = content[:max_length] + "..."
    else:
        summary = content
    
    return {
        "success": True,
        "url": url,
        "summary": summary,
        "original_length": len(content)
    }

# 注意：移除 @mcp.resource，因为它会导致 URL 解析错误
# 服务器信息通过工具提供，不作为资源暴露

# 提示词：使用示例
@mcp.prompt()
def usage_example() -> str:
    """MCP 服务器使用示例"""
    return """
# 使用示例

## 读取文章
工具: read_wechat_article
输入: {"url": "https://mp.weixin.qq.com/s/xxx"}

## 提取关键信息
工具: extract_article_info
输入: {"url": "https://mp.weixin.qq.com/s/xxx"}

## 生成摘要
工具: summarize_article
输入: {"url": "https://mp.weixin.qq.com/s/xxx", "max_length": 100}
    """

# 运行服务器
if __name__ == "__main__":
    mcp.run()
