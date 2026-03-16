#!/bin/bash
# 版本自动追踪脚本
# 作者: 大领导系统 v5.16.0
# 日期: 2026-03-16
#
# 用法: ./track-version.sh "版本号" "变更类型" "变更描述"
#
# 示例: ./track-version.sh "5.17.0" "新增" "添加新功能"

set -e

VERSION=$1
TYPE=$2
DESCRIPTION=$3
DATE=$(date +%Y-%m-%d)

if [ -z "$VERSION" ] || [ -z "$TYPE" ] || [ -z "$DESCRIPTION" ]; then
    echo "❌ 错误: 缺少参数"
    echo "用法: $0 \"版本号\" \"变更类型\" \"变更描述\""
    echo ""
    echo "示例:"
    echo "  $0 \"5.17.0\" \"新增\" \"添加新功能\""
    echo "  $0 \"5.16.1\" \"修复\" \"修复 Bug\""
    echo "  $0 \"5.17.0\" \"优化\" \"优化性能\""
    exit 1
fi

echo "📝 追踪版本变更..."
echo "版本: $VERSION"
echo "类型: $TYPE"
echo "描述: $DESCRIPTION"
echo "日期: $DATE"
echo ""

# 更新 CHANGELOG.md
CHANGELOG_FILE="/root/.openclaw/workspace/CHANGELOG.md"

# 创建新版本条目
cat > /tmp/new_version.md << EOF
## [$VERSION] - $DATE

### 🎉 $TYPE
- ✅ $DESCRIPTION

### 📊 迭代统计
- **版本号**: $(grep -oP '\[\d+\.\d+\.\d+\]' $CHANGELOG_FILE | head -1 | sed 's/\[//;s/\]//') → $VERSION
- **迭代次数**: $(grep -c "## \[" $CHANGELOG_FILE)
- **变更时间**: $DATE

---

EOF

# 插入到 CHANGELOG.md 的第二行（第一个版本条目之后）
if [ -f "$CHANGELOG_FILE" ]; then
    # 备份原文件
    cp "$CHANGELOG_FILE" "$CHANGELOG_FILE.backup-$(date +%Y%m%d-%H%M%S)"
    
    # 插入新版本
    sed -i "2r /tmp/new_version.md" "$CHANGELOG_FILE"
    
    echo "✅ CHANGELOG.md 已更新"
else
    echo "❌ 错误: CHANGELOG.md 不存在"
    exit 1
fi

# 更新 SOUL.md 中的版本号
SOUL_FILE="/root/.openclaw/workspace/SOUL.md"
if [ -f "$SOUL_FILE" ]; then
    # 备份原文件
    cp "$SOUL_FILE" "$SOUL_FILE.backup-$(date +%Y%m%d-%H%M%S)"
    
    # 更新版本号
    sed -i "s/\*\*版本\*\*:.*/\*\*版本\*\*: $VERSION/" "$SOUL_FILE"
    sed -i "s/\*\*最后升级\*\*:.*/\*\*最后升级\*\*: $(date '+%Y-%m-%d %H:%M')/" "$SOUL_FILE"
    
    echo "✅ SOUL.md 版本号已更新"
else
    echo "⚠️ 警告: SOUL.md 不存在"
fi

# 清理临时文件
rm -f /tmp/new_version.md

echo ""
echo "================================"
echo "✅ 版本追踪完成！"
echo ""
echo "📋 下一步:"
echo "   1. 检查 CHANGELOG.md 是否正确"
echo "   2. 更新具体的变更内容"
echo "   3. 提交到 Git: git add . && git commit -m \"版本 $VERSION\""
echo ""
echo "💡 提示:"
echo "   - 变更类型: 新增、修复、优化、文档"
echo "   - 详细描述会自动记录到 CHANGELOG.md"
