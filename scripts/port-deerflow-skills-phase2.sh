#!/bin/bash

# DeerFlow Skills移植脚本 - Phase2
# 功能：自动移植 DeerFlow 设计相关技能到 OpenClaw
# 创建日期：2026-03-23

set -e

# 配置变量
SOURCE_DIR="/root/.openclaw/workspace/projects/deerflow-study/deer-flow-source/skills/public"
TARGET_DIR="/root/.openclaw/skills"
PORTED_DATE=$(date +%Y-%m-%d)
REPORT_FILE="/root/.openclaw/workspace/projects/deerflow-study/SKILL-PORTING-PHASE2-REPORT.md"
LOG_FILE="/root/.openclaw/workspace/projects/deerflow-study/port-skills-phase2.log"

# 要移植的设计相关技能列表
DESIGN_SKILLS=(
    "frontend-design"
    "chart-visualization"
    "image-generation"
    "ppt-generation"
    "web-design-guidelines"
)

echo "=== DeerFlow技能移植日志 - Phase2 ===" > "$LOG_FILE"
echo "开始时间: $(date)" >> "$LOG_FILE"
echo "源目录: $SOURCE_DIR" >> "$LOG_FILE"
echo "目标目录: $TARGET_DIR" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 函数：检查技能目录结构
check_skill_structure() {
    local skill_name="$1"
    local skill_path="$SOURCE_DIR/$skill_name"
    
    echo "检查技能结构: $skill_name"
    
    if [ ! -d "$skill_path" ]; then
        echo "错误：技能目录不存在: $skill_path"
        return 1
    fi
    
    if [ ! -f "$skill_path/SKILL.md" ]; then
        echo "错误：SKILL.md 文件不存在"
        return 1
    fi
    
    echo "  ✓ 包含 SKILL.md"
    
    for dir in scripts references assets templates agents; do
        if [ -d "$skill_path/$dir" ]; then
            local count=$(find "$skill_path/$dir" -type f | wc -l)
            echo "  ✓ 包含 $dir/ ($count 个文件)"
        fi
    done
    
    return 0
}

# 函数：添加OpenClaw兼容性元数据
add_compatibility_metadata() {
    local skill_name="$1"
    local skill_path="$TARGET_DIR/$skill_name"
    local skill_file="$skill_path/SKILL.md"
    
    if [ ! -f "$skill_file" ]; then
        echo "  ✗ SKILL.md 不存在"
        return 1
    fi
    
    local original_content=$(cat "$skill_file")
    
    if grep -q "^---" "$skill_file"; then
        echo "  ⚠ 已有 frontmatter，跳过"
        return 0
    fi
    
    local new_content=$(cat <<EOF
---
compatibility: ["openclaw"]
ported-from: deerflow
ported-date: $PORTED_DATE
---

$original_content
EOF
)
    
    echo "$new_content" > "$skill_file"
    echo "  ✓ 已添加兼容性元数据"
    return 0
}

# 函数：移植技能目录
port_skill() {
    local skill_name="$1"
    local source_path="$SOURCE_DIR/$skill_name"
    local target_path="$TARGET_DIR/$skill_name"
    
    echo "正在移植: $skill_name"
    
    if [ -d "$target_path" ]; then
        local backup_path="${target_path}.backup.${PORTED_DATE}"
        echo "  ! 备份已存在目录"
        mv "$target_path" "$backup_path"
    fi
    
    cp -r "$source_path" "$target_path"
    
    if [ ! -d "$target_path" ]; then
        echo "  ✗ 复制失败"
        return 1
    fi
    
    echo "  ✓ 复制完成"
    return 0
}

# 函数：列出技能文件
list_skill_files() {
    local skill_name="$1"
    local skill_path="$TARGET_DIR/$skill_name"
    
    echo "### 📁 $skill_name" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "\`\`\`" >> "$REPORT_FILE"
    find "$skill_path" -type f | sed "s|$skill_path/||" | sort | while read f; do
        echo "  • $f" >> "$REPORT_FILE"
    done
    echo "\`\`\`" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
}

# 主函数
main() {
    echo "开始 DeerFlow 设计相关技能移植 - Phase2"
    echo "移植日期: $PORTED_DATE"
    echo "========================================"
    
    if [ ! -d "$SOURCE_DIR" ]; then
        echo "错误：源目录不存在: $SOURCE_DIR"
        exit 1
    fi
    
    mkdir -p "$TARGET_DIR"
    
    # 初始化报告
    echo "# DeerFlow 技能移植报告 - Phase2 (设计相关)" > "$REPORT_FILE"
    echo "## 移植信息" >> "$REPORT_FILE"
    echo "- **日期**: $PORTED_DATE" >> "$REPORT_FILE"
    echo "- **源目录**: $SOURCE_DIR" >> "$REPORT_FILE"
    echo "- **目标目录**: $TARGET_DIR" >> "$REPORT_FILE"
    echo "- **技能数量**: ${#DESIGN_SKILLS[@]}" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "## 技能列表" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    local success_count=0
    local error_count=0
    
    for skill in "${DESIGN_SKILLS[@]}"; do
        echo ""
        echo "========================================"
        echo "处理技能: $skill"
        echo "========================================"
        
        if ! check_skill_structure "$skill"; then
            echo "❌ 结构检查失败: $skill"
            error_count=$((error_count + 1))
            continue
        fi
        
        if ! port_skill "$skill"; then
            echo "❌ 移植失败: $skill"
            error_count=$((error_count + 1))
            continue
        fi
        
        add_compatibility_metadata "$skill"
        
        # 读取技能描述
        local desc=$(grep "^description:" "$TARGET_DIR/$skill/SKILL.md" | head -1 | cut -d: -f2- | xargs)
        
        echo "### ✅ $skill" >> "$REPORT_FILE"
        echo "- **描述**: ${desc:-无描述}" >> "$REPORT_FILE"
        echo "- **状态**: 移植成功" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        
        list_skill_files "$skill"
        
        success_count=$((success_count + 1))
        echo "✅ 完成: $skill"
    done
    
    echo ""
    echo "========================================"
    echo "移植完成总结"
    echo "========================================"
    echo "成功: $success_count / ${#DESIGN_SKILLS[@]}"
    echo "失败: $error_count"
    
    echo "## 总结" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "| 项目 | 数量 |" >> "$REPORT_FILE"
    echo "|------|------|" >> "$REPORT_FILE"
    echo "| 总技能数 | ${#DESIGN_SKILLS[@]} |" >> "$REPORT_FILE"
    echo "| 成功移植 | $success_count |" >> "$REPORT_FILE"
    echo "| 移植失败 | $error_count |" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    echo "完成时间: $(date)" >> "$LOG_FILE"
    
    echo ""
    echo "详细报告: $REPORT_FILE"
}

main "$@"
