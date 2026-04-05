#!/bin/bash
# Claude Code + GLM-4.7 测试脚本

echo "🧪 测试 Claude Code 配置 GLM-4.7"
echo "=========================="
echo ""

# 显示配置
echo "📋 当前配置："
cat ~/.config/claude/config.json
echo ""

# 测试命令
echo "🚀 测试命令："
echo "claude --model glm-4.7 \"你好，请用一句话介绍你自己\""
echo ""

echo "💡 使用示例："
echo "1. 基础对话："
echo "   claude --model glm-4.7 \"你好\""
echo ""
echo "2. 技术研究："
echo "   claude --model glm-4.7 \"深入研究 PAI 的架构\""
echo ""
echo "3. 代码实施："
echo "   claude --model glm-4.7 \"实现学习信号捕获系统\""
echo ""

echo "✅ 配置完成！现在可以使用 GLM-4.7 了"
