#!/bin/bash

# Deep Research MiroThinker Helper Script
# 用于辅助深度研究的辅助脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo -e "${BLUE}Deep Research MiroThinker Helper Script${NC}"
    echo ""
    echo "用法: $0 <command> [options]"
    echo ""
    echo "可用命令:"
    echo "  test          测试技能是否正确安装"
    echo "  search <query> 快速搜索相关信息"
    echo "  validate <file> 验证研究报告格式"
    echo "  help          显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 test"
    echo "  $0 search '人工智能教育应用'"
    echo "  $0 validate research-report.md"
}

# 测试技能安装
test_skill() {
    echo -e "${YELLOW}🔍 测试 deep-research-mirothinker 技能安装...${NC}"
    
    # 检查目录结构
    local skill_dir="/root/.openclaw/workspace/skills/deep-research-mirothinker"
    
    if [ ! -d "$skill_dir" ]; then
        echo -e "${RED}❌ 技能目录不存在: $skill_dir${NC}"
        return 1
    fi
    
    # 检查必要文件
    local required_files=("SKILL.md" "README.md")
    local missing_files=()
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$skill_dir/$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        echo -e "${RED}❌ 缺少必要文件: ${missing_files[*]}${NC}"
        return 1
    fi
    
    # 检查 SKILL.md 内容
    if ! grep -q "deep-research-mirothinker" "$skill_dir/SKILL.md"; then
        echo -e "${RED}❌ SKILL.md 内容不正确${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ 技能安装正确${NC}"
    echo "📁 目录位置: $skill_dir"
    echo "📄 SKILL.md: $(wc -l < "$skill_dir/SKILL.md") 行"
    echo "📄 README.md: $(wc -l < "$skill_dir/README.md") 行"
    
    return 0
}

# 快速搜索
quick_search() {
    local query="$1"
    
    if [ -z "$query" ]; then
        echo -e "${RED}❌ 请提供搜索查询${NC}"
        echo "示例: $0 search '人工智能教育应用'"
        return 1
    fi
    
    echo -e "${BLUE}🔍 快速搜索: $query${NC}"
    
    # 使用 web_search 进行搜索
    local temp_file="/tmp/research-search-$(date +%s).txt"
    
    # 这里可以调用实际的搜索功能
    echo -e "${YELLOW}模拟搜索结果...${NC}"
    echo "搜索查询: $query"
    echo "搜索时间: $(date)"
    echo ""
    echo "📄 搜索结果（模拟）:"
    echo "1. [标题1] 相关信息摘要..."
    echo "2. [标题2] 相关信息摘要..."
    echo "3. [标题3] 相关信息摘要..."
    
    # 清理临时文件
    rm -f "$temp_file"
    
    return 0
}

# 验证研究报告格式
validate_report() {
    local file="$1"
    
    if [ -z "$file" ]; then
        echo -e "${RED}❌ 请提供要验证的文件${NC}"
        echo "示例: $0 validate research-report.md"
        return 1
    fi
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ 文件不存在: $file${NC}"
        return 1
    fi
    
    echo -e "${BLUE}📋 验证研究报告格式: $file${NC}"
    
    # 检查基本结构
    local issues=()
    
    # 检查是否有标题
    if ! grep -q "^# " "$file"; then
        issues+=("缺少主标题")
    fi
    
    # 检查是否有关键发现部分
    if ! grep -q "^## 2\. 关键发现" "$file"; then
        issues+=("缺少'关键发现'部分")
    fi
    
    # 检查是否有结论部分
    if ! grep -q "^## 5\. 结论和建议" "$file"; then
        issues+=("缺少'结论和建议'部分")
    fi
    
    # 检查是否有参考资料
    if ! grep -q "^## 6\. 参考资料" "$file"; then
        issues+=("缺少'参考资料'部分")
    fi
    
    if [ ${#issues[@]} -gt 0 ]; then
        echo -e "${YELLOW}⚠️  发现以下格式问题:${NC}"
        for issue in "${issues[@]}"; do
            echo "  - $issue"
        done
        return 1
    else
        echo -e "${GREEN}✅ 报告格式正确${NC}"
        return 0
    fi
}

# 主逻辑
case "${1:-help}" in
    "test")
        test_skill
        ;;
    "search")
        quick_search "$2"
        ;;
    "validate")
        validate_report "$2"
        ;;
    "help"|*)
        show_help
        ;;
esac