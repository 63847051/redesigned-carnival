# CLIProxyAPI管理界面访问说明

**配置完成时间**: 2026-03-08 23:28

---

## 🔑 认证信息

**管理密钥**: `CC123456`

**管理界面**: http://43.134.63.176:8317/management.html

---

## ❗ 认证失败的可能原因

### 问题分析

CLIProxyAPI有**两种认证方式**：

#### 方式1: HTTP Header（API调用）

**正确方式**：
```bash
curl -X GET http://localhost:8317/v0/management/config \
  -H "X-Management-Key: CC123456"
```

#### 方式2: Web界面（浏览器）

**Web界面应该**：
1. 在登录框输入密钥
2. 通过API发送认证请求

**可能的问题**：
- Web界面版本不匹配
- 密钥输入格式错误
- 浏览器缓存问题

---

## 🔧 解决方案

### 方案1: 清除浏览器缓存

**步骤**:
1. 按 `Ctrl + Shift + Delete`
2. 清除缓存和Cookie
3. 刷新页面

### 方案2: 使用API直接调用

**如果Web界面无法使用，可以通过API调用**：

**查看配置**:
```bash
curl -X GET http://43.134.63.176:8317/v0/management/config \
  -H "X-Management-Key: CC123456"
```

**查看OAuth状态**:
```bash
curl -X GET http://43.134.63.176:8317/v0/management/oauth \
  -H "X-Management-Key: CC123456"
```

### 方案3: 使用命令行OAuth

**如果Web界面无法使用，直接用命令行**：

```bash
cd /opt/CLIProxyAPI
./cliproxyapi -login
```

**这会打开浏览器完成OAuth登录**。

---

## 🎯 推荐做法

**使用命令行OAuth**（最简单）:

```bash
cd /opt/CLIProxyAPI
./cliproxyapi -login
```

**优点**:
- ✅ 不需要Web界面
- ✅ 直接在服务器上操作
- ✅ 支持SSH隧道
- ✅ 更安全

---

## 📊 当前状态

**CLIProxyAPI配置**:
- ✅ 服务运行中（端口8317）
- ✅ 管理密钥已设置（CC123456）
- ✅ 允许远程访问
- ✅ API认证正常工作

**Web界面问题**:
- ⚠️ 可能存在版本兼容问题
- ⚠️ 或需要特定认证格式

---

## 💡 最佳方案

**不使用Web界面，直接用命令行**:

```bash
# 配置Google OAuth
cd /opt/CLIProxyAPI
./cliproxyapi -login

# 或配置OpenAI OAuth
./cliproxyapi -codex-login

# 或配置Claude OAuth
./cliproxyapi -claude-login
```

**这样更简单，不需要Web界面！** 🚀

---

**要现在使用命令行配置OAuth吗？** ✨
