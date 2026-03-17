# 大领导系统 v5.17 - Phase 1 任务清单

**目标**: 建立系统化基础架构
**时间**: 2026-03-17 开始
**工具**: OpenCode 1.2.17

---

## 📋 Phase 1 任务列表

### ✅ 已完成
- [x] 创建 `.claw/` 目录结构
- [x] 创建 `projects/ecc-integration/` 项目
- [x] 制定进化方案（EVOLUTION_PLAN_V5.17.md）

### 🔄 进行中

#### 任务 1.1: 创建 catalog.js 脚本
**目标**: 建立单一数据源机制

**位置**: `.claw/scripts/ci/catalog.js`

**功能**:
- 扫描 `agents/` 目录，统计 Agent 数量
- 扫描 `skills/` 目录，统计 Skill 数量
- 扫描 `commands/` 目录，统计 Command 数量
- 生成 JSON 格式的目录清单
- 生成 Markdown 格式的文档摘要

**输出**:
```json
{
  "agents": {
    "count": 2,
    "list": ["小新", "小蓝"]
  },
  "skills": {
    "count": 10,
    "list": ["技术支持", "日志管理", ...]
  },
  "commands": {
    "count": 5,
    "list": ["/plan", "/review", ...]
  }
}
```

#### 任务 1.2: 创建第一个测试
**目标**: 为 PAI 学习系统添加单元测试

**位置**: `.claw/tests/unit/pai-learning.test.js`

**测试内容**:
- [ ] 测试学习信号捕获
- [ ] 测试三层记忆系统
- [ ] 测试报告生成

**目标覆盖率**: 60%

#### 任务 1.3: 建立 .claw/agents/ 结构
**目标**: 将现有 Agent 迁移到新结构

**位置**: `.claw/agents/`

**Agent 定义**:
- `小新.md` - 技术支持专家
- `小蓝.md` - 工作日志管理专家

**格式**: YAML frontmatter + Markdown 内容

---

## 🎯 立即开始

**优先级 1**: 创建 catalog.js 脚本

**优先级 2**: 创建第一个测试

**优先级 3**: 迁移 Agent 定义

---

*创建时间: 2026-03-17*
*状态: 🔄 Phase 1 进行中*
