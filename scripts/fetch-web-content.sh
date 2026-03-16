#!/bin/bash
# 网页内容提取快捷脚本
# 作者: 大领导系统 v5.15
# 日期: 2026-03-16

URL="$1"

if [ -z "$URL" ]; then
  echo "❌ 错误: 缺少 URL 参数"
  echo ""
  echo "用法: $0 <URL>"
  echo ""
  echo "示例:"
  echo "  $0 https://github.com/openclaw/openclaw"
  echo "  $0 https://mp.weixin.qq.com/s/xxx"
  exit 1
fi

echo "🔍 正在提取网页内容..."
echo "📍 URL: $URL"
echo ""

python3 ~/.openclaw/workspace/skills/web-content-fetcher/scripts/fetch.py "$URL"
