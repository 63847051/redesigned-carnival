# everything-claude-code 研究记录

**日期**: 2026-03-17
**项目**: affaan-m/everything-claude-code
**GitHub**: https://github.com/affaan-m/everything-claude-code
**Stars**: 50K+ | Forks: 6K+

---

## 📊 项目概述

**定位**: AI agent harness 性能优化系统

**核心理念**: Not just configs. A complete system: skills, instincts, memory optimization, continuous learning, security scanning, and research-first development.

**支持工具**:
- Claude Code ⭐ 主要目标
- Cursor IDE
- OpenCode
- Codex CLI

---

## 🎯 核心特性

### 1️⃣ Token 优化 ⭐⭐⭐
- **模型选择**: sonnet vs opus（60% 成本节省）
- **系统提示词精简**: 减少 thinking tokens
- **后台进程**: 优化 token 消耗

**推荐配置**:
```json
{
  "model": "sonnet",
  "env": {
    "MAX_THINKING_TOKENS": "10000",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50"
  }
}
```

**与 DP-006 的关联**:
- ✅ DP-006: 子 Agent Token 优化（65% 节省）
- ✅ ECC: 上下文管理 + 模型选择
- ✅ 两者理念一致：上下文分层 + 成本优化

### 2️⃣ Memory 持久化
- **Hooks**: 自动保存/加载会话上下文
- **跨会话**: SessionStart/SessionEnd hooks
- **Strategic Compact**: 逻辑断点压缩

**实现机制**:
```javascript
// hooks/session-start.js - 加载上下文
// hooks/session-end.js - 保存状态
// hooks/suggest-compact.js - 压缩建议
```

### 3️⃣ 持续学习
- **Instinct-based**: 自动提取模式
- **置信度评分**: 评估学习质量
- **导入/导出**: 分享学习成果
- **进化**: 聚类相关模式

**命令**:
- `/learn` - 提取模式
- `/instinct-status` - 查看学习结果
- `/instinct-import` - 导入
- `/instinct-export` - 导出
- `/evolve` - 聚类

### 4️⃣ 验证循环
- **Checkpoint vs Continuous**: 检查点 vs 持续评估
- **Grader Types**: 评估器类型
- **pass@k 指标**: 通过率指标

### 5️⃣ 并行化
- **Git worktrees**: 工作树并行
- **Cascade method**: 级联方法
- **Instance scaling**: 实例扩展

### 6️⃣ 子 Agent 编排
- **Context 问题**: 上下文问题
- **Iterative retrieval**: 迭代检索模式

---

## 🏗️ 系统架构

### 目录结构
```
everything-claude-code/
├── agents/          # 25 个专业子 Agent
├── skills/          # 108 个技能
├── commands/        # 57 个命令
├── rules/           # 34 条规则
├── hooks/           # 20+ 个 Hook 脚本
├── scripts/         # 跨平台 Node.js 脚本
├── contexts/        # 动态系统提示词注入
├── mcp-configs/     # MCP 服务器配置
└── tests/           # 997 个内部测试
```

### 核心 Agent（25 个）
- **planner** - 功能实现规划
- **architect** - 系统设计决策
- **tdd-guide** - 测试驱动开发
- **code-reviewer** - 质量和安全审查
- **security-reviewer** - 漏洞分析
- **build-error-resolver** - 构建错误解决
- **e2e-runner** - Playwright E2E 测试
- **refactor-cleaner** - 死代码清理
- **doc-updater** - 文档同步

### 核心 Skill（108 个）
- **coding-standards** - 语言最佳实践
- **backend-patterns** - API、数据库、缓存模式
- **frontend-patterns** - React、Next.js 模式
- **continuous-learning** - 自动提取模式
- **iterative-retrieval** - 子 Agent 渐进式上下文细化
- **strategic-compact** - 手动压缩建议
- **tdd-workflow** - TDD 方法论
- **security-review** - 安全检查清单
- **eval-harness** - 验证循环评估
- **verification-loop** - 持续验证

### 核心 Command（57 个）
- `/plan` - 实现规划
- `/tdd` - 测试驱动开发
- `/code-review` - 质量审查
- `/build-fix` - 修复构建错误
- `/e2e` - E2E 测试生成
- `/refactor-clean` - 死代码移除
- `/learn` - 提取模式
- `/checkpoint` - 保存验证状态
- `/verify` - 运行验证循环
- `/security-scan` - 安全扫描

---

## 🔒 安全扫描（AgentShield）

**集成**: AgentShield 安全审计器

**功能**:
- **1282 个测试**
- **102 条规则**
- **5 个类别**: secrets 检测、权限审计、Hook 注入分析、MCP 服务器风险分析、Agent 配置审查

**使用**:
```bash
# 快速扫描
npx ecc-agentshield scan

# 自动修复
npx ecc-agentshield scan --fix

# 深度分析（3 个 Opus 4.6 Agent）
npx ecc-agentshield scan --opus --stream
```

**红队/蓝队/审计员流程**:
- 攻击者: 找到利用链
- 防守者: 评估保护
- 审计员: 综合风险评估

---

## 🎓 与大领导系统的对比

### 相似之处 ✅

1. **Token 优化**
   - ECC: sonnet vs opus，60% 成本节省
   - v5.16: DP-006，65% Token 节省
   - 理念一致: 上下文分层 + 成本优化

2. **持续学习**
   - ECC: Instinct-based 学习
   - v5.16: PAI 学习系统
   - 都强调自动提取模式

3. **多 Agent 架构**
   - ECC: 25 个专业 Agent
   - v5.16: 小新 + 小蓝
   - 都是"专业的事交给专业的人"

4. **Hook 系统**
   - ECC: 20+ 个 Hook
   - v5.16: WAL Protocol
   - 都是事件驱动的自动化

### 差异之处 ⚖️

| 维度 | ECC | 大领导 v5.16 |
|------|-----|-------------|
| **规模** | 25 Agent, 108 Skill, 57 Command | 2 专业 Agent（小新、小蓝）|
| **工具支持** | Claude Code, Cursor, OpenCode, Codex | OpenClaw |
| **测试覆盖** | 997 个内部测试 | 有限测试 |
| **文档** | 极其完善 | 正在完善 |
| **安全** | AgentShield 集成 | 6 层防护 + 三重防护 |

---

## 💡 可借鉴的经验

### 1️⃣ 系统化
- ECC 是一个**完整的系统**，不只是配置
- 有清晰的目录结构和模块划分
- 大量自动化脚本和测试

### 2️⃣ 安全第一
- AgentShield 集成
- 1282 个测试，102 条规则
- 红队/蓝队/审计员流程

### 3️⃣ 持续学习
- Instinct-based 自动学习
- 置信度评分
- 导入/导出/进化机制

### 4️⃣ Token 优化
- 详细的优化指南
- 模型选择策略
- 上下文管理技巧

### 5️⃣ 跨工具支持
- Claude Code, Cursor, OpenCode, Codex
- AGENTS.md 通用文件
- DRY 适配器模式

---

## 🎯 对大领导系统的启发

### 短期改进（1-2 周）

1. **添加更多测试**
   - ECC 有 997 个测试
   - 大领导系统测试较少
   - 建议: 为核心功能添加单元测试

2. **完善文档**
   - ECC 文档极其完善
   - 大领导系统文档正在完善
   - 建议: 参考 ECC 的文档结构

3. **Token 优化实践**
   - ECC 的 MAX_THINKING_TOKENS 优化
   - 与 DP-006 结合使用
   - 建议: 在 SOUL.md 中添加最佳实践

### 中期改进（1-2 个月）

1. **Instinct-based 学习**
   - ECC 的持续学习 v2
   - 与 PAI 学习系统结合
   - 建议: 实现置信度评分

2. **AgentShield 集成**
   - ECC 的安全扫描
   - 与大领导系统的安全防护结合
   - 建议: 创建安全扫描 Skill

3. **更多专业 Agent**
   - ECC 有 25 个 Agent
   - 大领导系统目前只有 2 个
   - 建议: 根据需要添加更多专家

### 长期愿景（3-6 个月）

1. **跨工具支持**
   - ECC 支持 4 个主要工具
   - 大领导系统目前只支持 OpenClaw
   - 建议: 考虑支持其他 AI 工具

2. **完整的 Hook 系统**
   - ECC 有 20+ 个 Hook
   - 大领导系统有 WAL Protocol
   - 建议: 扩展 Hook 事件类型

3. **Marketplace 生态**
   - ECC 有 GitHub Marketplace
   - 大领导系统有 GitHub 仓库
   - 建议: 创建技能包分享平台

---

## 📚 学习资源

### 官方文档
- [Shorthand Guide](https://x.com/affaanmustafa/status/2012378465664745795)
- [Longform Guide](https://x.com/affaanmustafa/status/2014040193557471352)
- [Token Optimization Guide](https://github.com/affaan-m/everything-claude-code/blob/main/docs/token-optimization.md)

### 相关项目
- [zenith.chat](https://zenith.chat) - 使用 Claude Code 构建
- [AgentShield](https://github.com/affaan-m/agentshield) - 安全扫描工具

---

## 🎉 总结

**ECC 是一个成熟、完善的 AI agent harness 优化系统**

核心亮点：
- ✅ 50K+ stars，社区活跃
- ✅ 完整的系统设计（Agent + Skill + Command + Hook）
- ✅ Token 优化 + 安全扫描 + 持续学习
- ✅ 跨工具支持（Claude Code, Cursor, OpenCode, Codex）
- ✅ 997 个测试，102 条安全规则

**与大领导系统的关系**：
- ✅ 理念一致：Token 优化 + 持续学习 + 多 Agent
- ✅ 可以借鉴：系统化设计 + 安全机制 + 文档结构
- ✅ 差异互补：ECC 更成熟，大领导系统更轻量

**建议**：
1. 学习 ECC 的系统化设计
2. 借鉴 AgentShield 的安全机制
3. 结合 DP-006 进一步优化 Token
4. 扩展专业 Agent 团队

---

*研究时间: 2026-03-17*
*项目版本: 最新*
*核心价值: ⭐⭐⭐⭐⭐*
