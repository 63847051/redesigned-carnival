# CLIProxyAPI访问路径说明

**服务地址**: http://43.134.63.176:8317

---

## 🔍 CLIProxyAPI没有Web管理界面！

### 重要发现

**CLIProxyAPI是纯API服务**，不是Web应用！

**它只提供API端点**:
- `POST /v1/chat/completions` - 对话API
- `POST /v1/completions` - 补全API
- `GET /v1/models` - 模型列表

**没有**:
- ❌ Web管理界面
- ❌ 可视化UI
- ❌ 浏览器界面

---

## 🎯 正确的使用方式

### 方式1: API调用（唯一方式）

**查看可用端点**:
```bash
curl http://localhost:8317/
```

**返回**:
```json
{
  "endpoints": [
    "POST /v1/chat/completions",
    "POST /v1/completions",
    "GET /v1/models"
  ],
  "message": "CLI Proxy API Server"
}
```

### 方式2: TUI管理界面（需要SSH）

**启动TUI**:
```bash
cd /opt/CLIProxyAPI
./cliproxyapi -tui
```

**这会打开终端管理界面**，不是浏览器界面。

### 方式3: 使用v5.2轻量级接口

**调用API**:
```bash
bash /root/.openclaw/workspace/scripts/free-model-caller.sh auto \
  "代码" \
  "写一个快速排序算法" \
  "medium"
```

---

## 💡 配置OAuth

### 问题：服务器无浏览器

**OAuth需要浏览器**，但服务器没有。

### 解决方案：SSH隧道

**在你的本地电脑执行**:
```bash
ssh -L 8317:localhost:8317 root@43.134.63.176
```

**然后在服务器上启动OAuth**:
```bash
cd /opt/CLIProxyAPI
./cliproxyapi -login
```

**浏览器会打开** `http://localhost:8317/...`（OAuth回调地址）

**完成Google登录授权**。

---

## 🚀 总结

**CLIProxyAPI访问说明**:

1. **没有Web管理界面** ❌
   - 它是纯API服务
   - 只能通过API调用

2. **可以远程访问** ✅
   - 开放8317端口后
   - 可以从外部调用API

3. **配置OAuth需要特殊方法** ⚠️
   - 使用SSH隧道
   - 或手动配置token

**正确使用**:
- ✅ API调用（curl、v5.2接口）
- ✅ TUI管理（SSH连接）
- ❌ 浏览器界面（不存在）

---

**要测试API调用吗？** 🚀
