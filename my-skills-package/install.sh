#!/bin/bash
# 技能系统一键安装脚本

set -e

WORKSPACE="${WORKSPACE:-/root/.openclaw/workspace}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📦 安装技能系统到 $WORKSPACE"

# 1. 安装技能
echo "📋 安装技能..."
for skill_dir in "$SCRIPT_DIR"/*; do
    if [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ]; then
        skill_name=$(basename "$skill_dir")
        if [ "$skill_name" != "system" ]; then
            echo "  安装: $skill_name"
            rm -rf "$WORKSPACE/skills/$skill_name"
            cp -r "$skill_dir" "$WORKSPACE/skills/"
        fi
    fi
done

# 2. 安装系统文件
echo "🔧 安装系统文件..."
cp -r "$SCRIPT_DIR/system/"* "$WORKSPACE/" 2>/dev/null || true

# 3. 设置执行权限
echo "⚙️  设置权限..."
chmod +x "$WORKSPACE"/scripts/*.sh 2>/dev/null || true

echo ""
echo "✅ 技能系统安装完成！"
echo ""
echo "📊 已安装技能："
ls -1 "$SCRIPT_DIR" | grep -v "^system$" | while read skill; do
    echo "  - $skill"
done
