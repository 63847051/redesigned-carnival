#!/bin/bash
# 启动小蓝子 agent

SESSION_KEY="xiaolan-blueprint"
MODEL="glm-4-flash"  # 使用便宜的 Flash 模型

echo "🚀 启动小蓝子 agent..."
echo "   模型: $MODEL"
echo "   会话: $SESSION_KEY"

# 使用 sessions_spawn 创建持久化子 agent
# 注意:这需要通过 OpenClaw API 调用,不是直接执行
# 这里只是配置文件

cat > /tmp/xiaolan-config.json << EOF
{
  "label": "小蓝",
  "agentId": "xiaolan",
  "model": "$MODEL",
  "task": "你是小蓝,蓝色光标工作日志专家。参考 /root/.openclaw/workspace/agents/xiaolan-profile.md",
  "mode": "session",
  "thread": true,
  "runtime": "subagent"
}
EOF

echo "配置已生成: /tmp/xiaolan-config.json"
echo "请通过 OpenClaw sessions_spawn API 启动"
