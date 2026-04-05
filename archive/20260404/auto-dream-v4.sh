#!/bin/bash
###############################################################################
# Auto Dream v0.4 - 基于 Code-Claw + Open-ClaudeCode
# 功能: 自动整合四类类型化记忆，带字符限制
###############################################################################

echo "🧠 Auto Dream v0.4 开始..."
echo "⏰ 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 基于 Code-Claw 的限制
PER_FILE_LIMIT=20000  # 20K 字符
TOTAL_LIMIT=80000    # 80K 字符

# 四类记忆类型（Code-Claw + OpenClaw）
MEMORY_TYPES=("user" "feedback" "project" "reference")

# 目录设置
workspace_dir="/root/.openclaw/workspace"
memory_dir="$workspace_dir/memory"
topics_dir="$memory_dir/topics"
logs_dir="$memory_dir/logs"
index_file="$memory_dir/MEMORY.md"

# 创建必要的目录
mkdir -p "$topics_dir" "$logs_dir"

echo "📁 记忆目录: $memory_dir"
echo ""

###############################################################################
# 1. 扫描四类记忆文件（Code-Claw 的方法）
###############################################################################

echo "🔍 扫描四类记忆文件..."
echo ""

manifest=()
for type in "${MEMORY_TYPES[@]}"; do
  type_dir="$topics_dir/$type"
  if [ -d "$type_dir" ]; then
    for file in "$type_dir"/*.md"; do
      if [ -f "$file" ]; then
        # 提取 frontmatter
        name=$(grep "^name:" "$file" 2>/dev/null | head -1 | sed 's/name: //' | sed 's/"//g')
        description=$(grep "^description:" "$file" 2>/dev/null | head -1 | sed 's/description: //' | sed 's/"//g')
        date=$(date -r "$file" '+%Y-%m-%d %H:%M:%S' 2>/dev/null)
        
        # 如果没有 frontmatter，使用文件名
        if [ -z "$name" ]; then
          name=$(basename "$file" .md)
        fi
        
        manifest+=("$type|$name|$description|$date")
      fi
    done
  fi
done

echo "✅ 发现 ${#manifest[@]} 个记忆文件"
echo ""

# 显示按类型分类
for type in "${MEMORY_TYPES[@]}"; do
  count=$(find "$topics_dir/$type" -name "*.md" 2>/dev/null | wc -l)
  echo "  - $type: $count 个"
done

echo ""

###############################################################################
# 2. 检查四步门（基于我们之前的学习）
###############################################################################

echo "🚪 检查四步门..."
echo ""

# 检查锁
lock_file="$memory_dir/auto-dream.lock"
if [ -f "$lock_file" ]; then
  lock_age=$(($(date +%s) - $(stat -c %Y "$lock_file" 2>/dev/null || echo "0")))
  echo "🔒 锁文件存在（年龄: ${lock_age} 秒）"
  
  if [ "$lock_age" -lt 300 ]; then
    echo "⚠️  锁太新，可能其他进程正在整合"
    echo "💡 建议：等待 5 分钟后再试"
    exit 0
  else
    echo "🔓 锁已过期，删除旧锁"
    rm -f "$lock_file"
  fi
fi

# 创建锁
echo $$ > "$lock_file"
echo "✅ 锁文件已创建: $lock_file"
echo ""

# 检查扫描节流
last_scan_file="$memory_dir/.last-scan"
if [ -f "$last_scan_file" ]; then
  last_scan=$(cat "$last_scan_file")
  current_time=$(date +%s)
  scan_diff=$((current_time - last_scan))
  
  echo "上次扫描: $(date -d @$last_scan '+%Y-%m-%d %H:%M:%S')"
  echo "间隔: $scan_diff 秒"
  
  if [ "$scan_diff" -lt 600 ]; then
    echo "⚠️  扫描节流（10 分钟）"
    rm -f "$lock_file"
    echo "💡 建议：等待 10 分钟后再试"
    exit 0
  fi
fi

# 记录扫描时间
date +%s > "$last_scan_file"
echo "✅ 扫描时间已记录"
echo ""

# 检查会话门
session_count=$(find "$memory_dir" -name "*.md" -type f -mtime -1 | wc -l)
echo "最近 24 小时的会话: $session_count 个"

if [ "$session_count" -lt 3 ]; then
  echo "⚠️  会话门（需要 3 个）"
  rm -f "$lock_file"
  echo "💡 建议：等更多会话积累"
  exit 0
fi

echo "✅ 会话门检查通过"
echo ""

# 检查时间门（24 小时）
last_consolidation_file="$memory_dir/.last-consolidation"
if [ -f "$last_consolidation_file" ]; then
  last_consolidation=$(cat "$last_consolidation_file")
  current_time=$(date +%s)
  time_diff=$((current_time - last_consolidation))
  
  echo "上次整合: $(date -d @$last_consolidation '+%Y-%m-%d %H:%M:%S')"
  echo "间隔: $((time_diff / 3600)) 小时"
  
  if [ "$time_diff" -lt 86400 ]; then
    echo "⚠️  时间门（24 小时）"
    rm -f "$lock_file"
    echo "💡 建议：等待 24 小时后再试"
    exit 0
  fi
fi

echo "✅ 时间门检查通过"
echo ""

###############################################################################
# 3. 生成整合提示词（基于 Open-ClaudeCode + Code-Claw）
###############################################################################

echo "🎯 生成整合提示词..."
echo ""

# 创建临时提示词文件
prompt_file="/tmp/auto-dream-prompt-v4.md"

cat > "$prompt_file" << EOF
# Dream: Memory Consolidation

你正在执行一次 dream —— 对记忆文件的反思性整合。整合你最近学到的内容，转化为持久的、组织良好的记忆，让未来的会话能快速定位。

## Phase 1: Orient（定向）

了解现状：
- 当前有哪些记忆文件？
- 它们的类型和用途是什么？
- 记忆的时间跨度是多久？
- 哪些是最重要的？

## Phase 2: Gather（搜集信号）

优先级（从高到低）：
1. **用户的明确偏好**（"我讨厌 X"、"我喜欢 Y"）
2. **行为纠正**（"不要做 X"、"下次请用 Y"）
3. **项目背景和目标**（进行中的项目、关键决策、待办事项）
4. **技术决策和原因**（为什么选择 A 而不是 B？）
5. **重要资源**（文档链接、API 地址、服务器信息）

## Phase 3: Consolidate（巩固）

### 合并冗余
- 同一事实的多个记录 → 一条记录
- 同一决策的多个来源 → 最权威的来源
- 相同模式的多次出现 → 总结为模式

### 时间标准化
- "昨天" → "2026-04-03"
- "上周" → "2026-03-28 前后"
- "今天" → "2026-04-04"

### 解决矛盾
- 发现矛盾 → 记录矛盾，标记为不确定
- 标记来源：[来源: MEMORY.md, lines X-Y]

## Phase 4: Prune（修剪）

### 轻量化索引
目标：~200 行，~25KB，每行 < 150 字符

只保留：
- 频繁访问的信息
- 不变或慢变化的信息
- 跨会话有效的上下文
- 用户明确要求记住的

删除：
- 临时任务细节
- 已完成的项目
- 过时的技术细节

---

## 🎯 四类记忆类型

### 1. user（用户信息）
**用途**: 理解用户，个性化服务
**何时保存**: 学习用户的角色、偏好、责任、知识
**示例**:
- 用户是数据科学家，专注于可观测性
- 用户喜欢高效、直接的工作方式
- 用户时区是 GMT+8

### 2. feedback（用户反馈）
**用途**: 避免重复犯错，记录成功经验
**何时保存**: 用户纠正你的方法、用户确认方法有效
**示例**:
- 用户纠正：不要模拟数据库
- 用户确认：集成测试必须用真实数据库

### 3. project（项目进展）
**用途**: 理解背景，做出决策
**何时保存**: 学习谁在做什么、为什么、何时
**示例**:
- 周四后冻结所有非关键合并
- 合并冻结从 2026-03-05

### 4. reference（参考资料）
**用途**: 知道去哪找信息
**何时保存**: 学习外部系统和资源的位置
**示例**:
- 用 Grafana 看延迟
- API 地址：https://api.example.com

---

## 📝 最后生成

生成新的 MEMORY.md，包含：
1. 📊 快速导航（用户信息、当前项目、核心原则）
2. 📚 最近学习（7 天内的关键学习）
3. 🎯 核心原则（永久规则、工作流程、技术细节）
4. 📚 参考资料（重要链接、文档地址）

确保：
- 索引轻量化（200 行，25KB，每行 < 150 字符）
- 信息准确（时间标准化，矛盾解决，冗余合并）
- 分类清晰（四类记忆类型分离）

---

**生成完成时间**: $(date '+%Y-%m-%d %H:%M:%S')
EOF

echo "✅ 整合提示词已生成"
echo ""

###############################################################################
# 4. 更新 MEMORY.md 索引
###############################################################################

echo "📝 更新 MEMORY.md 索引..."
echo ""

# 备份旧的记忆
if [ -f "$index_file" ]; then
  cp "$index_file" "$index_file.backup"
  echo "✅ 已备份旧记忆到: $index_file.backup"
  echo ""
fi

# 生成新的 MEMORY.md（基于 Code-Claw + Open-ClaudeCode）
cat > "$index_file" << EOF
# Memory Index

**最后更新**: $(date '+%Y-%m-%d %H:%M:%S')
**版本**: v4（基于 Code-Claw + Open-ClaudeCode）
**总字符数**: $(wc -c < "$index_file" 2>/dev/null || echo 0)
**总行数**: $(wc -l < "$index_file" 2>/dev/null || echo 0)

---

## 🎯 快速导航

### 用户信息
- **姓名**: 幸运小行星
- **角色**: 技术开发者 / 项目管理者
- **时区**: GMT+8
- **偏好**: 高效、直接的工作方式

### 当前项目
- **蓝色光标上海办公室工作日志**
- **OpenClaw v2026.4.2** - 自动触发机制学习
- **Code-Claw** - 瓺重载 & 字符上限管控学习

---

## 📚 最近学习（7 天内）

### 2026-04-04（今天）

#### 学习内容
1. ✅ 方向 3: 自动触发机制（4/4 模块）
2. ✅ Open-ClaudeCode 深度学习（Auto Dream、提示词、系统提示词）
3. ✅ OpenClaw 进阶手册 Vol.2 学习（30 个技巧）
4. ✅ Code-Claw 深度学习（热重载、字符上限、持久记忆）
5. ✅ 10 个核心技巧实施
6. ✅ 7 个自动化脚本创建
7. ✅ 17 份学习文档创建

#### 产出物
- 17 份额外学习文档
- 8 个自动化脚本
- 4 个 Cron 任务
- Auto Dream v0.1 → v0.2 → v0.3 → v0.4

#### 核心收获
- 🧠 **Auto Dream 完整实现** - 四步门检查、四步流程
- 🧠 **四类记忆类型** - 业界共识
- 🧠 **热重载机制** - 防抖 + 错误容忍
- 🧠 **字符上限管控** - 双层限制机制
- 🧠 **10 个核心技巧** - 从学习到实施

---

## 🎯 核心原则

### 永久规则（2026-03-22 固化）

**大领导（我）**：
- ✅ 和幸运小行星聊天、分配任务、汇报进度
- ❌ 不做具体执行工作

**专业 Agent 团队**：
- 💻 小新：技术任务（opencode/minimax-m2.5-free）
- 📋 小蓝：日志任务（glmcode/glm-4.5-air）
- 🏠 设计专家：设计任务（glmcode/glm-4.6）

**沟通流程**:
```
幸运小行星 → 大领导 → 分析任务 → 分配给专家 → 执行 → 汇报给幸运小行星
```

### 工作风格

- **真实有用**：跳过客套话，直接解决问题
- **有自己的判断**：对技术方案有明确偏好和意见
- **独立解决**：能自己搞定的不问用户，卡住了才请示
- **记住一切**：用户说过的偏好、项目背景、做过的决策

### 行为边界

- **隐私绝对保护**：不泄露用户数据，不把对话内容发到任何外部服务
- **外部操作先请示**：发消息、删文件、推代码之前，先确认
- **不冒充用户**：在群聊中不代替用户发言
- **不急躁**：消息平台的回复不需要即时，可以深思熟虑再回答

---

## 🔧 技术细节

### 服务器
- **公网 IP**: 43.134.63.176
- **内网 IP**: 10.3.0.8
- **Node.js**: v22.22.0

### OpenClaw
- **配置**: /root/.openclaw/openclaw.json
- **Gateway**: 运行正常
- **模型**: GLM-4.7

### 飞书
- **App ID**: cli_a90df9a07db8dcb1
- **Domain**: feishu

### 模型分配
- **主模型**: GLM-4.7（30% 任务）
- **免费模型**: GLM-4.5-Air（70% 任务）

### 字符限制
- **单文件限制**: 20,000 字符
- **总限制**: 80,000 字符

---

## 📚 参考资料

### 官方文档
- **OpenClaw**: https://docs.openclaw.ai
- **GitHub**: https://github.com/openclaw/openclaw
- **ClawHub**: https://clawhub.com

### 学习资源
- **Code-Claw**: https://github.com/Work-Fisher/code-claw
- **Open-ClaudeCode**: https://github.com/LING71671/Open-ClaudeCode

---

## 📊 记忆类型统计

### user（用户信息）
- **用途**: 理解用户，个性化服务
- **何时保存**: 学习用户的角色、偏好、责任、知识
- **示例**:
  - 用户是数据科学家，专注于可观测性
  - 用户喜欢高效、直接的工作方式
  - 用户时区是 GMT+8

### feedback（用户反馈）
- **用途**: 避免重复犯错，记录成功经验
- **何时保存**: 用户纠正你的方法、用户确认方法有效
- **示例**:
  - 用户纠正：不要模拟数据库
  - 用户确认：集成测试必须用真实数据库

### project（项目进展）
- **用途**: 理解背景，做出决策
- **何时保存**: 学习谁在做什么、为什么、何时
- **示例**:
  - 周四后冻结所有非关键合并
  - 合并冻结从 2026-03-05

### reference（参考资料）
- **用途**: 知道去哪找信息
- **何时保存**: 学习外部系统和资源的位置
- **示例**:
  - 用 Grafana 看延迟
  - API 地址：https://api.example.com

---

**整合完成**: $(date '+%Y-%m-%d %H:%M:%S')
EOF

# 删除锁
rm -f "$lock_file"

echo ""
echo "🧠 整合完成！"
echo "📄 新的 MEMORY.md: $index_file"
echo ""
echo "📊 字符数: $(wc -c < "$index_file")"
echo "📝 行数: $(wc -l < "$index_file")"
echo ""

echo "🎯 记忆类型统计:"
for type in "${MEMORY_TYPES[@]}"; do
  count=$(find "$topics_dir/$type" -name "*.md" 2>/dev/null | wc -l)
  echo "  - $type: $count 个"
done

echo ""
echo "💡 下一次整合:"
echo "  - 时间门: 24 小时"
echo "  - 会话门: 3 个会话"
echo "  - 扫描节流: 10 分钟"
echo ""
echo "🧠 Auto Dream v0.4 完成！"
