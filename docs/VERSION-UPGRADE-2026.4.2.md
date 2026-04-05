# OpenClaw v2026.4.2 升级分析

**当前版本**: 2026.4.2 (d74a122)
**发布时间**: 2026-04-02
**升级时间**: 2026-04-04
**状态**: ✅ 已完成

---

## 📋 版本信息

- **版本号**: 2026.4.2
- **发布日期**: 2026-04-02
- **Git Commit**: d74a122
- **包大小**: 193.1 MB
- **文件数**: 21,256
- **依赖数量**: 48

---

## 🚨 Breaking Changes（破坏性更新）

### 1. Plugins/xAI 配置迁移
- **变更**: `x_search` 设置从 `tools.web.x_search.*` 迁移到 `plugins.entries.xai.config.xSearch.*`
- **认证**: 标准化到 `plugins.entries.xai.config.webSearch.apiKey` / `XAI_API_KEY`
- **迁移**: 使用 `openclaw doctor --fix` 自动迁移
- **影响**: 需要运行 `openclaw doctor --fix` 更新配置

### 2. Plugins/web fetch 配置迁移
- **变更**: Firecrawl `web_fetch` 配置从 `tools.web.fetch.firecrawl.*` 迁移到 `plugins.entries.firecrawl.config.webFetch.*`
- **路由**: 通过新的 fetch-provider 边界
- **迁移**: 使用 `openclaw doctor --fix` 自动迁移
- **影响**: 需要运行 `openclaw doctor --fix` 更新配置

---

## ✨ 新功能（Changes）

### 1. **Tasks/Task Flow** - 任务流系统 🎯
- **功能**: 恢复核心 Task Flow 基板
- **特性**:
  - 托管 vs 镜像同步模式
  - 持久化流状态/修订跟踪
  - `openclaw flows` 检查/恢复原语
- **影响**: 后台编排可以持久化并独立运行

### 2. **Plugins/hooks** - before_agent_reply 钩子 ⭐
- **功能**: 添加 `before_agent_reply` 钩子
- **用途**: 插件可以在内联操作后用合成回复短路 LLM
- **影响**: 扩展了插件能力

### 3. **Feishu/comments** - 飞书评论支持 💬
- **功能**: 添加专用的 Drive 评论事件流
- **特性**:
  - 评论线程上下文解析
  - 线程内回复
  - `feishu_drive` 评论操作
- **影响**: 支持文档协作工作流

### 4. **Exec defaults** - YOLO 模式 ⚡
- **变更**: Gateway/node host exec 默认为 YOLO 模式
- **行为**: 请求 `security=full` 并设置 `ask=off`
- **影响**: 减少提示，但需要注意安全性

### 5. **Agents/compaction** - 压缩通知优化 🧹
- **功能**: 添加 `agents.defaults.compaction.notifyUser`
- **用途**: 使 `🧹 Compacting context...` 开始通知变为可选
- **影响**: 减少不必要的通知

---

## 🐛 Bug 修复（Fixes）

### 1. **Gateway/hooks 配置悖论** ⭐ 重要发现
- **问题**: v2026.4.2 的文档提到 `gateway.hooks` 配置
- **实际**: Gateway 后端不支持这个配置
- **行为**: Gateway 启动时自动删除"未知字段"
- **解决**: 使用 `openclaw hooks` 命令管理 hooks
- **状态**: ✅ 已确认

### 2. **Providers/transport policy** - 传输策略集中化
- **修复**: 集中化请求认证、代理、TLS 和头部整形
- **影响**: 更安全的传输策略

### 3. **Gateway/exec loopback** - 本地 exec 恢复
- **修复**: 恢复空配对设备令牌映射的遗留角色回退
- **影响**: 本地 exec 和 node 客户端不再失败

### 4. **Agents/subagents** - 子 Agent 修复
- **修复**: 将管理级子 Agent gateway 调用固定为 `operator.admin`
- **影响**: `sessions_spawn` 不再因回送范围升级配对而死掉

### 5. **Webhooks/secret comparison** - 安全比较
- **修复**: 替换临时安全密钥比较为共享 `safeEqualSecret` 辅助函数
- **影响**: 更安全的 webhook 验证

---

## 🔧 配置变更

### 需要迁移的配置
```bash
# 运行自动迁移
openclaw doctor --fix
```

### 检查配置
```bash
# 验证配置
openclaw doctor

# 检查插件状态
openclaw plugins status
```

---

## 📊 依赖更新

### 新增依赖
- `crner: ^10.0.1` - Cron 调度
- `hono: 4.12.9` - Web 框架
- `zod: ^4.3.6` - 验证库

### 更新的依赖
- `express: ^5.2.1` (从 ^5.x)
- `chokidar: ^5.0.0` (从 ^4.x)
- `commander: ^14.0.3` (从 ^12.x)

---

## 🎯 对现有功能的影响

### 1. **Cron 定时任务** ✅
- **状态**: 正常工作
- **测试**: 已验证 `openclaw cron add/list/remove`
- **影响**: 无

### 2. **Webhook 触发** ⚠️
- **状态**: 发现版本 Bug
- **问题**: `gateway.hooks` 配置不支持
- **解决**: 使用 `openclaw hooks` 命令
- **影响**: 需要调整学习计划

### 3. **Browser Control** ✅
- **状态**: 未测试
- **影响**: 无

### 4. **记忆系统** ✅
- **状态**: 正常工作
- **影响**: 无

---

## 💡 升级后的工作方式变化

### 1. **Exec 安全性** ⚠️
- **变更**: 默认 YOLO 模式（`security=full`, `ask=off`）
- **建议**: 注意 exec 命令的安全性
- **影响**: 减少提示，但需要更小心

### 2. **任务流系统** 🎯
- **新增**: `openclaw flows` 命令
- **用途**: 检查和恢复后台任务流
- **影响**: 可以持久化后台编排

### 3. **Hooks 管理** 🔧
- **新增**: `openclaw hooks` 命令
- **用途**: 管理内部 Agent hooks
- **影响**: 不再依赖配置文件

### 4. **压缩通知** 🧹
- **新增**: `agents.defaults.compaction.notifyUser` 选项
- **用途**: 控制是否显示压缩通知
- **影响**: 可以减少不必要的通知

---

## 🚀 下一步行动

### 立即行动
1. ✅ 运行 `openclaw doctor --fix` 迁移配置
2. ✅ 检查 `openclaw hooks list` 查看可用 hooks
3. ✅ 测试 `openclaw flows` 命令

### 学习调整
1. ✅ **模块 2**: Webhook 触发 - 使用 `openclaw hooks` 命令
2. ⬜ **模块 3**: Gmail Pub/Sub - 继续学习
3. ⬜ **模块 4**: Browser Control - 继续学习

### 文档更新
1. ✅ 创建版本升级分析文档
2. ⬜ 更新学习文档中的 Webhook 部分
3. ⬜ 添加 Task Flow 系统说明

---

## 📝 总结

### 主要变化
1. ✅ **Breaking Changes**: xAI 和 web fetch 配置迁移
2. ✅ **新功能**: Task Flow 系统、before_agent_reply 钩子
3. ✅ **Bug 修复**: 大量安全和稳定性修复
4. ⚠️ **发现 Bug**: gateway.hooks 配置悖论

### 影响评估
- **影响程度**: 中等
- **需要迁移**: 是（运行 `openclaw doctor --fix`）
- **功能变化**: 小（主要是内部优化）
- **学习影响**: 需要调整 Webhook 学习方式

---

**最后更新**: 2026-04-04 19:20
**状态**: ✅ 已完成
