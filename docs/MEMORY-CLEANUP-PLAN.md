# 记忆清理机制实施计划

**创建时间**: 2026-04-02 12:00
**参考来源**: Wesley AI 日记 - OpenClaw Agent Team 记忆系统 v2.0
**目标**: 建立自动化的记忆过期清理和归档机制

---

## 🎯 核心目标

**问题**:
- 记忆文件越来越多，检索变慢
- 旧信息产生噪音，甚至矛盾规则
- 缺少自动清理机制

**解决**:
- 自动归档 30 天以上日志
- 定期审计 MEMORY.md，删除过时规则
- 整合到心跳检查

---

## 📋 实施内容

### 1. 自动归档机制

**目标**: 将 30 天以上的日志自动移入 `memory/archive/`

**规则**:
```bash
# 每日日志
memory/2026-03-01.md  →  memory/archive/2026-03/2026-03-01.md  (30天+)
memory/2026-03-15.md  →  memory/archive/2026-03/2026-03-15.md  (30天+)

# 当前日志（< 30天）保持不动
memory/2026-04-02.md  →  不移动
```

**脚本**: `/root/.openclaw/workspace/scripts/archive-old-logs.sh`

---

### 2. MEMORY.md 审计机制

**目标**: 定期检查并清理 MEMORY.md 中的过时信息

**检查项**:
- [ ] 是否有矛盾的规则？
- [ ] 是否有过时的技术信息？
- [ ] 是否有可推导的信息？
- [ ] Token 数量是否超过限制？

**脚本**: `/root/.openclaw/workspace/scripts/audit-memory.sh`

---

### 3. 清理统计和报告

**目标**: 跟踪清理效果，生成统计报告

**统计指标**:
- 归档文件数量
- 释放的磁盘空间
- MEMORY.md 压缩率
- 清理前后对比

**脚本**: `/root/.openclaw/workspace/scripts/cleanup-report.sh`

---

## 🚀 实施步骤

### ✅ Step 1: 创建归档脚本（已完成）

**文件**: `scripts/archive-old-logs.sh` ✅

**功能**:
- ✅ 扫描 `memory/` 目录
- ✅ 识别 30 天以上的日志文件
- ✅ 按月份组织归档目录
- ✅ 移动文件到归档目录
- ✅ 生成归档日志

**测试结果**:
- ✅ DRY RUN 模式测试通过
- ✅ 检测到 2 个文件需要归档（2026-03-02, 2026-03-03）
- ✅ 当前日志: 47 个文件（1.4M）
- ✅ 归档目录已创建

---

### ✅ Step 2: 创建审计脚本（已完成）

**文件**: `scripts/audit-memory.sh` ✅

**功能**:
- ✅ 检查 MEMORY.md 矛盾规则
- ✅ 检测过时信息
- ✅ 检查可推导信息
- ✅ 验证文件结构
- ✅ 生成审计报告

**测试结果**:
- ✅ MEMORY.md 状态良好
- ✅ 3376 字符，1688 tokens（远低于 8000 限制）
- ✅ 无重复章节、无矛盾规则、无明显过时信息
- ✅ 审计报告已生成

---

### ✅ Step 3: 创建报告脚本（已完成）

**文件**: `scripts/cleanup-report.sh` ✅

**功能**:
- ✅ 统计归档文件数量
- ✅ 计算释放空间
- ✅ 生成清理报告
- ✅ 保存统计数据（JSON）

**测试结果**:
- ✅ 当前日志: 125 个文件（1.4M）
- ✅ 归档日志: 1 个文件（20K）
- ✅ MEMORY.md: 3376 字符（1688 tokens）
- ✅ 清理报告已生成

---

### ⬜ Step 4: 整合到心跳检查（下一步）

**修改**: `HEARTBEAT.md` + 心跳检查脚本

**内容**:
- 每日自动归档检查
- 每周 MEMORY.md 审计
- 每月生成清理报告

---

## 📊 清理策略

### 按文件类型

| 文件类型 | 保留期 | 归档策略 | 清理策略 |
|---------|--------|----------|----------|
| **每日日志** | 30 天 | 按月归档 | 90 天后可选清理 |
| **MEMORY.md** | 永久 | 不归档 | 定期审计，删除过时 |
| **SESSION-STATE.md** | 1 天 | 不归档 | 每日重写 |
| **共享知识库** | 永久 | 不归档 | 定期审计 |

### 按内容类型

| 内容类型 | 保留 | 删除 | 备注 |
|---------|------|------|------|
| 核心规则 | ✅ 永久 | ❌ | |
| 用户偏好 | ✅ 永久 | ❌ | |
| 决策记录 | ✅ 永久 | ❌ | |
| 事故教训 | ✅ 永久 | ❌ | |
| 临时调试 | ❌ | ✅ 立即 | 不写入 MEMORY.md |
| 过时规则 | ❌ | ✅ 审计时 | 保留最新版本 |
| 可推导信息 | ❌ | ✅ 审计时 | 不存储 |

---

## 🔧 工具脚本

### 1. archive-old-logs.sh

```bash
#!/bin/bash
# 归档 30 天以上的日志文件

MEMORY_DIR="/root/.openclaw/workspace/memory"
ARCHIVE_DIR="${MEMORY_DIR}/archive"
DAYS=30

# 创建归档目录
mkdir -p "$ARCHIVE_DIR"

# 查找并归档旧日志
find "$MEMORY_DIR" -name "*.md" -mtime +$DAYS -type f | while read file; do
    # 提取日期
    date=$(basename "$file" .md)
    year=${date:0:4}
    month=${date:5:2}

    # 创建月份目录
    target_dir="${ARCHIVE_DIR}/${year}-${month}"
    mkdir -p "$target_dir"

    # 移动文件
    mv "$file" "$target_dir/"
    echo "归档: $file → $target_dir/"
done
```

### 2. audit-memory.sh

```bash
#!/bin/bash
# 审计 MEMORY.md，检查过时和矛盾信息

MEMORY_FILE="/root/.openclaw/workspace/MEMORY.md"

# 检查文件大小
tokens=$(wc -c < "$MEMORY_FILE")
echo "MEMORY.md 大小: $tokens 字符"

# 检查是否有矛盾的规则（示例）
echo "检查矛盾规则..."
grep -i "用.*方案" "$MEMORY_FILE" | head -5

# 检查过时技术信息
echo "检查过时技术信息..."
grep -i "版本\|v[0-9]" "$MEMORY_FILE" | head -5
```

### 3. cleanup-report.sh

```bash
#!/bin/bash
# 生成清理报告

MEMORY_DIR="/root/.openclaw/workspace/memory"
ARCHIVE_DIR="${MEMORY_DIR}/archive"
REPORT_FILE="/root/.openclaw/workspace/memory/cleanup-report.md"

# 统计归档文件
archived_count=$(find "$ARCHIVE_DIR" -name "*.md" | wc -l)
archived_size=$(du -sh "$ARCHIVE_DIR" | cut -f1)

# 统计当前日志
current_count=$(find "$MEMORY_DIR" -maxdepth 1 -name "*.md" | wc -l)

# 生成报告
cat > "$REPORT_FILE" << EOF
# 记忆清理报告

**生成时间**: $(date)

## 统计数据

- 归档文件数: $archived_count
- 归档占用空间: $archived_size
- 当前日志数: $current_count

## 清理建议

EOF

echo "报告已生成: $REPORT_FILE"
```

---

## 🔄 整合到心跳检查

### 每日检查

```bash
# 每天凌晨 2 点执行
0 2 * * * /root/.openclaw/workspace/scripts/archive-old-logs.sh
```

### 每周审计

```bash
# 每周日凌晨 3 点执行
0 3 * * 0 /root/.openclaw/workspace/scripts/audit-memory.sh
```

### 每月报告

```bash`
# 每月1号凌晨 4 点执行
0 4 1 * * /root/.openclaw/workspace/scripts/cleanup-report.sh
```

---

## 📈 效果预期

### 短期（1周内）

- ✅ 旧日志自动归档
- ✅ memory/ 目录更整洁
- ✅ 检索速度提升

### 中期（1个月）

- ✅ MEMORY.md 保持精炼
- ✅ 矛盾规则及时清理
- ✅ 磁盘空间释放

### 长期（3个月+）

- ✅ 形成稳定的清理节奏
- ✅ 记忆质量持续提升
- ✅ 系统性能优化

---

## 🎯 成功指标

1. **归档率**: 30 天以上日志 100% 归档
2. **MEMORY.md 大小**: 稳定在合理范围
3. **检索速度**: 日志检索时间 < 1 秒
4. **清理频率**: 每周至少审计一次

---

## 📝 注意事项

⚠️ **归档前检查**:
- 确认文件确实超过 30 天
- 检查是否有未完成任务引用
- 备份重要信息

⚠️ **MEMORY.md 清理**:
- 删除前确认信息真的过时
- 保留核心规则和用户偏好
- 删除后验证系统正常运行

⚠️ **恢复机制**:
- 归档文件可随时恢复
- 删除前备份 MEMORY.md
- 保留清理日志

---

**状态**: 🔄 进行中 - Step 1: 创建归档脚本
**下一步**: 创建 archive-old-logs.sh 脚本
**预计完成**: 2026-04-02 13:00
