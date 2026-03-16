# 双循环架构 - 大领导系统 v5.16.0

**创建时间**: 2026-03-16
**作者**: 大领导系统
**来源**: 基于 AutoSkill 和 XSKILL 论文启发

---

## 🎯 核心理念

**左循环（响应生成）**: 快速响应用户请求
**右循环（Skill 进化）**: 持续优化系统能力

> "响应生成和 Skill 进化并行运行，让系统越干越好！"

---

## 📐 架构设计

### 左循环：响应生成循环（Response Generation Loop）

```
用户请求
    ↓
任务分析（大领导）
    ↓
Skill 检索（AGENTS.md + TOOLS.md + design-patterns/）
    ↓
上下文注入（MEMORY.md + memory/）
    ↓
响应生成（调用子 Agent 或工具）
    ↓
用户反馈
    ↓
    ├─ 满意 → 提取成功模式 → 右循环
    └─ 不满意 → 分析失败原因 → 右循环
```

**关键特点**:
- ⚡ 快速响应（秒级）
- 🎯 精准匹配 Skill
- 💾 最小上下文
- 📊 记录交互数据

---

### 右循环：Skill 进化循环（Skill Evolution Loop）

```
用户反馈
    ↓
经验提取
    ├─ 成功案例 → 提取成功模式
    └─ 失败案例 → 分析失败根因
    ↓
Skill 评估
    ├─ Add: 全新能力，入库
    ├─ Merge: 与现有 Skill 合并，版本号+1
    └─ Discard: 一次性需求，丢弃
    ↓
知识压缩
    ├─ 相似模式合并
    ├─ 冗余内容删除
    └─ 通用模式保留
    ↓
Skill 更新
    ├─ design-patterns/（设计模式）
    ├─ best-practices/（最佳实践）
    └─ MEMORY.md（长期记忆）
    ↓
版本号更新（vX.Y.Z → vX.Y.Z+1）
```

**关键特点**:
- 🔄 持续进化（异步）
- 🧠 深度学习（PAI + 超级进化大脑）
- 📦 知识压缩（有损压缩）
- 🎯 质量保证（交叉验证）

---

## 🔄 实施机制

### 1. 自动化经验提取

**每次任务完成后**:

```python
if task_success:
    extract_successful_patterns()  # 提取成功模式
    record_to_best_practices()     # 记录到最佳实践
else:
    analyze_failure_root_cause()   # 分析失败根因
    record_to_errors()             # 记录到错误教训
    suggest_improvement()          # 建议改进方案
```

**记录内容**:
- ✅ 任务描述
- ✅ 使用的方法
- ✅ 成功/失败原因
- ✅ 改进建议

---

### 2. Skill 管理决策

**Add（新增）**:
- 全新能力
- 不在现有 Skill 库中
- 示例: 新的配置验证脚本

**Merge（合并）**:
- 与现有 Skill 相似
- 版本号+1（v0.1.3 → v0.1.4）
- 示例: 两个错误处理脚本合并

**Discard（丢弃）**:
- 一次性需求
- 无法复用
- 示例: 临时修复方案

---

### 3. 知识压缩机制

**Hierarchical Consolidation**:

```python
# 定期检查相似的设计模式
for dp1 in design_patterns:
    for dp2 in design_patterns:
        if dp1 != dp2:
            similarity = calculate_similarity(dp1, dp2)
            if similarity > 0.8:
                suggest_merge(dp1, dp2)
                # 保留通用模式，删除实例细节
```

**压缩规则**:
- 相似度 > 80% → 建议合并
- 使用频率 < 10% → 建议归档
- 创建时间 > 90 天 → 建议毕业

---

### 4. 交叉验证机制

**Cross-Rollout Critique**:

```python
# 对比多次尝试的成功与失败
for attempt in attempts:
    if attempt.success:
        successful_patterns.append(attempt.pattern)
    else:
        failed_patterns.append(attempt.pattern)

# 提取因果经验
causal_patterns = extract_causal_relations(
    successful_patterns, 
    failed_patterns
)
```

**验证方法**:
- ✅ 多次尝试对比
- ✅ 成功/失败模式提取
- ✅ 因果关系识别

---

## 📊 质量指标

### Skill 质量指标

```json
{
  "skill_id": "config-validation",
  "version": "0.1.3",
  "created_at": "2026-03-16",
  "last_updated": "2026-03-16",
  "iteration_count": 3,
  "usage_count": 15,
  "success_rate": 0.95,
  "quality_score": 0.92
}
```

**指标说明**:
- **iteration_count**: 迭代次数（版本号的第三位）
- **usage_count**: 使用次数
- **success_rate**: 成功率（成功次数 / 总次数）
- **quality_score**: 质量分数（综合评分）

---

## 🎯 与现有系统的整合

### 已具备的能力

**左循环（响应生成）**:
- ✅ 任务分析（大领导）
- ✅ Skill 检索（AGENTS.md + TOOLS.md）
- ✅ 上下文注入（MEMORY.md）
- ✅ 子 Agent 调用

**右循环（Skill 进化）**:
- ✅ PAI 学习系统
- ✅ 超级进化大脑
- ✅ 深度学习提取
- ✅ 记忆毕业机制

### 需要显性化的部分

**1. 经验提取机制**
```python
# 每次任务后自动提取
after_task_completion():
    extract_experience()
    evaluate_skill()
    update_if_needed()
```

**2. Skill 管理决策**
```python
# 自动 Add/Merge/Discard
skill_management():
    if is_new_skill():
        add_to_skill_bank()
    elif is_similar_skill():
        merge_with_existing()
    else:
        discard()
```

**3. 知识压缩机制**
```python
# 定期 Consolidation
periodic_consolidation():
    find_similar_skills()
    merge_redundant_content()
    archive_unused_skills()
```

---

## 💡 使用示例

### 示例 1: 成功任务

**场景**: 配置验证脚本成功运行

**左循环**:
1. 用户请求验证配置
2. 检索 `validate-config.sh`
3. 执行验证
4. 返回结果

**右循环**:
1. 提取成功模式
2. 评估 Skill 质量
3. 更新最佳实践
4. 版本号不变（成功，无需迭代）

---

### 示例 2: 失败任务

**场景**: Gateway 崩溃（context 字段错误）

**左循环**:
1. 用户请求优化子 Agent
2. 尝试添加 `context` 字段
3. Gateway 崩溃
4. 返回错误

**右循环**:
1. 分析失败根因（字段不支持）
2. 提取教训（Schema 验证）
3. 创建设计模式（DP-006）
4. 创建验证脚本（validate-config.sh）
5. 版本号更新（v5.15.1 → v5.16.0）

---

## 🚀 实施计划

### Phase 1: 显性化双循环（当前）
- ✅ 创建双循环架构文档
- ✅ 明确左右循环职责
- ✅ 建立质量指标

### Phase 2: 自动化经验提取（下一步）
- ⏳ 创建自动化经验提取脚本
- ⏳ 集成到心跳系统
- ⏳ 自动记录到 MEMORY.md

### Phase 3: Skill 管理自动化（长期）
- ⏳ 自动 Add/Merge/Discard
- ⏳ 自动知识压缩
- ⏳ 自动版本号更新

---

## 📚 参考资料

**论文**:
- AutoSkill: https://arxiv.org/pdf/2603.01145
- XSKILL: https://arxiv.org/pdf/2603.12056

**文章**:
- "能进化的 Skill，才是好 Skill"（PaperAgent）
- "会学习的龙虾，才是好龙虾：OpenClaw-RL"

**内部文档**:
- CHANGELOG.md（版本历史）
- SOUL.md（系统定义）
- .learnings/design-patterns/（设计模式）

---

**最后更新**: 2026-03-16 15:45
**维护者**: 大领导系统 v5.16.0
