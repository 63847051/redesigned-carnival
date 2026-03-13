#!/bin/bash
# 添加工作日志记录
# 使用方法: ./add_worklog.sh "工作内容" "项目类型" "优先级别"

APP_TOKEN="BISAbNgYXa7Do1sc36YcBChInnS"
TABLE_ID="tbl5s8TEZ0tKhEm7"

CONTENT="${1:-默认工作内容}"
TYPE="${2:-现场}"
PRIORITY="${3:-普通重要}"
TODAY=$(date +%s)000  # 转换为毫秒时间戳

echo "添加工作日志:"
echo "  内容: $CONTENT"
echo "  类型: $TYPE"
echo "  优先级: $PRIORITY"
echo "  日期: $(date +%Y/%m/%d)"

# 通过 OpenClaw 工具调用 (需在 OpenClaw 环境中执行)
# 这里只作为模板参考,实际使用时通过 feishu_bitable_create_record 工具
