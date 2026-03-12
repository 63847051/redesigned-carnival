# 版本升级日志

## v1.0.0 (2026-03-12)

### 安装
- ✅ 从 GitHub 克隆项目
- ✅ 安装 npm 依赖
- ✅ 配置环境变量
- ✅ 构建项目

### 配置
- ✅ 外网访问（UI_HOST=0.0.0.0）
- ✅ 只读模式（READONLY_MODE=true）
- ✅ 本地认证（LOCAL_TOKEN_AUTH_REQUIRED=true）
- ✅ 端口配置（UI_PORT=4310）

### 启动
- ✅ 创建启动脚本
- ✅ 后台运行
- ✅ 日志记录

---

## 升级说明

### 自动升级
```bash
cd openclaw-control-center
bash upgrade-version.sh
```

### 手动升级
1. 修改 `package.json.backup` 中的版本号
2. 记录升级原因到 CHANGELOG.md
3. 提交到 Git

---

## 注意事项

- ⚠️ 每次升级后都要更新版本号
- ⚠️ 记录升级原因和变更内容
- ⚠️ 测试所有功能是否正常
