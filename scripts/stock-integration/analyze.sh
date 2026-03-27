#!/bin/bash
# 股票分析快捷脚本（增强版）

# 使用说明
usage() {
    echo "使用方法: $0 [选项] <股票代码>..."
    echo ""
    echo "选项:"
    echo "  -q, --quantitative  量化分析（包含预测）"
    echo "  -b, --brief         基本分析（仅数据）"
    echo "  -h, --help          显示帮助"
    echo ""
    echo "示例:"
    echo "  # 量化分析（推荐）"
    echo "  $0 -q SH600000"
    echo ""
    echo "  # 基本分析"
    echo "  $0 -b SH600000"
    echo ""
    echo "  # 批量量化分析"
    echo "  $0 -q SH600000 SH600519 SZ00700"
    echo ""
    exit 1
}

# 默认模式
MODE="quantitative"

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -q|--quantitative)
            MODE="quantitative"
            shift
            ;;
        -b|--brief)
            MODE="brief"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            break
            ;;
    esac
done

# 检查股票代码
if [ -z "$1" ]; then
    usage
fi

# 脚本目录
SCRIPT_DIR="/root/.openclaw/workspace/scripts/stock-integration"
PYTHON_BIN="/root/.openclaw/workspace/mcp-cn-a-stock/venv/bin/python3"

# 分析函数
analyze_stock() {
    local stock=$1
    local mode=$2
    
    echo "========================================"
    echo "分析: $stock (模式: $mode)"
    echo "========================================"
    
    cd "$SCRIPT_DIR"
    if [ "$mode" = "quantitative" ]; then
        $PYTHON_BIN quantitative_analysis.py "$stock"
    else
        $PYTHON_BIN integrated_analysis.py "$stock"
    fi
    
    echo ""
}

# 分析单只或多只股票
for stock in "$@"; do
    analyze_stock "$stock" "$MODE"
done

echo "✅ 分析完成！"
echo ""
echo "报告位置: /root/.openclaw/workspace/stock-reports/"
ls -lh /root/.openclaw/workspace/stock-reports/ | tail -5
