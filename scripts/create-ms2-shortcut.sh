#!/bin/bash
# 创建智能检索快捷命令

WORKSPACE="/root/.openclaw/workspace"

# 创建 ms2.sh（带 LLM 排序）
cat > "$WORKSPACE/ms2.sh" << 'EOF'
#!/bin/bash
# 智能检索快捷命令（带 LLM 排序）
# 使用方法: ./ms2.sh "查询" [数量]

bash /root/.openclaw/workspace/scripts/smart-retrieve.sh "$@" 1
EOF

chmod +x "$WORKSPACE/ms2.sh"

echo "✅ 智能检索快捷命令已创建"
echo ""
echo "🚀 使用方法:"
echo "   cd /root/.openclaw/workspace"
echo "   ./ms2.sh \"查询\" 5"
echo ""
echo "📝 对比:"
echo "   ./ms.sh  - 快速检索（无 LLM）"
echo "   ./ms2.sh - 智能检索（有 LLM）"
echo ""
echo "💡 推荐使用 ms2.sh，更智能！"
