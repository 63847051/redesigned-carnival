#!/bin/bash

# DeerFlow Skills移植脚本 - Phase1
# 功能：自动移植 DeerFlow 核心技能到 OpenClaw
# 作者：AI Assistant
# 创建日期：2026-03-23

set -e  # 遇到错误立即退出

# 配置变量
SOURCE_DIR="/root/.openclaw/workspace/projects/deerflow-study/deer-flow-source/skills/public"
TARGET_DIR="/root/.openclaw/skills"
PORTED_DATE=$(date +%Y-%m-%d)
REPORT_FILE="/root/.openclaw/workspace/projects/deerflow-study/SKILL-PORTING-PHASE1-REPORT.md"
LOG_FILE="/root/.openclaw/workspace/projects/deerflow-study/port-skills.log"

# 要移植的核心技能列表
CORE_SKILLS=(
    "deep-research"
    "data-analysis" 
    "skill-creator"
    "github-deep-research"
    "find-skills"
)

# 创建日志文件
echo "=== DeerFlow技能移植日志 - Phase1 ===" > "$LOG_FILE"
echo "开始时间: $(date)" >> "$LOG_FILE"
echo "源目录: $SOURCE_DIR" >> "$LOG_FILE"
echo "目标目录: $TARGET_DIR" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 函数：检查技能目录结构
check_skill_structure() {
    local skill_name="$1"
    local skill_path="$SOURCE_DIR/$skill_name"
    
    echo "检查技能结构: $skill_name" | tee -a "$LOG_FILE"
    
    if [ ! -d "$skill_path" ]; then
        echo "错误：技能目录不存在: $skill_path" | tee -a "$LOG_FILE"
        return 1
    fi
    
    if [ ! -f "$skill_path/SKILL.md" ]; then
        echo "错误：SKILL.md 文件不存在: $skill_path/SKILL.md" | tee -a "$LOG_FILE"
        return 1
    fi
    
    # 检查 scripts 目录
    if [ -d "$skill_path/scripts" ]; then
        echo "  ✓ 包含 scripts/ 目录" | tee -a "$LOG_FILE"
        local script_count=$(find "$skill_path/scripts" -name "*.py" -o -name "*.sh" | wc -l)
        echo "  ✓ 脚本数量: $script_count" | tee -a "$LOG_FILE"
    else
        echo "  - 无 scripts/ 目录" | tee -a "$LOG_FILE"
    fi
    
    # 检查其他资源目录
    for dir in assets references eval-viewer agents; do
        if [ -d "$skill_path/$dir" ]; then
            echo "  ✓ 包含 $dir/ 目录" | tee -a "$LOG_FILE"
        fi
    done
    
    return 0
}

# 函数：添加OpenClaw兼容性元数据
add_compatibility_metadata() {
    local skill_name="$1"
    local skill_path="$TARGET_DIR/$skill_name"
    local skill_file="$skill_path/SKILL.md"
    
    echo "添加兼容性元数据: $skill_name" | tee -a "$LOG_FILE"
    
    # 读取原有内容
    local original_content=$(cat "$skill_file")
    
    # 创建新的YAML frontmatter
    local new_content=$(cat <<EOF
---
compatibility: ["openclaw"]
ported-from: deerflow
ported-date: $PORTED_DATE
---

$original_content
EOF
)
    
    # 写入文件
    echo "$new_content" > "$skill_file"
    echo "  ✓ 已添加兼容性元数据" | tee -a "$LOG_FILE"
    
    return 0
}

# 函数：移植技能目录
port_skill() {
    local skill_name="$1"
    local source_path="$SOURCE_DIR/$skill_name"
    local target_path="$TARGET_DIR/$skill_name"
    
    echo "正在移植技能: $skill_name" | tee -a "$LOG_FILE"
    
    # 检查目标目录是否存在，如果存在则备份
    if [ -d "$target_path" ]; then
        local backup_path="${target_path}.backup.${PORTED_DATE}"
        echo "  ! 目标目录已存在，创建备份: $backup_path" | tee -a "$LOG_FILE"
        mv "$target_path" "$backup_path"
    fi
    
    # 复制技能目录
    echo "  → 复制目录: $source_path → $target_path" | tee -a "$LOG_FILE"
    cp -r "$source_path" "$target_path"
    
    # 检查复制结果
    if [ ! -d "$target_path" ]; then
        echo "  ✗ 复制失败" | tee -a "$LOG_FILE"
        return 1
    fi
    
    echo "  ✓ 目录复制完成" | tee -a "$LOG_FILE"
    
    return 0
}

# 函数：测试技能
test_skill() {
    local skill_name="$1"
    local skill_path="$TARGET_DIR/$skill_name"
    local skill_file="$skill_path/SKILL.md"
    
    echo "测试技能: $skill_name" | tee -a "$LOG_FILE"
    
    # 检查SKILL.md格式
    if [ ! -f "$skill_file" ]; then
        echo "  ✗ SKILL.md 文件不存在" | tee -a "$LOG_FILE"
        return 1
    fi
    
    # 检查YAML frontmatter格式
    if ! grep -q "^---" "$skill_file" || ! grep -q "^compatibility:" "$skill_file"; then
        echo "  ✗ YAML frontmatter 格式错误" | tee -a "$LOG_FILE"
        return 1
    fi
    
    # 检查技能名称
    local skill_name_in_file=$(head -n 20 "$skill_file" | grep "^name:" | cut -d' ' -f2- | tr -d '"')
    if [ "$skill_name_in_file" != "$skill_name" ]; then
        echo "  ⚠ 技能名称不匹配 (文件: $skill_name_in_file, 期望: $skill_name)" | tee -a "$LOG_FILE"
    else
        echo "  ✓ 技能名称正确: $skill_name_in_file" | tee -a "$LOG_FILE"
    fi
    
    # 检查描述
    local description=$(head -n 20 "$skill_file" | grep "^description:" | cut -d' ' -f2- | tr -d '"')
    if [ -z "$description" ]; then
        echo "  ⚠ 技能描述为空" | tee -a "$LOG_FILE"
    else
        echo "  ✓ 技能描述: $description" | tee -a "$LOG_FILE"
    fi
    
    # 列出文件清单
    echo "  📋 文件清单:" | tee -a "$LOG_FILE"
    find "$skill_path" -type f -name "*.md" -o -name "*.py" -o -name "*.sh" | while read file; do
        local rel_path="${file#$target_path/}"
        local file_size=$(stat -c%s "$file")
        echo "    • $rel_path ($file_size bytes)" | tee -a "$LOG_FILE"
    done
    
    return 0
}

# 函数：列出技能文件清单
list_skill_files() {
    local skill_name="$1"
    local skill_path="$TARGET_DIR/$skill_name"
    
    echo "📁 $skill_name 文件清单:" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    # 按类型分类列出文件
    echo "### 文档文件:" >> "$REPORT_FILE"
    find "$skill_path" -name "*.md" -type f | while read file; do
        local rel_path="${file#$skill_path/}"
        local line_count=$(wc -l < "$file")
        local file_size=$(stat -c%s "$file")
        echo "- $rel_path ($line_count 行, $file_size 字节)" >> "$REPORT_FILE"
    done
    
    if ! find "$skill_path" -name "*.md" -type f | head -1 >/dev/null; then
        echo "- 无文档文件" >> "$REPORT_FILE"
    fi
    
    echo "" >> "$REPORT_FILE"
    
    echo "### 脚本文件:" >> "$REPORT_FILE"
    find "$skill_path" -name "*.py" -o -name "*.sh" | while read file; do
        local rel_path="${file#$skill_path/}"
        local line_count=$(wc -l < "$file")
        local file_size=$(stat -c%s "$file")
        echo "- $rel_path ($line_count 行, $file_size 字节)" >> "$REPORT_FILE"
    done
    
    if ! find "$skill_path" -name "*.py" -o -name "*.sh" | head -1 >/dev/null; then
        echo "- 无脚本文件" >> "$REPORT_FILE"
    fi
    
    echo "" >> "$REPORT_FILE"
    
    echo "### 资源文件:" >> "$REPORT_FILE"
    find "$skill_path" -type d | while read dir; do
        local rel_dir="${dir#$skill_path/}"
        if [ "$rel_dir" != "." ] && [ "$rel_dir" != "./" ]; then
            local file_count=$(find "$dir" -type f | wc -l)
            if [ "$file_count" -gt 0 ]; then
                echo "- 📁 $rel_dir ($file_count 个文件)" >> "$REPORT_FILE"
            fi
        fi
    done
    
    echo "" >> "$REPORT_FILE"
}

# 主函数
main() {
    echo "开始 DeerFlow 核心技能移植 - Phase1"
    echo "移植日期: $PORTED_DATE"
    echo "========================================"
    
    # 检查源目录
    if [ ! -d "$SOURCE_DIR" ]; then
        echo "错误：源目录不存在: $SOURCE_DIR"
        exit 1
    fi
    
    # 检查目标目录
    if [ ! -d "$TARGET_DIR" ]; then
        echo "创建目标目录: $TARGET_DIR"
        mkdir -p "$TARGET_DIR"
    fi
    
    # 初始化报告文件
    echo "# DeerFlow 技能移植报告 - Phase1" > "$REPORT_FILE"
    echo "## 移植信息" >> "$REPORT_FILE"
    echo "- **移植日期**: $PORTED_DATE" >> "$REPORT_FILE"
    echo "- **源目录**: $SOURCE_DIR" >> "$REPORT_FILE"
    echo "- **目标目录**: $TARGET_DIR" >> "$REPORT_FILE"
    echo "- **移植技能数量**: ${#CORE_SKILLS[@]}" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "## 技能列表" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    # 移植计数器
    local success_count=0
    local error_count=0
    local modified_count=0
    
    # 逐个移植技能
    for skill in "${CORE_SKILLS[@]}"; do
        echo ""
        echo "========================================"
        echo "处理技能: $skill"
        echo "========================================"
        
        # 步骤1: 检查结构
        if ! check_skill_structure "$skill"; then
            echo "❌ 技能结构检查失败: $skill" | tee -a "$LOG_FILE"
            echo "## 错误记录" >> "$REPORT_FILE"
            echo "- **技能**: $skill" >> "$REPORT_FILE"
            echo "- **问题**: 结构检查失败" >> "$REPORT_FILE"
            echo "- **状态**: ❌ 移植失败" >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
            error_count=$((error_count + 1))
            continue
        fi
        
        # 步骤2: 移植目录
        if ! port_skill "$skill"; then
            echo "❌ 技能移植失败: $skill" | tee -a "$LOG_FILE"
            echo "## 错误记录" >> "$REPORT_FILE"
            echo "- **技能**: $skill" >> "$REPORT_FILE"
            echo "- **问题**: 目录复制失败" >> "$REPORT_FILE"
            echo "- **状态**: ❌ 移植失败" >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
            error_count=$((error_count + 1))
            continue
        fi
        
        # 步骤3: 添加兼容性元数据
        if add_compatibility_metadata "$skill"; then
            echo "✅ 兼容性元数据添加成功" | tee -a "$LOG_FILE"
            modified_count=$((modified_count + 1))
        else
            echo "⚠️ 兼容性元数据添加失败" | tee -a "$LOG_FILE"
        fi
        
        # 步骤4: 测试验证
        if test_skill "$skill"; then
            echo "✅ 技能移植成功: $skill" | tee -a "$LOG_FILE"
            success_count=$((success_count + 1))
            
            # 记录到报告
            echo "### 🎯 $skill" >> "$REPORT_FILE"
            echo "- **状态**: ✅ 移植成功" >> "$REPORT_FILE"
            echo "- **兼容性**: 已添加 OpenClaw 兼容性元数据" >> "$REPORT_FILE"
            echo "- **修改**: 添加了 frontmatter 元数据" >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
            
            # 列出文件清单
            list_skill_files "$skill"
        else
            echo "❌ 技能测试失败: $skill" | tee -a "$LOG_FILE"
            echo "## 错误记录" >> "$REPORT_FILE"
            echo "- **技能**: $skill" >> "$REPORT_FILE"
            echo "- **问题**: 测试验证失败" >> "$REPORT_FILE"
            echo "- **状态**: ❌ 移植失败" >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
            error_count=$((error_count + 1))
        fi
        
        echo "" >> "$REPORT_FILE"
    done
    
    # 生成总结
    echo "========================================"
    echo "移植完成总结"
    echo "========================================"
    echo "成功移植: $success_count / ${#CORE_SKILLS[@]}"
    echo "修改技能: $modified_count"
    echo "错误技能: $error_count"
    
    # 更新报告的总结部分
    echo "## 总结报告" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "### 📊 统计信息" >> "$REPORT_FILE"
    echo "- **总技能数**: ${#CORE_SKILLS[@]}" >> "$REPORT_FILE"
    echo "- **成功移植**: $success_count" >> "$REPORT_FILE"
    echo "- **需要修改**: $modified_count" >> "$REPORT_FILE"
    echo "- **移植失败**: $error_count" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    if [ $error_count -eq 0 ]; then
        echo "### ✅ 移植状态" >> "$REPORT_FILE"
        echo "所有技能均成功移植，可以正常使用。" >> "$REPORT_FILE"
    else
        echo "### ⚠️ 移植状态" >> "$REPORT_FILE"
        echo "有 $error_count 个技能移植失败，请检查日志: $LOG_FILE" >> "$REPORT_FILE"
    fi
    
    # 记录完成时间
    echo "完成时间: $(date)" >> "$LOG_FILE"
    
    echo ""
    echo "移植日志: $LOG_FILE"
    echo "详细报告: $REPORT_FILE"
}

# 执行主函数
main "$@"