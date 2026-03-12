#!/bin/bash
# 天气查询脚本
# 查询上海宝山天气

LOCATION="上海"
TIMEOUT=10

echo "🌤️ 查询 ${LOCATION} 天气..."
echo ""

# 尝试 wttr.in
echo "📡 正在获取天气数据..."
weather_data=$(curl -s --max-time $TIMEOUT "wttr.in/${LOCATION}?format=3" 2>/dev/null)

if [ -n "$weather_data" ]; then
    echo "📍 当前天气：${weather_data}"
    echo ""
    echo "📅 详细预报："
    curl -s --max-time $TIMEOUT "wttr.in/${LOCATION}?T" 2>/dev/null | head -20
else
    echo "⚠️ 天气服务暂时不可用"
    echo ""
    echo "💡 替代方案："
    echo "  - 访问: https://wttr.in/上海"
    echo "  - 查询: \"上海宝山天气\""
fi

echo ""
echo "✅ 天气查询完成"
