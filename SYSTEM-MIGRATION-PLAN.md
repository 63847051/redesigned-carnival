# 📁 用户/系统分离架构

**创建时间**: 2026-03-05
**目的**: 实现用户/系统分离，确保升级安全

---

## 🏗️ 目录结构

```
/root/.openclaw/workspace/
├── USER/                    # 用户自定义（升级安全）
│   ├── IDENTITY.md         # 用户身份
│   ├── SOUL.md            # 用户灵魂和使命
│   ├── AGENTS.md          # 用户团队配置
│   ├── TOOLS.md           # 用户工具配置
│   └── CUSTOM/            # 用户自定义内容
│
├── SYSTEM/                 # PAI 基础设施（可升级）
│   ├── CORE/              # 核心系统
│   │   ├── PAI-LEARNING/  # PAI 学习系统
│   │   ├── TELOS/         # Telos 系统
│   │   └── SCRIPTS/       # 系统脚本
│   ├── SKILLS/            # 技能系统
│   ├── WORKFLOWS/         # 工作流
│   └── DOCUMENTATION/     # 系统文档
│
├── MEMORY.md              # 长期记忆（共享）
├── memory/                # 每日记忆（共享）
└── AGENTS.md              # 工作团队配置（共享）
```

---

## 🔄 迁移计划

### 阶段 1: 创建目录结构 ✅
- [x] 创建 USER/ 目录
- [x] 创建 SYSTEM/ 目录

### 阶段 2: 迁移用户文件
- [ ] 迁移 IDENTITY.md → USER/
- [ ] 迁移 SOUL.md → USER/
- [ ] 迁移 AGENTS.md → USER/
- [ ] 迁移 TOOLS.md → USER/
- [ ] 迁移 USER.md → USER/

### 阶段 3: 迁移系统文件
- [ ] 迁移 .pai-learning/ → SYSTEM/CORE/PAI-LEARNING/
- [ ] 迁移 TELOS/ → SYSTEM/CORE/TELOS/
- [ ] 迁移 scripts/ → SYSTEM/CORE/SCRIPTS/
- [ ] 迁移 agents/ → SYSTEM/SKILLS/
- [ ] 迁移 docs/ → SYSTEM/DOCUMENTATION/

### 阶段 4: 更新引用
- [ ] 更新所有脚本中的路径
- [ ] 更新文档中的路径
- [ ] 测试所有功能

---

## 🎯 原则

### 用户文件（USER/）
- **升级安全**: 永远不被覆盖
- **用户所有权**: 完全由用户控制
- **可移植**: 可以在不同系统间迁移

### 系统文件（SYSTEM/）
- **可升级**: 可以被新版本覆盖
- **标准化**: 遵循 PAI 架构
- **版本控制**: 跟踪版本变化

---

## 📋 迁移清单

### 用户文件（5 个）
- [ ] IDENTITY.md
- [ ] SOUL.md
- [ ] AGENTS.md
- [ ] TOOLS.md
- [ ] USER.md

### 系统文件（10+ 个）
- [ ] .pai-learning/ → SYSTEM/CORE/PAI-LEARNING/
- [ ] TELOS/ → SYSTEM/CORE/TELOS/
- [ ] scripts/pai-*.sh → SYSTEM/CORE/SCRIPTS/
- [ ] agents/ → SYSTEM/SKILLS/
- [ ] docs/ → SYSTEM/DOCUMENTATION/

---

*创建时间: 2026-03-05*
*状态: 🟢 执行中*
*下一步: 迁移用户文件*
