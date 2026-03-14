#!/bin/bash
# 微信文章统一读取脚本
# 使用方法: ./wechat-reader.sh <URL> [模式]
# 模式: auto(默认) | fast | screenshot | full

URL="$1"
MODE="${2:-auto}"  # auto, fast, screenshot, full

# 显示帮助
if [ -z "$URL" ]; then
  echo "📖 微信文章统一读取脚本"
  echo ""
  echo "使用方法:"
  echo "  $0 <URL> [模式]"
  echo ""
  echo "模式:"
  echo "  auto       - 自动选择最佳工具（默认）"
  echo "  fast       - 快速导出 Markdown（推荐）"
  echo "  screenshot - 带截图的完整读取"
  echo "  full       - 完整分析（wechat-reader）"
  echo ""
  echo "示例:"
  echo "  $0 https://mp.weixin.qq.com/s/XXXXX"
  echo "  $0 https://mp.weixin.qq.com/s/XXXXX fast"
  echo ""
  exit 1
fi

# 验证 URL
if [[ ! "$URL" =~ mp\.weixin\.qq\.com ]]; then
  echo "❌ 错误: URL 不是微信公众号文章链接"
  exit 1
fi

echo "📖 开始读取微信文章..."
echo "URL: $URL"
echo "模式: $MODE"
echo ""

case "$MODE" in
  fast)
    echo "🚀 使用快速模式（wechat-article-reader）"
    python3 /root/.openclaw/workspace/skills/wechat-article-reader/scripts/export.py "$URL"
    ;;

  screenshot)
    echo "📸 使用截图模式（wxmp-reader）"
    cd /root/.openclaw/workspace/skills/wxmp-reader
    node scripts/fetch_wechat.js "$URL" --json --chrome-path=/root/.cache/ms-playwright/chromium-1194/chrome-linux/chrome
    echo ""
    echo "💡 提示: 文章内容已显示在上方"
    echo "💡 如需截图，运行: node scripts/screenshot_wechat.js \"$URL\""
    ;;

  full)
    echo "🔍 使用完整分析模式（wechat-reader）"
    cd /root/.openclaw/workspace/skills/wechat-reader
    # 使用 wechat-reader 的完整功能
    if [ -f "scripts/fetch_wechat.js" ]; then
      node scripts/fetch_wechat.js "$URL" --json
    else
      echo "❌ 错误: wechat-reader 未正确安装"
      exit 1
    fi
    ;;

  auto|*)
    echo "🎯 自动选择最佳工具"
    # 默认使用 wechat-article-reader（最快）
    python3 /root/.openclaw/workspace/skills/wechat-article-reader/scripts/export.py "$URL"
    ;;
esac

echo ""
echo "✅ 完成！"
