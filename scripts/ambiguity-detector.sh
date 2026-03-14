#!/bin/bash
# ambiguity-detector.sh - 歧义检测脚本
# Token 成本: ~50 tokens (输出)
# 用途: 自动检测用户指令是否有歧义

USER_MESSAGE="$1"

# 疑问词列表（精简版）
QUESTION_WORDS=("吗" "?" "怎么" "如何" "什么" "哪个" "是否" "能不能" "可不可以")

# 检测疑问词
for word in "${QUESTION_WORDS[@]}"; do
    if [[ "$USER_MESSAGE" == *"$word"* ]]; then
        echo "⚠️ 检测到疑问句"
        echo "❓ 用户在询问，不是指令"
        echo "请回复问题，不要执行操作"
        exit 1  # 有歧义
    fi
done

# 检测不完整指令（如只有"方案 C"，没有"执行"）
if [[ "$USER_MESSAGE" =~ ^方案[[:space:]][ABC]$ ]]; then
    echo "⚠️ 检测到不完整指令"
    echo "❓ 用户选择了方案，但没有确认执行"
    echo "请询问：是否执行方案 X？"
    exit 1  # 有歧义
fi

echo "✅ 无歧义"
exit 0  # 无歧义
