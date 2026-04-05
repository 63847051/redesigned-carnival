# HEARTBEAT.md - 系统健康检查 v5.0

**版本**: v5.0 (整合记忆系统监控)
**更新**: 2026-04-02 12:50

---

## 🧬 每次心跳必做（进化系统 v3.0 + WAL Protocol）

### 🚨 最高优先级：自动进化
```bash
# 每次心跳时自动执行
bash /root/.openclaw/workspace/scripts/self-evolution-system.sh
```

**系统自动**：
1. 检查最近的错误
2. 分析错误原因
3. 自动学习
4. 生成进化报告

---

## 🚀 Proactive Agent检查（新增）

### 系统健康检查
```bash
# Gateway状态
systemctl --user is-active openclaw-gateway

# 内存使用
free | awk '/Mem/{printf("%.1f%"), $3/$2*100}'

# 最近错误
journalctl --user -u openclaw-gateway --since "10 minutes ago" --no-pager | grep -i "error\|failed" || echo "无错误"
```

### WAL Protocol状态恢复
```bash
# 恢复SESSION-STATE.md
bash /root/.openclaw/workspace/scripts/wal-protocol-automation.sh restore
```

**检查内容**:
- 当前任务状态
- 进度跟踪
- 关键细节
- 下一步行动

---

## 📝 记忆管理（新增）

### 每日必做
```bash
# 每日记忆整理
bash /root/.openclaw/workspace/scripts/wal-protocol-automation.sh daily
```

**功能**:
- 压缩working-buffer.md
- 整理今日日志到MEMORY.md
- 清理30天前的旧日志

### 每周必做
- 整理MEMORY.md
- 归档旧日志
- 更新最佳实践

---

## 💓 心跳检查内容

### 1️⃣ Gateway健康检查

```bash
# 检查Gateway状态
systemctl --user is-active openclaw-gateway || echo "Gateway未运行"

# 检查重启次数
journalctl --user -u openclaw-gateway --no-pager | grep "Scheduled restart job" | wc -l

# 检查配置文件修改时间
ls -la /root/.openclaw/openclaw.json | awk '{print "修改时间:", $6, $7, $8}'

# 检查启动错误
journalctl --user -u openclaw-gateway --since "10 minutes ago" --no-pager | grep -i "error\|failed" || echo "无错误"
```

### 2️⃣ 配置文件验证

```bash
# 检查配置是否有效
python3 -c "import json; json.load(open('/root/.openclaw/openclaw.json'))" 2>/dev/null && echo "✅ 配置文件有效" || echo "❌ 配置文件损坏"

# L7配置验证
bash /root/.openclaw/workspace/scripts/l7-config-validation.sh
```

### 3️⃣ 内存使用检查

```bash
# 检查内存使用（超过80%报警）
free | awk '/Mem/{printf("%.1f%"), $3/$2*100}'
```

### 4️⃣ SESSION-STATE检查（新增）

```bash
# 检查当前任务状态
bash /root/.openclaw/workspace/scripts/wal-protocol-automation.sh restore
```

**输出示例**:
```
📋 当前任务:
- **任务**: 整合proactive-agent-skill
- **状态**: 🔄 进行中
- **进度**: 40%
```

### 5️⃣ 三重防护检查（v5.9 新增）⭐

```bash
# 检查三重防护机制是否正常
bash /root/.openclaw/workspace/.learnings/rules/confirmation-check-helper.sh test
```

**检查内容**:
- ✅ 确认词白名单是否加载
- ✅ 操作前检查清单是否就绪
- ✅ 阶段性确认机制是否激活

**输出示例**:
```
🔒 三重防护检查:
  ✅ 第 1 重: 确认词白名单 - 已加载
  ✅ 第 2 重: 操作前检查清单 - 就绪
  ✅ 第 3 重: 阶段性确认机制 - 激活
```

---

## 🔄 Proactive主动行为（新增）

### 周期性检查（每30分钟）

#### 系统检查
- ✅ Gateway状态
- ✅ 内存使用
- ✅ 错误日志
- ✅ 配置验证

#### 主动学习
- ✅ PAI学习系统
- ✅ 自我进化系统
- ✅ 错误模式分析

#### 记忆管理
- ✅ 更新SESSION-STATE.md
- ✅ 记录到working-buffer.md
- ✅ 整理每日日志

---

## 📊 检查结果报告

### 正常状态
```
✅ Gateway: 运行正常 | 重启次数: X
✅ 配置: 有效
✅ 内存: XX%
✅ 版本: 一致
✅ SESSION-STATE: 已恢复
✅ WAL Protocol: 运行中
```

### 异常状态
```
🚨 Gateway: 异常 | 重启次数: X (超过阈值)
🔧 正在执行自动修复...
```

---

## 🎯 优先级

1. **Gateway可用性** - 最重要
2. **配置完整性** - 次重要
3. **资源使用** - 监控
4. **WAL Protocol** - 状态恢复 ⭐ v4.0新增
5. **PAI学习系统** - 持续进化
6. **三重防护机制** - 永不违规 ⭐ v5.9新增

---

## 🧬 自我进化系统（整合版）

### 每次心跳必做（推荐使用这个）
```bash
# 运行完整的自我进化系统v3.0
bash /root/.openclaw/workspace/scripts/self-evolution-system.sh
```

**整合的系统**:
- 🧠 PAI学习系统
- 🧬 超级进化大脑
- 🛡️ 6层防护系统
- 💾 memu-engine
- 🔄 四步自我改进循环 ⭐ v3.0
- 📝 WAL Protocol ⭐ v4.0新增

---

## 💡 如果需要关注

### 立即关注
- Gateway停止
- 配置文件错误
- 内存使用 > 90%
- SESSION-STATE显示阻塞任务

### 主动检查
- 重要Email（如果配置了）
- Calendar事件（如果配置了）
- 系统性能指标
- 错误趋势

---

## 📋 记录到working-buffer

### 每次重要交换
```bash
# 使用WAL Protocol记录
bash /root/.openclaw/workspace/scripts/wal-protocol-automation.sh log \
  "用户提问" \
  "什么时候完成" \
  "已完成以下任务..." \
  "✅ 完成"
```

---

**v4.0 - 整合proactive-agent-skill的完整心跳系统！** 🧬✨

**核心改进**:
- ✅ WAL Protocol支持
- ✅ SESSION-STATE恢复
- ✅ working-buffer记录
- ✅ 主动行为检查
- ✅ 记忆管理自动化

**v5.9 - 整合三重防护机制！** 🔐✨

**核心改进**:
- ✅ 三重防护机制检查
- ✅ 确认词白名单验证
- ✅ 操作前强制检查清单
- ✅ 阶段性确认机制

---

## 🚨 关键规则检查（每次心跳必做）⭐ v5.9加强

```bash
# 每次心跳时自动执行
bash /root/.openclaw/workspace/scripts/check-critical-rules.sh
```

**RULE-001: 重要操作必须等待确认** ⭐ v5.9 加强版

**RULE-003: OpenCode CLI 使用规则** ⭐ v5.26 新增

**RULE-004: OpenCode CLI 正确使用方法** ⭐ v5.28 新增 🔴 CRITICAL

**RULE-005: 备份前必须更新 README.md** ⭐ v6.1.1 新增 🔴 CRITICAL

**核心规则**:
> **"备份不是简单的 git push，而是完整的版本发布流程。"**

**备份前检查清单**:
1. [ ] 检查 SOUL.md 和 README.md 版本号是否一致
2. [ ] 如果不一致，先更新 README.md
3. [ ] 更新版本历史和最新更新内容
4. [ ] 使用完整备份流程脚本：`bash scripts/complete-backup.sh`

**快速备份**:
```bash
# 使用完整备份流程脚本（推荐）
bash /root/.openclaw/workspace/scripts/complete-backup.sh

# 或者手动执行
# 1. 更新 README.md
# 2. git add -A
# 3. git commit -m "备份信息"
# 4. git push origin main
```

**违反此规则 = 版本号不一致，用户困惑**
**错误次数**: 3 次（重复犯错）

**核心规则**:
> **"OpenCode CLI 是独立系统，有自己的配置，永远不要用 sessions_spawn 调用。"**

**检查方法**:
```bash
# 检查最近的命令历史
bash /root/.openclaw/workspace/scripts/check-opencode-usage.sh history
```

**违反此规则 = 严重错误（用户极度不满）**

**v5.27.1 更新**：现在支持通过 `sessions_spawn` 调用小新！

**opencode 模型只能通过 OpenCode CLI 使用！**

```bash
# ✅ 正确方式 1: 直接使用 OpenCode CLI
opencode -m opencode/minimax-m2.5-free run "任务"

# ✅ 正确方式 2: 使用智能分配脚本（v5.27.1 新增）
bash /root/.openclaw/workspace/scripts/assign-task.sh "任务" "tech"

# ✅ 正确方式 3: 使用 sessions_spawn（v5.27.1 更新）
sessions_spawn -runtime subagent -model opencode/minimax-m2.5-free

# ❌ 错误方式（旧版本）
# sessions_spawn -runtime subagent -model glmcode/glm-4.5-air  # 这是小蓝的模型
```

**小新 = OpenCode CLI + opencode/minimax-m2.5-free**

**三种调用方式对比**：

| 方式 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| **OpenCode CLI** | 技术任务 | 原生支持，工具完整 | 需要手动输入 |
| **智能分配脚本** | 自动检测类型 | 自动选择 Agent | 需要脚本 |
| **sessions_spawn** | 通用任务 | 灵活，统一接口 | 可能忘记配置 |

**推荐使用**：
- 🥇 **智能分配脚本**（最推荐）
- 🥈 **OpenCode CLI**（技术任务）
- 🥉 **sessions_spawn**（通用任务）

**三重防护机制**：

**第 1 重：确认词白名单**
- ✅ 只有这些才是真正的确认：
  - "确认"、"确认执行"、"开始实施"、"执行"
- ❌ 以下绝对不是确认：
  - "继续"、"方案 C"、"可以吗"

**第 2 重：操作前强制检查清单**
```
- [ ] 用户明确说了确认词吗？
- [ ] 我明确询问用户确认了吗？
- [ ] 我收到了用户的明确回复吗？
```

**第 3 重：阶段性确认机制**
- 每个阶段都要重新确认
- 不再假设"用户之前同意，现在也同意"

**违反此规则 = 严重错误**

---

## 🧠 记忆系统健康检查（新增）⭐ v5.0

```bash
# 每次心跳时检查记忆系统
bash /root/.openclaw/workspace/scripts/heartbeat-memory-check.sh
```

**检查内容**:
- ✅ MEMORY.md 大小是否正常（< 8000 tokens）
- ✅ 当前日志数量是否合理（< 50 个）
- ✅ 归档目录是否正常
- ✅ 最新日志是否及时更新（< 48 小时）
- ✅ 是否使用 Retain 格式
- ✅ 是否有重复发布问题

**健康报告**: `memory/health-status.md`

---

### 📅 每日检查（每次心跳）

**基础检查**:
- [ ] MEMORY.md 是否超出 2000 tokens？
- [ ] 当前日志数量是否正常？
- [ ] 最近 24 小时是否有新日志？
- [ ] 归档目录是否正常？

**异常检测**:
- [ ] 是否有矛盾规则？
- [ ] 是否有过时信息？
- [ ] 是否有重复发布事故？

---

### 📅 每周检查（每周日凌晨）

**深度审计**:
```bash
# 每周运行完整审计
bash /root/.openclaw/workspace/scripts/audit-memory.sh
```

**检查项**:
- [ ] 运行完整 MEMORY.md 审计
- [ ] 检查所有 Retain 条目
- [ ] 清理临时性信息
- [ ] 更新文档索引

**任务跟踪**:
- [ ] 检查任务完成情况
- [ ] 验证决策记录
- [ ] 审查事故日志

---

### 📅 每月检查（每月1号）

**全面清理**:
```bash
# 每月生成清理报告
bash /root/.openclaw/workspace/scripts/cleanup-report.sh

# 归档旧日志
bash /root/.openclaw/workspace/scripts/archive-old-logs.sh
```

**系统优化**:
- [ ] 生成完整清理报告
- [ ] 归档 30 天以上日志
- [ ] 清理旧归档（90 天+）
- [ ] 更新统计数据

---

