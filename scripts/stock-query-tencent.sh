#!/bin/bash
# =============================================================================
# 📊 股票查询工具（腾讯财经 API）
# =============================================================================
# 功能：查询中国 A 股实时价格和基本信息
# 使用：./stock-query-tencent.sh <股票代码>
# =============================================================================

STOCK_CODE="$1"

if [ -z "$STOCK_CODE" ]; then
    echo "❌ 请提供股票代码"
    echo ""
    echo "用法: $0 <股票代码>"
    echo ""
    echo "示例:"
    echo "  $0 sh600318  # 中国平安"
    echo "  $0 sz000001  # 平安银行"
    echo "  $0 sh600519  # 贵州茅台"
    exit 1
fi

echo "📊 股票查询工具"
echo "======================================"
echo "股票代码: $STOCK_CODE"
echo ""

# 清理代码格式
STOCK_CODE=$(echo "$STOCK_CODE" | tr '[:lower:]' '[:upper:]')

# 判断市场并添加前缀
if [[ ! "$STOCK_CODE" =~ ^[shSH][szSZ] ]]; then
    if [[ "$STOCK_CODE" =~ ^6 ]]; then
        STOCK_CODE="sh$STOCK_CODE"
    elif [[ "$STOCK_CODE" =~ ^0 ]] || [[ "$STOCK_CODE" =~ ^3 ]]; then
        STOCK_CODE="sz$STOCK_CODE"
    fi
fi

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

# 检查是否有数据
if [[ "$STOCK_DATA" =~ ~ ]]; then
    echo "❌ 未找到该股票，请确认代码是否正确"
    echo ""
    echo "提示："
    echo "  - 上海股票以 6 开头（如 600318）"
    echo "  - 深圳股票以 0 或 3 开头（如 000001）"
    exit 1
fi

# 解析数据（腾讯返回格式：v_name="股票名,当前价,昨收,..."）
STOCK_NAME=$(echo "$STOCK_DATA" | grep -oP '(?<=v_)[^=]+(?==)')
STOCK_INFO=$(echo "$STOCK_DATA" | grep -oP '(?<==")[^"]+')

# 分割数据
IFS=',' read -ra DATA <<< "$STOCK_INFO"

STOCK_NAME="${DATA[0]}"
CURRENT_PRICE="${DATA[1]}"
YESTERDAY_CLOSE="${DATA[2]}"
OPEN_PRICE="${DATA[3]}"
HIGH_PRICE="${DATA[4]}"
LOW_PRICE="${DATA[5]}"
BUY_PRICE="${DATA[6]}"
SELL_PRICE="${DATA[7]}"
VOLUME="${DATA[8]}"
TURNOVER="${DATA[9]}"

if [ -z "$CURRENT_PRICE" ] || [ "$CURRENT_PRICE" = "0.000" ]; then
    echo "❌ 无法解析股票数据"
    exit 1
fi

# 计算涨跌额和涨跌幅
if [ "$YESTERDAY_CLOSE" != "0.000" ]; then
    CHANGE=$(awk "BEGIN {printf \"%.2f\", $CURRENT_PRICE - $YESTERDAY_CLOSE}")
    CHANGE_PERCENT=$(awk "BEGIN {printf \"%.2f\", ($CURRENT_PRICE - $YESTERDAY_CLOSE) / $YESTERDAY_CLOSE * 100}")
else
    CHANGE="N/A"
    CHANGE_PERCENT="N/A"
fi

# 显示结果
echo "📈 股票信息"
echo "======================================"
echo "股票名称: $STOCK_NAME"
echo "股票代码: ${STOCK_CODE:0:2}${STOCK_CODE:2}"
echo ""
echo "💰 价格信息"
echo "--------------------------------------"
echo "当前价格: ¥$CURRENT_PRICE"
echo "昨收价格: ¥$YESTERDAY_CLOSE"
echo "涨    额: ¥$CHANGE"
echo "涨    跌: $CHANGE_PERCENT%"

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
echo "今开价格: ¥$OPEN_PRICE"
echo "最高价格: ¥$HIGH_PRICE"
echo "最低价格: ¥$LOW_PRICE"
echo "买一价格: ¥$BUY_PRICE"
echo "卖一价格: ¥$SELL_PRICE"
echo ""

# 成交量（转换为手）
if [ -n "$VOLUME" ] && [ "$VOLUME" != "0" ]; then
    VOLUME_HANDS=$(awk "BEGIN {printf \"%.0f\", $VOLUME / 100}")
    echo "成交量: $VOLUME_HANDS 手"
fi

# 成交额（转换为万元）
if [ -n "$TURNOVER" ] && [ "$TURNOVER" != "0.00" ]; then
    TURNOVER_WAN=$(awk "BEGIN {printf \"%.2f\", $TURNOVER / 10000}")
    echo "成交额: $TURNOVER_WAN 万元"
fi

echo ""
echo "======================================"
echo "⏰ 查询时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "💡 提示："
echo "  - 数据来源于腾讯财经"
echo "  - 可能有 15-20 分钟延迟"
echo "  - 仅供参考，不构成投资建议"
