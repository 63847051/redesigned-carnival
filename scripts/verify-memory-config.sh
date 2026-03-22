#!/bin/bash
# Memory Core 配置验证脚本
# 用途：验证 memorySearch 配置是否正确

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 文件路径
MAIN_CONFIG="/root/.openclaw/openclaw.json"

echo -e "${GREEN}=== Memory Core 配置验证 ===${NC}"
echo ""

# 检查配置文件
if [ ! -f "$MAIN_CONFIG" ]; then
    echo -e "${RED}❌ 错误: 配置文件不存在${NC}"
    exit 1
fi

# 检查 memorySearch 配置
echo -e "${YELLOW}🔍 检查 memorySearch 配置...${NC}"
if grep -q '"memorySearch"' "$MAIN_CONFIG"; then
    echo -e "${GREEN}✅ memorySearch 配置存在${NC}"
else
    echo -e "${RED}❌ memorySearch 配置不存在${NC}"
    echo ""
    echo "请运行配置合并脚本:"
    echo "  bash /root/.openclaw/workspace/scripts/merge-memory-config.sh"
    exit 1
fi

# 提取并显示配置
echo ""
echo -e "${YELLOW}📊 当前配置:${NC}"
python3 << EOF
import json

with open('$MAIN_CONFIG', 'r') as f:
    config = json.load(f)

memory_search = config['agents']['defaults'].get('memorySearch', {})

if not memory_search:
    print("❌ memorySearch 配置为空")
    exit(1)

# 检查关键配置
print("✅ Provider:", memory_search.get('provider', '未配置'))
print("✅ Model:", memory_search.get('model', '未配置'))

# 检查混合检索
hybrid = memory_search.get('query', {}).get('hybrid', {})
if hybrid.get('enabled'):
    print("✅ 混合检索: 已启用")
    print("   - 语义权重:", hybrid.get('vectorWeight', 0))
    print("   - 关键词权重:", hybrid.get('textWeight', 0))
    print("   - 候选池大小:", hybrid.get('candidateMultiplier', 0))

    # MMR
    mmr = hybrid.get('mmr', {})
    if mmr.get('enabled'):
        print("✅ MMR 多样性重排: 已启用")
        print("   - Lambda:", mmr.get('lambda', 0))

    # 时间衰减
    decay = hybrid.get('temporalDecay', {})
    if decay.get('enabled'):
        print("✅ 时间衰减: 已启用")
        print("   - 半衰期:", decay.get('halfLifeDays', 0), "天")
else:
    print("⚠️  混合检索: 未启用")

# 批量处理和缓存
remote = memory_search.get('remote', {})
if remote.get('batch', {}).get('enabled'):
    print("✅ 批量 embedding: 已启用")

cache = memory_search.get('cache', {})
if cache.get('enabled'):
    print("✅ 缓存: 已启用")
    print("   - 最大条目:", cache.get('maxEntries', 0))

print()
print("🎉 配置看起来不错！")
EOF

echo ""
echo -e "${YELLOW}🔍 检查 Gateway 状态...${NC}"
if systemctl --user is-active --quiet openclaw-gateway; then
    echo -e "${GREEN}✅ Gateway 运行中${NC}"

    # 检查最近的日志
    echo ""
    echo -e "${YELLOW}📋 最近的日志（最后 10 行）:${NC}"
    journalctl --user -u openclaw-gateway --no-pager -n 10 | grep -i "memory\|embedding\|search" || echo "（无相关日志）"
else
    echo -e "${YELLOW}⚠️  Gateway 未运行${NC}"
    echo ""
    echo "启动 Gateway:"
    echo "  systemctl --user start openclaw-gateway"
fi

echo ""
echo -e "${GREEN}=== 验证完成 ===${NC}"
