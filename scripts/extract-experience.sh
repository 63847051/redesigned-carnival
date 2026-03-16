#!/bin/bash
# 自动化经验提取脚本
# 作者: 大领导系统 v5.16.0
# 日期: 2026-03-16
#
# 用法: ./extract-experience.sh "任务描述" "成功/失败" "原因" "改进建议"
#
# 示例: ./extract-experience.sh "配置验证" "成功" "使用了 validate-config.sh" "继续保持"

set -e

TASK=$1
STATUS=$2
REASON=$3
SUGGESTION=$4
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)

if [ -z "$TASK" ] || [ -z "$STATUS" ]; then
    echo "❌ 错误: 缺少参数"
    echo "用法: $0 \"任务描述\" \"成功/失败\" \"原因\" \"改进建议\""
    echo ""
    echo "示例:"
    echo "  $0 \"配置验证\" \"成功\" \"使用了 validate-config.sh\" \"继续保持\""
    echo "  $0 \"Gateway 配置\" \"失败\" \"添加了不支持的字段\" \"先验证字段\""
    exit 1
fi

echo "🧠 提取经验..."
echo "任务: $TASK"
echo "状态: $STATUS"
echo "原因: $REASON"
echo "建议: $SUGGESTION"
echo ""

MEMORY_FILE="/root/.openclaw/workspace/memory/2026-03-16.md"

# 根据状态决定记录位置
if [ "$STATUS" = "成功" ]; then
    # 成功经验 → 记录到最佳实践
    cat >> "$MEMORY_FILE" << EOF

### ✅ 成功经验: $TASK
**时间**: $DATE $TIME
**原因**: $REASON
**结果**: 成功完成

**可复用的模式**:
- ✅ 任务描述: $TASK
- ✅ 使用方法: $REASON
- ✅ 成功要素: $SUGGESTION

**经验提炼**:
- 记录成功的模式和要素
- 总结可复用的方法
- 更新到最佳实践

EOF
    echo "✅ 成功经验已记录到: $MEMORY_FILE"
    
elif [ "$STATUS" = "失败" ]; then
    # 失败教训 → 记录到错误教训
    cat >> "$MEMORY_FILE" << EOF

### ❌ 失败教训: $TASK
**时间**: $DATE $TIME
**原因**: $REASON
**结果**: 失败

**问题分析**:
- ❌ 任务描述: $TASK
- ❌ 失败原因: $REASON
- ❌ 关键错误: $SUGGESTION

**改进建议**:
1. 立即修复: $SUGGESTION
2. 预防措施: 建立检查机制
3. 经验总结: 更新到设计模式

**行动项**:
- [ ] 修复问题
- [ ] 更新文档
- [ ] 建立检查清单

EOF
    echo "✅ 失败教训已记录到: $MEMORY_FILE"
    
    # 提示创建设计模式
    echo ""
    echo "💡 建议: 从这次失败中提取设计模式？"
    echo "   创建新的设计模式: .learnings/design-patterns/DP-XXX.md"
    
else
    echo "❌ 错误: 状态必须是 '成功' 或 '失败'"
    exit 1
fi

# 更新统计
echo ""
echo "📊 经验统计:"
echo "   今日成功: $(grep -c "✅ 成功经验" "$MEMORY_FILE" 2>/dev/null || echo 0) 次"
echo "   今日失败: $(grep -c "❌ 失败教训" "$MEMORY_FILE" 2>/dev/null || echo 0) 次"
echo ""

echo "================================"
echo "✅ 经验提取完成！"
echo ""
echo "📋 下一步:"
if [ "$STATUS" = "成功" ]; then
    echo "   1. 提炼可复用的模式"
    echo "   2. 更新到 best-practices/"
    echo "   3. 分享给团队"
else
    echo "   1. 分析失败根因"
    echo "   2. 创建设计模式"
    echo "   3. 建立检查清单"
fi
