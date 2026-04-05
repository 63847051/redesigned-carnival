# 安全最佳实践学习计划

**创建时间**: 2026-04-02 22:00
**参考来源**: OpenClaw 进阶手册 Vol.2 - Tip 15-20
**目标**: 建立系统安全防护机制，防止暴露和攻击

---

## 🎯 学习目标

1. **理解安全威胁**
   - 公网暴露的 135,000+ 实例
   - 常见的安全漏洞
   - 攻击向量分析

2. **掌握防护措施**
   - 专用部署
   - 网络隔离
   - 访问控制
   - 容器隔离

3. **实施安全加固**
   - 配置检查
   - 安全审计
   - 持续监控

---

## 📋 学习内容（基于 Tip 15-20）

### Tip 15: 不要在主力机跑 Gateway

**原因**:
- 主力机有代码、文档、密码、SSH key
- Gateway 默认可以执行 bash 命令、读写文件
- 配置出问题或有问题的 Skill 会影响整台机器

**解决方案**:
- ✅ 使用专用部署：
  - Mac Mini（闲置的那台）
  - Raspberry Pi 5（静音，低功耗）
  - VPS（Hetzner CAX11 €3.79/月）

**如果非要在本地跑**:
```json
{
  "gateway": {
    "bind": "127.0.0.1"  // 只监听本地回环
  }
}
```

---

### Tip 16: Tailscale - 安全远程访问

**功能**:
- 给你一个私有网络
- Gateway 只在这个网络里可见
- 公网不可见

**两种模式**:

**serve 模式**（推荐）:
```json
{
  "gateway": {
    "tailscale": {
      "mode": "serve"  // 只有 tailnet 设备能访问
    }
  }
}
```

**funnel 模式**（公网访问）:
```json
{
  "gateway": {
    "auth": {
      "mode": "password"
    },
    "tailscale": {
      "mode": "funnel"  // 可以从公网访问
    }
  }
}
```

**注意**: Funnel 没开密码不让启动（这是保护）

---

### Tip 17: Docker Sandbox - 群组消息隔离

**ClawHavoc 事件之后成为必做项**:

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "non-main"  // 只有主会话不隔离
      }
    }
  }
}
```

**含义**:
- 主会话（你直接对话）不隔离
- 群组、频道、webhook 触发的会话在独立容器
- 恶意 Skill 只能影响那个容器，碰不到主机

---

### Tip 18: Gateway Token 安全

**生成强 Token**:
```bash
openssl rand -hex 32
# 输出: a3f8b2c1d4e5...（64 位十六进制）
```

**配置**:
```json
{
  "gateway": {
    "token": "你生成的64位token"
  }
}
```

**保护**:
- ❌ 不要用简单密码（123456、openclaw）
- ❌ 不要出现在代码里（用环境变量）
- ❌ 不要出现在群聊截图里
- ❌ 不要出现在公开文档里
- ❌ 不要出现在日志里

---

### Tip 19: openclaw security audit

**使用方法**:
```bash
# 基础审计
openclaw security audit

# 深度审计（实时探测 Gateway）
openclaw security audit --deep
```

**检查内容**:
- Gateway 绑在 0.0.0.0（公网暴露）
- token 太弱
- allowFrom 过宽
- 浏览器控制暴露在公网
- 文件系统权限过松

**升级后必跑**:
- 每次大版本升级后
- 旧配置需要更新
- 跑一遍 audit，10 分钟

---

### Tip 20: 升级策略

**按版本走，不要跳版本**:

**版本号格式**: `vYYYY.M.D`（如 v2026.2.23）

**2026.1-2 之间的 breaking change**:
- DM 策略：open → pairing
- Sandbox 配置：新增 `non-main`
- 默认值可能变化

**正确流程**:
```bash
# 查看当前版本
openclaw --version

# 升级到 stable 最新
openclaw update --channel stable

# 备份配置（重要！）
cp -r ~/.openclaw ~/.openclaw-backup-$(date +%Y%m%d)

# 升级
openclaw update

# 升级后检查
openclaw doctor
```

---

## 🚀 实施计划

### 阶段 1: 创建安全检查清单 ⭐ 当前任务

**文件**: `docs/SECURITY-CHECKLIST.md`

**内容**:
- 部署检查
- 网络隔离检查
- 访问控制检查
- 隔离机制检查
- Token 强度检查

---

### 阶段 2: 创建安全审计脚本

**文件**: `scripts/security-audit.sh`

**功能**:
- 检查 Gateway 配置
- 检查文件权限
- 检查网络绑定
- 生成审计报告
- 提供修复建议

---

### 阶段 3: 实施安全加固

**任务**:
- [ ] 检查当前部署方式
- [ ] 配置 Tailscale（如果需要）
- [ ] 启用 Docker Sandbox
- [ ] 生成强 Gateway Token
- [ ] 运行 security audit
- [ ] 修复发现的问题

---

## 📊 安全检查清单

### 部署检查
- [ ] 不在主力机运行 Gateway
- [ ] 使用专用部署（VPS / Pi 5 / Mac Mini）
- [ ] 服务器有防火墙
- [ ] 系统及时更新

### 网络隔离
- [ ] 使用 Tailscale 私有网络
- [ ] Gateway 不直接暴露到公网
- [ ] 使用 serve 模式（非 funnel）
- [ ] 端口转发有密码保护

### 访问控制
- [ ] Gateway Token 已加强（64 位）
- [ ] allowFrom 配置合理
- ] DM Policy 设置为 pairing
- [ ] 群组路由显式允许

### 隔离机制
- [ ] Docker Sandbox 启用
- [ ] non-main 模式配置
- [ ] 群组消息隔离
- [ ] webhook 验证 Token

### Token 安全
- [ ] Gateway Token 不在代码中
- [ ] Token 不在公开文档中
- [ ] Token 不在日志中
- [ ] Token 定期更换

---

## 🔧 工具脚本

### security-audit.sh（创建中）

**功能**:
```bash
# 全面安全审计
bash scripts/security-audit.sh

# 快速检查
bash scripts/security-audit.sh --quick

# 生成报告
bash scripts/security-audit.sh --report > security-report.md
```

**检查项**:
- Gateway 配置
- 文件权限
- 网络绑定
- Token 强度
- 隔离状态
- 暴露端口扫描

---

## 🎯 成功指标

- ✅ 安全审计通过
- ✅ 无高危漏洞
- ✅ Token 强度足够
- ✅ 隔离机制生效
- ✅ 网络隔离正常

---

**状态**: 🔄 开始学习
**预计时间**: 2-3 小时
**优先级**: 🔴 最高
**目标**: 建立完整的安全防护体系
