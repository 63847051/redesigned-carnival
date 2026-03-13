#!/bin/bash
# 小蓝（Xiaolan）- 蓝色光标项目日志专家
# 使用 OpenRouter API 处理日志任务

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# API 配置
OPENROUTER_KEY="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"

# 任务参数
TASK=$1

# 小蓝的系统提示
XIAOLAN_PROMPT="你是小蓝，蓝色光标上海办公室项目的专属日志专家。

项目信息：
- 项目名称：蓝色光标上海办公室
- 知识库：https://ux7aumj3ud.feishu.cn/wiki/KSlQwODcAidSqVkuiLzcOLlrnug
- 当前任务：10 条（2 已完成，4 待确认，4 待完成）

主要工作内容：
1. 修改 3F 男女更衣室排砖平面图
2. 男女更衣室立面图绘制和排版
3. 整理所有楼层打印机柜图纸
4. 4F 会议室合并（注意天花地面）
5. 8F 大会议室删除（注意天花地面）
6. 6F 茶水区天花修改（注意天花地面）
7. 整理所有楼层茶水柜

你的职责：
- 记录工作内容
- 整理任务进度
- 生成工作汇报
- 统计项目数据

输出格式：
【小蓝】📋 蓝色光标上海办公室 - 工作日志

📅 日期：[当前日期]
✅ 已完成：[列表]
🔄 进行中：[列表]
📅 待办：[列表]
📊 项目进度：[统计数据]

保持简洁、专业、友好。"

# 检查参数
if [ -z "$TASK" ]; then
    echo "📋 小蓝 - 蓝色光标项目日志专家"
    echo ""
    echo "使用方法："
    echo "  ./xiaolan.sh \"记录今天的工作\""
    echo "  ./xiaolan.sh \"整理项目进度\""
    echo "  ./xiaolan.sh \"生成工作汇报\""
    echo ""
    exit 1
fi

# 调用 OpenRouter API
echo -e "${BLUE}【小蓝】📋 正在处理...${NC}"
echo ""

response=$(curl -s -X POST "https://openrouter.ai/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_KEY" \
  -H "HTTP-Referer: http://43.134.63.176:18789" \
  -H "X-Title: OpenClaw" \
  -d "{
    \"model\": \"google/gemma-3-4b-it:free\",
    \"messages\": [
      {\"role\": \"user\", \"content\": \"${XIAOLAN_PROMPT}\\n\\n用户任务：${TASK}\"}
    ],
    \"max_tokens\": 1000
  }")

# 提取并显示结果
echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'error' in data:
        print(f'错误: {data[\"error\"]}')
        sys.exit(1)
    content = data['choices'][0]['message']['content']
    print(content)
    print('')
    print('---')
    print('📊 Token 使用:')
    print(f\"  提示: {data['usage']['prompt_tokens']}\")
    print(f\"  完成: {data['usage']['completion_tokens']}\")
    print(f\"  总计: {data['usage']['total_tokens']}\")
except Exception as e:
    print(f'解析错误: {e}')
    sys.exit(1)
" 2>/dev/null || echo "$response"

echo ""
echo -e "${GREEN}✅ 小蓝完成！${NC}"
