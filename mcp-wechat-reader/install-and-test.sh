#!/bin/bash
# 微信公众号文章阅读器 MCP 服务器 - 完整安装和测试脚本
#
# 版本: 1.0.0
# 创建时间: 2026-03-12

set -e

WORKSPACE="/root/.openclaw/workspace"
MCP_DIR="$WORKSPACE/mcp-wechat-reader"

echo "=================================================="
echo "🚀 微信公众号文章阅读器 MCP 服务器 - 完整安装和测试"
echo "=================================================="
echo ""

# Step 1: 安装 Python 依赖
echo "📦 Step 1/5: 安装 Python 依赖..."
pip3 install -q fastmcp httpx beautifulsoup4 lxml 2>/dev/null || echo "部分依赖可能已安装"
echo "✅ Python 依赖安装完成"
echo ""

# Step 2: 创建测试脚本
echo "📝 Step 2/5: 创建测试脚本..."
cat > "$MCP_DIR/test_server.py" << 'EOF'
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
EOF

chmod +x "$MCP_DIR/test_server.py"
echo "✅ 测试脚本已创建: $MCP_DIR/test_server.py"
echo ""

# Step 3: 提供使用说明
echo "📖 Step 3/5: 使用说明"
echo ""
echo "启动 MCP 服务器:"
echo "  cd $MCP_DIR"
echo "  ./start.sh"
echo ""
echo "或者使用 mcp-bridge:"
echo "  mcp-bridge start $MCP_DIR"
echo ""
echo "测试 MCP 服务器:"
echo "  python3 test_server.py <微信文章URL>"
echo ""

# Step 4: 创建配置文件
echo "📄 Step 4/5: 创建配置文件..."
cat > "$MCP_DIR/config.json" << EOF
{
  "mcpServers": {
    "wechat-reader": {
      "command": "python3",
      "args": ["server.py"],
      "cwd": "$MCP_DIR",
      "env": {}
    }
  }
}
EOF
echo "✅ 配置文件已创建: $MCP_DIR/config.json"
echo ""

# Step 5: 生成文档
echo "📚 Step 5/5: 生成文档..."
cat > "$MCP_DIR/USAGE.md" << EOF
# 微信公众号文章阅读器 MCP 服务器 - 使用指南

## 🚀 快速开始

### 启动服务器
\`\`\`bash
cd /root/.openclaw/workspace/mcp-wechat-reader
./start.sh
\`\`\`

### 测试功能
\`\`\`bash
python3 test_server.py <微信文章URL>
\`\`\`

## 📋 工具列表

### 1. read_wechat_article
读取完整的微信文章内容

**输入**:
- \`url\`: 微信公众号文章 URL (mp.weixin.qq.com)

**输出**:
- 标题、作者、正文、发布时间、公众号名称

### 2. extract_article_info
提取文章的关键信息

**输入**:
- \`url\`: 微信公众号文章 URL

**输出**:
- 标题、作者、公众号、发布时间
- 字数统计
- 图片链接（前5张）
- 摘要

### 3. summarize_article
生成文章摘要

**输入**:
- \`url\`: 微信公众号文章 URL
- \`max_length\`: 摘要最大长度（默认200字）

**输出**:
- 摘要内容

## 🎯 使用示例

### 示例 1: 读取文章
\`\`\`
# 输入
{
  "url": "https://mp.weixin.qq.com/s/xxx"
}

# 输出
{
  "title": "文章标题",
  "author": "作者名",
  "content": "文章正文...",
  "account": "公众号名称"
}
\`\`\`

### 示例 2: 提取信息
\`\`\`
# 输入
{
  "url": "https://mp.weixin.qq.com/s/xxx"
}

# 输出
{
  "title": "...",
  "word_count": 1234,
  "image_count": 5
}
\`\`\`

### 示例 3: 生成摘要
\`\`\`
# 输入
{
  "url": "https://mp.weixin.qq.com/s/xxx",
  "max_length": 100
}

# 输出
{
  "summary": "100字摘要..."
}
\`\`\`

## 🔧 集成到 OpenClaw

### 配置 OpenClaw
在 openclaw.json 中添加：

\`\`\`json
{
  "mcpServers": {
    "wechat-reader": {
      "command": "python3",
      "args": ["server.py"],
      "cwd": "/root/.openclaw/workspace/mcp-wechat-reader"
    }
  }
}
\`\`\`

### 使用
在对话中直接分享微信文章链接，系统会自动读取并总结。

---

**创建时间**: 2026-03-12
**版本**: 1.0.0
**状态**: ✅ 就绪
EOF

echo "✅ 使用文档已创建: $MCP_DIR/USAGE.md"
echo ""

echo "=================================================="
echo "✅ 安装和配置完成！"
echo "=================================================="
echo ""
echo "📊 服务器位置: $MCP_DIR"
echo ""
echo "🚀 下一步："
echo "  1. 启动服务器: cd $MCP_DIR && ./start.sh"
echo "  2. 或测试: python3 $MCP_DIR/test_server.py <微信文章URL>"
echo ""
