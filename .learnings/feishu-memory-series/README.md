# 彬子 OpenClaw 记忆系统系列 - 学习笔记

**学习时间**: 2026-03-21
**来源**: 彬子 AI Agent 新手村
**文章**: 三篇系列文章
**整合**: 大领导 🎯

---

## 📚 **文章概览**

### 第一篇：构建主被动记忆的防线
**主题**: 记录机制 + 补录机制
**核心**: 三道防线设计
- 第一道：Memory Flush（内部机制）
- 第二道：心跳扫描（60分钟周期）
- 第三道：夜间反思（天级别梳理）

### 第二篇：打造记忆检索的引擎
**主题**: 检索引擎优化
**核心**: Memory Core + QMD 双轨方案
- Memory Core：开箱即用，稳定
- QMD：高质量检索，多 Collection

### 第三篇：优化上下文管理（预告）
**主题**: Context Engine 插槽机制
**核心**: 持续理解能力提升

---

## 🎯 **核心理念**

### 📦 **Local First**
一切以本地文件为唯一真实信源
- 可查阅、可追溯、可解释
- 文件 > 应用、数据库

### 📄 **Files are the source of truth**
- Markdown 文件是核心
- 记录一切
- 结构化知识

### 🔄 **File Over App**
- 应用只是视图层
- 文件是数据层
- 数据 > 应用

---

## 🛡️ **三道防线设计**

### 🥇 **第一道：Memory Flush（内部机制）**

**触发时机**: 上下文 80k tokens

**流程**:
```
上下文增长 → [74k/100k] Memory Flush 触发
  ↓
静默 Agent 轮次 → 写入记忆文件 → NO_REPLY
  ↓
[80k/100k] Session Compact 触发
  ↓
LLM 总结旧对话 → 写入压缩摘要 → 保留最近消息
```

**约束**:
- ✅ 只追加，不覆盖
- ✅ 标准文件名 `YYYY-MM-DD.md`
- ✅ 不碰引导文件
- ✅ 没内容就回 NO_REPLY

---

### 🥈 **第二道：心跳扫描机制（60 分钟周期）**

**任务配置**: `HEARTBEAT.md`

**Skill**: `memory-heartbeat`

**功能**:
1. 扫描所有 sessions
2. 消息清洗（过滤噪音）
3. 信息提取（加权打分）
4. 知识提取（CRUD 验证）
5. 刷新 NOW.md

**脚本**: `~/.openclaw/scripts/general-session-scanner.sh`

**评分规则**:
- **结论/建议/已完成/根因** → +2~5 分
- **示例块** → -6 分

---

### 🥉 **第三道：夜间反思（天级别梳理）**

#### 任务 1: 00:45 - 日志查缺补漏
**脚本**: `lcm-daily-sync.py`

**功能**:
- 扫描 24 小时消息
- 结构化清洗
- 对比分析
- 生成反思素材

**输出**: `memory/{targetDate}-reflection-prep.md`

#### 任务 2: 01:00 - 深度反思和文件整理
**模型**: Qwen3.5-plus

**功能**:
- 深度反思
- 知识回写
- 文件整理

**输出**: `memory/reflections/{targetDate}.md`

---

## 🔍 **检索引擎优化**

### Memory Core 调优

#### 混合检索
```
BM25 检索 ←─────┐
↓                  │
向量检索 ←─────┤ 并行
↓                  │
候选池合并 ←───────┘（去重）
↓
加权打分（70% 语义 + 30% 关键词）
↓
MMR 多样性重排
↓
时间衰减调整
↓
Top-N 返回（带引用）
```

#### 配置要点
- **vectorWeight**: 0.7（语义）
- **textWeight**: 0.3（关键词）
- **candidateMultiplier**: 4
- **mmr.lambda`: 0.7
- **temporalDecay.halfLifeDays**: 30

---

### QMD 备选方案

#### 优势
- ✅ **Markdown 优先**：文件是唯一真实信源
- ✅ **多 Collection**：独立管理，灵活检索
- ✅ **跨 App 统一**：Memory + Obsidian 联合

#### 配置示例
```json
{
  "memory": {
    "backend": "qmd",
    "citations": "auto",
    "qmd": {
      "command": "qmd",
      "searchMode": "vsearch",
      "includeDefaultMemory": true,
      "paths": [
        {
          "name": "obsidian",
          "path": "~/Documents/ObsidianVault",
          "pattern": "**/*.md"
        }
      ]
    }
  }
}
```

#### Collection 配置
```
memory-root-main:  ~/.openclaw/workspace/
obsidian:         ~/Documents/ObsidianVault/
```

---

## 📁 **记忆文件结构演进**

```
memory/
├── MEMORY.md         # 重要事项
├── NOW.md              # 当前待办
├── INDEX.md            # 分类索引
├── YYYY-MM-DD.md       # 每日日志
├── YYYY-MM-DD-reflection-prep.md   # 每日备忘录
├── lessons/            # 经验教训
├── decisions/          # 重大决策
├── projects/           # 项目状态
├── preferences/        # 偏好选择
└── reflections/        # 深度反思
```

---

## 📊 **效果对比**

| 指标 | 之前 | 之后 |
|------|------|------|
| **日志完整性** | ~60% | ~95% |
| **决策可追溯** | 靠主动记录 | memory/decisions/ |
| **经验复用** | 几乎为零 | 30+ lessons |
| **过时文件** | 无人问津 | 自动标记 |

---

## 🎯 **对你的建议**

### 💡 **建议 1: 优化 Memory Core 配置**

我可以帮你：
- 📊 配置混合检索（语义 70% + 关键词 30%）
- 🤖 配置 Qwen Embedding（中文优化）
- 🔧 配置 MMR 多样性重排
- ⏰ 配置时间衰减（30 天半衰期）

### 💡 **建议 2: 增强记忆扫描**

我可以帮你：
- 🤖 创建 memory-heartbeat Skill
- 📊 每天定时扫描对话
- 🤝 自动提取关键信息
- 📝 自动更新 MEMORY.md

### 💡 **建议 3: 集成 QMD 系统**

我可以帮你：
- 🔧 安装 QMD CLI
- 📁 配置多 Collection
- 🔗 连接 Obsidian 笔记库
- 🚀 启动常驻服务

### 💡 **建议 4: 创建检索优化脚本**

我可以帮你：
- 🔍 创建查询扩展脚本
- 🎯 配置 Reranker 重排
- 📈 提升检索准确度

---

## 🚀 **下一步**

**你想让我帮你实现这些功能吗？** 🤔

1. **优化 Memory Core 配置**
2. **安装和配置 QMD**
3. **创建检索优化脚本**
4. **集成 Obsidian 笔记库**

**或者你想先解决其他问题？** 🤔
