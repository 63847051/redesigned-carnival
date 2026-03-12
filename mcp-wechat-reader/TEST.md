# 🧪 测试脚本 - 微信公众号文章阅读器

**版本**: 1.0.0
**创建时间**: 2026-03-12

---

## 🧪 测试场景

### 测试 1: 读取文章
```python
import asyncio
from server import mcp

async def test_read_article():
    # 测试 URL（需要替换为真实文章链接）
    test_url = "https://mp.weixin.qq.com/s/xxx"
    
    result = await mcp.call_tool("read_wechat_article", url=test_url)
    print(result)

# 运行测试
asyncio.run(test_read_article())
```

### 测试 2: 提取关键信息
```python
async def test_extract_info():
    test_url = "https://mp.weixin.qq.com/s/xxx"
    
    result = await mcp.call_tool("extract_article_info", url=test_url)
    print(result)

asyncio.run(test_extract_info())
```

### 测试 3: 生成摘要
```python
async def test_summarize():
    test_url = "https://mp.weixin.qq.com/s/xxx"
    
    result = await mcp.call_tool("summarize_article", url=test_url, max_length=100)
    print(result)

asyncio.run(test_summarize())
```

---

## 📝 测试清单

- [ ] 服务器正常启动
- [ ] 能够读取微信文章
- [ ] 能够提取关键信息
- [ ] 能够生成摘要
- [ ] 错误处理正常

---

## 🚨 注意事项

1. **需要真实文章 URL** - 使用实际的微信公众号文章链接进行测试
2. **网络连接** - 需要能够访问 mp.weixin.qq.com
3. **反爬虫** - 部分文章可能有访问限制

---

*测试脚本版本: 1.0.0*
*创建时间: 2026-03-12*
