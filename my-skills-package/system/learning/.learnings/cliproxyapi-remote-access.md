# CLIProxyAPI远程访问配置指南

**目标**: 从浏览器访问 http://43.134.63.176:8317

---

## 🔧 腾讯云控制台配置（必须）

### 步骤1: 登录腾讯云

1. 访问: https://console.cloud.tencent.com/
2. 登录你的账号

### 步骤2: 找到服务器

1. 左侧菜单 → "云服务器"
2. 找到服务器: VM-0-8-opencloudos (43.134.63.176)

### 步骤3: 配置安全组

1. 点击服务器ID
2. 点击"安全组"标签
3. 点击"配置规则"
4. 点击"添加规则"

### 步骤4: 添加入站规则

**规则配置**:
- **类型**: 自定义
- **来源**: 0.0.0.0/0（或你的IP）
- **协议端口**: TCP:8317
- **策略**: 允许

**详细配置**:
```
类型: IPv4
协议: TCP
端口: 8317
源地址: 0.0.0.0/0
策略: 允许
```

5. 点击"完成"

---

## ✅ 验证配置

### 1. 检查服务状态

```bash
# 在服务器上执行
netstat -tuln | grep 8317
```

**应该看到**:
```
tcp6       0      0 :::8317                 :::*                    LISTEN
```

### 2. 测试本地访问

```bash
curl http://localhost:8317/
```

**应该返回**:
```json
{"endpoints":["POST /v1/chat/completions","POST /v1/completions","GET /v1/models"],"message":"CLI Proxy API Server"}
```

### 3. 测试远程访问

**在浏览器中访问**:
```
http://43.134.63.176:8317
```

**应该看到API响应**

---

## 🌐 使用CLIProxyAPI

### 1. Web管理界面

**访问**: http://43.134.63.176:8317

**功能**:
- 查看API端点
- 测试API调用
- 查看服务状态

### 2. 配置OAuth（重要）

**需要在本地电脑配置OAuth**（因为服务器无浏览器）:

#### 方法1: 使用SSH隧道

**在你的本地电脑执行**:
```bash
ssh -L 8317:localhost:8317 root@43.134.63.176
```

**然后访问**:
```
http://localhost:8317
```

**启动OAuth**:
```bash
cd /opt/CLIProxyAPI
./cliproxyapi -login
```

**浏览器会自动打开**，完成OAuth登录。

#### 方法2: 手动配置Token

**获取Google OAuth Token**:
1. 在本地电脑完成OAuth
2. 复制token文件到服务器

**token位置**:
```
/root/.cli-proxy-api/auth/google/*.json
```

### 3. 使用API

**配置好OAuth后，调用API**:
```bash
curl -X POST http://43.134.63.176:8317/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.5-pro",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

---

## 🔒 安全建议

### 1. 限制访问IP

**不要使用0.0.0.0/0**，改为你的IP:

**获取你的IP**:
```bash
curl ifconfig.me
```

**安全组配置**:
- 源地址: 你的IP/32
- 例如: 123.45.67.89/32

### 2. 使用HTTPS（可选）

**配置nginx反向代理**:
```bash
# 安装nginx
yum install nginx -y

# 配置SSL
# 使用Let's Encrypt免费证书
```

### 3. 添加认证

**在CLIProxyAPI配置中添加API Key认证**。

---

## 🎯 快速测试

### 1. 确认安全组已配置

**在腾讯云控制台检查**:
- 安全组规则中是否有TCP:8317
- 策略是否为"允许"

### 2. 测试端口连通性

**在你的本地电脑执行**:
```bash
telnet 43.134.63.176 8317
```

**如果成功**:
```
Trying 43.134.63.176...
Connected to 43.134.63.176.
```

### 3. 浏览器访问

**打开浏览器**:
```
http://43.134.63.176:8317
```

---

## 💡 常见问题

### Q1: 无法访问

**检查**:
1. 安全组是否配置
2. 服务是否运行
3. 端口是否正确

### Q2: OAuth无法配置

**解决**:
- 使用SSH隧道
- 或在本地电脑配置后复制token

### Q3: API调用失败

**检查**:
1. OAuth是否配置
2. Token是否有效
3. 查看日志: `tail -f /var/log/cliproxyapi-startup.log`

---

## 📊 总结

**配置远程访问的步骤**:
1. ✅ 腾讯云控制台开放8317端口
2. ✅ 服务已在运行
3. ✅ 浏览器访问 http://43.134.63.176:8317
4. ⚠️ 配置OAuth（需要SSH隧道或手动配置token）

**下一步**:
1. 去腾讯云控制台配置安全组
2. 测试浏览器访问
3. 配置OAuth获取免费AI额度

---

**配置完成后，你就能在浏览器中使用CLIProxyAPI了！** 🚀
