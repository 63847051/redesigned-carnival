# Auto Dream 实现方案

**创建时间**: 2026-04-04 19:57
**基于**: Claude Code Auto Dream 功能
**目标**: 为 OpenClaw 实现自动记忆巩固系统

---

## 🎯 核心目标

实现一个类似 Claude Code Auto Dream 的自动记忆巩固系统，定期整理、优化、清理记忆文件。

---

## 📋 现有系统对比

### ✅ 我们已有的功能

| 功能 | 我们系统 | Claude Code | 状态 |
|------|---------|-------------|------|
| **随手记录** | WAL Protocol | Auto Memory | ✅ 已有 |
| **记忆整理** | 手动执行 | Auto Dream | ⚠️ 半自动 |
| **分层存储** | MEMORY.md + 归档 | 4 层架构 | ✅ 已有 |
| **矛盾检测** | 基础检查 | 自动解决 | ⚠️ 部分有 |
| **时间标准化** | 手动 | 自动 | ❌ 缺少 |
| **定期清理** | 手动脚本 | 自动触发 | ⚠️ 半自动 |

### 🚨 需要改进的地方

1. **自动化触发**: 需要手动执行，不够智能
2. **后台执行**: 会影响当前对话
3. **矛盾解决**: 只检测不自动解决
4. **时间标准化**: "昨天"、"上周"等相对时间未处理

---

## 🏗️ Auto Dream 实现架构

### 触发条件

```bash
# 检查是否满足触发条件
function check_trigger_conditions() {
  # 条件 1: 距离上次整理已过 24 小时
  local last_run=$(get_last_dream_time)
  local hours_since=$(( ($(date +%s) - last_run) / 3600 ))
  
  # 条件 2: 中间至少积累了 5 条对话记录
  local conversation_count=$(get_recent_conversation_count)
  
  if [ $hours_since -ge 24 ] && [ $conversation_count -ge 5 ]; then
    return 0  # 触发
  else
    return 1  # 不触发
  fi
}
```

### 四步流程

#### Step 1: Orient（定向）

```bash
function orient() {
  echo "🧠 Step 1: Orient - 定向"
  
  # 读取记忆目录结构
  local memory_dir="/root/.openclaw/workspace/memory"
  
  # 列出所有记忆文件
  ls -lh $memory_dir/*.md
  
  # 分析文件关系
  echo "📋 记忆文件索引:"
  cat $memory_dir/MEMORY.md
  
  # 统计信息
  local total_files=$(find $memory_dir -name "*.md" | wc -l)
  local total_size=$(du -sh $memory_dir | cut -f1)
  
  echo "📊 统计: $total_files 个文件, 总大小 $total_size"
}
```

#### Step 2: 搜集信号

```bash
function collect_signals() {
  echo "🔍 Step 2: 搜集信号"
  
  # 搜索对话记录中的重要信息
  local sessions_dir="/root/.openclaw/agents/main/sessions"
  
  # 搜索纠正内容
  echo "✅ 搜索纠正内容:"
  grep -r "纠正\|修正\|错误" $sessions_dir/*.jsonl | head -10
  
  # 搜索重要决策
  echo "🎯 搜索重要决策:"
  grep -r "决定\|决策\|选择" $sessions_dir/*.jsonl | head -10
  
  # 搜索重复出现的内容
  echo "🔄 搜索重复内容:"
  grep -r "记住\|记录" $sessions_dir/*.jsonl | head -10
}
```

#### Step 3: 巩固

```bash
function consolidate() {
  echo "💪 Step 3: 巩固"
  
  # 1. 合并重复信息
  echo "🔄 合并重复信息..."
  # TODO: 实现重复检测和合并
  
  # 2. 解决矛盾规则
  echo "⚖️ 解决矛盾规则..."
  # TODO: 实现矛盾检测和解决
  
  # 3. 标准化时间
  echo "📅 标准化时间..."
  standardize_relative_dates
  
  # 4. 更新索引
  echo "📝 更新索引..."
  update_memory_index
}
```

#### Step 4: 修剪和索引

```bash
function prune_and_index() {
  echo "✂️ Step 4: 修剪和索引"
  
  # 1. 删除冗余信息
  echo "🗑️ 删除冗余信息..."
  remove_redundant_content
  
  # 2. 清理过期内容
  echo "🧹 清理过期内容..."
  remove_expired_content
  
  # 3. 优化索引
  echo "📚 优化索引..."
  optimize_memory_index
  
  # 4. 生成报告
  echo "📊 生成报告..."
  generate_dream_report
}
```

---

## 🔧 核心功能实现

### 1. 时间标准化

```bash
function standardize_relative_dates() {
  local memory_dir="/root/.openclaw/workspace/memory"
  
  # 查找所有包含相对时间的文件
  find $memory_dir -name "*.md" -exec grep -l "昨天\|上周\|前天" {} \; | while read file; do
    echo "📅 处理文件: $file"
    
    # 获取文件的修改日期作为参考
    local file_date=$(stat -c %Y "$file")
    local yesterday=$(date -d "yesterday" +%Y-%m-%d)
    local last_week=$(date -d "last week" +%Y-%m-%d)
    
    # 替换相对时间
    sed -i "s/昨天/$yesterday/g" "$file"
    sed -i "s/上周/$last_week/g" "$file"
    
    echo "✅ 已替换相对时间"
  done
}
```

### 2. 矛盾规则检测

```bash
function detect_conflicts() {
  local memory_dir="/root/.openclaw/workspace/memory"
  
  # 搜索可能的矛盾配置
  echo "⚖️ 检测矛盾规则..."
  
  # 搜索相互冲突的配置
  grep -r "方案A\|方案B" $memory_dir/*.md
  grep -r "启用\|禁用" $memory_dir/*.md
  grep -r "使用\|不使用" $memory_dir/*.md
  
  # TODO: 实现更智能的矛盾检测
}
```

### 3. 重复内容合并

```bash
function merge_duplicates() {
  local memory_dir="/root/.openclaw/workspace/memory"
  
  # 搜索重复的内容块
  echo "🔄 检测重复内容..."
  
  # 使用哈希检测重复段落
  # TODO: 实现智能去重
}
```

### 4. 过期内容清理

```bash
function remove_expired_content() {
  local memory_dir="/root/.openclaw/workspace/memory"
  
  # 删除 30 天前的归档
  echo "🗑️ 清理过期归档..."
  find $memory_dir/archive -name "*.md" -mtime +30 -delete
  
  # 删除临时文件
  find $memory_dir -name "*.tmp" -mtime +7 -delete
  
  echo "✅ 清理完成"
}
```

---

## 🚀 自动化触发

### 方式 1: Cron 定时任务

```bash
# 每天凌晨 3 点检查是否需要 Auto Dream
openclaw cron add \
  --cron "0 3 * * *" \
  --tz "Asia/Shanghai" \
  --name "Auto Dream 检查" \
  --message "检查是否需要运行 Auto Dream，如果满足条件（24小时 + 5条对话）则自动执行"
```

### 方式 2: 对话启动时触发

```bash
# 在每次对话启动时检查
# 添加到 HEARTBEAT.md 或启动脚本

function check_and_run_dream() {
  if check_trigger_conditions; then
    echo "🧠 触发 Auto Dream..."
    
    # 在后台运行，不影响当前对话
    nohup bash /root/.openclaw/workspace/scripts/auto-dream.sh > /tmp/dream.log 2>&1 &
    
    echo "✅ Auto Dream 已在后台运行"
  fi
}
```

---

## 📊 报告生成

```bash
function generate_dream_report() {
  local report_file="/root/.openclaw/workspace/memory/dream-report-$(date +%Y%m%d).md"
  
  cat > $report_file << EOF
# Auto Dream 报告

**时间**: $(date)
**耗时**: $DREAM_DURATION 秒

## 📊 整理统计

- **处理文件数**: $PROCESSED_FILES
- **删除重复**: $DUPLICATES_REMOVED
- **解决矛盾**: $CONFLICTS_RESOLVED
- **标准化时间**: $DATES_STANDARDIZED
- **清理过期**: $EXPIRED_REMOVED

## 🔍 主要发现

$(cat /tmp/dream-findings.txt)

## ✅ 改进建议

$(cat /tmp/dream-suggestions.txt)

---

**Auto Dream v1.0**
EOF

  echo "📝 报告已生成: $report_file"
}
```

---

## 🛡️ 安全措施

### 1. 只读隔离

```bash
# Auto Dream 只能写记忆文件，不动源代码
DREAM_ALLOWED_PATHS=(
  "/root/.openclaw/workspace/memory"
  "/root/.openclaw/workspace/.cache"
)

# 禁止访问的路径
DREAM_BLOCKED_PATHS=(
  "/root/.openclaw/workspace/projects"
  "/root/.openclaw/workspace/scripts"
  "/root/.openclaw/workspace/docs"
)
```

### 2. 备份机制

```bash
# 运行前先备份
function backup_before_dream() {
  local backup_dir="/root/.openclaw/workspace/memory/backups/dream-$(date +%Y%m%d-%H%M%S)"
  
  mkdir -p $backup_dir
  cp -r /root/.openclaw/workspace/memory/*.md $backup_dir/
  
  echo "💾 备份完成: $backup_dir"
}
```

### 3. 回滚机制

```bash
# 如果出错，可以回滚
function rollback_dream() {
  local backup_dir=$1
  
  if [ -d "$backup_dir" ]; then
    cp -r $backup_dir/* /root/.openclaw/workspace/memory/
    echo "↩️ 已回滚到: $backup_dir"
  else
    echo "❌ 备份不存在: $backup_dir"
  fi
}
```

---

## 🎯 实施计划

### Phase 1: 基础功能（1-2 天）

- [ ] 创建 auto-dream.sh 脚本
- [ ] 实现四步流程
- [ ] 时间标准化功能
- [ ] 基础报告生成

### Phase 2: 自动化（1 天）

- [ ] 触发条件检测
- [ ] Cron 定时任务
- [ ] 后台执行机制
- [ ] 备份和回滚

### Phase 3: 智能化（2-3 天）

- [ ] 重复内容检测
- [ ] 矛盾规则解决
- [ ] 智能合并
- [ ] 高级报告

### Phase 4: 集成（1 天）

- [ ] 整合到 HEARTBEAT.md
- [ ] 添加到启动脚本
- [ ] 测试和优化

---

## 📝 配置文件

```yaml
# openclaw.json
agents:
  defaults:
    autoDream:
      enabled: true
      trigger:
        hoursSinceLastRun: 24
        minConversationCount: 5
      execution:
        mode: "background"  # background | foreground
        timeout: 600  # 10 分钟
        backup: true
        rollbackOnError: true
      paths:
        memoryDir: "/root/.openclaw/workspace/memory"
        backupDir: "/root/.openclaw/workspace/memory/backups"
      reporting:
        enabled: true
        outputPath: "/root/.openclaw/workspace/memory/dream-reports"
```

---

## 🚀 立即可用的命令

```bash
# 手动触发 Auto Dream
bash /root/.openclaw/workspace/scripts/auto-dream.sh

# 检查是否满足触发条件
bash /root/.openclaw/workspace/scripts/auto-dream.sh --check

# 查看最近的 Dream 报告
cat /root/.openclaw/workspace/memory/dream-report-*.md | tail -1

# 回滚到最近的备份
bash /root/.openclaw/workspace/scripts/auto-dream.sh --rollback
```

---

## 💡 核心优势

### vs Claude Code Auto Dream

| 特性 | Claude Code | 我们的实现 | 优势 |
|------|-------------|-----------|------|
| **触发条件** | 24h + 5 条对话 | 相同 | ✅ |
| **后台执行** | ✅ | ✅ | ✅ |
| **只读隔离** | ✅ | ✅ | ✅ |
| **回滚机制** | ❌ | ✅ | 🚀 更安全 |
| **中文优化** | ❌ | ✅ | 🚀 更好 |
| **相对时间** | 英文 | 中英文 | 🚀 更全 |

---

**最后更新**: 2026-04-04 19:57
**状态**: 📋 计划中
**优先级**: 高
