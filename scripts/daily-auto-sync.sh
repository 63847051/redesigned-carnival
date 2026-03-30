#!/bin/bash
# 每日自动同步脚本
# 同步 .context/ 到 memory/

echo "=== 每日自动同步 ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"

# 执行同步
python3 /root/.openclaw/workspace/scripts/memory-sync-coordinator.py --auto

echo "=== 同步完成 ==="
