#!/bin/bash
# GitHub 推送指南 - 使用环境变量

echo "🚀 推送 v5.3 到 GitHub"
echo ""

echo "📋 本地提交信息:"
cd /root/.openclaw/workspace
git log --oneline -1

echo ""
echo "────────────────────────────────────"
echo "🔑 推送方式（选择一种）"
echo "────────────────────────────────────"
echo ""

echo "方式 1: 使用环境变量（推荐）"
echo "-----------------------------------"
echo "运行以下命令（替换 <YOUR_TOKEN>）:"
echo ""
echo "export GITHUB_TOKEN='<YOUR_TOKEN>'"
echo "git push https://\${GITHUB_TOKEN}@github.com/63847051/self-evolution-system.git master"
echo ""

echo "方式 2: 使用 git credential-store"
echo "-----------------------------------"
echo "运行以下命令（替换 <YOUR_TOKEN>）:"
echo ""
echo "git config credential.helper store"
echo "git push https://<YOUR_TOKEN>@github.com/63847051/self-evolution-system.git master"
echo ""

echo "方式 3: 一次性推送"
echo "-----------------------------------"
echo "直接运行（替换 <YOUR_TOKEN>）:"
echo ""
echo "git push https://<YOUR_TOKEN>@github.com/63847051/self-evolution-system.git master"
echo ""

echo "────────────────────────────────────"
echo "📝 Token 获取步骤:"
echo "────────────────────────────────────"
echo "1. 访问: https://github.com/settings/tokens"
echo "2. 点击 'Generate new token'"
echo "3. 勾选权限:"
echo "   ☑️ repo (完整仓库访问权限)"
echo "4. 生成并复制 Token"
echo "5. 粘贴到上面的命令中"
echo ""

echo "🌐 推送成功后访问:"
echo "https://github.com/63847051/self-evolution-system"
echo ""
