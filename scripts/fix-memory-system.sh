#!/bin/bash
# 修复记忆系统

echo "=== 记忆系统诊断和修复 ==="
echo ""

# 1. 检查 QMD Memory Search
echo "1. 检查 QMD Memory Search..."
if command -v qmd-search &> /dev/null; then
    echo "   ✅ QMD 已安装"
    qmd-search "测试" | head -3
else
    echo "   ❌ QMD 未安装"
fi

# 2. 检查记忆文件
echo ""
echo "2. 检查记忆文件..."
ls -lh /root/.openclaw/workspace/memory/*.md | tail -7

# 3. 检查向量搜索配置
echo ""
echo "3. 检查 OpenAI API Key..."
if [ -f /root/.openclaw/credentials/openai-key.txt ]; then
    echo "   ✅ OpenAI Key 文件存在"
else
    echo "   ❌ OpenAI Key 文件不存在"
    echo "   需要配置 OpenAI API Key 用于向量搜索"
fi

# 4. 创建今天的记忆文件
TODAY=$(date +%Y-%m-%d)
echo ""
echo "4. 创建今日记忆文件：memory/$TODAY.md"
if [ ! -f "/root/.openclaw/workspace/memory/$TODAY.md" ]; then
    cat > "/root/.openclaw/workspace/memory/$TODAY.md" << MD
# 日记 - $TODAY

## 记忆系统修复

**问题**：
- 向量搜索失效（OpenAI API Key 401 错误）
- 每次对话只加载当天和昨天的文件
- 会话历史不永久保存

**解决方案**：
- 使用 QMD Memory Search（基于 Groq API，免费）
- 每次对话前使用 qmd-search 搜索相关记忆
- 定期整理重要信息到 MEMORY.md

---

MD
    echo "   ✅ 已创建"
else
    echo "   ℹ️  文件已存在"
fi

echo ""
echo "=== 修复完成 ==="
echo ""
echo "建议："
echo "1. 使用 qmd-search 搜索记忆（不用 OpenAI）"
echo "2. 每次对话前先搜索相关历史"
echo "3. 重要信息及时更新到 MEMORY.md"
