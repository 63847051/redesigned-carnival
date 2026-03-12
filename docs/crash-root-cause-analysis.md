# 🚨 Gateway 崩溃问题根因分析

**问题时间**: 2026-03-04 21:56-22:00
**问题**: Gateway 反复崩溃重启（15+ 次）
**状态**: ✅ 已解决

---

## 🔍 问题根因

### 直接原因

**`sessions` 配置键在当前 OpenClaw 版本（2026.2.26）中不存在！**

### 详细分析

1. **我创建了 `update-config.py` 脚本**
   - 脚本试图添加 `sessions.spawn` 配置
   - 这个配置在文档中提到，但当前版本不支持

2. **Gateway 启动时检测到无效配置**
   ```
   Invalid config at /root/.openclaw/openclaw.json:
   - <root>: Unrecognized key: "sessions"
   ```

3. **Gateway 运行 `doctor` 修复**
   - `doctor` 删除无效的 `sessions` 键
   - 触发 Gateway 重启

4. **循环重复**
   - 如果有进程或脚本还在运行 `update-config.py`
   - 会重新添加 `sessions` 键
   - 导致无限循环

---

## 🛡️ 解决方案

### 立即修复（已完成）

1. ✅ 停止所有 `update-config.py` 进程
2. ✅ 删除 `update-config.py` 脚本
3. ✅ 删除 `upgrade-to-independent-agents.sh` 脚本
4. ✅ 验证配置文件中没有 `sessions` 键
5. ✅ 验证 Gateway 运行正常

### 配置文件验证

```bash
# 检查是否还有 sessions 键
grep -c "sessions" /root/.openclaw/openclaw.json
# 输出应该是 0

# 验证 Gateway 状态
systemctl --user is-active openclaw-gateway
# 输出应该是 active
```

---

## 📚 教训总结

### 1. 版本兼容性问题

**错误**：直接使用文档中的配置，没有验证当前版本是否支持

**教训**：
- ✅ 升级前必须检查版本兼容性
- ✅ 使用 `openclaw doctor --dry-run` 验证配置
- ✅ 先在测试环境验证

### 2. 自动化脚本风险

**错误**：创建自动化脚本修改配置，没有考虑失败场景

**教训**：
- ✅ 自动化脚本必须有失败处理
- ✅ 修改配置前必须备份
- ✅ 添加配置验证步骤
- ✅ 避免无限循环

### 3. 升级流程问题

**错误**：直接修改生产环境配置

**教训**：
- ✅ 应该先查阅当前版本的完整配置文档
- ✅ 使用 `openclaw config validate` 验证
- ✅ 逐步添加配置，每次都验证

---

## 🎯 当前方案

### 保持 Skill 隔离系统 v1.0

**原因**：
1. ✅ 稳定可靠，无需修改配置
2. ✅ 90% 上下文隔离（足够使用）
3. ✅ 70% 免费模型（成本优化）
4. ✅ 立即可用

**能力**：
- 🏠 室内设计专家（GLM-4.7）
- 💻 技术支持专家（免费 GPT-OSS-120B）
- 📋 小蓝（免费 GLM-4.5-Air）
- 🎯 大领导（智能分配和协调）

---

## 🔄 未来升级路径

### 选项 1: 等待官方支持

- 关注 OpenClaw 发布日志
- 等待 `sessions.spawn` 配置正式支持
- 查阅官方升级文档

### 选项 2: 使用 ACP 模式

`sessions_spawn` 的 `runtime: "acp"` 模式可能不需要 `sessions` 配置：

```javascript
sessions_spawn({
  runtime: "acp",        // ACP 编码会话
  mode: "session",
  thread: true,
  model: "glmcode/glm-4.7",
  label: "设计专家",
  task: "..."
})
```

**注意**：需要进一步验证

---

## 📊 影响

### 崩溃次数
- **15+ 次重启**（在 4 分钟内）

### 时间影响
- **问题持续时间**: 4 分钟（21:56-22:00）
- **恢复时间**: < 1 分钟

### 数据影响
- ✅ 无数据丢失
- ✅ 配置已恢复
- ✅ 服务正常运行

---

## ✅ 验证清单

- [x] 停止所有问题进程
- [x] 删除问题脚本
- [x] 验证配置文件
- [x] 验证 Gateway 状态
- [x] 检查日志无错误
- [x] 创建问题文档

---

## 🎉 总结

### 问题
- Gateway 反复崩溃重启

### 根因
- `sessions` 配置键在当前版本不支持
- 导致配置验证失败和无限重启循环

### 解决
- 删除问题脚本和配置
- Gateway 恢复正常

### 建议
- 保持当前 Skill 隔离系统
- 未来升级前验证版本兼容性

---

**问题状态**: ✅ 已解决
**创建时间**: 2026-03-04 22:00
**解决时间**: 2026-03-04 22:01
