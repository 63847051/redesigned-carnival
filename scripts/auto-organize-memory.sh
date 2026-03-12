#!/bin/bash
# 自组织记忆系统
# 基于ivangdavila/self-improving的自组织记忆思想

set -e

WORKSPACE="/root/.openclaw/workspace"
LEARNINGS_DIR="$WORKSPACE/.learnings"
AUTO_ORG_DIR="$LEARNINGS_DIR/auto-organized"

# 创建目录结构
mkdir -p "$AUTO_ORG_DIR"/{by-topic,by-severity/{high,medium,low},by-frequency}

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$WORKSPACE/.evolution/evolution.log"
}

# ============================================================================
# 功能1: 按主题分类
# =============================================================================

classify_by_topic() {
    log "📁 按主题分类记忆..."

    local topics=("配置管理" "错误处理" "文件管理" "API集成" "工作流程" "最佳实践")

    # 扫描所有学习文件
    for learn_file in "$LEARNINGS_DIR"/*.md; do
        if [ -f "$learn_file" ]; then
            filename=$(basename "$learn_file")

            # 简化分类：根据文件名关键词
            if [[ "$filename" =~ (config|配置) ]]; then
                topic="配置管理"
            elif [[ "$filename" =~ (error|错误) ]]; then
                topic="错误处理"
            elif [[ "$filename" =~ (file|文件) ]]; then
                topic="文件管理"
            elif [[ "$filename" =~ (api|API) ]]; then
                topic="API集成"
            elif [[ "$filename" =~ (workflow|流程) ]]; then
                topic="工作流程"
            else
                topic="最佳实践"
            fi

            # 创建符号链接
            ln -sf "$learn_file" "$AUTO_ORG_DIR/by-topic/$topic/$filename" 2>/dev/null || true
        fi
    done

    log "主题分类完成"
}

# ============================================================================
# 功能2: 按严重程度分类
# =============================================================================

classify_by_severity() {
    log "📊 按严重程度分类..."

    # 扫描错误文件
    for error_file in "$LEARNINGS_DIR/errors"/error_*.md; do
        if [ -f "$error_file" ]; then
            # 统计错误数量
            error_count=$(grep -c "❌\|错误\|failed" "$error_file" 2>/dev/null || echo 0)

            # 根据错误数量分类
            if [ "$error_count" -ge 10 ]; then
                severity="high"
            elif [ "$error_count" -ge 5 ]; then
                severity="medium"
            else
                severity="low"
            fi

            # 创建符号链接
            filename=$(basename "$error_file")
            ln -sf "$error_file" "$AUTO_ORG_DIR/by-severity/$severity/$filename" 2>/dev/null || true
        fi
    done

    log "严重程度分类完成"
}

# ============================================================================
# 功能3: 按频率排序
# =============================================================================

sort_by_frequency() {
    log "🔄 按频率排序记忆..."

    # 统计文件访问/修改频率
    for learn_file in "$LEARNINGS_DIR"/*.md; do
        if [ -f "$learn_file" ]; then
            filename=$(basename "$learn_file")

            # 获取修改次数（简化：使用文件修改时间）
            mtime=$(stat -c %Y "$learn_file" 2>/dev/null || stat -f %m "$learn_file")

            # 按时间分类（最近7天=高频，30天=中频，其他=低频）
            now=$(date +%s)
            days_old=$(( (now - mtime) / 86400 ))

            if [ $days_old -lt 7 ]; then
                freq="high"
            elif [ $days_old -lt 30 ]; then
                freq="medium"
            else
                freq="low"
            fi

            mkdir -p "$AUTO_ORG_DIR/by-frequency/$freq"
            ln -sf "$learn_file" "$AUTO_ORG_DIR/by-frequency/$freq/$filename" 2>/dev/null || true
        fi
    done

    log "频率排序完成"
}

# ============================================================================
# 功能4: 生成记忆索引
# =============================================================================

generate_memory_index() {
    log "📝 生成记忆索引..."

    {
        echo "# 自组织记忆索引"
        echo ""
        echo "**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        echo "---"
        echo ""

        # 按主题统计
        echo "## 📁 按主题"
        echo ""
        for topic_dir in "$AUTO_ORG_DIR/by-topic"/*; do
            if [ -d "$topic_dir" ]; then
                topic=$(basename "$topic_dir")
                count=$(ls -1 "$topic_dir" 2>/dev/null | wc -l)
                echo "- **$topic**: $count 个文件"
            fi
        done
        echo ""

        # 按严重程度统计
        echo "## 📊 按严重程度"
        echo ""
        for severity in high medium low; do
            count=$(ls -1 "$AUTO_ORG_DIR/by-severity/$severity" 2>/dev/null | wc -l)
            echo "- **$severity**: $count 个文件"
        done
        echo ""

        # 按频率统计
        echo "## 🔄 按访问频率"
        echo ""
        for freq in high medium low; do
            count=$(ls -1 "$AUTO_ORG_DIR/by-frequency/$freq" 2>/dev/null | wc -l)
            case $freq in
                high) label="高频 (最近7天)" ;;
                medium) label="中频 (最近30天)" ;;
                low) label="低频 (30天前)" ;;
            esac
            echo "- **$label**: $count 个文件"
        done
        echo ""

        # 最新文件
        echo "## 📝 最新添加"
        echo ""
        ls -t "$LEARNINGS_DIR"/*.md 2>/dev/null | head -5 | while read file; do
            filename=$(basename "$file")
            mtime=$(stat -c %y "$file" 2>/dev/null | cut -d'.' -f1)
            echo "- $filename ($mtime)"
        done
        echo ""

    } > "$AUTO_ORG_DIR/INDEX.md"

    log "索引生成完成: $AUTO_ORG_DIR/INDEX.md"
}

# ============================================================================
# 功能5: 自动组织所有记忆
# =============================================================================

organize_all_memory() {
    log "🗂️  开始自组织记忆..."

    echo ""
    echo "🗂️  自组织记忆系统"
    echo "======================"
    echo ""

    # 执行所有分类
    classify_by_topic
    classify_by_severity
    sort_by_frequency
    generate_memory_index

    echo ""
    echo "======================"
    echo "✅ 记忆组织完成！"
    echo ""
    echo "📊 组织结果:"
    echo "  - 按主题: $(ls -1 "$AUTO_ORG_DIR/by-topic" 2>/dev/null | wc -l) 个主题"
    echo "  - 按严重程度: $(ls -1 "$AUTO_ORG_DIR/by-severity"/* 2>/dev/null | wc -l) 个级别"
    echo "  - 按频率: $(ls -1 "$AUTO_ORG_DIR/by-frequency"/* 2>/dev/null | wc -l) 个级别"
    echo "  - 索引文件: $AUTO_ORG_DIR/INDEX.md"
    echo ""
    echo "💡 查看索引: cat $AUTO_ORG_DIR/INDEX.md"
}

# ============================================================================
# 主程序
# =============================================================================

# 如果直接运行脚本
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    organize_all_memory
fi
