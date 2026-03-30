# 最佳实践文档 - Subagents

**版本**: v1.0
**更新时间**: 2026-03-29 19:53
**状态**: ✅ **已创建**

---

## 🎯 **Subagents 最佳实践**

### 📋 **什么是 Subagent？**

Subagent 是一个**独立上下文的自主执行者**：
- ✅ 自定义工具
- ✅ 独立权限
- ✅ 独立模型
- ✅ 持久身份
- ✅ 持久记忆

### 🎯 **何时使用 Subagent？**

**适用场景**：
- ✅ **隔离任务** - 需要独立环境
- ✅ **并行工作** - 多个任务同时进行
- ✅ **特定专长** - 需要专业知识
- ✅ **长时间运行** - 避免阻塞主会话

**不适用场景**：
- ❌ 简单查询
- ❌ 快速任务
- ❌ 单步操作

---

## 🚀 **创建 Subagent**

### 方法 1: 通过文件创建

**位置**: `.claude/agents/<name>.md`

**模板**：
```markdown
# <Agent Name>

## Role
You are a <role> specializing in <domain>.

## Context
<Background information>

## Tasks
- Task 1
- Task 2
- Task 3

## Guidelines
- Guideline 1
- Guideline 2
- Guideline 3

## Tools
- tool1: <description>
- tool2: <description>
```

### 方法 2: 通过对话创建

**在 Claude Code 中**：
```
> 创建一个 subagent，专门负责 <task>
```

**Claude 会自动**：
1. 创建 agent 文件
2. 配置工具和权限
3. 设置模型和记忆

---

## 🎯 **最佳实践**

### ✅ **1. 明确角色定义**
- ✅ 清晰的职责范围
- ✅ 专业的领域知识
- ✅ 明确的任务边界

### ✅ **2. 提供工具**
- ✅ 必要的 CLI 工具
- ✅ API 访问权限
- ✅ 文件读写权限

### ✅ **3. 设置记忆**
- ✅ 持久化记忆
- ✅ 会话上下文
- ✅ 知识库

### ✅ **4. 选择合适模型**
- ✅ 根据任务复杂度
- ✅ 考虑成本和速度
- ✅ 平衡质量和效率

---

## 📊 **示例 Subagents**

### 1️⃣ **安全审计员**
```markdown
# Security Auditor

## Role
You are a security specialist specializing in code security audits.

## Tasks
- 扫描代码漏洞
- 检测依赖风险
- 生成安全报告

## Tools
- security-scanner
- dependency-checker
- vulnerability-db

## Guidelines
- 优先级：Critical > High > Medium > Low
- 标准：OWASP Top 10
- 报告：包含风险等级、修复建议
```

### 2️⃣ **文档生成器**
```markdown
# Documentation Generator

## Role
You are a technical writer specializing in API documentation.

## Tasks
- 生成 API 文档
- 编写使用示例
- 创建教程

## Tools
- doc-generator
- markdown-processor
- example-builder

## Guidelines
- 风格：OpenAPI/Markdown
- 示例：可运行的代码
- 语气：清晰简洁
```

---

## 🎯 **调用 Subagent**

### 方法 1: 通过对话
```
> 使用 security-auditor 审计这个代码
```

### 方法 2: 通过命令
```
/agent security-auditor
```

### 方法 3: 通过技能
在技能中引用：
```
请使用 security-auditor subagent 审计以下代码...
```

---

## 🔄 **Subagent 编排模式**

### Command → Agent → Skill 模式

**工作流**：
1. **Command** - 用户触发
2. **Agent** - Subagent 执行
3. **Skill** - 使用技能知识

**示例**：
```
用户: /audit-security
Command: 触发安全审计
Agent: security-auditor subagent
Skill: 使用安全检查技能
```

---

## 💡 **核心价值**

> **"独立上下文，专业执行，并行工作！"**
> **"Subagents 让专业的人做专业的事！"**

---

**文档人**: 大领导 🎯
**创建时间**: 2026-03-29 19:53
**版本**: v1.0
**状态**: ✅ **Subagents 最佳实践已完成！**
