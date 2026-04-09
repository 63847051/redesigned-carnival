#!/bin/bash
# 记忆新鲜度系统 v1.0 - 自然语言时间戳
# 基于 Claude Code 设计：模型不擅长日期计算，用自然语言触发陈旧性推理

set -e

echo "🕰 记忆新鲜度系统 v1.0 - 自然语言时间戳"
echo "⏰ 时间: $(date)"

# 配置
MEMORY_DIR="/root/.openclaw/workspace/memory"
TODAY_LOG=$(find "$MEMORY_DIR" -name "2026-$(date +%m-%d).md" -type f)

# =============================================================================
# 🕐 时间转换函数（核心逻辑）
# =============================================================================

age_to_natural_language() {
    local memory_timestamp=$1
    local current_time=$(date +%s)
    
    # 计算时间差（秒）
    local age_seconds=$((current_time - memory_timestamp))
    local age_days=$((age_seconds / 86400))
    
    # 根据时间差返回自然语言
    if [ $age_seconds -lt 60 ]; then
        echo "刚刚"
    elif [ $age_days -eq 0 ]; then
        echo "今天"
    elif [ $age_days -eq 1 ]; then
        echo "昨天"
    elif [ $age_days -lt 7 ]; then
        echo "$age_days 天前"
    elif [ $age_days -lt 30 ]; then
        echo "$(date -d "@$memory_timestamp" +"%Y-%m-%d" +%Y-%m-%d)"
    else
        echo "$(date -d "@$memory_timestamp" +"%Y年%m月%d日" +%Y年%m月%d日)"
    fi
}

# =============================================================================
# 📊 测试函数
# =============================================================================

test_age_conversion() {
    echo ""
    echo "🧪 测试时间转换函数..."
    
    # 测试：刚刚
    local just_now=$(date +%s)
    echo "📌 刚刚: $(age_to_natural_language $just_now)"
    
    # 测试：今天
    local today=$(date -d "today 00:00:00" +%s)
    echo "📌 今天: $(age_to_natural_language $today)"
    
    # 测试：昨天
    local yesterday=$(date -d "yesterday 00:00:00" +%s)
    echo "📌 昨天: $(age_to_natural_language $yesterday)"
    
    # 测试：5天前
    local days_5=$(date -d "5 days ago 00:00:00" +%s)
    echo "📌 5天前: $(age_to_natural_language $days_5)"
    
    # 测试：超过30天
    local long_ago=$(date -d "60 days ago 00:00:00" +%s)
    echo "📌 60天前: $(age_to_natural_language $long_ago)"
}

# =============================================================================
# 🎯 应用到记忆文件
# =============================================================================

apply_to_memory_files() {
    echo ""
    echo "🎯 应用到记忆文件..."
    
    # 扫到所有记忆文件
    for memory_file in $(find "$MEMORY_DIR" -name "*.md" ! -path "*/backups/*" ! -path "*/archive/*"); do
        # 提取记忆中的时间戳
        memory_timestamp=$(grep -o '"created_at": "[0-9]*' "$memory_file" 2>/dev/null | head -1)
        
        if [ -n "$memory_timestamp" ]; then
            # 转换为自然语言
            natural_age=$(age_to_natural_language $memory_timestamp)
            
            # 在记忆文件中添加新鲜度标注
            echo "📝 处理: $memory_file"
            
            # 在文件末尾添加新鲜度标注
            cat >> "$memory_file" << FRESH

---

**记忆新鲜度**: $natural_age

> ⚠️ 注意：记忆是时间快照，不是实时状态。引用之前请先验证。

FRESH
        fi
    done
    
    echo "✅ 已更新所有记忆文件的新鲜度标注"
}

# =============================================================================
# 🚀 主流程
# =============================================================================

main() {
    echo ""
    echo "🚀 记忆新鲜度系统启动..."
    
    # 测试时间转换
    # test_age_conversion
    
    # 应用到记忆文件
    apply_to_memory_files
    
    echo ""
    echo "🎉 记忆新鲜度系统 v1.0 完成！"
}

# 执行主流程
main
