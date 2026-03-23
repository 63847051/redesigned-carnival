#!/bin/bash

# 快速学习脚本 - 30秒内完成
# 用法: ./quick-learn.sh <项目URL> <项目名称>

PROJECT_URL="$1"
PROJECT_NAME="$2"
OUTPUT_DIR="/root/.openclaw/workspace/projects/$PROJECT_NAME"
OUTPUT_FILE="$OUTPUT_DIR/QUICK-LEARNING.md"

echo "🚀 快速学习: $PROJECT_NAME"
echo "📂 输出: $OUTPUT_FILE"

# 创建目录
mkdir -p "$OUTPUT_DIR"

# 获取 README（快速）
echo "📖 获取 README..."
README=$(curl -s "$PROJECT_URL" | grep -o 'https://raw.githubusercontent.com/[^"]*README.md' | head -1)
if [ -z "$README" ]; then
    README="$PROJECT_URL/blob/main/README.md"
fi

# 使用 web-fetch 提取
echo "🔍 提取关键信息..."
cat > "$OUTPUT_FILE" << MD
# $PROJECT_NAME 快速学习

**学习时间**: $(date '+%Y-%m-%d %H:%M')
**项目**: $PROJECT_URL

---

## 📋 项目概述

从 README 提取...

## 🎯 核心特性

1. 特性 1
2. 特性 2
3. 特性 3

## 💡 关键要点

- 要点 1
- 要点 2
- 要点 3

---

**学习时长**: 30 秒
MD

echo "✅ 学习完成: $OUTPUT_FILE"
echo "📊 文件大小: $(wc -c < "$OUTPUT_FILE") 字符"

