# MemPalace 深度研究 - 集成方案

**研究时间**: 2026-04-08 12:20
**目标**: 将 MemPalace 集成到大领导系统
**研究者**: 大领导 + 小新

---

## 🎯 研究目标

1. **深度分析 MemPalace 架构**
2. **对比现有系统差异**
3. **制定集成方案**
4. **评估实施难度**

---

## 📊 MemPalace 核心架构分析

### 1. 宫殿式记忆结构 ⭐⭐⭐

```
Palace（宫殿）
├── Wing（翼）- 人物或项目
│   ├── Room（房间）- 具体主题
│   │   ├── Closet（壁橱）- 摘要
│   │   │   └── Drawer（抽屉）- 原始文件
│   ├── Hall（走廊）- 连接房间
│   └── Tunnel（隧道）- 跨 Wing 连接
```

**关键洞察**:
- **Wing** = 我们的 Scene Block 分类
- **Room** = 具体场景或任务
- **Hall** = 场景类型（技术支持、AI交互、信息采集）
- **Tunnel** = 跨场景关联（如"系统使用咨询"在多个项目中出现）

### 2. AAAK 压缩语言 ⭐⭐⭐

**特点**:
- 有损缩写系统
- 实体代码（如 KAI = Kai, DRFTWD = Driftwood）
- 结构标记（|, →, ★）
- 句子截断

**示例**:
```
原始: "Kai decided to migrate auth to Clerk because it's cheaper than Auth0"
AAAK: "KAI→auth.migrate|Clerk>Auth0|cost.decision"
```

**优势**:
- 30x 压缩（理论上）
- 任何 LLM 可读
- 无需解码器

**劣势**:
- 有损（精度下降）
- 小规模不节省 token
- 当前版本：84.2% vs 原始 96.6%

### 3. 知识图谱 ⭐⭐

**特点**:
- 时序实体关系（SQLite）
- 有效期窗口
- 时间线查询

**示例**:
```python
kg.add_triple("Kai", "works_on", "Orion", valid_from="2025-06-01")
kg.invalidate("Kai", "works_on", "Orion", ended="2026-03-01")
kg.timeline("Orion")  # 项目时间线
```

### 4. Agent Diary ⭐⭐

**特点**:
- 每个 Agent 独立日记
- AAAK 格式持久化
- 跨会话保持

**示例**:
```python
mempalace_diary_write("reviewer", "PR#42|auth.bypass.found|★★★★")
mempalace_diary_read("reviewer", last_n=10)
```

---

## 🔍 与我们系统的对比

### 当前系统架构

```
memory-tdai/
├── scene_blocks/
│   ├── 技术支持-系统使用咨询.md
│   ├── 信息采集-HackerNews资讯.md
│   └── AI交互-协作模式设定.md
└── （索引文件）
```

### 对比分析

| 维度 | MemPalace | 我们的系统 |
|------|-----------|-----------|
| **结构** | Wing → Room → Closet → Drawer | Scene Blocks（扁平） |
| **关联** | Hall + Tunnel（自动） | 手动搜索 |
| **压缩** | AAAK | 无 |
| **知识图谱** | SQLite（时序） | 无 |
| **Agent 记忆** | Agent Diary | 共享记忆 |
| **评分** | 96.6% | 未测试 |
| **开源** | ✅ MIT | ✅ |

---

## 💡 集成方案

### 方案 A: 完全替换（激进）⭐⭐⭐

**步骤**:
1. 安装 MemPalace
2. 迁移现有 Scene Blocks
3. 重新设计记忆架构
4. 更新所有 Agent

**优势**:
- ✅ 最高性能（96.6%）
- ✅ 完整功能（KG + AAAK）
- ✅ MCP 集成（19 工具）

**劣势**:
- ❌ 工作量大（2-4 周）
- ❌ 破坏现有系统
- ❌ 需要重新训练

### 方案 B: 并行运行（保守）⭐⭐

**步骤**:
1. 安装 MemPalace（新路径）
2. 保留现有系统
3. 新项目用 MemPalace
4. 逐步迁移

**优势**:
- ✅ 风险低
- ✅ 可以测试
- ✅ 逐步过渡

**劣势**:
- ❌ 双系统维护
- ❌ 数据分散

### 方案 C: 借鉴设计（推荐）⭐⭐⭐

**步骤**:
1. **借鉴宫殿架构**
   - Wing → Scene Block 分类
   - Room → 具体场景
   - Hall → 场景类型
   - Tunnel → 跨场景关联

2. **实现知识图谱**
   - 使用 SQLite
   - 时序实体关系
   - 时间线查询

3. **优化压缩**
   - 保留 QMD（已有）
   - 可选集成 AAAK

4. **添加 Agent Diary**
   - 每个专业 Agent 独立日记
   - 跨会话持久化

**优势**:
- ✅ 保持现有系统
- ✅ 借鉴核心思想
- ✅ 渐进式改进
- ✅ 控制风险

**劣势**:
- ❌ 需要开发时间
- ❌ 可能不如原版

---

## 🎯 推荐方案：C（借鉴设计）

### 实施计划

#### Phase 1: 宫殿架构升级（1 周）

**目标**: 将 Scene Blocks 升级为宫殿结构

**步骤**:
1. **创建 Wing 分类**
   ```python
   wings = {
       "wing_tech": "技术支持",
       "wing_info": "信息采集",
       "wing_ai": "AI交互",
       "wing_project": "项目管理"
   }
   ```

2. **创建 Room 映射**
   ```python
   rooms = {
       "系统使用咨询": "wing_tech",
       "HackerNews资讯": "wing_info",
       "协作模式设定": "wing_ai"
   }
   ```

3. **实现 Hall 连接**
   ```python
   halls = {
       "hall_facts": "决策和事实",
       "hall_events": "事件和里程碑",
       "hall_discoveries": "发现和洞察",
       "hall_preferences": "偏好和习惯",
       "hall_advice": "建议和方案"
   }
   ```

4. **实现 Tunnel 关联**
   ```python
   # 自动检测跨 Wing 的相同 Room
   tunnels = auto_detect_tunnels(scene_blocks)
   ```

#### Phase 2: 知识图谱实现（1-2 周）

**目标**: 添加时序实体关系

**步骤**:
1. **创建 SQLite 数据库**
   ```python
   # memory-tdai/knowledge_graph.db
   CREATE TABLE triples (
       subject TEXT,
       predicate TEXT,
       object TEXT,
       valid_from TEXT,
       valid_until TEXT,
       created_at TEXT
   );
   ```

2. **实现基础操作**
   ```python
   kg = KnowledgeGraph()
   kg.add_triple("幸运小行星", "使用", "OpenClaw", valid_from="2026-03-01")
   kg.query_entity("幸运小行星")
   kg.timeline("OpenClaw")
   ```

3. **集成到搜索**
   ```python
   # 先查知识图谱，再查 Scene Blocks
   kg_results = kg.query(query)
   scene_results = search_scene_blocks(query)
   ```

#### Phase 3: Agent Diary（1 周）

**目标**: 每个专业 Agent 独立记忆

**步骤**:
1. **创建 Diary 目录**
   ```
   memory-tdai/agents/
   ├── agent_xiaoxin_diary.md
   ├── agent_xiaolan_diary.md
   └── agent_designer_diary.md
   ```

2. **实现 Diary API**
   ```python
   def write_diary(agent_id, entry):
       """写入日记"""
       diary_path = f"memory-tdai/agents/{agent_id}_diary.md"
       with open(diary_path, "a") as f:
           f.write(f"\n## {datetime.now()}\n{entry}\n")
   
   def read_diary(agent_id, last_n=10):
       """读取最近 N 条"""
       pass
   ```

3. **集成到 Agent 工作流**
   ```python
   # 小新完成任务后
   write_diary("xiaoxin", "完成了 FinanceDatabase 集成，健康度 70/100")
   ```

#### Phase 4: 压缩优化（可选，1 周）

**目标**: 评估是否需要 AAAK

**步骤**:
1. **测试 AAAK 压缩**
   ```python
   from mempalace.dialect import AAAKCompressor
   compressor = AAAKCompressor()
   compressed = compressor.compress(original_text)
   ```

2. **对比 QMD**
   - QMD：已有，效果好
   - AAAK：有损，小规模不节省

3. **决策**
   - 如果 QMD 足够 → 保留 QMD
   - 如果需要更高压缩 → 评估 AAAK

---

## 📊 预期成果

### 短期（2-4 周）

**Phase 1-2**:
- ✅ 宫殿架构升级
- ✅ 知识图谱实现
- ✅ 搜索性能提升

**Phase 3**:
- ✅ Agent Diary 实现
- ✅ 专业 Agent 记忆隔离

**Phase 4**:
- ✅ 压缩方案评估
- ✅ Token 优化

### 中期（1-2 个月）

**性能提升**:
- 搜索精度：预计 +20-30%
- 关联发现：自动 Tunnel 检测
- 时序查询：知识图谱支持

**功能增强**:
- Agent 独立记忆
- 时间线查询
- 跨场景关联

### 长期（3-6 个月）

**完整集成**:
- ✅ 宫殿式架构
- ✅ 知识图谱
- ✅ Agent Diary
- ✅ 压缩优化

**测试验证**:
- LongMemEval 测试
- 与原版 MemPalace 对比
- 性能基准测试

---

## 🚀 下一步行动

### 立即行动（本周）

1. **安装 MemPalace**（测试）
   ```bash
   pip install mempalace
   mempalace init /tmp/mempalace-test
   ```

2. **测试基础功能**
   ```bash
   mempalace mine /root/.openclaw/workspace/memory-tdai/scene_blocks/
   mempalace search "系统使用"
   ```

3. **评估性能**
   - 搜索速度
   - 结果质量
   - 资源占用

### 短期行动（下周）

1. **开始 Phase 1**
   - 创建 Wing 分类
   - 实现 Room 映射
   - 实现 Hall 连接

2. **设计知识图谱**
   - 数据库 schema
   - API 设计
   - 集成方案

### 中期行动（2-4 周）

1. **完整实现 Phase 1-3**
2. **测试和优化**
3. **性能对比**

---

## 🎯 成功指标

### 性能指标

- **搜索精度**: >90%（目标 95%）
- **搜索速度**: <100ms
- **关联发现**: 自动检测 Tunnel

### 功能指标

- **知识图谱**: 时序查询支持
- **Agent Diary**: 3 个专业 Agent
- **宫殿架构**: Wing/Room/Hall/Tunnel

### 质量指标

- **LongMemEval**: >90%
- **用户满意度**: 主观评估
- **稳定性**: 零崩溃

---

**最后更新**: 2026-04-08 12:20
**研究者**: 大领导 🎯
**状态**: 📖 研究完成，等待确认
