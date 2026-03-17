# Phase 2: Hook 系统扩展

**目标**: 扩展 WAL Protocol，添加更多 Hook 事件
**时间**: 2026-03-17 开始
**预计**: 2-3 周

---

## 📋 Phase 2 任务列表

### 🔄 进行中

#### 任务 2.1: 扩展 Hook 事件类型
**目标**: 从当前 WAL Protocol 扩展到 20+ 个 Hook 事件

**当前 WAL Protocol 事件**:
- SessionStart
- SessionEnd
- PreCompact

**新增事件**（参考 ECC）:
- PreToolUse - 工具使用前
- PostToolUse - 工具使用后
- PreWrite - 写入前
- PostWrite - 写入后
- PreEdit - 编辑前
- PostEdit - 编辑后
- PreBash - Bash 命令执行前
- PostBash - Bash 命令执行后
- PreRead - 读取前
- PostRead - 读取后
- Stop - 会话停止时

**目标**: 15+ 个 Hook 事件

#### 任务 2.2: 创建 Hook 脚本库
**目标**: 参考 ECC 的 hooks/ 目录，创建实用脚本

**脚本列表**:
- session-start.js - 会话开始时加载上下文
- session-end.js - 会话结束时保存状态
- suggest-compact.js - 在逻辑断点建议压缩
- pre-compact.js - 压缩前保存状态
- post-edit-typecheck.js - 编辑后类型检查
- post-edit-format.js - 编辑后格式化
- check-console-log.js - 检查 console.log
- cost-tracker.js - 成本追踪

**目标**: 10+ 个 Hook 脚本

#### 任务 2.3: 添加运行时控制
**目标**: 支持环境变量控制 Hook 行为

**环境变量**:
```bash
export CLAW_HOOK_PROFILE=standard|strict|minimal
export CLAW_DISABLED_HOOKS="pre:bash:tmux-reminder,post:edit:typecheck"
```

**目标**: 实现运行时控制机制

---

## 🎯 立即开始

**优先级 1**: 创建 session-start.js Hook 脚本

**优先级 2**: 创建 session-end.js Hook 脚本

**优先级 3**: 添加运行时控制

---

*创建时间: 2026-03-17*
*状态: 🔄 Phase 2 进行中*
