#!/bin/bash
# 升级兼容性检查脚本
# 升级前必须执行，防止配置错误导致崩溃

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

CONFIG_FILE="/root/.openclaw/openclaw.json"

echo -e "${YELLOW}🔍 升级兼容性检查${NC}"
echo ""

# 检查 1: JSON 格式有效性
echo -e "${YELLOW}检查 1/3: JSON 格式有效性...${NC}"
if python3 -c "import json; json.load(open('$CONFIG_FILE'))" 2>/dev/null; then
    echo -e "${GREEN}✓ JSON 格式有效${NC}"
else
    echo -e "${RED}❌ JSON 格式错误${NC}"
    echo "请先修复配置文件："
    echo "  python3 -m json.tool $CONFIG_FILE"
    exit 1
fi
echo ""

# 检查 2: skills.load.paths 格式
echo -e "${YELLOW}检查 2/3: skills.load.paths 格式...${NC}"
if grep -q '"skills".*"load".*"paths"' "$CONFIG_FILE" 2>/dev/null; then
    echo -e "${GREEN}✓ skills.load.paths 配置存在${NC}"

    # 检查是否是数组格式
    if python3 -c "import json; config=json.load(open('$CONFIG_FILE')); isinstance(config.get('skills',{}).get('load',{}).get('paths',[]), list)" 2>/dev/null; then
        echo -e "${GREEN}✓ paths 格式正确（数组）${NC}"
    else
        echo -e "${RED}❌ paths 格式错误（应为数组）${NC}"
        echo "示例格式："
        echo '  "skills": {'
        echo '    "load": {'
        echo '      "paths": ["/path/to/skills"]'
        echo '    }'
        echo '  }'
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️ 未找到 skills.load.paths 配置（可能不需要）${NC}"
fi
echo ""

# 检查 3: gateway.controlUi.allowedOrigins 配置
echo -e "${YELLOW}检查 3/3: gateway.controlUi.allowedOrigins...${NC}"
if grep -q '"controlUi".*"allowedOrigins"' "$CONFIG_FILE" 2>/dev/null; then
    echo -e "${GREEN}✓ controlUi.allowedOrigins 配置存在${NC}"

    # 检查是否是数组格式
    if python3 -c "import json; config=json.load(open('$CONFIG_FILE')); isinstance(config.get('gateway',{}).get('controlUi',{}).get('allowedOrigins',[]), list)" 2>/dev/null; then
        echo -e "${GREEN}✓ allowedOrigins 格式正确（数组）${NC}"

        # 显示当前配置
        echo ""
        echo -e "${YELLOW}当前配置:${NC}"
        python3 -c "import json; config=json.load(open('$CONFIG_FILE')); print('\n'.join(config.get('gateway',{}).get('controlUi',{}).get('allowedOrigins',[])))" 2>/dev/null || echo "无法读取"
    else
        echo -e "${RED}❌ allowedOrigins 格式错误（应为数组）${NC}"
        echo "示例格式："
        echo '  "gateway": {'
        echo '    "controlUi": {'
        echo '      "allowedOrigins": ["http://localhost:18789"]'
        echo '    }'
        echo '  }'
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️ 未找到 controlUi.allowedOrigins 配置${NC}"
fi
echo ""

# 检查 4: 飞书配对文件
echo -e "${YELLOW}额外检查: 飞书配对文件...${NC}"
if [ -f "/root/.openclaw/credentials/feishu-pairing.json" ]; then
    echo -e "${GREEN}✓ 飞书配对文件存在${NC}"
else
    echo -e "${RED}❌ 飞书配对文件丢失${NC}"
    echo "⚠️ 升级后需要重新配对飞书"
fi
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ 兼容性检查通过！可以安全升级${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "下一步："
echo "  1. 备份配置: bash /root/.openclaw/workspace/scripts/backup-before-update.sh"
echo "  2. 执行升级: npm install -g openclaw"
echo ""
