# Skill Bank - 大领导系统 v5.16.0

**创建时间**: 2026-03-16
**目的**: 系统化的 Skill 管理，版本控制，质量追踪

---

## 📁 目录结构

```
skills-bank/
├── system/                    # 系统级 Skills
│   ├── config-validation/     # 配置验证
│   ├── error-diagnosis/       # 错误诊断
│   ├── web-content-fetcher/   # 网页内容提取
│   └── opencode-integration/  # OpenCode 集成
│
├── design-patterns/           # 设计模式
│   ├── DP-001/               # 第一个设计模式
│   ├── DP-002/               # 第二个设计模式
│   └── ...
│
└── best-practices/            # 最佳实践
    ├── BP-001/               # 第一个最佳实践
    ├── BP-002/               # 第二个最佳实践
    └── ...
```

---

## 🎯 Skill 元数据格式

每个 Skill 目录包含：

```
skill-id/
├── skill.md                  # Skill 描述
├── version.json             # 版本信息
├── history/                 # 历史记录
│   └── changelog.md        # 变更日志
└── tests/                   # 测试用例（可选）
    └── test.md
```

---

## 📊 版本信息示例

```json
{
  "skill_id": "config-validation",
  "name": "配置验证",
  "version": "0.1.3",
  "created_at": "2026-03-16",
  "last_updated": "2026-03-16",
  "iteration_count": 3,
  "usage_count": 15,
  "success_rate": 0.95,
  "quality_score": 0.92,
  "category": "system",
  "tags": ["validation", "config", "gateway"],
  "status": "active"
}
```

**字段说明**:
- `version`: 主版本.次版本.迭代次数
- `iteration_count`: 迭代次数（第三位数字）
- `usage_count`: 使用次数
- `success_rate`: 成功率（0-1）
- `quality_score`: 质量分数（0-1）
- `status`: active（活跃）, archived（归档）, deprecated（废弃）

---

## 🔄 Skill 管理决策

### Add（新增）
**条件**:
- 全新能力
- 不在现有 Skill 库中
- 有明确的使用场景

**操作**:
```bash
# 创建新 Skill
mkdir -p skills-bank/system/new-skill
echo "创建 skill.md, version.json"
```

---

### Merge（合并）
**条件**:
- 与现有 Skill 相似度 > 80%
- 功能重叠
- 可以整合

**操作**:
```bash
# 合并 Skill
# 1. 保留通用模式
# 2. 版本号+1（v0.1.3 → v0.1.4）
# 3. 删除冗余内容
# 4. 更新 changelog
```

**示例**:
- `config-validation` (v0.1.3) + `config-check` (v0.1.1)
- → 合并为 `config-validation` (v0.1.4)

---

### Discard（丢弃）
**条件**:
- 一次性需求
- 无法复用
- 已被更好的方案替代

**操作**:
```bash
# 归档或删除
mv skills-bank/unused-skill skills-bank/archived/
```

---

## 📈 质量指标

### 使用频率
- 高频（使用次数 > 50）: 核心技能
- 中频（10-50）: 常用技能
- 低频（< 10）: 辅助技能

### 成功率
- 优秀（> 0.9）: 稳定可靠
- 良好（0.7-0.9）: 基本可用
- 需改进（< 0.7）: 需要优化

### 质量分数
```
quality_score = (success_rate * 0.6) + (usage_frequency * 0.3) + (recency * 0.1)
```

---

## 🎯 当前 Skills

### 系统 Skills（system/）

#### config-validation（配置验证）
- **版本**: v0.1.3
- **迭代次数**: 3
- **使用次数**: 15
- **成功率**: 0.95
- **质量分数**: 0.92
- **描述**: 验证 OpenClaw 配置文件，检查无效字段

#### error-diagnosis（错误诊断）
- **版本**: v0.1.1
- **迭代次数**: 1
- **使用次数**: 5
- **成功率**: 0.90
- **质量分数**: 0.88
- **描述**: 快速诊断 Gateway 错误，提供修复建议

#### web-content-fetcher（网页内容提取）
- **版本**: v0.1.2
- **迭代次数**: 2
- **使用次数**: 10
- **成功率**: 0.98
- **质量分数**: 0.94
- **描述**: 提取微信公众号等 6 大平台的正文内容

#### opencode-integration（OpenCode 集成）
- **版本**: v0.1.1
- **迭代次数**: 1
- **使用次数**: 8
- **成功率**: 0.92
- **质量分数**: 0.90
- **描述**: OpenCode CLI 集成，免费模型调用

---

### 设计模式（design-patterns/）

**现有数量**: 31+ 个
**版本范围**: v0.1.0 - v0.1.5
**最高迭代**: DP-001（5 次迭代）

**热门模式**:
- DP-001: API 分页处理（v0.1.5，使用 45 次）
- DP-006: 子 Agent Token 优化（v0.1.3，使用 12 次）

---

### 最佳实践（best-practices/）

**现有数量**: 30+ 个
**版本范围**: v0.1.0 - v0.1.4
**最高迭代**: BP-001（4 次迭代）

**热门实践**:
- BP-001: 配置验证优先（v0.1.4，使用 50 次）
- BP-002: 错误诊断流程（v0.1.3，使用 30 次）

---

## 🚀 自动化管理

### 定期任务

**每周**:
- 统计 Skill 使用频率
- 计算成功率
- 生成质量报告

**每月**:
- 检查相似 Skill（建议合并）
- 归档低频 Skill
- 更新质量分数

**每季度**:
- 全面审查 Skill Bank
- 删除废弃 Skill
- 优化目录结构

---

## 💡 使用示例

### 创建新 Skill

```bash
# 1. 创建目录
mkdir -p skills-bank/system/new-skill

# 2. 创建 skill.md
cat > skills-bank/system/new-skill/skill.md << EOF
# Skill 名称

## 描述
简要描述这个 Skill 的功能

## 使用方法
1. 步骤 1
2. 步骤 2

## 示例
\`\`\`bash
command here
\`\`\`

## 注意事项
- 注意 1
- 注意 2
EOF

# 3. 创建 version.json
cat > skills-bank/system/new-skill/version.json << EOF
{
  "skill_id": "new-skill",
  "name": "新技能",
  "version": "0.1.0",
  "created_at": "$(date +%Y-%m-%d)",
  "last_updated": "$(date +%Y-%m-%d)",
  "iteration_count": 0,
  "usage_count": 0,
  "success_rate": 1.0,
  "quality_score": 0.5,
  "category": "system",
  "tags": [],
  "status": "active"
}
EOF
```

---

### 更新 Skill 版本

```bash
# 使用版本追踪脚本
~/.openclaw/workspace/scripts/track-version.sh "0.1.4" "优化" "改进功能"

# 手动更新 version.json
vim skills-bank/system/skill/version.json
# 更新 version, iteration_count, last_updated
```

---

## 📚 参考资料

**内部文档**:
- CHANGELOG.md（系统版本历史）
- docs/dual-loop-architecture.md（双循环架构）
- .learnings/design-patterns/（设计模式库）

**外部论文**:
- AutoSkill: https://arxiv.org/pdf/2603.01145
- XSKILL: https://arxiv.org/pdf/2603.12056

---

**最后更新**: 2026-03-16 15:50
**维护者**: 大领导系统 v5.16.0
