#!/bin/bash
# Lightpanda 快速使用脚本

LIGHTPANDA_BIN="/root/.openclaw/workspace/lightpanda"

# 检查 Lightpanda 是否存在
if [ ! -f "$LIGHTPANDA_BIN" ]; then
    echo "❌ Lightpanda 未找到"
    echo "请先运行: cd /root/.openclaw/workspace && curl -L -o lightpanda https://github.com/lightpanda-io/browser/releases/download/nightly/lightpanda-x86_64-linux && chmod +x ./lightpanda"
    exit 1
fi

# 显示帮助
show_help() {
    echo "Lightpanda - 专为 AI 设计的无头浏览器"
    echo ""
    echo "用法:"
    echo "  $0 fetch <url>           - 获取网页（HTML）"
    echo "  $0 markdown <url>         - 获取网页（Markdown）"
    echo "  $0 semantic <url>         - 获取语义树"
    echo "  $0 serve                 - 启动 CDP 服务器"
    echo "  $0 test                  - 测试 Lightpanda"
    echo ""
    echo "示例:"
    echo "  $0 fetch https://example.com"
    echo "  $0 markdown https://example.com"
}

case "$1" in
    fetch)
        if [ -z "$2" ]; then
            echo "❌ 请提供 URL"
            exit 1
        fi
        $LIGHTPANDA_BIN fetch --dump html "$2"
        ;;
    
    markdown)
        if [ -z "$2" ]; then
            echo "❌ 请提供 URL"
            exit 1
        fi
        $LIGHTPANDA_BIN fetch --dump markdown "$2"
        ;;
    
    semantic)
        if [ -z "$2" ]; then
            echo "❌ 请提供 URL"
            exit 1
        fi
        $LIGHTPANDA_BIN fetch --dump semantic_tree_text "$2"
        ;;
    
    serve)
        echo "🚀 启动 Lightpanda CDP 服务器..."
        echo "端口: 9222"
        echo "WebSocket: ws://localhost:9222"
        echo ""
        $LIGHTPANDA_BIN serve --host 127.0.0.1 --port 9222
        ;;
    
    test)
        echo "🧪 测试 Lightpanda"
        echo "="*60
        echo "获取: https://example.com"
        $LIGHTPANDA_BIN fetch --dump markdown https://example.com
        echo ""
        echo "✅ 测试完成"
        ;;
    
    *)
        show_help
        ;;
esac
