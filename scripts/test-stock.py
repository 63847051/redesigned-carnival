#!/usr/bin/env python3
import httpx
import re

# 测试上证指数
url = "https://r.jina.ai/https://quote.eastmoney.com/unify/r/1.000001"

try:
    response = httpx.get(url, timeout=10)
    print("状态码:", response.status_code)
    print("内容长度:", len(response.text))
    print("\n前200字符:")
    print(response.text[:200])
except Exception as e:
    print(f"错误: {e}")
