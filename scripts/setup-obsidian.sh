#!/bin/bash
# Obsidian 集成脚本
# 将知识库链接到 Obsidian

WORKSPACE="/root/.openclaw/workspace"
KNOWLEDGE_DIR="$WORKSPACE/knowledge-compiled"
OBSIDIAN_DIR="$HOME/Obsidian"
OBSIDIAN Vault="$OBSIDIAN_DIR/Knowledge"

echo "🔧 Obsidian 集成"
echo "======================================"
echo ""

# 检查 Obsidian 是否安装
if ! command -v obsidian &> /dev/null; then
    echo "⚠️  Obsidian 未安装"
    echo ""
    echo "📦 安装方法:"
    echo "   1. 下载: https://obsidian.md/"
    echo "   2. 安装: 按照安装向导操作"
    echo ""
    echo "⏸️  先创建符号链接，稍后手动安装 Obsidian"
    ln -sf "$WORKSPACE" "$OBSIDIAN_DIR/Knowledge"
    echo "   已创建符号链接: $OBSIDIAN_DIR/Knowledge -> $WORKSPACE"
else
    echo "✅ Obsidian 已安装"
fi

echo ""
echo "📁 Obsidian Vault 路径: $OBSIDIAN Vault"
echo "📂 符号链接: $OBSIDIAN_DIR/Knowledge -> $WORKSPACE"
echo ""

echo "✅ Obsidian 集成准备完成！"
echo ""
echo "🚀 使用方法:"
echo "   1. 打开 Obsidian"
echo "   2. 打开 Vault: Knowledge"
echo "   3. 你的知识库会自动同步显示"
echo ""
echo "📝 提示:"
echo "   在 Obsidian 中，所有 memory/*.md 文件都会自动显示"
echo "   你可以像 Wiki 一样浏览和编辑"
