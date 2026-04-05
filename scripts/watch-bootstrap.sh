#!/bin/bash
###############################################################################
# 监听 SOUL 人格文件变化并自动热重载
# 功能：检测文件变化，防抖 2 秒，自动重新加载人格
###############################################################################

echo "👁️ 开始监听 SOUL 人格文件..."
echo "📁 目录: /root/.openclaw/openclaw/workspace"
echo "⏰ 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查是否安装了 inotify-tools
if ! command -v inotifywait &> /dev/null; then
  echo "❌ 错误: 未安装 inotify-tools"
  echo "💡 安装方法:"
  echo "   apt-get install inotify-tools"
  echo ""
  echo "💡 临时方案：使用轮询模式（每 30 秒检查一次）"
  echo ""
  echo "🔄 启动轮询模式..."
  
  while true; do
    # 检查文件变化
    current_sum=$(find /root/.openclaw/openclaw/workspace -name "SOUL.md" -o -name "IDENTITY.md" -o -name "USER.md" -o -name "AGENTS.md" -exec wc -c {} \; | awk '{sum+=$1} END')
    
    # 记录上次检查的总和
    if [ -z "$last_sum" ]; then
      last_sum=$current_sum
    fi
    
    # 检查是否变化
    if [ "$current_sum" != "$last_sum" ]; then
      echo ""
      echo "🔥 检测到人格文件变化！"
      echo "📊 新的总字符数: $current_sum"
      echo "🔄 重新加载 SOUL 人格..."
      
      # 重新加载
      bash /root/.openclaw/workspace/scripts/hot-reload-bootstrap.sh
      
      last_sum=$current_sum
      echo "✅ 热重载完成"
      echo "---"
    fi
    
    # 等待 30 秒
    sleep 30
  done
fi

echo "🔍 启动 inotifywait 监听..."
echo ""

# 使用 inotifywait 监听文件变化
# 格式: <watch> <file> <event>
# 我们监听 modify 事件
inotifywait -m -e modify \
  /root/.openclaw/workspace/SOUL.md \
  /root/.openclaw/workspace/IDENTITY.md \
  /root/.openclaw/workspace/USER.md \
  /root/.claw/workspace/AGENTS.md |
  while read event; do
  # 解析事件
  watch_file=$(echo "$event" | awk '{print $1}')
  event_type=$(echo "$event" | awk '{print $2}')
  timestamp=$(echo "$event" | awk '{print $3}')
  
  # 只处理修改事件
  if [ "$event_type" = "MODIFY" ]; then
    echo ""
    echo "🔥 检测到文件变化:"
    echo "  文件: $watch_file"
    echo "  事件: $event_type"
    echo "  时间: $(date -d @$timestamp '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # 防抖：等待 2 秒
    echo "⏳ 防抖中（2 秒）..."
    sleep 2
    
    # 重新加载人格
    echo "🔄 重新加载 SOUL 人格..."
    bash /root/.openclaw/workspace/scripts/hot-reload-bootstrap.sh
    
    echo "✅ 热重载完成"
    echo "---"
  fi
done
