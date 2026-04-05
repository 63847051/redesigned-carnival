#!/bin/bash
# pageindex-rag 快捷命令
# 一键记忆搜索

WORKSPACE="/root/.openclaw/workspace"

# 创建快捷命令
cat > "$WORKSPACE/ms.sh" << 'EOF'
#!/bin/bash
# pageindex-rag 快捷命令
# 使用方法: ./ms.sh "查询" [数量]

bash /root/.openclaw/workspace/scripts/memory-search-pageindex.sh "$@"
EOF

chmod +x "$WORKSPACE/ms.sh"

echo "✅ 快捷命令已创建"
echo ""
echo "🚀 使用方法:"
echo "   cd /root/.openclaw/workspace"
echo "   ./ms.sh \"查询\" 3"
echo ""
echo "📝 示例:"
echo "   ./ms.sh \"部署\""
echo "   ./ms.sh \"防护\" 5"
echo "   ./ms.sh \"OpenCode\""
