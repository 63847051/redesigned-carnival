#!/bin/bash
# 定时进化学习配置
# 每 6 小时自动运行进化学习

# 添加到 crontab
(crontab -l 2>/dev/null; echo "0 */6 * * * bash /root/.openclaw/workspace/scripts/self-evolution-system.sh >> /root/.openclaw/logs/evolution.log 2>&1") | crontab -

echo "✅ 定时进化学习已配置"
echo "   - 运行频率: 每 6 小时"
echo "   - 日志位置: /root/.openclaw/logs/evolution.log"
echo "   - 下次运行: $(date -d '+6 hours' '+%Y-%m-%d %H:%M:%S')"
