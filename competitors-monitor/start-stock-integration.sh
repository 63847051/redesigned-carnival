#!/bin/bash
# 股票分析系统快速集成启动脚本

echo "🚀 启动股票分析系统快速集成..."
echo ""

# 检查依赖
echo "📋 检查依赖..."

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 检查 Flask
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask 未安装，正在安装..."
    pip install flask
fi

echo "✅ 依赖检查完成"
echo ""

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p /root/.openclaw/workspace/competitors-monitor/data
echo "✅ 数据目录创建完成"
echo ""

# 启动 Webhook 接收端
echo "📡 启动 Webhook 接收端..."
cd /root/.openclaw/workspace/competitors-monitor

# 后台运行
nohup python3 webhook-receiver.py > webhook-receiver.log 2>&1 &
RECEIVER_PID=$!

echo "✅ Webhook 接收端已启动 (PID: $RECEIVER_PID)"
echo ""

# 等待启动
sleep 2

# 健康检查
echo "❤️ 健康检查..."
HEALTH_CHECK=$(curl -s http://127.0.0.1:5001/health)

if [ $? -eq 0 ]; then
    echo "✅ Webhook 接收端运行正常"
else
    echo "❌ Webhook 接收端启动失败"
    exit 1
fi

echo ""
echo "🎉 快速集成启动完成！"
echo ""
echo "📡 Webhook URL: http://127.0.0.1:5001/webhook/stock"
echo "📊 报告查询: http://127.0.0.1:5001/webhook/stock/reports"
echo "📝 查看日志: tail -f webhook-receiver.log"
echo ""
echo "💡 下一步："
echo "1. 启动股票分析系统: cd daily_stock_analysis && python main.py --webui"
echo "2. 在股票分析系统配置 Webhook: MONITOR_WEBHOOK_URL=http://127.0.0.1:5001/webhook/stock"
echo "3. 运行插件: python3 plugins/stock-ai.py"
echo ""
