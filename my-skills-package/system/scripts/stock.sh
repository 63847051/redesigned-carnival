#!/bin/bash
# =============================================================================
# 📊 股票查询工具（专业版）
# =============================================================================
# 功能：查询中国 A 股实时价格和基本信息
# 使用：./stock.sh <股票代码>
# =============================================================================

STOCK_CODE="$1"

if [ -z "$STOCK_CODE" ]; then
    cat << 'EOF'
📊 股票查询工具
======================================
❌ 请提供股票代码

用法: ./stock.sh <股票代码>

示例:
  ./stock.sh 600318  # 中国平安
  ./stock.sh 000001  # 平安银行
  ./stock.sh 600519  # 贵州茅台
EOF
    exit 1
fi

echo "📊 股票查询工具"
echo "======================================"
echo "股票代码: $STOCK_CODE"
echo ""

# 清理代码格式
STOCK_CODE=$(echo "$STOCK_CODE" | grep -o '[0-9]\{6\}')

if [ -z "$STOCK_CODE" ]; then
    echo "❌ 无效的股票代码格式"
    exit 1
fi

# 判断市场并添加前缀
if [[ "$STOCK_CODE" =~ ^6 ]]; then
    STOCK_CODE="sh$STOCK_CODE"
    MARKET="上海"
elif [[ "$STOCK_CODE" =~ ^0 ]] || [[ "$STOCK_CODE" =~ ^3 ]]; then
    STOCK_CODE="sz$STOCK_CODE"
    MARKET="深圳"
fi

echo "所属市场: $MARKET 证券交易所"
echo ""
echo "🔍 正在查询股票信息..."
echo ""

# 使用腾讯财经 API
TENCENT_URL="http://qt.gtimg.cn/q=$STOCK_CODE"

# 获取数据
STOCK_DATA=$(curl -s "$TENCENT_URL")

if [ -z "$STOCK_DATA" ]; then
    echo "❌ 无法获取股票数据，请检查网络连接"
    exit 1
fi

# 提取数据段（去掉前面的 "v_sh600318=" 和后面的引号）
DATA_SEGMENT=$(echo "$STOCK_DATA" | sed 's/^[^"]*"\(.*\)"$/\1/')

# 使用 ~ 作为分隔符
IFS='~' read -ra FIELDS <<< "$DATA_SEGMENT"

# 腾讯 API 数据格式：
# 0: 未知
# 1: 股票名称（中文，可能有编码问题）
# 2: 股票代码
# 3: 当前价
# 4: 昨收价
# 5: 今开价
# 6: 最高价
# 7: 最低价
# 8: 成交量
# 9-17: 买卖盘
# 18: 日期时间
# 19: 涨跌额
# 20: 涨跌幅%

CURRENT_PRICE="${FIELDS[3]}"
YESTERDAY_CLOSE="${FIELDS[4]}"
OPEN_PRICE="${FIELDS[5]}"
HIGH_PRICE="${FIELDS[6]}"
LOW_PRICE="${FIELDS[7]}"
VOLUME="${FIELDS[8]}"
CHANGE="${FIELDS[19]}"
CHANGE_PERCENT="${FIELDS[20]}"

if [ -z "$CURRENT_PRICE" ] || [ "$CURRENT_PRICE" = "" ] || [ "$CURRENT_PRICE" = "0.00" ]; then
    echo "❌ 未找到该股票，请确认代码是否正确"
    echo ""
    echo "提示："
    echo "  - 上海股票以 6 开头（如 600318）"
    echo "  - 深圳股票以 0 或 3 开头（如 000001）"
    exit 1
fi

# 显示结果
echo "📈 股票信息"
echo "======================================"
echo "股票代码: ${STOCK_CODE:0:2}${STOCK_CODE:2}"
echo ""
echo "💰 价格信息"
echo "--------------------------------------"
printf "当前价格: ¥%.2f\n" "$CURRENT_PRICE"
printf "昨收价格: ¥%.2f\n" "$YESTERDAY_CLOSE"
printf "涨    额: ¥%.2f\n" "$CHANGE"
printf "涨    跌: %.2f%%\n" "$CHANGE_PERCENT"

# 判断涨跌
if awk "BEGIN {exit !($CHANGE > 0)}"; then
    echo "状态: 📈 上涨"
elif awk "BEGIN {exit !($CHANGE < 0)}"; then
    echo "状态: 📉 下跌"
else
    echo "状态: ➡️ 平盘"
fi

echo ""
echo "📊 详细数据"
echo "--------------------------------------"
printf "今开价格: ¥%.2f\n" "$OPEN_PRICE"
printf "最高价格: ¥%.2f\n" "$HIGH_PRICE"
printf "最低价格: ¥%.2f\n" "$LOW_PRICE"
echo ""

# 成交量（转换为手）
if [ -n "$VOLUME" ] && [ "$VOLUME" != "0" ]; then
    VOLUME_HANDS=$(awk "BEGIN {printf \"%.0f\", $VOLUME / 100}")
    echo "成交量: $VOLUME_HANDS 手"
fi

echo ""
echo "======================================"
echo "⏰ 查询时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "💡 提示："
echo "  - 数据来源于腾讯财经"
echo "  - 可能有 15-20 分钟延迟"
echo "  - 仅供参考，不构成投资建议"
echo ""
echo "📊 常用股票："
echo "  600519  贵州茅台    600036  招商银行"
echo "  000001  平安银行    000002  万科A"
echo "  600036  招商银行    600276  恒瑞医药"
