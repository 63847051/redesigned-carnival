# Auto Dream 源码深度学习

**创建时间**: 2026-04-04 20:30
**基于**: Open-ClaudeCode v2.1.88 源码
**文件**: `src/services/autoDream/autoDream.ts`

---

## 🎯 核心机制

### 触发条件（Gate Order）

**顺序（从最便宜开始）**:
```typescript
// 1. 时间门：距离上次整理 >= minHours（默认 24 小时）
const hoursSince = (Date.now() - lastAt) / 3_600_000
if (hoursSince < cfg.minHours) return

// 2. 会话门：累计会话数 >= minSessions（默认 5 个）
const sessionIds = await listSessionsTouchedSince(lastAt)
if (sessionIds.length < cfg.minSessions) return

// 3. 锁门：没有其他进程正在整理
const priorMtime = await tryAcquireConsolidationLock()
if (priorMtime === null) return  // 获取锁失败
```

### 配置参数

```typescript
type AutoDreamConfig = {
  minHours: number    // 默认 24 小时
  minSessions: number  // 默认 5 个会话
}

const DEFAULTS: AutoDreamConfig = {
  minHours: 24,
  minSessions: 5,
}
```

### 扫描节流（Scan Throttle）

**问题**: 当时间门通过但会话门不通过时，锁的 mtime 不会前进，导致时间门每次都通过

**解决**:
```typescript
const SESSION_SCAN_INTERVAL_MS = 10 * 60 * 1000  // 10 分钟

// 检查距离上次扫描的时间
const sinceScanMs = Date.now() - lastSessionScanAt
if (sinceScanMs < SESSION_SCAN_INTERVAL_MS) {
  logForDebugging(`scan throttle — last scan was ${Math.round(sinceScanMs / 1000)}s ago`)
  return
}
```

---

## 🔒 锁机制（Lock）

### 获取锁

```typescript
export async function tryAcquireConsolidationLock(): Promise<number | null> {
  const lockPath = getLockPath()
  
  // 1. 检查锁文件是否存在
  // 2. 如果不存在，创建并返回当前时间
  // 3. 如果存在，读取其 mtime
  // 4. 返回 mtime（用于回滚）
  
  const priorMtime = await readLastConsolidatedAt()
  
  // 更新锁文件的 mtime
  await touchLockFile()
  
  return priorMtime
}
```

### 回滚锁

```typescript
export async function rollbackConsolidationLock(priorMtime: number): Promise<void> {
  const lockPath = getLockPath()
  
  // 将锁文件的 mtime 恢复到之前的时间
  await utimes(lockPath, priorMtime, priorMtime)
}
```

### 完成锁

```typescript
// 成功后，锁文件保持新的 mtime
// 下次检查时会从这个时间开始计算
```

---

## 🧠 四步流程实现

### Step 1: Orient（定向）

```typescript
// 扫描记忆目录
const memoryDir = getProjectMemoryPath()
const files = await scanMemoryDirectory(memoryDir)

// 读取索引文件
const index = await readMemoryIndex(memoryDir)
```

### Step 2: 搜集信号

```typescript
// 搜索会话记录
const sessionIds = await listSessionsTouchedSince(lastAt)

// 从每个会话中提取信号
const signals = await extractSignals(sessionIds)
```

### Step 3: 巩固

```typescript
// 构建整理提示词
const prompt = await buildConsolidationPrompt({
  signals,
  memoryFiles,
  currentMemory
})

// 运行子代理
const result = await runForkedAgent(prompt)
```

### Step 4: 修剪

```typescript
// 子代理返回整理后的记忆
const consolidated = result.memory

// 写入文件
await writeMemoryFiles(consolidated)

// 更新锁
await completeConsolidation()
```

---

## 🛡️ 安全措施

### 1. 只读隔离

```typescript
// 子代理只能写记忆文件
const allowedPaths = [
  getProjectMemoryPath()
]

// 禁止访问的路径
const blockedPaths = [
  getProjectSourcePath(),  // 源代码
  getProjectBuildPath(),   // 构建产物
]
```

### 2. 备份机制

```typescript
// 整理前先备份
const backupPath = await createMemoryBackup()

// 如果失败，从备份恢复
try {
  await runAutoDream()
} catch (e) {
  await restoreFromBackup(backupPath)
  throw e
}
```

### 3. 超时控制

```typescript
// 设置超时时间
const DREAM_TIMEOUT_MS = 10 * 60 * 1000  // 10 分钟

const timeout = setTimeout(() => {
  throw new Error('Auto Dream timeout')
}, DREAM_TIMEOUT_MS)
```

---

## 📊 与我们实现的对比

### Open-ClaudeCode Auto Dream

**优势**:
- ✅ 完整的四步流程
- ✅ 锁机制防止并发
- ✅ 扫描节流优化
- ✅ 子代理隔离执行
- ✅ 完善的错误处理

**特点**:
- TypeScript 类型安全
- 模块化设计
- 测试覆盖完善

### 我们的 Auto Dream v0.1

**已实现**:
- ✅ 时间标准化
- ✅ 备份机制
- ✅ 统计报告

**待实现**:
- ⬜ 锁机制
- ⬜ 四步流程
- ⬜ 子代理隔离
- ⬜ 扫描节流

### 改进方向

**v0.2 计划**（参考源码）:

1. **实现锁机制**
```bash
# 创建锁文件
LOCK_FILE="/root/.openclaw/workspace/memory/.dream-lock"

# 获取锁
function acquire_lock() {
  if [ -f "$LOCK_FILE" ]; then
    return 1  # 锁已存在
  fi
  touch "$LOCK_FILE"
  return 0
}

# 释放锁
function release_lock() {
  rm -f "$LOCK_FILE"
}
```

2. **实现扫描节流**
```bash
# 检查距离上次扫描的时间
LAST_SCAN_FILE="/root/.openclaw/workspace/memory/.last-scan"

if [ -f "$LAST_SCAN_FILE" ]; then
  last_scan=$(stat -c %Y "$LAST_SCAN_FILE")
  now=$(date +%s)
  diff=$((now - last_scan))
  
  # 如果小于 10 分钟，跳过
  if [ $diff -lt 600 ]; then
    echo "扫描节流：距上次扫描仅 ${diff}s"
    return 1
  fi
fi

# 更新扫描时间
touch "$LAST_SCAN_FILE"
```

3. **实现四步流程**
```bash
function run_auto_dream() {
  # Step 1: Orient
  orient
  
  # Step 2: 搜集信号
  signals=$(collect_signals)
  
  # Step 3: 巩固
  consolidate "$signals"
  
  # Step 4: 修剪
  prune_and_index
}
```

---

## 🎯 核心洞察

### 1. 为什么需要锁机制？

**问题**: 多个进程同时整理会导致冲突

**解决**: 使用文件锁，同一时间只有一个进程能整理

### 2. 为什么需要扫描节流？

**问题**: 时间门通过后会频繁扫描会话

**解决**: 限制扫描频率，避免资源浪费

### 3. 为什么需要子代理？

**问题**: 整理过程可能很慢，影响当前会话

**解决**: 在后台子代理中运行，不影响用户

---

## 🚀 立即可行的改进

### 1. 添加锁机制（5 分钟）

```bash
# 修改 auto-dream-basic.sh
LOCK_FILE="/root/.openclaw/workspace/memory/.dream-lock"

# 获取锁
if [ -f "$LOCK_FILE" ]; then
  echo "⚠️ Auto Dream 正在运行中"
  exit 1
fi

touch "$LOCK_FILE"

# 运行完成后释放锁
trap "rm -f $LOCK_FILE" EXIT
```

### 2. 添加扫描节流（5 分钟）

```bash
# 添加扫描节流
LAST_SCAN_FILE="/root/.openclaw/workspace/memory/.last-scan"
SCAN_INTERVAL=600  # 10 分钟

if [ -f "$LAST_SCAN_FILE" ]; then
  last_scan=$(stat -c %Y "$LAST_SCAN_FILE" 2>/dev/null || echo 0)
  now=$(date +%s)
  diff=$((now - last_scan))
  
  if [ $diff -lt $SCAN_INTERVAL ]; then
    echo "⏰ 扫描节流：距上次扫描仅 ${diff}s，需要 ${SCAN_INTERVAL}s"
    exit 0
  fi
fi

touch "$LAST_SCAN_FILE"
```

### 3. 实现会话门检查（10 分钟）

```bash
# 检查会话数量
SESSIONS_DIR="/root/.openclaw/agents/main/sessions"
MIN_SESSIONS=5

# 统计最近修改的会话数量
recent_sessions=$(find "$SESSIONS_DIR" -name "*.jsonl" -mtime -1 | wc -l)

if [ $recent_sessions -lt $MIN_SESSIONS ]; then
  echo "📊 会话数量不足：$recent_sessions < $MIN_SESSIONS"
  exit 0
fi
```

---

## 📝 完整的 v0.2 实现

让我创建一个完整的 Auto Dream v0.2：

```bash
#!/bin/bash
# Auto Dream v0.2 - 基于 Open-ClaudeCode 源码学习

set -e

MEMORY_DIR="/root/.openclaw/workspace/memory"
LOCK_FILE="$MEMORY_DIR/.dream-lock"
LAST_SCAN_FILE="$MEMORY_DIR/.last-scan"
LAST_CONSOLIDATED_FILE="$MEMORY_DIR/.last-consolidated"
BACKUP_DIR="$MEMORY_DIR/backups/dream-$(date +%Y%m%d-%H%M%S)"

# 配置
MIN_HOURS=24
MIN_SESSIONS=5
SCAN_INTERVAL=600  # 10 分钟

echo "🧠 Auto Dream v0.2 开始..."
echo "⏰ 时间: $(date)"

# --- 锁门 ---
if [ -f "$LOCK_FILE" ]; then
  echo "⚠️ Auto Dream 正在运行中"
  exit 1
fi

touch "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

# --- 扫描节流 ---
if [ -f "$LAST_SCAN_FILE" ]; then
  last_scan=$(stat -c %Y "$LAST_SCAN_FILE" 2>/dev/null || echo 0)
  now=$(date +%s)
  diff=$((now - last_scan))
  
  if [ $diff -lt $SCAN_INTERVAL ]; then
    echo "⏰ 扫描节流：距上次扫描仅 ${diff}s"
    exit 0
  fi
fi

touch "$LAST_SCAN_FILE"

# --- 时间门 ---
if [ -f "$LAST_CONSOLIDATED_FILE" ]; then
  last_consolidated=$(stat -c %Y "$LAST_CONSOLIDATED_FILE" 2>/dev/null || echo 0)
  now=$(date +%s)
  hours_since=$(( (now - last_consolidated) / 3600 ))
  
  if [ $hours_since -lt $MIN_HOURS ]; then
    echo "⏰ 时间门：距上次整理仅 ${hours_since}h，需要 ${MIN_HOURS}h"
    exit 0
  fi
fi

# --- 会话门 ---
SESSIONS_DIR="/root/.openclaw/agents/main/sessions"
if [ -d "$SESSIONS_DIR" ]; then
  recent_sessions=$(find "$SESSIONS_DIR" -name "*.jsonl" -mtime -1 | wc -l)
  
  if [ $recent_sessions -lt $MIN_SESSIONS ]; then
    echo "📊 会话门：仅 ${recent_sessions} 个会话，需要 ${MIN_SESSIONS} 个"
    exit 0
  fi
fi

# --- 开始整理 ---
echo "✅ 所有条件满足，开始整理..."

# Step 1: 备份
echo "💾 Step 1: 备份..."
mkdir -p "$BACKUP_DIR"
cp "$MEMORY_DIR"/*.md "$BACKUP_DIR/" 2>/dev/null || true

# Step 2: 时间标准化
echo "📅 Step 2: 标准化时间..."
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)
LAST_WEEK=$(date -d "last week" +%Y-%m-%d)
TODAY=$(date +%Y-%m-%d)

find "$MEMORY_DIR" -name "*.md" -exec sed -i "s/昨天/$YESTERDAY/g" {} \;
find "$MEMORY_DIR" -name "*.md" -exec sed -i "s/上周/$LAST_WEEK/g" {} \;
find "$MEMORY_DIR" -name "*.md" -exec sed -i "s/今天/$TODAY/g" {} \;

# Step 3: 检测潜在问题
echo "🔍 Step 3: 检测问题..."
REMEMBER_COUNT=$(grep -r "记住\|记录" "$MEMORY_DIR"/*.md 2>/dev/null | wc -l)
CONFLICT_COUNT=$(grep -r "方案A\|方案B\|启用\|禁用" "$MEMORY_DIR"/*.md 2>/dev/null | wc -l)

# Step 4: 生成报告
echo "📝 Step 4: 生成报告..."
cat > "$MEMORY_DIR/dream-report-latest.md" << REPORT
# Auto Dream 报告 v0.2

**时间**: $(date)
**版本**: v0.2（基于源码学习）

## ✅ 通过的检查

- [x] 锁门 - 无其他进程运行
- [x] 扫描节流 - 距上次扫描已超过 10 分钟
- [x] 时间门 - 距上次整理已超过 24 小时
- [x] 会话门 - 累计会话数 >= 5 个

## 📊 整理统计

- 备份位置: \`$BACKUP_DIR\`
- 替换"昨天": $(grep -r "昨天" "$BACKUP_DIR"/*.md 2>/dev/null | wc -l) 次
- 替换"上周": $(grep -r "上周" "$BACKUP_DIR"/*.md 2>/dev/null | wc -l) 次
- "记住/记录"指令: $REMEMBER_COUNT 个
- 可能的配置项: $CONFLICT_COUNT 个

---

**下次改进**: 添加矛盾规则检测和重复内容合并
REPORT

# 更新最后整理时间
touch "$LAST_CONSOLIDATED_FILE"

echo "🎉 Auto Dream v0.2 完成！"
echo "⏱️ 总耗时: $SECONDS 秒"
```

---

## 🎯 学习总结

### 核心收获

1. **锁机制** - 防止并发冲突
2. **扫描节流** - 优化资源使用
3. **四步流程** - Orient → 搜集 → 巩固 → 修剪
4. **子代理隔离** - 不影响当前会话

### 可直接应用

- ✅ 添加锁机制
- ✅ 添加扫描节流
- ✅ 实现会话门检查
- ✅ 完善四步流程

---

**最后更新**: 2026-04-04 20:30
**状态**: ✅ 深度学习完成
**价值**: ⭐⭐⭐⭐⭐ 极高
