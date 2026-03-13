#!/bin/bash
# =============================================================================
# PAI 完整工作流集成脚本
# =============================================================================
# 功能：一键运行所有 PAI 系统组件
# 使用：通过心跳或手动调用
# =============================================================================

PAI_DIR="/root/.openclaw/workspace/.pai-learning"
SCRIPT_DIR="/root/.openclaw/workspace/scripts"
TODAY=$(date +%Y-%m-%d)

echo "🚀 PAI 完整工作流"
echo "======================================"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# =============================================================================
# 步骤 1: 分层记忆
# =============================================================================

echo "📊 步骤 1: 分层学习信号..."

SIGNAL_FILE="$PAI_DIR/signals/$TODAY-signals.jsonl"
if [ -f "$SIGNAL_FILE" ]; then
    bash "$SCRIPT_DIR/pai-memory-manager.sh" layer "$SIGNAL_FILE"
else
    echo "⚠️  今日无学习信号，跳过分层"
fi

echo ""

# =============================================================================
# 步骤 2: 生成分析报告
# =============================================================================

echo "🔬 步骤 2: 生成分析报告..."

if [ -f "$PAI_DIR/hot-memory.jsonl" ]; then
    bash "$SCRIPT_DIR/pai-analyzer-v2.sh" all
else
    echo "⚠️  Hot Memory 为空，跳过分析"
fi

echo ""

# =============================================================================
# 步骤 3: 智能建议 + 集成超级进化大脑
# =============================================================================

echo "💡 步骤 3: 智能建议 + 集成..."

if [ -f "$PAI_DIR/hot-memory.jsonl" ]; then
    # 先生成智能建议
    bash "$SCRIPT_DIR/pai-advisor-v2.sh" all
    
    echo ""
    echo "🔄 集成超级进化大脑..."
    
    # 检查成功率
    local total=$(wc -l < "$PAI_DIR/hot-memory.jsonl")
    local success=$(jq -r 'select(.success == 1) .success' "$PAI_DIR/hot-memory.jsonl" | wc -l)
    local rate=$(awk "BEGIN {printf \"%.1f\", ($success/$total)*100}")

    echo "   成功率: $rate%"
    
    # 如果成功率低于 80%，调用超级进化大脑
    if awk "BEGIN {exit !($rate < 80)}"; then
        echo "   ⚠️  成功率低于 80%，调用超级进化大脑..."
        
        # 调用超级进化大脑进行进化分析
        if [ -f "$SCRIPT_DIR/pai-integration.sh" ]; then
            bash "$SCRIPT_DIR/pai-integration.sh" evolve "低成功率分析" "成功率: $rate%, 需要优化"
        fi
    else
        echo "   ✅ 成功率良好，继续正常工作"
    fi
    
    # 检查内存使用
    local mem_usage=$(free | awk '/Mem/{printf "%.1f", $3/$2*100}')
    echo "   内存: $mem_usage%"
    
    # 如果内存使用高于 85%，调用超级进化大脑
    if awk "BEGIN {exit !($mem_usage > 85)}"; then
        echo "   ⚠️  内存使用过高，调用超级进化大脑..."
        
        # 调用超级进化大脑进行风险预警
        if [ -f "$SCRIPT_DIR/pai-integration.sh" ]; then
            bash "$SCRIPT_DIR/pai-integration.sh" risk "高风险" "内存使用: $mem_usage%, 需要优化"
        fi
    else
        echo "   ✅ 内存使用健康"
    fi
else
    echo "⚠️  Hot Memory 为空，跳过建议和集成"
fi

echo ""

# =============================================================================
# 步骤 4: 更新可视化仪表板
# =============================================================================

echo "📊 步骤 4: 更新可视化仪表板..."

bash "$SCRIPT_DIR/pai-dashboard-generator.sh"

echo ""

# =============================================================================
# 步骤 5: 显示记忆统计
# =============================================================================

echo "📊 步骤 5: 记忆统计..."

bash "$SCRIPT_DIR/pai-memory-manager.sh" stats

echo ""

# =============================================================================
# 步骤 6: 智能建议
# =============================================================================

echo "💡 步骤 6: 智能建议..."

bash "$SCRIPT_DIR/pai-memory-manager.sh" advice

echo ""
echo "======================================"
echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "🎉 PAI 完整工作流执行完毕！"
