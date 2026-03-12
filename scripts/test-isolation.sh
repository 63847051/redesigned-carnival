#!/bin/bash
# 测试 Skill 隔离规则系统
# 创建时间: 2026-03-04

echo "========================================"
echo "🧪 测试 Skill 隔离规则系统"
echo "========================================"
echo ""

# 测试用例
test_cases=(
    "设计:3F男女更衣室怎么排砖？"
    "技术:写个Python脚本抓取数据"
    "日志:记录一下，今天完成了会议室设计"
    "设计越界:写个爬虫抓取设计网站"  # 应该检测到越界
    "技术越界:这个会议室怎么设计"    # 应该检测到越界
)

echo "📋 测试用例："
for i in "${!test_cases[@]}"; do
    IFS=':' read -r type message <<< "${test_cases[$i]}"
    echo "  $((i+1)). [$type] $message"
done

echo ""
echo "✅ 测试准备完成"
echo ""
echo "🎯 下一步：在主控 Agent 中测试隔离规则"
echo ""
echo "📝 预期结果："
echo "  - 设计任务 → 设计专家处理"
echo "  - 技术任务 → 技术专家处理"
echo "  - 日志任务 → 小蓝处理"
echo "  - 越界任务 → 检测并转发给主控"
echo ""
