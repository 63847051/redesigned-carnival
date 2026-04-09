# 项目上下文

---
name: Claude Code 记忆系统深度学习
description: 学习 Claude Code 的六个维度、十二个模块记忆系统架构
type: project
---

## 项目目标
深入学习 Claude Code 记忆系统架构，理解：
- 六个维度：指令记忆、短期记忆、工作记忆、长期记忆、摘要记忆、休眠重塑记忆
- 十二个模块：静态指令、长期记忆、自动提取、自动整理、会话记忆
- 核心设计：双轨注入、四种封闭类型、Sonnet 动态召回、API 不变量保护

## Why
用户希望 AI 真正理解 Claude Code 的设计思想，而不是表面学习。目标是达到能自己实现同等水平系统的能力。

## How to apply
在回答问题时，应用 Claude Code 的设计原则：
- 双轨注入：指令记忆和行为规范分离
- 四种封闭类型：只存储不可从代码推导的信息
- Sonnet 动态召回：用 AI 决策替代向量检索
- API 不变量保护：维护完整性

## 关键资源
- **源码**: https://github.com/LING71671/Open-ClaudeCode
- **核心文件**:
  - `src/memdir/memoryTypes.ts` - 四种封闭类型定义
  - `src/memdir/memdir.ts` - memdir 存储引擎
  - `src/services/SessionMemory/sessionMemory.ts` - Session Memory
  - `src/services/extractMemories/extractMemories.ts` - 自动记忆提取

## 时间规划
- **开始时间**: 2026-04-06
- **学习方式**: 结合源码深入理解
- **目标**: 9-15 天后能自己实现同等水平的系统

---

**记录时间**: 2026-04-06
**类型**: project
**优先级**: 高
