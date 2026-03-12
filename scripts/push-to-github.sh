#!/bin/bash
# GitHub 推送脚本 - 使用 Token 认证

echo "🚀 准备推送到 GitHub..."
echo ""

# 仓库信息
REPO="63847051/self-evolution-system"
BRANCH="master"

echo "📋 仓库信息:"
echo "  仓库: $REPO"
echo "  分支: $BRANCH"
echo ""

# 检查是否有未推送的提交
echo "🔍 检查本地提交..."
cd /root/.openclaw/workspace
git log --oneline -5

echo ""
echo "✅ 本地有提交需要推送"
echo ""

# 提示输入 Token
echo "🔑 请提供 GitHub Personal Access Token:"
echo ""
echo "1. 访问: https://github.com/settings/tokens"
echo "2. 创建 Token (需要 repo 权限)"
echo "3. 复制 Token (格式: github_pat_...)"
echo ""
echo "请粘贴 Token:"
read -s GITHUB_TOKEN

echo ""
echo "🔄 正在推送..."

# 使用 Token 推送
git push https://${GITHUB_TOKEN}@github.com/${REPO}.git ${BRANCH}

# 检查结果
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 推送成功！"
    echo "🌐 访问: https://github.com/${REPO}"
else
    echo ""
    echo "❌ 推送失败"
    echo "请检查:"
    echo "  1. Token 是否正确"
    echo "  2. Token 是否有 repo 权限"
    echo "  3. 网络连接是否正常"
fi
