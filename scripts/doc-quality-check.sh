#!/bin/bash
# 文档质量检查脚本
# 检查文档是否包含必要章节

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查单个文档
check_doc() {
    local file="$1"
    local doc_type="$2"
    
    # 根据文档类型定义必需章节
    case "$doc_type" in
        task)
            REQUIRED_SECTIONS="任务描述|验收标准|执行步骤|风险和依赖|执行记录|经验教训"
            ;;
        config)
            REQUIRED_SECTIONS="配置概述|配置项|配置验证|变更历史|回滚方案"
            ;;
        review)
            REQUIRED_SECTIONS="审查概述|检查清单|审查结果|审查结论"
            ;;
        *)
            REQUIRED_SECTIONS="标题|描述|步骤|验证"
            ;;
    esac
    
    # 检查必需章节
    if grep -qE "$REQUIRED_SECTIONS" "$file"; then
        echo -e "${GREEN}✅ 文档完整${NC}: $file"
        return 0
    else
        echo -e "${RED}❌ 文档缺少章节${NC}: $file"
        echo -e "   ${YELLOW}需要章节${NC}: $REQUIRED_SECTIONS"
        return 1
    fi
}

# 自动检测文档类型
detect_doc_type() {
    local file="$1"
    local filename=$(basename "$file")
    
    case "$filename" in
        *task*)
            echo "task"
            ;;
        *config*)
            echo "config"
            ;;
        *review*)
            echo "review"
            ;;
        *)
            echo "general"
            ;;
    esac
}

# 主函数
main() {
    local target_dir="${1:-.}"
    local total=0
    local passed=0
    local failed=0
    
    echo "📋 文档质量检查"
    echo "================"
    echo "检查目录: $target_dir"
    echo ""
    
    # 查找所有 Markdown 文件
    while IFS= read -r -d '' file; do
        ((total++))
        
        # 检测文档类型
        doc_type=$(detect_doc_type "$file")
        
        # 检查文档
        if check_doc "$file" "$doc_type"; then
            ((passed++))
        else
            ((failed++))
        fi
    done < <(find "$target_dir" -name "*.md" -type f -print0)
    
    # 输出统计
    echo ""
    echo "📊 检查统计"
    echo "=========="
    echo -e "总计: ${GREEN}$total${NC} 个文档"
    echo -e "通过: ${GREEN}$passed${NC} 个"
    echo -e "失败: ${RED}$failed${NC} 个"
    echo ""
    
    if [ $failed -eq 0 ]; then
        echo -e "${GREEN}✅ 所有文档质量检查通过！${NC}"
        return 0
    else
        echo -e "${RED}❌ 有 $failed 个文档需要改进${NC}"
        return 1
    fi
}

# 帮助信息
show_help() {
    echo "文档质量检查脚本"
    echo ""
    echo "用法: $0 [目录]"
    echo ""
    echo "示例:"
    echo "  $0 .                    # 检查当前目录"
    echo "  $0 ~/workspace/docs     # 检查指定目录"
    echo ""
}

# 参数处理
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

main "$@"
