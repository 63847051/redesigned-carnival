#!/bin/bash
# =============================================================================
# 📊 股票查询工具（网易财经版）
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

# 判断市场
if [[ "$STOCK_CODE" =~ ^6 ]]; then
    STOCK_CODE="0$STOCK_CODE"
    MARKET="上海"
elif [[ "$STOCK_CODE" =~ ^0 ]] || [[ "$STOCK_CODE" =~ ^3 ]]; then
    STOCK_CODE="1$STOCK_CODE"
    MARKET="深圳"
fi

echo "所属市场: $MARKET 证券交易所"
echo ""
echo "🔍 正在查询股票信息..."
echo ""

# 使用网易财经 API
# 格式：http://money.163.com/special/1004241/\$data.js
# 或者直接使用简化接口
WANGYI_URL="http://api.money.126.net/data/feed/$STOCK_CODE,${STOCK_CODE:0:2}${STOCK_CODE:1}"

# 获取数据
STOCK_DATA=$(curl -s "$WANGYI_URL")

if [ -z "$STOCK_DATA" ]; then
    echo "❌ 无法获取股票数据，请检查网络连接"
    exit 1
fi

# 提取股票名称和价格（网易返回 JSON 格式）
STOCK_NAME=$(echo "$STOCK_DATA" | grep -oP '(?<="name":")[^"]+')
CURRENT_PRICE=$(echo "$STOCK_DATA" | grep -oP '(?<="price":)[0-9.]+')
YESTERDAY_CLOSE=$(echo "$STOCK_DATA" | grep -oP '(?<="yestclose":)[0-9.]+')
OPEN_PRICE=$(echo "$STOCK_DATA" | grep -oP '(?<="open":)[0-9.]+')
HIGH_PRICE=$(echo "$STOCK_DATA" | grep -oP '(?<="high":)[0-9.]+')
LOW_PRICE=$(echo "$STOCK_DATA" | grep -oP '(?<="low":)[0-9.]+')
VOLUME=$(echo "$STOCK_DATA" | grep -oP '(?<="volume":)[0-9.]+')
TURNOVER=$(echo "$STOCK_DATA" | grep -oP '(?<="turnover":)[0-9.]+')

if [ -z "$CURRENT_PRICE" ]; then
    echo "❌ 未找到该股票，请确认代码是否正确"
    echo ""
    echo "提示："
    echo "  - 上海股票以 6 开头（如 600318）"
    echo "  - 深圳股票以 0 或 3 开头（如 000001）"
    exit 1
fi

# 计算涨跌额和涨跌幅
if [ -n "$YESTERDAY_CLOSE" ] && [ "$YESTERDAY_CLOSE" != "0" ]; then
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
echo "股票代码: ${STOCK_CODE:1}"
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

# 成交额（转换为万元）
if [ -n "$TURNOVER" ] && [ "$TURNOVER" != "0" ]; then
    TURNOVER_WAN=$(awk "BEGIN {printf \"%.2f\", $TURNOVER / 10000}")
    echo "成交额: $TURNOVER_WAN 万元"
fi

echo ""
echo "======================================"
echo "⏰ 查询时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "💡 提示："
echo "  - 数据来源于网易财经"
echo "  - 可能有 15-20 分钟延迟"
echo "  - 仅供参考，不构成投资建议"
