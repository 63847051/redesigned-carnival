#!/bin/bash
# 文档质量改进系统快速启动脚本

VERSION="1.0.0"
AUTHOR="文档质量改进系统"
DATE="2026-03-28"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    cat << EOF
文档质量改进系统快速启动脚本 v${VERSION}

用法: $0 [选项] [任务名称]

选项:
    -h, --help          显示帮助信息
    -l, --list          列出可用模板
    -t, --template     指定模板类型 (task/config/review)
    -v, --verify       验证现有文档
    -d, --dir PATH     指定工作目录

示例:
    $0 "新功能开发"              # 创建任务文档
    $0 -t config "系统配置"       # 创建配置文档
    $0 -v "现有文档.md"           # 验证文档质量
    $0 -l                        # 列出所有模板
EOF
}

# 显示模板列表
show_templates() {
    echo -e "${BLUE}📚 可用模板列表:${NC}"
    echo "==================================="
    
    local template_dir="/root/.openclaw/workspace/templates/docs"
    
    if [[ -d "$template_dir" ]]; then
        for template in "$template_dir"/*.md; do
            if [[ -f "$template" ]]; then
                local name=$(basename "$template")
                local size=$(stat -c%s "$template")
                echo -e "${GREEN}📄 $name${NC} (${size} bytes)"
            fi
        done
    else
        echo -e "${RED}❌ 模板目录不存在: $template_dir${NC}"
    fi
}

# 创建文档
create_document() {
    local task_name="$1"
    local template_type="${2:-task}"
    local template_dir="/root/.openclaw/workspace/templates/docs"
    local output_dir="./docs"
    
    # 确保输出目录存在
    mkdir -p "$output_dir"
    
    # 选择模板文件
    local template_file=""
    case "$template_type" in
        task)
            template_file="$template_dir/task-template.md"
            ;;
        config)
            template_file="$template_dir/config-template.md"
            ;;
        review)
            template_file="$template_dir/review-template.md"
            ;;
        *)
            echo -e "${RED}❌ 不支持的模板类型: $template_type${NC}"
            return 1
            ;;
    esac
    
    # 检查模板文件是否存在
    if [[ ! -f "$template_file" ]]; then
        echo -e "${RED}❌ 模板文件不存在: $template_file${NC}"
        return 1
    fi
    
    # 生成输出文件名
    local output_file="$output_dir/${task_name}-$(date +%Y-%m-%d).md"
    
    # 复制模板
    cp "$template_file" "$output_file"
    
    # 替换占位符（如果有的话）
    sed -i "s/\[任务名称\]/$task_name/g" "$output_file"
    sed -i "s/\[日期 YYYY-MM-DD\]/$(date +%Y-%m-%d)/g" "$output_file"
    
    echo -e "${GREEN}✅ 文档已创建: $output_file${NC}"
    
    # 提示用户编辑
    echo -e "${YELLOW}💡 请编辑文档内容: $output_file${NC}"
    
    # 可选：自动打开编辑器
    if command -v nano &> /dev/null; then
        echo -e "${BLUE}📝 正在打开编辑器...${NC}"
        nano "$output_file"
    fi
}

# 验证文档
verify_document() {
    local doc_file="$1"
    
    if [[ ! -f "$doc_file" ]]; then
        echo -e "${RED}❌ 文件不存在: $doc_file${NC}"
        return 1
    fi
    
    echo -e "${BLUE}🔍 正在验证文档: $doc_file${NC}"
    
    # 检查必需章节
    local required_sections="标题|描述|步骤|验证"
    local missing_sections=()
    local found_sections=0
    
    for section in $required_sections; do
        if grep -qE "^##\s*$section|^###\s*$section" "$doc_file"; then
            echo -e "${GREEN}✅ 找到章节: $section${NC}"
            found_sections=$((found_sections + 1))
        else
            missing_sections+=("$section")
        fi
    done
    
    echo ""
    echo "📊 验证结果:"
    echo "- 总章节数: $(echo $required_sections | wc -w)"
    echo "- 已找到: $found_sections"
    echo "- 缺少章节: ${#missing_sections[@]}"
    
    if [[ ${#missing_sections[@]} -eq 0 ]]; then
        echo -e "${GREEN}✅ 文档质量检查通过!${NC}"
        return 0
    else
        echo -e "${RED}❌ 文档缺少以下章节:${NC}"
        for section in "${missing_sections[@]}"; do
            echo -e "   🔸 $section"
        done
        return 1
    fi
}

# 主函数
main() {
    local template_type="task"
    local work_dir="."
    local verify_mode=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -l|--list)
                show_templates
                exit 0
                ;;
            -t|--template)
                template_type="$2"
                shift 2
                ;;
            -v|--verify)
                verify_mode=true
                shift
                ;;
            -d|--dir)
                work_dir="$2"
                shift 2
                ;;
            *)
                # 剩余的参数作为任务名称
                break
                ;;
        esac
    done
    
    cd "$work_dir"
    
    if [[ "$verify_mode" == true ]]; then
        if [[ $# -eq 0 ]]; then
            echo -e "${RED}❌ 验证模式需要指定文档路径${NC}"
            exit 1
        fi
        verify_document "$1"
    else
        if [[ $# -eq 0 ]]; then
            echo -e "${RED}❌ 请提供任务名称${NC}"
            echo ""
            show_help
            exit 1
        fi
        create_document "$1" "$template_type"
    fi
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi