# 服务配置总结 - 大领导系统 v5.16.0

**更新时间**: 2026-03-16 18:25
**状态**: 部分完成

---

## ✅ 已完成

### 1. 创建了启动脚本

**Control Center**:
- `control-center/auto-start.sh` - 自动启动脚本
- `control-center/start-foreground.sh` - 前台启动脚本
- `scripts/setup-control-center-service.sh` - 系统服务配置脚本

**AI Team Dashboard**:
- `ai-team-dashboard/auto-start.sh` - 自动启动脚本
- `scripts/setup-ai-dashboard-service.sh` - 系统服务配置脚本

**统一启动**:
- `scripts/start-all.sh` - 一键启动所有服务

---

## ⚠️ 遇到的问题

### Control Center 系统服务启动失败

**原因**: Control Center 在后台运行时无法连接到 Gateway

**解决方案**: 前台启动
```bash
/root/.openclaw/control-center/start-foreground.sh
```

---

### AI Team Dashboard 需要 Docker

**原因**: Docker 未安装

**解决方案**: 
1. 安装 Docker
2. 或暂时不使用 AI Team Dashboard

---

## 🎯 推荐方案

### 方案 1: 前台启动 Control Center（推荐）

**启动**:
```bash
/root/.openclaw/control-center/start-foreground.sh
```

**优点**:
- ✅ 可以看到日志
- ✅ 便于调试
- ✅ 环境变量生效

**缺点**:
- ⚠️ 占用一个终端

---

### 方案 2: 不使用监控面板（最简单）

**核心功能都正常**:
- ✅ Gateway（飞书集成）
- ✅ Multi-Agent 协作
- ✅ 自动进化系统
- ✅ 所有脚本工具

**监控方式**:
- 命令行：`journalctl --user -u openclaw-gateway -f`
- 脚本：`bash /root/.openclaw/workspace/scripts/validate-config.sh`

---

## 💡 最终建议

**暂时不启用监控面板，核心功能都正常！**

**如果确实需要，可以手动前台启动 Control Center**：
```bash
/root/.openclaw/control-center/start-foreground.sh
```

**访问**: http://43.134.63.176:4310

---

**最后更新**: 2026-03-16 18:25
**维护者**: 大领导系统 v5.16.0
