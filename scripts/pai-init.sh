#!/bin/bash
# =============================================================================
# PAI 系统初始化脚本
# =============================================================================
# 功能：加载个性、规则和配置到每次会话
# 使用：每次会话开始时自动调用
# =============================================================================

SETTINGS="/root/.openclaw/workspace/settings.json"
PERSONALITY="/root/.openclaw/workspace/PERSONALITY.md"
STEERING_RULES="/root/.openclaw/workspace/AI-STEERING-RULES.md"
IDENTITY="/root/.openclaw/workspace/IDENTITY.md"

echo "🚀 PAI 系统初始化 v1.0"
echo "======================================"
echo ""

# =============================================================================
# 步骤 1: 加载身份和个性
# =============================================================================

echo "📝 步骤 1: 加载身份和个性..."
echo ""

if [ -f "$SETTINGS" ]; then
    ai_name=$(grep '"ai_name"' "$SETTINGS" | head -1)
    version=$(grep '"version"' "$SETTINGS" | head -1)
    relationship=$(grep '"relationship_model"' "$SETTINGS" | head -1)
    echo "   ✅ settings.json"
    echo "   - AI 名称: $ai_name"
    echo "   - 版本: $version"
    echo "   - 关系模型: $relationship"
else
    echo "   ⚠️  settings.json 不存在"
fi

echo ""
echo "   个性特征:"
if [ -f "$PERSONALITY" ]; then
    echo "   - 高能量: 80"
    echo "   - 高韧性: 90"
    echo "   - 高精确度: 90"
    echo "   - 高好奇心: 95"
    echo "   - 同伴关系（Peer）"
else
    echo "   ⚠️  PERSONALITY.md 不存在"
fi

echo ""

# =============================================================================
# 步骤 2: 加载 AI 转向规则
# =============================================================================

echo "🛡️ 步骤 2: 加载 AI 转向规则..."
echo ""

if [ -f "$STEERING_RULES" ]; then
    echo "   SYSTEM 规则（3 个）:"
    echo "   - ✅ Verify Before Claiming Completion"
    echo "   - ✅ Ask Before Destructive Actions"
    echo "   - ✅ Read Before Modifying"
    echo ""
    echo "   USER 规则（5 个）:"
    echo "   - ✅ Use Fast CLI Utilities"
    echo "   - ✅ Verify All Browser Work with Screenshots"
    echo "   - ✅ Be Direct and Concise"
    echo "   - ✅ Use Chinese for Chinese Users"
    echo "   - ✅ Professional Task Assignment"
else
    echo "   ⚠️  AI-STEERING-RULES.md 不存在"
fi

echo ""

# =============================================================================
# 步骤 3: 验证配置完整性
# =============================================================================

echo "🔍 步骤 3: 验证配置完整性..."
echo ""

files=("$SETTINGS" "$PERSONALITY" "$STEERING_RULES" "$IDENTITY")
all_exist=true

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $(basename $file)"
    else
        echo "   ❌ $(basename $file) - 不存在"
        all_exist=false
    fi
done

echo ""

if [ "$all_exist" = true ]; then
    echo "🎉 系统初始化完成！"
    echo ""
    echo "🤖 我是 $(jq -r '.identity.ai_name' $SETTINGS) 🎯"
    echo "📊 版本: $(jq -r '.identity.version' $SETTINGS)"
    echo "🤝 关系: 同伴（Peer）"
    echo "💪 能量: 80 | 韧性: 90 | 精确: 90 | 好奇: 95"
else
    echo "⚠️  配置不完整，某些文件缺失"
fi

echo ""
echo "======================================"
