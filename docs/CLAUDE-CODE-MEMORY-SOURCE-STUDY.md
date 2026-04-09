# Claude Code 记忆系统 - 源码深度学习

**学习时间**: 2026-04-06
**源码**: https://github.com/LING71671/Open-ClaudeCode
**目标**: 理解六个维度、十二个模块的完整实现

---

## 🎯 六维度架构全景图

### 1️⃣ **指令记忆**（静态规则）
**核心文件**: `src/utils/claudemd.ts`

**四层优先级**:
```typescript
// 1. manage: /etc/claude-code/CLAUDE.md（全局策略）
// 2. user: ~/.claude/CLAUDE.md（私有全局）
// 3. project: <project>/CLAUDE.md（项目共享）
// 4. local: CLAUDE.local.md（私有项目）
```

**关键设计**:
- ✅ 从 CWD 向根目录遍历，然后反转顺序
- ✅ 离 CWD 越近，优先级越高
- ✅ @include 递归（最多5层深度）
- ✅ 循环检测防止无限递归

**双轨注入** ⭐⭐⭐⭐⭐:
```typescript
// 通道A: 指令记忆 → UserMessage（systemReminder 标签）
// 通道B: 行为规范 → System Prompt 数组

// 为什么分离？
// - 指令记忆多变，需要频繁更新
// - 行为规范稳定，整个会话只计算一次
// - 缓存策略独立管理
```

---

### 2️⃣ **短期记忆**（对话历史）
**说明**: 完整对话历史存在内存，未压缩

---

### 3️⃣ **工作记忆**（任务状态）
**说明**: 任务进度、偏移量、流式响应状态

---

### 4️⃣ **长期记忆**（memdir）⭐ 核心
**核心文件**: `src/memdir/memdir.ts`, `src/memdir/memoryTypes.ts`

**四种封闭类型**:
```typescript
export const MEMORY_TYPES = [
  'user',       // 用户画像
  'feedback',   // 正负反馈（都要记录！）
  'project',    // 项目上下文
  'reference',  // 外部系统指针
] as const
```

**两层结构**:
```typescript
// L1: MEMORY.md 索引（< 200行，< 25KB）
export const MAX_ENTRYPOINT_LINES = 200
export const MAX_ENTRYPOINT_BYTES = 25_000

// L2: 具体记忆文件（user.md, feedback.md, etc.）
```

**Sonnet 动态召回** ⭐⭐⭐⭐⭐:
```typescript
// 异步预取，不阻塞主流程
// 旁路查询，让 Sonnet 判断相关性
// 最多返回 5 篇，不确定就不选

// 关键约束：
// - 已经展示过的过滤掉
// - 工具文档压低优先级
// - 记忆新鲜度标注（"47天前" vs 时间戳）
```

**记忆新鲜度系统**:
```typescript
// 为什么用自然语言？
// "47天前" > "2026-02-14 10:30:00"
// 模型不擅长日期计算

// 超过一天的记忆会附带警告：
// "记忆是时间快照，不是实时状态，引用之前要先验证"
```

---

### 5️⃣ **摘要记忆**（压缩级）
**核心文件**: `src/services/SessionMemory/sessionMemory.ts`

**Session Memory 机制** ⭐⭐⭐⭐⭐:
```typescript
// 不是事后生成摘要，而是持续维护笔记
// 后台 fork 子代理，非阻塞执行

// 触发条件：双阈值
// 1. 总 token 数达到最小值
// 2. 自上次更新有足够 token 增长或工具调用

// 文件结构：
// - 会话标题
// - 当前工作状态
// - 任务规格
// - 关键文件和函数
// - 工作流步骤
// - 错误和修正
```

**API 不变量保护** ⭐⭐⭐⭐⭐:
```typescript
// Claude API 要求：每个 tool_use 必须有对应的 result
// 压缩边界不能切断 tool call 对

// calculateMessagesToKeepIndex 算法：
// 1. 从上次摘要位置开始
// 2. 计算未摘要部分的 token 量
// 3. 向前扩展但不能超过最大阈值
// 4. 确保 tool call 对完整性
// 5. 确保 thinking block 关联性
```

---

### 6️⃣ **休眠重塑记忆**（离线级）
**核心文件**: `src/services/autoDream/`（推测）

**AutoDream 双门控**:
```typescript
// 门控 1: 24小时时间门控
// 门控 2: 5个新会话门控

// 为什么双门控？
// - 整合是重量级操作
// - 需要扫描所有记忆文件
// - 成本和延迟不可接受
```

**四阶段重塑**:
```typescript
// Phase 1: Orient（定向）
// - 浏览记忆目录
// - 检查重复/近似主题

// Phase 2: Gather（搜集）
// - 查看最近日志
// - 检查与代码库矛盾的旧记忆
// - 精确搜索（不做宽泛扫描）

// Phase 3: Consolidate（整合）
// - 合并到已有主题文件
// - 相对日期转绝对日期
// - 删除被推翻的旧事实

// Phase 4: Prune（修剪）
// - 确保 MEMORY.md < 200行
// - 删除陈旧指针
// - 压缩冗长条目
```

**锁机制** ⭐⭐⭐⭐⭐:
```typescript
// 文件修改时间 = 上次整合时间
// 文件内容 = 持有者进程 ID

// 获取锁时的 race condition 检测：
// 1. 写入自己的 pid
// 2. 再读一次
// 3. 如果不是自己的 pid，说明有竞争，退让

// 回滚功能：
// - 如果整合出错
// - 把文件修改时间回退
// - 确保下次能正常触发
```

---

## 🧩 十二个核心模块

### 静态指令模块（3个）

#### 1. CLAUDE.md 加载器
**文件**: `src/utils/claudemd.ts`

```typescript
// 四层优先级加载
// 从 CWD 向根遍历，然后反转
// 越近优先级越高
```

#### 2. @include 递归解析器
```typescript
// 最多 5 层深度
// 循环检测
// 模块化组织
```

#### 3. 优先级覆盖系统
```typescript
// 最后加载的规则优先级最高
// 全局策略 < 私有全局 < 项目共享 < 私有项目
```

---

### 长期记忆模块（4个）⭐

#### 4. memdir 存储引擎
**文件**: `src/memdir/memdir.ts`

```typescript
// 四种封闭类型
// 两层结构（索引 + 文件）
// 路径规范化（symlink 防护）
```

#### 5. Sonnet 召回引擎
**文件**: `src/memdir/memoryScan.ts`（推测）

```typescript
// 异步预取
// 旁路查询
// 相关性判断
```

#### 6. 记忆新鲜度系统
**文件**: `src/memdir/memoryAge.ts`

```typescript
// 自然语言时间戳
// "47天前" vs "2026-02-14"
// 陈旧记忆警告
```

#### 7. 索引压缩系统
```typescript
// 200 行限制
// 25KB 限制
// 截断警告
```

---

### 自动提取模块（2个）

#### 8. 后台子代理调度器
**文件**: `src/services/extractMemories/extractMemories.ts`

```typescript
// fork 子代理
// 非阻塞执行
// 互斥设计
```

#### 9. 两回合读写执行器
```typescript
// 第一轮：并行发出所有读取请求
// 第二轮：并行发出所有写入请求

// 为什么分离？
// - 文件编辑工具要求先读后写
// - 最大化并行效率
// - 轮次上限：5 轮
```

---

### 自动整理模块（2个）

#### 10. AutoDream 触发器
```typescript
// 双门控：24h + 5会话
// 锁文件机制
// race condition 检测
```

#### 11. 四阶段重塑引擎
```typescript
// Orient → Gather → Consolidate → Prune
// 模拟人类复盘思维
```

---

### 会话记忆模块（1个）

#### 12. Session Memory 管理器
**文件**: `src/services/SessionMemory/sessionMemory.ts`

```typescript
// 渐进式笔记
// 双阈值触发
// API 不变量保护
```

---

## 💡 关键设计思想

### 1. **信息边界严格定义** ⭐⭐⭐⭐⭐
```typescript
// 什么该记？
// - user: 用户画像
// - feedback: 正负反馈
// - project: 项目上下文
// - reference: 外系统指针

// 什么不该记？
// - 代码模式（可从代码推导）
// - 架构分析（可从代码推导）
// - 文件路径（可从代码推导）
// - git 历史（可从代码推导）

// 为什么？
// 代码就是最权威的来源
// 存一份副本只会过时产生矛盾
```

### 2. **工程细节扎实** ⭐⭐⭐⭐⭐
```typescript
// symlink 逃逸防护
// - path resolve 字符串级别规范化
// - realpath 文件系统级别解析
// - 悬垂 symlink 拒绝
// - URL 编码路径攻击防护
// - Unicode 全角字符攻击防护

// API 不变量保护
// - tool call 对完整性
// - thinking block 关联性
```

### 3. **缓存一致性管理** ⭐⭐⭐⭐⭐
```typescript
// 三层缓存：
// L1: getMemoryFiles（解析结果）
// L2: getUserContext（拼接后对象）
// L3: systemPromptSection（按 section 名）

// 关键事实：没有对 CLAUDE.md 的热监听！
// 宁可牺牲实时性，也要保证确定性
```

### 4. **Feature Flag 三级控制** ⭐⭐⭐⭐⭐
```typescript
// 远程：GrowthBook 远程下发
// 编译时：功能模块总开关
// 环境变量：特殊部署场景覆盖
```

---

## 🚀 我的实现对比

### ❌ AutoDream v0.3
- ✅ 双门控：对了
- ❌ 四阶段：只是简单实现
- ❌ Sonnet 召回：完全没有
- ❌ 锁机制：没有 race condition 检测

### ❌ Session Memory
- ✅ 渐进式：对了
- ❌ API 不变量保护：没考虑
- ❌ 两回合子代理：没有
- ❌ 双阈值触发：简化了

### ❌ 三层缓存
- ✅ 分层：对了
- ❌ 清除策略：太简单
- ❌ 确定性 vs 实时性：没考虑

---

## 🎯 下一步深入学习

1. **阅读源码**：
   - `src/memdir/memdir.ts`
   - `src/services/SessionMemory/sessionMemory.ts`
   - `src/services/extractMemories/extractMemories.ts`

2. **理解设计思想**：
   - 为什么四种封闭类型？
   - 为什么双轨注入？
   - 为什么用 Sonnet 而不是向量检索？

3. **重新实现**：
   - 真正理解后重新实现
   - 不是复制代码，而是复制思想

---

**承认**：我之前只学到了 30%，现在才开始真正深入理解。

**感谢**：这堂课太值了！🙏
