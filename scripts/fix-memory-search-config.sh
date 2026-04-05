#!/bin/bash
# =============================================================================
# 修复记忆搜索配置
# =============================================================================
# 问题: memorySearch.provider 设置为 "openai"，但使用的是 Groq API
#       Groq 不支持 embedding 模型，导致记忆搜索失败
# 解决: 改用智谱 AI 的免费 embeddings 服务（embedding-2，1024维）
# =============================================================================

set -euo pipefail

CONFIG_FILE="${HOME}/.openclaw/openclaw.json"
BACKUP_FILE="${HOME}/.openclaw/openclaw.json.backup"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}修复记忆搜索配置${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. 备份原配置
echo -e "${YELLOW}步骤 1: 备份原配置...${NC}"
if [ ! -f "$BACKUP_FILE" ]; then
    cp "$CONFIG_FILE" "$BACKUP_FILE"
    echo -e "${GREEN}✅ 备份完成: $BACKUP_FILE${NC}"
else
    echo -e "${YELLOW}⚠️  备份文件已存在，跳过备份${NC}"
fi
echo ""

# 2. 使用 Python 修改配置
echo -e "${YELLOW}步骤 2: 修改配置...${NC}"
python3 << 'PYTHON_SCRIPT'
import json

config_file = "/root/.openclaw/openclaw.json"

# 读取配置
with open(config_file, 'r') as f:
    config = json.load(f)

# 修改 memorySearch 配置
memory_search = config['agents']['defaults']['memorySearch']

# 修改为使用 glmcode provider（智谱 AI）
memory_search['provider'] = 'glmcode'
memory_search['remote'] = {
    'baseUrl': 'https://open.bigmodel.cn/api/paas/v4/embeddings',
    'apiKey': 'c26c6bd6acfc44cda167b15dc338dabc.Hmfe3HhV5TjJiXqp'
}
memory_search['model'] = 'embedding-2'

# 保存配置
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print("✅ 配置已修改")
print("  - provider: openai → glmcode")
print("  - baseUrl: Groq → 智谱 AI")
print("  - model: text-embedding-3-small → embedding-2")
PYTHON_SCRIPT

echo ""

# 3. 验证配置
echo -e "${YELLOW}步骤 3: 验证配置...${NC}"
python3 << 'PYTHON_SCRIPT'
import json

config_file = "/root/.openclaw/openclaw.json"

with open(config_file, 'r') as f:
    config = json.load(f)

memory_search = config['agents']['defaults']['memorySearch']

print("当前配置:")
print(f"  Provider: {memory_search['provider']}")
print(f"  Base URL: {memory_search['remote']['baseUrl']}")
print(f"  Model: {memory_search['model']}")
print(f"  API Key: {memory_search['remote']['apiKey'][:20]}...")
PYTHON_SCRIPT

echo ""

# 4. 测试 embeddings API
echo -e "${YELLOW}步骤 4: 测试 embeddings API...${NC}"
response=$(curl -s "https://open.bigmodel.cn/api/paas/v4/embeddings" \
  -H "Authorization: Bearer c26c6bd6acfc44cda167b15dc338dabc.Hmfe3HhV5TjJiXqp" \
  -H "Content-Type: application/json" \
  -d '{"model":"embedding-2","input":"测试"}')

if echo "$response" | python3 -c "import json, sys; json.load(sys.stdin)" 2>/dev/null; then
    dimensions=$(echo "$response" | python3 -c "import json, sys; print(len(json.load(sys.stdin)['data'][0]['embedding']))")
    echo -e "${GREEN}✅ Embeddings API 可用（${dimensions} 维）${NC}"
else
    echo -e "${RED}❌ Embeddings API 测试失败${NC}"
    echo "$response"
    exit 1
fi

echo ""

# 5. 重启 Gateway
echo -e "${YELLOW}步骤 5: 重启 Gateway...${NC}"
if systemctl --user is-active --quiet openclaw-gateway; then
    echo "重启 Gateway 以加载新配置..."
    systemctl --user restart openclaw-gateway
    sleep 3
    if systemctl --user is-active --quiet openclaw-gateway; then
        echo -e "${GREEN}✅ Gateway 重启成功${NC}"
    else
        echo -e "${RED}❌ Gateway 重启失败${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Gateway 未运行，跳过重启${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 记忆搜索配置修复完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "修改内容:"
echo "  1. Provider: openai → glmcode（智谱 AI）"
echo "  2. Base URL: Groq → 智谱 AI"
echo "  3. Model: text-embedding-3-small → embedding-2"
echo "  4. Embeddings: 不支持 → 1024维（免费）"
echo ""
echo "测试记忆搜索:"
echo "  memory_search \"方向1 团队共享机制\""
