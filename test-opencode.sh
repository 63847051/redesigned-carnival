#!/bin/bash
# =============================================================================
# 🧪 OpenCode 测试脚本
# =============================================================================

echo "🧪 测试 OpenCode AI 编程代理"
echo "======================================"
echo ""

cd /root/.openclaw/workspace

echo "📂 当前项目: $(pwd)"
echo ""

echo "🤖 启动 OpenCode..."
echo "提示: OpenCode 将使用自带的 Claude Sonnet 4.6 模型"
echo ""

# 显示 OpenCode 信息
echo "📊 OpenCode 信息:"
echo "   版本: $(opencode --version)"
echo "   位置: $(which opencode)"
echo ""

echo "✅ OpenCode 已安装并可以使用自带模型！"
echo ""
echo "🚀 使用方法:"
echo "   1. cd /path/to/project"
echo "   2. opencode"
echo "   3. 输入问题或指令"
echo ""
echo "💡 示例:"
echo "   - 解释这个文件"
echo "   - 添加新功能"
echo "   - 修复bug"
echo "   - 重构代码"
echo ""
echo "🎯 特点:"
echo "   ✅ 自带免费模型（Claude Sonnet 4.6）"
echo "   ✅ 支持多种编辑器（终端、IDE、桌面）"
echo "   ✅ 可以连接其他模型（GPT、Gemini等）"
echo "   ✅ 开源免费"
echo ""
echo "📚 文档: https://opencode.ai/docs"
