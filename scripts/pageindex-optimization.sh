#!/bin/bash
# pageindex-rag 优化配置
# 加载配置并应用优化

WORKSPACE="/root/.openclaw/workspace"
source "$WORKSPACE/scripts/pageindex-config.sh"

echo "🔧 pageindex-rag 参数优化"
echo "======================================"
echo ""

echo "📊 当前配置:"
echo "  召回数量: $RECALL_COUNT"
echo "  返回数量: $FINAL_COUNT"
echo "  缓存时间: ${CACHE_TTL}秒"
echo "  最低分数: $QMD_MIN_SCORE"
echo ""

echo "🎯 推荐配置:"
echo "  快速检索: RECALL_COUNT=5, FINAL_COUNT=3"
echo "  标准检索: RECALL_COUNT=10, FINAL_COUNT=5"
echo "  深度检索: RECALL_COUNT=20, FINAL_COUNT=10"
echo ""

echo "💡 使用建议:"
echo "  1. 日常使用: ./ms.sh \"查询\" 3"
echo "  2. 深度搜索: ./ms.sh \"查询\" 10"
echo "  3. 精确匹配: 在查询中使用关键词"
echo ""

echo "✅ 配置文件: scripts/pageindex-config.sh"
echo "📝 修改配置后需要重新加载 source 命令"
