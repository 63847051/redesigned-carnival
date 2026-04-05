#!/bin/bash
# =============================================================================
# 📊 股票查询工具（修复版）
# =============================================================================
# 功能：查询中国 A 股实时价格和基本信息
# 使用：./stock-query-final.sh <股票代码>
# =============================================================================

STOCK_CODE="$1"

if [ -z "$STOCK_CODE" ]; then
    echo "❌ 请提供股票代码"
    echo ""
    echo "用法: $0 <股票代码>"
    echo ""
    echo "示例:"
    echo "  $0 600318  # 中国平安"
    echo "  $0 000001  # 平安银行"
    echo "  $0 600519  # 贵州茅台"
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
elif [[ "$STOCK_CODE" =~ ^0 ]] || [[ "$STOCK_CODE" =~ ^3 ]]; then
    STOCK_CODE="sz$STOCK_CODE"
fi

echo "🔍 正在查询股票信息..."
echo ""

# 使用腾讯财经 API
TENCENT_URL="http://qt.gtimg.cn/q=$STOCK_CODE"

# 获取数据（不转换编码，直接处理）
STOCK_DATA=$(curl -s "$TENCENT_URL")

if [ -z "$STOCK_DATA" ]; then
    echo "❌ 无法获取股票数据，请检查网络连接"
    exit 1
fi

# 提取数值数据（避免中文编码问题）
# 格式：v_sh600318="1~名称~代码~当前价~昨收~今开~最高~最低~..."
CURRENT_PRICE=$(echo "$STOCK_DATA" | grep -oP '(?<=~)[0-9.]+(?=~)' | sed -n '4p')
YESTERDAY_CLOSE=$(echo "$STOCK_DATA" | grep -oP '(?<=~)[0-9.]+(?=~)' | sed -n '5p')
OPEN_PRICE=$(echo "$STOCK_DATA" | grep -oP '(?<=~)[0-9.]+(?=~)' | sed -n '6p')
HIGH_PRICE=$(echo "$STOCK_DATA" | grep -oP '(?<=~)[0-9.]+(?=~)' | sed -n '7p')
LOW_PRICE=$(echo "$STOCK_DATA" | grep -oP '(?<=~)[0-9.]+(?=~)' | sed -n '8p')
BUY_PRICE=$(echo "$STOCK_DATA" | grep -oP '(?<=~)[0-9.]+(?=~)' | sed -n '10p')
SELL_PRICE=$(echo "$STOCK_DATA" | grep -oP '(?<=~)[0-9.]+(?=~)' | sed -n '11p')
VOLUME=$(echo "$STOCK_DATA" | grep -oP '(?<=~)[0-9.]+(?=~)' | sed -n '9p')
TURNOVER=$(echo "$STOCK_DATA" | grep -oP '(?<=~)[0-9.]+(?=~)' | sed -n '10p')

if [ -z "$CURRENT_PRICE" ] || [ "$CURRENT_PRICE" = "0.000" ]; then
    echo "❌ 未找到该股票，请确认代码是否正确"
    exit 1
fi

# 计算涨跌额和涨跌幅
if [ "$YESTERDAY_CLOSE" != "0.000" ] && [ -n "$YESTERDAY_CLOSE" ]; then
    CHANGE=$(awk "BEGIN {printf \"%.2f\", $CURRENT_PRICE - $YESTERDAY_CLOSE}")
    CHANGE_PERCENT=$(awk "BEGIN {printf \"%.2f\", ($CURRENT_PRICE - $YESTERDAY_CLOSE) / $YESTERDAY_CLOSE * 100}")
else
    CHANGE="N/A"
    CHANGE_PERCENT="N/A"
fi

# 显示结果
echo "📈 股票信息"
echo "======================================"
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
