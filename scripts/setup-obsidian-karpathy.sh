#!/bin/bash
# Obsidian 集成 - Karpathy 风格
# 认真应用 Obsidian 作为知识库 IDE

WORKSPACE="/root/.openclaw/workspace"
KB_DIR="$WORKSPACE/knowledge-base"
OBSIDIAN_DIR="$HOME/Obsidian"
OBSIDIAN_VAULT="$OBSIDIAN_DIR/Knowledge"

echo "📖 Obsidian 集成 - Karpathy 风格"
echo "======================================"
echo ""

# 检查 Obsidian 是否安装
if ! command -v obsidian &> /dev/null; then
    echo "⚠️  Obsidian 未安装"
    echo ""
    echo "📦 安装方法:"
    echo "   1. 访问: https://obsidian.md/"
    echo "   2. 下载: 根据系统选择版本"
    echo "   3. 安装: 按照安装向导操作"
    echo ""
    echo "⏸️  系统会继续准备，稍后手动安装 Obsidian"
else
    echo "✅ Obsidian 已安装"
fi

echo ""

# 创建符号链接
echo "🔗 创建 Obsidian Vault..."
ln -sf "$KB_DIR" "$OBSIDIAN_VAULT"

echo "✅ Vault 已创建: $OBSIDIAN_VAULT"
echo ""

echo "📂 目录结构:"
echo "   Vault: $OBSIDIAN_VAULT"
echo "   链接: $OBSIDIAN_VAULT -> $KB_DIR"
echo ""

echo "📝 Obsidian 配置建议:"
echo ""
echo "1. 安装 Obsidian 插件:"
echo "   - Marp: Markdown 转幻灯片"
echo "   - Dataview: 数据可视化"
echo "   - Graph Analysis: 知识图谱"
echo "   - Advanced Tables: 表格"
echo ""
echo "2. 配置插件:"
echo "   - 在 Obsidian 中打开设置"
echo "   - 启用第三方插件"
echo "   - 搜索并安装上述插件"
echo ""
echo "3. 查看知识库:"
echo "   - 打开 Obsidian"
echo "   - 打开 Vault: Knowledge"
echo "   - 浏览 raw/ 和 wiki/ 目录"
echo "   - 使用图谱视图查看连接"
echo ""

echo "✅ Obsidian 集成准备完成！"
echo ""
echo "🚀 使用方法:"
echo "   1. 打开 Obsidian"
echo "   2. 选择 Vault: Knowledge"
echo "   3. 像浏览 Wiki 一样查看知识库"
echo "   4. 使用 [[双向链接]] 连接文档"
