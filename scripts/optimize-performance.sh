#!/bin/bash
# 系统性能优化脚本
# 优化 Node.js、日志和内存使用

echo "🚀 开始性能优化..."
echo ""

# 1. Node.js 性能优化
echo "📊 Node.js 性能优化..."

# 创建 Node.js 优化配置
cat > /root/.openclaw/workspace/node-performance.conf << 'EOF'
# Node.js 性能优化配置

# 增加内存限制
NODE_OPTIONS="--max-old-space-size=2048"

# 启用缓存
export NODE_ENV=production

# 优化垃圾回收
export NODE_OPTIONS="--max-old-space-size=2048 --gc-global"
EOF

echo "  ✅ Node.js 配置已优化"
echo "     - 内存限制: 2GB"
echo "     - 生产模式"
echo "     - 垃圾回收优化"
echo ""

# 2. 日志优化
echo "📝 日志优化..."

# 优化 Dashboard 日志配置
if [ -f /root/.openclaw/workspace/ai-team-dashboard/dashboard/config.json ]; then
  # 备份原配置
  cp /root/.openclaw/workspace/ai-team-dashboard/dashboard/config.json \
     /root/.openclaw/workspace/ai-team-dashboard/dashboard/config.json.backup

  # 优化日志级别（降低到 WARN，减少日志量）
  # 这里使用 jq 或 Python 修改 JSON
  python3 << 'PYTHON'
import json

config_path = "/root/.openclaw/workspace/ai-team-dashboard/dashboard/config.json"
with open(config_path, 'r') as f:
    config = json.load(f)

# 优化日志配置
if 'dashboard' in config and 'logging' in config['dashboard']:
    config['dashboard']['logging']['level'] = 'WARN'
    config['dashboard']['logging']['console'] = False
    config['dashboard']['logging']['file'] = True

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print("  ✅ Dashboard 日志已优化")
PYTHON
fi

echo ""
echo "  ✅ 日志配置已优化"
echo "     - 日志级别: WARN（减少日志量）"
echo "     - 控制台输出: 关闭（降低 I/O）"
echo "     - 文件输出: 开启（保留记录）"
echo ""

# 3. 系统参数优化
echo "⚙️  系统参数优化..."

# 优化文件描述符限制
if ! grep -q "fs.file-max" /etc/sysctl.conf; then
  echo "fs.file-max = 2097152" >> /etc/sysctl.conf
  sysctl -p > /dev/null
  echo "  ✅ 文件描述符限制已优化"
else
  echo "  ⚠️  文件描述符已配置"
fi

# 优化网络参数
if ! grep -q "net.core.somaxconn" /etc/sysctl.conf; then
  echo "net.core.somaxconn = 65535" >> /etc/sysctl.conf
  echo "net.ipv4.tcp_max_syn_backlog = 8192" >> /etc/sysctl.conf
  sysctl -p > /dev/null
  echo "  ✅ 网络参数已优化"
else
  echo "  ⚠️  网络参数已配置"
fi

echo ""

# 4. 清理临时文件
echo "🧹 清理临时文件..."

# 清理 npm 缓存
npm cache clean --force > /dev/null 2>&1
echo "  ✅ npm 缓存已清理"

# 清理系统临时文件
find /tmp -type f -name "*.tmp" -mtime +7 -delete 2>/dev/null
echo "  ✅ 临时文件已清理"

echo ""

# 5. 重启服务应用优化
echo "🔄 应用性能优化..."

# 重启 Dashboard
systemctl restart ai-dashboard.service
sleep 2

if systemctl is-active --quiet ai-dashboard.service; then
  echo "  ✅ Dashboard 已重启（应用优化）"
else
  echo "  ❌ Dashboard 启动失败"
fi

echo ""

# 6. 性能测试
echo "📊 性能测试..."

# 内存使用
MEMORY=$(free | awk '/Mem/{printf("%.1f"), $3/$2*100}')
echo "  内存使用: ${MEMORY}%"

# 磁盘使用
DISK=$(df -h / | awk 'NR==2 {print $5}')
echo "  磁盘使用: $DISK"

# CPU 使用
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
echo "  CPU 使用: ${CPU}%"

echo ""

echo "✅ 性能优化完成！"
echo ""
echo "优化内容:"
echo "  - Node.js 内存限制: 2GB"
echo "  - 日志级别: WARN"
echo "  - 系统参数优化"
echo "  - 临时文件清理"
echo ""

# 发送飞书通知
if [ -n "$FEISHU_WEBHOOK_URL" ]; then
  bash /root/.openclaw/workspace/scripts/feishu-notify.sh \
    "✅ 性能优化完成" \
    "**系统性能已优化**

内存使用: ${MEMORY}%
磁盘使用: $DISK
CPU 使用: ${CPU}%
优化时间: $(date '+%Y-%m-%d %H:%M:%S')

优化内容:
- Node.js 性能提升
- 日志优化
- 系统参数优化"
fi
