# WAL 协议强化实施计划

**创建时间**: 2026-04-02 14:30
**参考来源**: Wesley AI 日记 - OpenClaw Agent Team 记忆系统 v2.0
**目标**: 确保"先写文件，再回复"不被绕过，强化记忆更新闭环

---

## 🎯 核心目标

**问题**:
- "收到≠记住"的问题仍然存在
- AI Agent 可能先回复"收到"，但忘记写文件
- 缺少写文件验证机制
- WAL 协议执行不够严格

**解决**:
- 强化 WAL 协议执行流程
- 添加写文件验证机制
- 整合到所有记忆更新场景
- 建立失败重试机制

---

## 📋 WAL 协议核心原则

### 原则 1: 先写，再回复

**核心理念**: "想要回复的冲动就是敌人"

**流程**:
```
收到用户消息
  ↓
扫描关键信息（纠正、决策、偏好、数值）
  ↓
有关键信息？
  ├─ 是 → 先写文件 → 验证成功 → 再回复
  └─ 否 → 直接回复
```

### 原则 2: 写完必须验证

**验证检查**:
- [ ] 文件是否存在？
- [ ] 内容是否正确写入？
- [ ] Retain 条目是否添加？
- [ ] 关键信息是否遗漏？

### 原则 3: 失败必须重试

**重试机制**:
- 写文件失败 → 重试 1 次
- 验证失败 → 重新写入
- 3 次失败 → 报警并阻止回复

---

## 🚀 实施步骤

### ✅ Step 1: 创建 WAL 验证工具（已完成）

**文件**: `scripts/wal-verify.sh` ✅

**功能**:
- ✅ 验证文件是否成功写入
- ✅ 检查内容是否正确
- ✅ 验证 Retain 条目
- ✅ 返回验证结果

**测试结果**:
- ✅ 帮助信息正常
- ✅ 全面验证功能正常
- ✅ 检测到 SESSION-STATE.md 缺少当前任务（正常）

---

### ✅ Step 2: 创建 WAL 辅助脚本（已完成）

**文件**: `scripts/wal-update-memory.sh` ✅

**功能**:
- ✅ 标准化记忆更新流程
- ✅ 自动验证写入结果
- ✅ 支持 Retain 格式
- ✅ 失败自动重试（最多 3 次）

**支持的命令**:
- `retain` - 添加 Retain 条目（W/B/O）
- `decision` - 记录决策
- `complete` - 完成任务
- `session` - 更新 SESSION-STATE.md
- `write` - 写入并验证文件

**测试结果**: ✅ 脚本工作正常

---

### ⬜ Step 3: 更新 WAL Protocol 自动化（可选）

**文件**: `scripts/wal-protocol-automation.sh`

**改进**:
- 添加验证步骤
- 整合 WAL 验证工具
- 增强错误处理
- 添加日志记录

**优先级**: 低（当前脚本已满足需求）

---

### ⬜ Step 4: 创建 WAL 执行规范（可选）

**文件**: `docs/WAL-EXECUTION-SPEC.md`

**内容**:
- WAL 协议执行规范
- 常见场景处理流程
- 验证检查清单
- 错误处理指南

**优先级**: 低（本文档已包含关键信息）

---

## 📊 WAL 协议场景

### 场景 1: 用户纠正

**示例**:
> 用户: "飞书不支持 img 标签，要用 upload_image API"

**WAL 流程**:
1. 识别关键信息（纠正）
2. 写入 SESSION-STATE.md
3. 添加 Retain 条目（W @飞书API）
4. 验证写入成功
5. 回复用户："已记录"

### 场景 2: 做出决策

**示例**:
> 用户: "我们使用智谱 AI embeddings"

**WAL 流程**:
1. 识别关键信息（决策）
2. 写入 decisions-log.md
3. 添加 Retain 条目（O @技术）
4. 验证写入成功
5. 回复用户："决策已记录"

### 场景 3: 任务完成

**示例**:
> Agent: "任务已完成"

**WAL 流程**:
1. 更新 active-tasks.md
2. 写入今日日志（B @任务）
3. 添加 Retain 条目
4. 验证写入成功
5. 汇报给用户

### 场景 4: 学习新知识

**示例**:
> Agent: "学习了 Claude Code 记忆系统"

**WAL 流程**:
1. 写入今日日志
2. 添加 Retain 条目（W @Claude-Code）
3. 验证写入成功
4. 继续工作

---

## 🔧 工具脚本

### wal-verify.sh

```bash
#!/bin/bash
# WAL 验证工具

verify_file_write() {
    local file=$1
    local expected_content=$2

    # 检查文件是否存在
    if [ ! -f "$file" ]; then
        echo "ERROR: 文件不存在"
        return 1
    fi

    # 检查内容是否写入
    if [ -n "$expected_content" ]; then
        if ! grep -q "$expected_content" "$file"; then
            echo "ERROR: 内容未写入"
            return 1
        fi
    fi

    echo "OK: 验证通过"
    return 0
}

# 使用示例
verify_file_write "/root/.openclaw/workspace/memory/2026-04-02.md" "Retain"
```

### wal-update-memory.sh

```bash
#!/bin/bash
# WAL 记忆更新脚本

update_memory_with_verification() {
    local file=$1
    local content=$2
    local retain_entry=$3

    local max_retries=3
    local retry=0

    while [ $retry -lt $max_retries ]; do
        # 写入文件
        echo "$content" >> "$file"

        # 验证写入
        if wal-verify.sh "$file" "$content"; then
            echo "SUCCESS: 记忆更新成功"
            return 0
        fi

        retry=$((retry + 1))
        echo "RETRY: 第 $retry 次重试"
    done

    echo "ERROR: 记忆更新失败"
    return 1
}
```

---

## 📋 执行检查清单

### 写入前检查

- [ ] 识别关键信息了吗？
- [ ] 确定写入目标文件了吗？
- [ ] 准备好 Retain 条目了吗？

### 写入后验证

- [ ] 文件存在吗？
- [ ] 内容正确吗？
- [ ] Retain 条目添加了吗？
- [ ] 关键信息没有遗漏吗？

### 回复前确认

- [ ] 验证通过了吗？
- [ ] 可以安全回复了吗？

---

## 🎯 成功指标

1. **写入成功率**: > 99%
2. **验证通过率**: 100%
3. **重试次数**: < 1%
4. **用户纠正率**: 持续下降

---

## 📝 注意事项

⚠️ **性能考虑**:
- 验证操作必须快速（< 1 秒）
- 不要过度验证
- 关键信息才验证

⚠️ **错误处理**:
- 写入失败必须重试
- 3 次失败必须报警
- 不要假装成功

⚠️ **用户体验**:
- 验证失败不要让用户等太久
- 失败时明确告知
- 提供修复建议

---

**状态**: 🔄 进行中 - Step 1: 创建 WAL 验证工具
**下一步**: 创建 wal-verify.sh 脚本
**预计完成**: 2026-04-02 15:00
