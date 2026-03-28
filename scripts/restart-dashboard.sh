#!/bin/bash
# 修改 UI 监听地址为所有网络接口

# 停止当前进程
pkill -f "node --import tsx src/index.ts"

# 设置环境变量
export UI_HOST="0.0.0.0"

# 重新启动
cd /root/.openclaw/workspace/openclaw-control-center
UI_MODE=true npm run dev:ui > /tmp/dashboard-ui.log 2>&1 &

echo "✅ UI 已重新启动"
echo "访问地址:"
echo "  公网: http://43.134.63.176:4310"
echo "  本地: http://127.0.0.1:4310"
echo ""
echo "等待 5 秒后测试连接..."
sleep 5

# 测试连接
if curl -s http://localhost:4310 >/dev/null; then
    echo "✅ UI 启动成功！"
else
    echo "❌ UI 启动失败"
    echo "请检查日志: cat /tmp/dashboard-ui.log"
fi
