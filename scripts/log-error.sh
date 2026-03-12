#!/bin/bash
# 自动记录错误脚本
# 用法: ./log-error.sh "错误名称" "错误描述"

set -e

ERROR_NAME=$1
ERROR_DESC=$2

# 创建错误目录
mkdir -p .learnings/errors

# 记录错误
cat > .learnings/errors/$(date +%Y%m%d)-${ERROR_NAME}.md << EOF
# ${ERROR_NAME}

## 时间
$(date '+%Y-%m-%d %H:%M:%S')

## 错误描述
${ERROR_DESC}

## 根本原因

## 改进措施

## 验证

EOF

echo "✅ 错误已记录: ${ERROR_NAME}"
echo "📁 位置: .learnings/errors/$(date +%Y%m%d)-${ERROR_NAME}.md"
