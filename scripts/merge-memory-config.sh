#!/bin/bash
# Memory Core 配置合并脚本（支持 Groq 和 DashScope）
# 用途：将 memorySearch 配置合并到 openclaw.json

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 文件路径
MAIN_CONFIG="/root/.openclaw/openclaw.json"
MEMORY_CONFIG_GROQ="/root/.openclaw/openclaw-memory-config-groq.json"
MEMORY_CONFIG_DASHSCOPE="/root/.openclaw/openclaw-memory-config.json"
BACKUP_CONFIG="/root/.openclaw/openclaw.json.backup"

echo -e "${GREEN}=== Memory Core 配置合并脚本 ===${NC}"
echo ""

# 检查文件是否存在
if [ ! -f "$MAIN_CONFIG" ]; then
    echo -e "${RED}❌ 错误: 配置文件不存在 $MAIN_CONFIG${NC}"
    exit 1
fi

# 选择 provider
echo -e "${BLUE}📋 选择 Embedding Provider:${NC}"
echo ""
echo "1. Groq（免费，已配置）"
echo "2. DashScope（阿里云，需要 API Key）"
echo ""
read -p "请选择 [1-2]: " choice

case $choice in
    1)
        MEMORY_CONFIG="$MEMORY_CONFIG_GROQ"
        PROVIDER_NAME="Groq"
        ;;
    2)
        MEMORY_CONFIG="$MEMORY_CONFIG_DASHSCOPE"
        PROVIDER_NAME="DashScope"

        # 检查 API Key
        if [ -f "$MEMORY_CONFIG" ] && grep -q "YOUR_DASHSCOPE_API_KEY_HERE" "$MEMORY_CONFIG"; then
            echo -e "${RED}❌ 错误: 请先配置 DashScope API Key！${NC}"
            echo ""
            echo "请编辑 $MEMORY_CONFIG"
            echo "将 YOUR_DASHSCOPE_API_KEY_HERE 替换为你的真实 API Key"
            echo ""
            echo "获取 API Key: https://dashscope.console.aliyun.com/"
            exit 1
        fi
        ;;
    *)
        echo -e "${RED}❌ 无效选择${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${YELLOW}📦 使用 Provider: $PROVIDER_NAME${NC}"

# 检查配置文件是否存在
if [ ! -f "$MEMORY_CONFIG" ]; then
    echo -e "${RED}❌ 错误: 配置文件不存在 $MEMORY_CONFIG${NC}"
    exit 1
fi

# 备份原配置
echo -e "${YELLOW}📦 备份原配置...${NC}"
cp "$MAIN_CONFIG" "$BACKUP_CONFIG"
echo -e "${GREEN}✅ 备份完成: $BACKUP_CONFIG${NC}"
echo ""

# 读取 memorySearch 配置
echo -e "${YELLOW}🔧 合并配置...${NC}"
python3 << EOF
import json

# 读取主配置
with open('$MAIN_CONFIG', 'r') as f:
    main_config = json.load(f)

# 读取 memorySearch 配置
with open('$MEMORY_CONFIG', 'r') as f:
    memory_config = json.load(f)
    memory_search = memory_config['agents']['defaults'].get('memorySearch', {})

# 合并到 agents.defaults
if 'agents' not in main_config:
    main_config['agents'] = {}
if 'defaults' not in main_config['agents']:
    main_config['agents']['defaults'] = {}

main_config['agents']['defaults']['memorySearch'] = memory_search

# 写回主配置
with open('$MAIN_CONFIG', 'w') as f:
    json.dump(main_config, f, indent=2, ensure_ascii=False)

print("✅ 配置合并完成")
EOF

echo ""
echo -e "${GREEN}=== 配置合并成功！ ===${NC}"
echo ""
echo -e "${YELLOW}📝 下一步：${NC}"
echo "1. 检查配置: cat $MAIN_CONFIG | grep -A 30 memorySearch"
echo "2. 验证配置: bash /root/.openclaw/workspace/scripts/verify-memory-config.sh"
echo "3. 重启 Gateway: systemctl --user restart openclaw-gateway"
echo "4. 检查日志: journalctl --user -u openclaw-gateway -f"
echo ""
echo -e "${YELLOW}📦 备份位置: $BACKUP_CONFIG${NC}"
echo -e "${YELLOW}🔄 回滚方法: cp $BACKUP_CONFIG $MAIN_CONFIG${NC}"
