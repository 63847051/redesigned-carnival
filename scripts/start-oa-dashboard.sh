#!/bin/bash
# OA Dashboard 启动脚本

echo "🚀 启动 OA Dashboard..."

# 停止旧的进程
pkill -9 -f "oa serve" 2>/dev/null
pkill -9 -f "oa-proxy.py" 2>/dev/null

# 启动 OA Dashboard（监听所有接口）
cd /root/.openclaw/workspace/oa-project

# 使用 python HTTPServer 监听所有接口
python3 -c "
import http.server
import socket
import urllib.request
import sys

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = 'http://127.0.0.1:8081' + self.path
        try:
            response = urllib.request.urlopen(path)
            self.send_response(response.status)
            for h, v in response.headers.items():
                if h.lower() != 'transfer-encoding':
                    self.send_header(h, v)
            self.end_headers()
            self.wfile.write(response.read())
        except Exception as e:
            self.send_error(502, str(e))
    
    def log_message(self, fmt, *args):
        pass

server = http.server.HTTPServer(('0.0.0.0', 8080), ProxyHandler)
print('OA Dashboard Proxy running at http://0.0.0.0:8080')
print('Forwarding to http://127.0.0.1:8081')
print('External access: http://43.134.63.176:8080')
server.serve_forever()
" &
OA_PROXY_PID=$!

# 启动 OA Dashboard（本地）
sleep 2
oa serve --port 8081 --no-open &
OA_DASHBOARD_PID=$!

echo "✅ OA Dashboard 已启动！"
echo "📊 访问地址: http://43.134.63.176:8080"
echo "🔧 代理进程 PID: $OA_PROXY_PID"
echo "🎯 Dashboard PID: $OA_DASHBOARD_PID"

# 保存 PID
echo $OA_PROXY_PID > /tmp/oa-proxy.pid
echo $OA_DASHBOARD_PID > /tmp/oa-dashboard.pid
