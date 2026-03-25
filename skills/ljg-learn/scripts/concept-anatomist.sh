#!/bin/bash
# Concept Anatomist Helper Script
# Usage: ./concept-anatomist.sh <concept>

CONCEPT="$1"

if [ -z "$CONCEPT" ]; then
    echo "Usage: $0 <concept>"
    echo "Example: $0 熵"
    exit 1
fi

TIMESTAMP=$(date +%Y%m%dT%H%M%S)
DATE=$(date "+%Y-%m-%d %a %H:%M")
OUTPUT_DIR="/root/.openclaw/workspace/output"

mkdir -p "$OUTPUT_DIR"

OUTPUT_FILE="$OUTPUT_DIR/${TIMESTAMP}--概念解剖-${CONCEPT}__concept.org"

echo "Concept: $CONCEPT"
echo "Output: $OUTPUT_FILE"
echo "Timestamp: $TIMESTAMP"
echo "Date: $DATE"

cat > "$OUTPUT_FILE" << EOF
#+title: 概念解剖：${CONCEPT}
#+filetags: :concept:
#+date: [${DATE}]
#+identifier: ${TIMESTAMP}

* 定锚
** 通行定义：
** 常见误解：

* 八刀
** 历史：
** 辩证：
** 现象：
** 语言：
** 形式：
** 存在：
** 美感：
** 元反思：

* 内观

* 压缩
** 公式：
** 一句话：
** 结构图：

EOF

echo "✓ Template created at: $OUTPUT_FILE"
