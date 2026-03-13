#!/bin/bash
# L7配置验证层 v1.1 - 预防配置错误
# 修复：调整检查逻辑，只检查存在的配置

echo "🔍 L7: 配置验证..."

CONFIG_FILE="/root/.openclaw/openclaw.json"
ERRORS=0

# 检查1: 字段命名约定
if grep -q '"base_url"' "$CONFIG_FILE"; then
    echo "❌ 错误: memu-engine使用了base_url，应该是baseUrl"
    ERRORS=$((ERRORS+1))
fi

# 检查2: JSON格式
if ! python3 -c "import json; json.load(open('$CONFIG_FILE'))" 2>/dev/null; then
    echo "❌ 错误: JSON格式无效"
    ERRORS=$((ERRORS+1))
fi

# 检查3: 检查memu-engine配置（如果存在）
if grep -q '"memu-engine"' "$CONFIG_FILE"; then
    if grep -A 10 '"memu-engine"' "$CONFIG_FILE" | grep -q '"provider": "openai-compatible"'; then
        echo "⚠️ 警告: provider应该是openai，不是openai-compatible"
        ERRORS=$((ERRORS+1))
    fi
fi

# 检查4: API Key格式（检查主要provider的API Key）
echo "🔍 检查主要provider的API Key格式..."

# 检查glmcode
if grep -A 3 '"glmcode"' "$CONFIG_FILE" | grep -q '"apiKey": "sk-'; then
    echo "✅ glmcode API Key格式正确"
elif grep -A 3 '"glmcode"' "$CONFIG_FILE" | grep -q '"apiKey"'; then
    echo "✅ glmcode API Key存在"
else
    echo "⚠️ 警告: glmcode API Key未找到"
fi

# 检查nvidia-gpt-oss
if grep -A 3 '"nvidia-gpt-oss"' "$CONFIG_FILE" | grep -q '"apiKey": "nvapi-'; then
    echo "✅ nvidia API Key格式正确"
elif grep -A 3 '"nvidia-gpt-oss"' "$CONFIG_FILE" | grep -q '"apiKey"'; then
    echo "✅ nvidia API Key存在"
else
    echo "⚠️ 警告: nvidia API Key未找到"
fi

# 检查groq
if grep -A 3 '"groq"' "$CONFIG_FILE" | grep -q '"apiKey": "gsk_'; then
    echo "✅ groq API Key格式正确"
elif grep -A 3 '"groq"' "$CONFIG_FILE" | grep -q '"apiKey"'; then
    echo "✅ groq API Key存在"
else
    echo "⚠️ 警告: groq API Key未找到"
fi

# 检查google
if grep -A 3 '"google"' "$CONFIG_FILE" | grep -q '"apiKey": "AIza'; then
    echo "✅ google API Key格式正确"
elif grep -A 3 '"google"' "$CONFIG_FILE" | grep -q '"apiKey"'; then
    echo "✅ google API Key存在"
else
    echo "⚠️ 警告: google API Key未找到"
fi

if [ $ERRORS -eq 0 ]; then
    echo "✅ L7验证通过"
    exit 0
else
    echo "❌ L7发现 $ERRORS 个问题"
    exit 1
fi
