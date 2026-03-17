#!/bin/bash
# 简单升级脚本 v5.16 - 前台运行，短超时，实时反馈
# 创建时间: 2026-03-17
# 适用版本: v5.16+
# 用途: 安全升级 OpenClaw，避免超时失联

set -e

echo "🔄 开始升级 OpenClaw..."
echo "⏰ 开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 步骤 1: 检查当前版本
echo "📊 步骤 1/6: 检查当前版本..."
openclaw --version || {
    echo "❌ 无法检查当前版本"
    exit 1
}
echo ""

# 步骤 2: 同步 GitHub（可选，但推荐）
echo "🔄 步骤 2/6: 检查 GitHub 版本同步..."
cd /root/.openclaw/workspace
if git diff --quiet origin/main; then
    echo "✅ 本地与 GitHub 同步"
else
    echo "⚠️  本地与 GitHub 不同步"
    echo "📝 建议: 先 git pull 或使用 git reset --hard origin/main"
    echo ""
    read -p "是否继续升级? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 取消升级"
        exit 1
    fi
fi
echo ""

# 步骤 3: 检查可用更新
echo "🔍 步骤 3/6: 检查可用更新..."
LATEST=$(npm view openclaw version 2>/dev/null || echo "unknown")
echo "📦 最新版本: $LATEST"
echo ""

# 步骤 4: 执行更新（带超时）
echo "⬇️  步骤 4/6: 下载并安装最新版本..."
echo "⚠️  这可能需要 30-60 秒..."
echo "⏱️  超时时间: 120 秒"

# 使用 timeout 防止卡住（最多 2 分钟）
timeout 120 npm install -g openclaw@latest --force 2>&1 || {
    echo "❌ 安装失败或超时"
    echo "💡 建议: 使用 Git 硬重置方法"
    echo "   git fetch origin main"
    echo "   git reset --hard origin/main"
    exit 1
}
echo ""

# 步骤 5: 验证新版本
echo "✅ 步骤 5/6: 验证安装..."
NEW_VERSION=$(openclaw --version | grep -oP '\d+\.\d+\.\d+' || echo "unknown")
echo "📦 新版本: $NEW_VERSION"

if [ "$NEW_VERSION" = "$LATEST" ]; then
    echo "✅ 版本匹配，安装成功"
else
    echo "⚠️  版本不匹配，可能有问题"
    echo "   本地: $NEW_VERSION"
    echo "   远程: $LATEST"
fi
echo ""

# 步骤 6: 重启 Gateway
echo "🔄 步骤 6/6: 重启 Gateway..."
systemctl --user restart openclaw-gateway

# 等待启动
sleep 3

# 检查状态
if systemctl --user is-active --quiet openclaw-gateway; then
    echo "✅ Gateway 运行正常"
else
    echo "❌ Gateway 启动失败"
    echo "💡 检查日志: journalctl --user -u openclaw-gateway -n 50"
    exit 1
fi

# 完成
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 升级完成！"
echo "⏰ 完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 当前状态:"
echo "  - OpenClaw: $NEW_VERSION"
echo "  - Gateway: 运行中"
echo "  - 内存使用: $(free | awk '/Mem/{printf "%.1f%%", $3/$2*100}')"
echo ""
echo "💡 提示:"
echo "  - 如遇问题，使用 Git 硬重置: git reset --hard origin/main"
echo "  - 查看版本: openclaw --version"
echo "  - 查看状态: openclaw status"
echo ""
