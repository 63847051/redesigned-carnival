#!/bin/bash
###############################################################################
# 清理和优化脚本
# 目标：减少脚本数量，保留真正有用的
###############################################################################

echo "🧹 开始清理和优化..."
echo "⏰ 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 统计当前状态
echo "📊 当前状态:"
echo "  - 脚本数量: $(ls /root/.openclaw/workspace/scripts/*.sh 2>/dev/null | wc -l) 个"
echo "  - 文档数量: $(find /root/.openclaw/workspace/docs -name "*.md" 2>/dev/null | wc -l) 份"
echo ""

# 创建备份目录
backup_dir="/root/.openclaw/workspace/archive/$(date +%Y%m%d)"
mkdir -p "$backup_dir"
echo "📦 备份目录: $backup_dir"
echo ""

###############################################################################
# 第一步：归档重复和过时的脚本
###############################################################################

echo "🗑️  第一步：归档重复和过时的脚本..."
echo ""

# 重复的脚本（相同功能）
duplicates=(
  "auto-dream-v2.sh"
  "auto-dream-v3.sh"
  "auto-dream-v4.sh"
  "pai-advisor.sh"
  "pai-advisor-v2.sh"
  "memory-search-simple.sh"
  "memory-search-glm.sh"
  "stock-query.sh"
  "stock-query-final.sh"
  "stock-query-tencent.sh"
  "stock-netease.sh"
)

# 归档重复脚本
for script in "${duplicates[@]}"; do
  if [ -f "/root/.openclaw/workspace/scripts/$script" ]; then
    mv "/root/.openclaw/workspace/scripts/$script" "$backup_dir/"
    echo "  ✅ 归档: $script"
  fi
done

echo ""
echo "✅ 已归档 ${#duplicates[@]} 个重复脚本"
echo ""

###############################################################################
# 第二步：归档测试和实验性脚本
###############################################################################

echo "🗑️  第二步：归档测试和实验性脚本..."
echo ""

# 测试脚本
tests=(
  "test-*.sh"
  "*-test.sh"
  "test*.sh"
)

for pattern in "${tests[@]}"; do
  for script in /root/.openclaw/workspace/scripts/$pattern; do
    if [ -f "$script" ]; then
      basename=$(basename "$script")
      mv "$script" "$backup_dir/"
      echo "  ✅ 归档: $basename"
    fi
  done
done

echo ""
echo "✅ 已归档所有测试脚本"
echo ""

###############################################################################
# 第三步：归档过时的文档
###############################################################################

echo "🗑️  第三步：归档过时的文档..."
echo ""

# 过时的文档（根据文件名判断）
outdated_docs=(
  "*OLD*.md"
  "*-OLD.md"
  "*-v1.md"
  "*-v2.md"
  "*-backup.md"
)

for pattern in "${outdated_docs[@]}"; do
  for doc in /root/.openclaw/workspace/docs/$pattern; do
    if [ -f "$doc" ]; then
      basename=$(basename "$doc")
      mv "$doc" "$backup_dir/"
      echo "  ✅ 归档: $basename"
    fi
  done
done

echo ""
echo "✅ 已归档过时文档"
echo ""

###############################################################################
# 第四步：创建核心脚本清单
###############################################################################

echo "📋 第四步：创建核心脚本清单..."
echo ""

core_scripts=(
  "auto-learning.sh"
  "auto-dream-basic.sh"
  "check-bootstrap-limits.sh"
  "hot-reload-bootstrap.sh"
  "verify-progress.sh"
  "monitor-agents.sh"
  "assign-task.sh"
  "extract-skills.sh"
)

echo "# 核心脚本清单" > /root/.openclaw/workspace/scripts/CORE_SCRIPTS.md
echo "" >> /root/.openclaw/workspace/scripts/CORE_SCRIPTS.md
echo "## 必须保留的核心脚本（9个）" >> /root/.openclaw/workspace/scripts/CORE_SCRIPTS.md
echo "" >> /root/.openclaw/workspace/scripts/CORE_SCRIPTS.md

for script in "${core_scripts[@]}"; do
  if [ -f "/root/.openclaw/workspace/scripts/$script" ]; then
    size=$(ls -lh "/root/.openclaw/workspace/scripts/$script" | awk '{print $5}')
    echo "### $script ($size)" >> /root/.openclaw/workspace/scripts/CORE_SCRIPTS.md
    echo "" >> /root/.openclaw/workspace/scripts/CORE_SCRIPTS.md
  fi
done

echo "✅ 核心脚本清单已创建"
echo ""

###############################################################################
# 第五步：创建核心文档清单
###############################################################################

echo "📋 第五步：创建核心文档清单..."
echo ""

core_docs=(
  "AUTO-DREAM-SOURCE-STUDY.md"
  "PROMPT-DEEP-STUDY.md"
  "SYSTEM-PROMPT-DEEP-STUDY.md"
  "OPENCLAW-ADVANCED-GUIDE-VOL2-DEEP-STUDY.md"
  "CODE-CLAW-ANALYSIS.md"
  "HOTRELOAD-IMPLEMENTATION.md"
  "PERSISTENT-MEMORY-OPTIMIZATION.md"
  "FINAL-ULTRA-ACHIEVEMENTS-CODE-CLAW.md"
)

echo "# 核心文档清单" > /root/.openclaw/workspace/docs/CORE_DOCS.md
echo "" >> /root/.openclaw/workspace/docs/CORE_DOCS.md
echo "## 必须保留的核心文档（8份）" >> /root/.openclaw/workspace/docs/CORE_DOCS.md
echo "" >> /root/.openclaw/workspace/docs/CORE_DOCS.md

for doc in "${core_docs[@]}"; do
  if [ -f "/root/.openclaw/workspace/docs/$doc" ]; then
    size=$(ls -lh "/root/.openclaw/workspace/docs/$doc" | awk '{print $5}')
    echo "### $doc ($size)" >> /root/.openclaw/workspace/docs/CORE_DOCS.md
    echo "" >> /root/.openclaw/workspace/docs/CORE_DOCS.md
  fi
done

echo "✅ 核心文档清单已创建"
echo ""

###############################################################################
# 统计结果
###############################################################################

echo "📊 清理结果:"
echo "  - 剩余脚本: $(ls /root/.openclaw/workspace/scripts/*.sh 2>/dev/null | wc -l) 个"
echo "  - 剩余文档: $(find /root/.openclaw/workspace/docs -name "*.md" 2>/dev/null | wc -l) 份"
echo "  - 归档文件: $(ls $backup_dir 2>/dev/null | wc -l) 个"
echo ""

echo "📦 备份位置: $backup_dir"
echo ""
echo "✅ 清理完成！"
echo ""
echo "💡 下一步："
echo "  1. 检查核心脚本清单: /root/.openclaw/workspace/scripts/CORE_SCRIPTS.md"
echo "  2. 检查核心文档清单: /root/.openclaw/workspace/docs/CORE_DOCS.md"
echo "  3. 确认后可以删除归档目录"
