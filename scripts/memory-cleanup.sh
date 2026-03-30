#!/bin/bash
# 记忆清理脚本
# 自动归档过期日志，清理旧文件

echo "🧹 记忆清理脚本"
echo "========================================"
echo "清理时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 配置
MEMORY_DIR="/root/.openclaw/workspace/memory"
ARCHIVE_DIR="$MEMORY_DIR/archive"
DAYS_TO_KEEP=30

# 创建归档目录
mkdir -p "$ARCHIVE_DIR"

# 1. 归档 30 天以上的日志
echo "📦 1. 归档旧日志（> $DAYS_TO_KEEP 天）"
archived_count=0

find "$MEMORY_DIR" -name "*.md" -mtime +$DAYS_TO_KEEP -not -path "*/archive/*" | while read file; do
    filename=$(basename "$file")
    echo "   归档: $filename"
    mv "$file" "$ARCHIVE_DIR/"
    ((archived_count++))
done

echo "   归档文件数: $archived_count"
echo ""

# 2. 压缩归档文件（可选）
echo "📦 2. 压缩归档文件"
if [ -d "$ARCHIVE_DIR" ]; then
    # 使用 gzip 压缩 .md 文件
    find "$ARCHIVE_DIR" -name "*.md" -not -name "*.gz" | while read file; do
        gzip "$file"
        echo "   压缩: $(basename "$file").gz"
    done
    echo "   压缩完成"
else
    echo "   无归档文件"
fi
echo ""

# 3. 清理临时文件
echo "🧹 3. 清理临时文件"
temp_files=$(find /tmp -name "memory-*" -mtime +7 2>/dev/null | wc -l)
if [ $temp_files -gt 0 ]; then
    find /tmp -name "memory-*" -mtime +7 -delete 2>/dev/null
    echo "   清理临时文件: $temp_files 个"
else
    echo "   无临时文件"
fi
echo ""

# 4. 统计信息
echo "📊 4. 清理统计"
total_files=$(find "$MEMORY_DIR" -name "*.md" -not -path "*/archive/*" | wc -l)
archive_files=$(find "$ARCHIVE_DIR" -name "*.md*" | wc -l)

echo "   当前日志文件: $total_files 个"
echo "   归档文件: $archive_files 个"
echo ""

# 5. 建议
echo "💡 5. 建议"
if [ $total_files -gt 50 ]; then
    echo "   ⚠️  当前日志文件过多（>50），建议进一步清理"
else
    echo "   ✅ 日志文件数量正常"
fi

archive_size=$(du -sh "$ARCHIVE_DIR" 2>/dev/null | awk '{print $1}')
echo "   归档目录大小: $archive_size"
echo ""

echo "========================================"
echo "✅ 清理完成"
