# 记忆系统 v2.0 - 完整方案

**版本**: v2.0
**创建时间**: 2026-03-30 17:10
**参考**: Wesley AI 日记 - 给 OpenClaw Agent Team 装上记忆

---

## 🎯 核心理念

> **记忆 ≠ 存储**
> **记忆 = 存储 + 检索 + 更新 + 清理**

---

## 📊 5 维度记忆系统

### 1️⃣ 分层存储（热/温/冷）

**热记忆**（≤2000 tokens，每次会话必读）：
- `MEMORY.md` - 核心身份、OKR、关键规则
- `SESSION-STATE.md` - 当前任务状态

**温记忆**（按需检索）：
- `bank/` - 结构化知识库
  - `decisions/` - 决策记录
  - `entities/` - 实体页面
  - `lessons-learned/` - 经验教训
- `memory/YYYY-MM-DD.md` - 每日日志

**冷记忆**（归档存储）：
- `memory/archive/` - 30 天以上日志自动归档

---

### 2️⃣ WAL 协议（Write-Ahead Log）

**核心理念**: 先写，再回复
> "想要回复的冲动就是敌人。"

**具体流程**：
```
收到用户消息
↓
判断是否包含关键信息（纠正、决策、偏好）
↓
有关键信息 → 先写入 SESSION-STATE.md → 再回复
无关键信息 → 直接回复
```

**脚本**: `/root/.openclaw/workspace/scripts/wal-protocol-check.sh`

---

### 3️⃣ 分级检索（4 步决策树）

```
用户提问
↓
Step 1: MEMORY.md（已加载）
↓ 未命中
Step 2: memory_search（语义搜索）
↓ 未命中
Step 3: memory_get（精确读取）
↓ 未命中
Step 4: grep（全局搜索）
↓ 全部未命中
坦诚说"没有记录"
```

**Skill**: `memory-search-glm`

---

### 4️⃣ Retain 格式（结构化记忆提取）

**三种标签**：
- **W**（World Fact）- 世界事实，客观持久
- **B**（Behavior）- 我们做了什么
- **O**（Opinion）- 观点/偏好，带信心度 (0.0-1.0)

**示例**：
```markdown
## Retain
- W @飞书API: 飞书不支持 img 标签，必须用 upload_image API
- B @CEO-Agent: 今日完成选题审核，发布3篇小红书
- O(c=0.9) @内容策略: 深度长文比短平快内容更受目标读者欢迎
```

**脚本**: `/root/.openclaw/workspace/scripts/retain-extractor.py`

---

### 5️⃣ 过期清理机制

| 类型 | 策略 |
|------|------|
| 任务状态 | 完成即时归档 |
| 每日日志 | 30 天自动归档 |
| 规范/事故 | 永久保留 + 定期审计 |

**脚本**: `/root/.openclaw/workspace/scripts/memory-cleanup.sh`

---

## 🔧 工具和命令

### 全局命令

```bash
# 提取 Retain 格式
retain-extract "用户消息"

# 记忆健康检查
memory-health

# 记忆清理
memory-cleanup

# 搜索记忆
memory-search-glm "关键词"

# 更新记忆
memory-update "内容" "important"
```

### Hook 系统

**对话前 Hook**（自动触发）：
- `~/.agents/skills/memory-search-hook/SKILL.md`
- 执行: `~/.agents/skills/memory-search-hook/scripts/search.sh "$USER_MESSAGE"`

---

## 📊 记忆健康监控

**每日检查清单**：
- MEMORY.md 是否超出 2000 tokens？
- 每日日志是否有 Retain 段落？
- SESSION-STATE.md 是否超过 24 小时未更新？
- 有没有相互矛盾的规则？
- 最近 7 天有没有重复发布事故？

**脚本**: `/root/.openclaw/workspace/scripts/memory-health-check.sh`

---

## 🎯 5 条根本性结论

1. **AI Agent 的记忆问题，本质是知识管理问题**
2. **记忆系统的成熟度，决定 AI Agent 的可靠性**
3. **事故是最好的设计老师**
4. **"收到" ≠ "记住"**
5. **从 v1.0 到 v2.0 的跃迁，是建立完整闭环**

---

## 📁 文件结构

```
/root/.openclaw/workspace/
├── MEMORY.md                  # 热记忆（核心身份）
├── SESSION-STATE.md           # 热记忆（当前状态）
├── memory/                    # 温记忆（每日日志）
│   ├── 2026-03-30.md
│   └── archive/               # 冷记忆（归档）
├── bank/                      # 温记忆（结构化知识库）
│   ├── decisions/
│   ├── entities/
│   └── lessons-learned/
└── scripts/                   # 工具脚本
    ├── retain-extractor.py    # Retain 提取
    ├── memory-health-check.sh # 健康检查
    ├── memory-cleanup.sh      # 清理归档
    └── wal-protocol-check.sh  # WAL 检查
```

---

## ✅ 已完成的改进

1. ✅ **SESSION-STATE.md** - 当前任务状态
2. ✅ **bank/** - 结构化知识库
3. ✅ **Retain 格式** - 结构化记忆提取
4. ✅ **记忆健康监控** - 每日检查脚本
5. ✅ **过期清理机制** - 自动归档
6. ✅ **WAL 协议检查** - 强制写入

---

## 🚀 下一步

1. **压缩 MEMORY.md** - 当前 12036 tokens，需要压缩到 2000 以内
2. **集成到 AGENTS.md** - 添加记忆系统到 Every Session 流程
3. **创建定期任务** - 使用 cron 自动执行健康检查和清理

---

**状态**: ✅ 记忆系统 v2.0 已部署
**参考**: [Wesley AI 日记 - 给 OpenClaw Agent Team 装上记忆](https://mp.weixin.qq.com/s/QO90WBfHDZuNGUCFezWyow)
