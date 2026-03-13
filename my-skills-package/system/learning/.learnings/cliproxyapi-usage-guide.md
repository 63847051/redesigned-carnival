# CLIProxyAPI使用指南

**部署时间**: 2026-03-08 22:43
**服务端口**: 8317
**访问地址**: http://43.134.63.176:8317

---

## 🌐 访问方式

### 1. 本地访问（服务器上）

**管理界面**: http://localhost:8317

**API端点**:
- `POST http://localhost:8317/v1/chat/completions` - 对话
- `POST http://localhost:8317/v1/completions` - 补全
- `GET http://localhost:8317/v1/models` - 模型列表

### 2. 远程访问（外部）

**管理界面**: http://43.134.63.176:8317

**⚠️ 需要开放防火墙端口**:
```bash
# 腾讯云控制台
# 安全组 → 添加规则 → 端口8317
```

---

## 🚀 使用方式

### 方式1: Web管理界面（推荐）

**启动TUI管理界面**:
```bash
cd /opt/CLIProxyAPI
./cliproxyapi -tui
```

**功能**:
- ✅ 可视化管理
- ✅ OAuth登录
- ✅ 账户管理
- ✅ 配置编辑

### 方式2: v5.2轻量级接口

**位置**: `/root/.openclaw/workspace/scripts/free-model-caller.sh`

**检查状态**:
```bash
bash /root/.openclaw/workspace/scripts/free-model-caller.sh status
```

**调用模型**:
```bash
bash /root/.openclaw/workspace/scripts/free-model-caller.sh call \
  gemini-2.5-pro \
  "写一个Python快速排序算法"
```

**自动任务**:
```bash
bash /root/.openclaw/workspace/scripts/free-model-caller.sh auto \
  "代码" \
  "写一个二叉树遍历函数" \
  "medium"
```

### 方式3: 直接API调用

**调用Gemini 2.5 Pro**:
```bash
curl -X POST http://localhost:8317/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.5-pro",
    "messages": [
      {"role": "user", "content": "写一个Python函数"}
    ]
  }'
```

**查看可用模型**:
```bash
curl http://localhost:8317/v1/models
```

---

## 🔧 配置OAuth账户

### 重要：获取无限免费额度

**当前模式**: standalone（有限制）

**完整功能**: 需要配置OAuth

### 配置步骤

#### 1. Google OAuth（Gemini）

**启动OAuth登录**:
```bash
cd /opt/CLIProxyAPI
./cliproxyapi -login
```

**流程**:
1. 浏览器自动打开
2. 登录Google账号
3. 授权访问
4. 完成认证

**多账户**:
```bash
# 重复执行，添加多个账户
./cliproxyapi -login
```

#### 2. OpenAI OAuth（GPT）

```bash
./cliproxyapi -codex-login
```

#### 3. Anthropic OAuth（Claude）

```bash
./cliproxyapi -claude-login
```

#### 4. 阿里OAuth（Qwen）

```bash
./cliproxyapi -qwen-login
```

---

## 📊 服务管理

### 启动服务

**方式1: 管理脚本**:
```bash
bash /opt/CLIProxyAPI/manage.sh start
```

**方式2: 手动启动**:
```bash
cd /opt/CLIProxyAPI
nohup ./cliproxyapi -standalone > /var/log/cliproxyapi.log 2>&1 &
```

### 停止服务

```bash
bash /opt/CLIProxyAPI/manage.sh stop
```

### 重启服务

```bash
bash /opt/CLIProxyAPI/manage.sh restart
```

### 检查状态

```bash
bash /opt/CLIProxyAPI/manage.sh status
```

### 查看日志

```bash
tail -f /var/log/cliproxyapi-startup.log
```

---

## 🎯 集成到v5.2

### 添加到心跳检查

**编辑HEARTBEAT.md**:
```markdown
## CLIProxyAPI状态检查
```bash
bash /root/.openclaw/workspace/scripts/free-model-caller.sh status
```
```

### 自动启动

**创建systemd服务**（可选）:
```bash
cat > /etc/systemd/system/cliproxyapi.service << 'EOF'
[Unit]
Description=CLIProxyAPI Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/CLIProxyAPI
ExecStart=/opt/CLIProxyAPI/cliproxyapi -standalone
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable cliproxyapi
systemctl start cliproxyapi
```

---

## 💡 使用技巧

### 1. 多账户负载均衡

**配置10个Google账户**:
```bash
for i in {1..10}; do
  ./cliproxyapi -login
done
```

**自动轮换**，无限免费额度！

### 2. 智能模型选择

**v5.2自动选择**:
- 简单任务 → Gemini 2.0 Flash（快速）
- 复杂任务 → Gemini 2.5 Pro（质量）
- 代码任务 → Claude 3.5 Sonnet

### 3. 批量处理

**处理多个任务**:
```bash
for task in "任务1" "任务2" "任务3"; do
  bash /root/.openclaw/workspace/scripts/free-model-caller.sh auto \
    "代码" \
    "$task"
done
```

---

## 🎊 总结

**CLIProxyAPI已部署完成！** ✨

**访问方式**:
- ✅ 本地: http://localhost:8317
- ✅ 远程: http://43.134.63.176:8317

**使用方式**:
- ✅ v5.2轻量级接口（推荐）
- ✅ 直接API调用
- ✅ Web管理界面

**下一步**:
- 配置OAuth获取无限额度
- 集成到v5.2心跳
- 享受免费AI！

---

**开始使用免费AI吧！** 🚀✨
