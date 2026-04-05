# 团队共享机制学习计划

**创建时间**: 2026-04-02 22:33
**参考来源**: ECC Tip 27 - Continuous Learning v2
**目标**: 实现团队级记忆共享和经验传承

---

## 🎯 学习目标

1. **理解 Continuous Learning v2**
   - Instincts vs 硬编码规则
   - 置信度机制（0.7-1.0）
   - 自动学习和应用

2. **掌握核心命令**
   - `/instinct-status` - 查看学到了什么
   - `/instinct-export` - 导出为文件
   - `/instinct-import` - 导入团队经验
   - `/instinct-evolve` - 升华为 Skill

3. **实现工具脚本**
   - instinct-export.sh
   - instinct-import.sh
   - instinct-merge.sh
   - instinct-evolve.sh

---

## 📋 学习内容（基于 ECC Tip 27）

### 核心概念

#### 1. Instincts 是什么？

**定义**:
- Instincts 是"学到的规则"（不是硬编码的）
- 从对话中自动提取
- 带置信度评分

**示例**:
```json
{
  "id": "instinct-001",
  "rule": "在写 Python 脚本时，总是使用 set -euo pipefail",
  "confidence": 0.9,
  "source": "user-feedback",
  "learnedAt": "2026-04-02T22:00:00Z"
}
```

#### 2. 置信度机制

| 置信度 | 行为 |
|--------|------|
| 0.7 - 1.0 | 自动执行 |
| 0.5 - 0.7 | 提示用户 |
| 0.0 - 0.5 | 标记为"仍在验证" |

**为什么**:
- 避免强制执行不确定的规则
- 让用户确认新学到的规则
- 逐步建立信任

#### 3. 核心命令

##### `/instinct-status`

**功能**: 查看学到了什么

**输出**:
```
📊 学到的规则（23 条）

高置信度（0.7-1.0）:
  ✓ [0.9] 总是使用 set -euo pipefail
  ✓ [0.8] 写 Bash 脚本时先写文档

中置信度（0.5-0.7）:
  ? [0.6] 优先使用 Python 3.10+
  ? [0.5] 使用 Git Worktrees 并行开发

低置信度（0.0-0.5）:
  ⏳ [0.4] 使用 Rust 重写关键路径
  ⏳ [0.3] 每周运行一次安全审计
```

##### `/instinct-export`

**功能**: 导出为文件

**格式**: JSON

**示例**:
```bash
/instinct-export > my-instincts.json
```

**输出**:
```json
{
  "version": "1.0",
  "exportedAt": "2026-04-02T22:00:00Z",
  "instincts": [
    {
      "id": "instinct-001",
      "rule": "在写 Python 脚本时，总是使用 set -euo pipefail",
      "confidence": 0.9,
      "source": "user-feedback",
      "learnedAt": "2026-04-02T22:00:00Z"
    }
  ]
}
```

##### `/instinct-import`

**功能**: 导入团队经验

**合并策略**:
- 自动去重
- 解决矛盾（保留高置信度）
- 更新置信度（取最大值）

**示例**:
```bash
/instinct-import team-instincts.json
```

**输出**:
```
📥 导入团队经验...

从: team-instincts.json
导入: 15 条规则
去重: 3 条重复
合并: 12 条新规则

✓ 导入完成
```

##### `/instinct-evolve`

**功能**: 升华为 Skill

**过程**:
1. 选择相关 Instincts
2. 生成 Skill 模板
3. 人工审核和编辑
4. 创建 Skill 文件

**示例**:
```bash
/instinct-evolve "Bash 脚本最佳实践"
```

**输出**:
```
🚀 升华为 Skill...

主题: Bash 脚本最佳实践
相关 Instincts: 5 条

生成 SKILL.md...
✓ 创建: skills/bash-best-practices/SKILL.md

下一步:
1. 编辑 SKILL.md
2. 添加示例代码
3. 测试验证
```

---

## 🚀 实施计划

### 阶段 1: 创建基础脚本（当前任务）

#### 1.1 instinct-export.sh

**功能**: 导出当前 Instincts

**输入**:
- 无（从记忆文件读取）

**输出**:
- JSON 文件

**步骤**:
1. 读取 Retain 条目（O 类型）
2. 提取规则和置信度
3. 生成 JSON
4. 保存到文件

#### 1.2 instinct-import.sh

**功能**: 导入团队经验

**输入**:
- JSON 文件

**输出**:
- 合并到记忆文件

**步骤**:
1. 读取 JSON 文件
2. 解析 Instincts
3. 去重和合并
4. 解决矛盾
5. 追加到记忆文件

#### 1.3 instinct-merge.sh

**功能**: 合并多个 Instincts 文件

**输入**:
- 多个 JSON 文件

**输出**:
- 合并后的 JSON 文件

**步骤**:
1. 读取所有文件
2. 解析所有 Instincts
3. 去重（相同规则保留高置信度）
4. 解决矛盾（相反规则保留高置信度）
5. 输出合并结果

#### 1.4 instinct-evolve.sh

**功能**: 升华为 Skill

**输入**:
- 主题关键词

**输出**:
- Skill 模板

**步骤**:
1. 搜索相关 Instincts
2. 提取共同模式
3. 生成 Skill 模板
4. 创建文件结构

---

### 阶段 2: 实现工具脚本

#### 文件结构

```
.instincts/
├── export/              # 导出的 Instincts
│   ├── my-instincts.json
│   └── team-instincts.json
├── merged/              # 合并后的 Instincts
│   └── merged-instincts.json
└── skills/              # 升华的 Skills
    └── bash-best-practices/
        └── SKILL.md
```

#### 数据格式

**Instinct JSON**:
```json
{
  "version": "1.0",
  "exportedAt": "2026-04-02T22:00:00Z",
  "exportedBy": "大领导 🎯",
  "instincts": [
    {
      "id": "instinct-001",
      "rule": "在写 Python 脚本时，总是使用 set -euo pipefail",
      "confidence": 0.9,
      "source": "user-feedback",
      "learnedAt": "2026-04-02T22:00:00Z",
      "category": "bash",
      "tags": ["bash", "python", "error-handling"]
    }
  ]
}
```

---

### 阶段 3: 测试和验证

#### 测试场景 1: 导出个人经验

```bash
# 导出今天的 Retain 条目
bash scripts/instinct-export.sh > .instincts/export/my-instincts.json

# 查看导出结果
cat .instincts/export/my-instincts.json
```

#### 测试场景 2: 导入团队经验

```bash
# 创建模拟团队经验
cat > .instincts/export/team-instincts.json << EOF
{
  "version": "1.0",
  "exportedAt": "2026-04-02T22:00:00Z",
  "instincts": [
    {
      "id": "team-001",
      "rule": "使用 Git Worktrees 进行并行开发",
      "confidence": 0.8,
      "source": "team-feedback",
      "learnedAt": "2026-04-01T10:00:00Z"
    }
  ]
}
EOF

# 导入
bash scripts/instinct-import.sh .instincts/export/team-instincts.json
```

#### 测试场景 3: 合并去重

```bash
# 合并多个文件
bash scripts/instinct-merge.sh \
  .instincts/export/my-instincts.json \
  .instincts/export/team-instincts.json \
  > .instincts/merged/merged-instincts.json
```

#### 测试场景 4: 升华为 Skill

```bash
# 升华为 Bash 最佳实践 Skill
bash scripts/instinct-evolve.sh "Bash 脚本最佳实践"
```

---

## 📊 成功指标

- ✅ 能够导出 Retain 条目为 JSON
- ✅ 能够导入团队经验并合并
- ✅ 能够去重和解决矛盾
- ✅ 能够升华为 Skill 模板
- ✅ 测试通过，功能正常

---

## 🎯 核心价值

**为什么重要**:
- **"一个人踩过的坑，团队都能规避"**
- 从个人级进化到团队级
- 持续学习和改进

**对比**:

| 维度 | 个人记忆 | 团队共享 |
|------|---------|---------|
| **范围** | 单个 Agent | 整个团队 |
| **价值** | 个人进化 | 团队进化 |
| **速度** | 自己踩坑 | 避免重复踩坑 |
| **质量** | 逐步积累 | 集体智慧 |

---

**状态**: 🔄 开始学习
**预计时间**: 3-4 小时
**优先级**: 🔴 最高
**目标**: 建立团队级经验传承机制
