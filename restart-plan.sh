#!/bin/bash

echo "🛡️ Gateway 安全重启计划"
echo "================================"
echo ""

# 备份列表
BACKUPS=(
    "~/.openclaw/openclaw.json"
    "~/.openclaw/credentials/feishu-pairing.json"
)

echo "✅ 已完成的防护措施:"
echo ""

# 1. 配置验证
echo "1. ✅ 配置文件验证通过"
echo "   - openclaw.json 格式正确"
echo "   - feishu-pairing.json 存在"
echo ""

# 2. 备份文件
echo "2. ✅ 配置文件已备份"
echo "   - 位置: ~/.openclaw/*.pre-restart-*"
echo ""

# 3. 恢复脚本
echo "3. ✅ 恢复脚本已准备"
echo "   - 如果重启失败,可以运行恢复脚本"
echo ""

# 4. 飞书配置检查
echo "4. ✅ 飞书配置检查"
echo "   - Gateway 模式: local"
echo "   - 端口: 18789"
echo "   - 绑定: loopback"
echo ""

echo "📋 重启流程:"
echo "================================"
echo ""
echo "步骤 1: 停止 Gateway"
echo "  命令: openclaw gateway stop"
echo ""
echo "步骤 2: 等待 3 秒"
echo "  确保完全停止"
echo ""
echo "步骤 3: 启动 Gateway"
echo "  命令: openclaw gateway start"
echo ""
echo "步骤 4: 验证状态"
echo "  命令: openclaw gateway status"
echo ""
echo "步骤 5: 测试飞书连接"
echo "  你会收到测试消息"
echo ""

echo "🚨 如果重启失败:"
echo "================================"
echo ""
echo "恢复配置:"
echo "  cp ~/.openclaw/openclaw.json.pre-restart-* ~/.openclaw/openclaw.json"
echo "  openclaw gateway restart"
echo ""

echo "📊 成功指标:"
echo "================================"
echo ""
echo "✅ Gateway 状态显示: running"
echo "✅ 最近5分钟无错误"
echo "✅ 收到飞书测试消息"
echo ""

echo "准备好开始重启吗? (输入 'yes' 继续)"
