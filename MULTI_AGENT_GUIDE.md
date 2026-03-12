# OpenClaw Multi-Agent 配置指南

## 📋 当前 Agent 列表

```
OpenClaw
├── main     (默认 Agent)
├── dev      (开发 Agent)
├── writer   (写作 Agent)
└── ops      (运维 Agent)
```

## 🎯 每个 Agent 的职责

### 1. **main** (默认)
- **职责**: 通用助手，接收所有消息
- **权限**: 所有工具
- **用途**: 日常对话、问答、任务分配

### 2. **dev** (开发)
- **职责**: 代码开发、调试、技术问题
- **权限**: 执行命令、修改文件、Git 操作
- **用途**:
  - 编写代码
  - 调试问题
  - 代码审查
  - 技术架构设计

### 3. **writer** (写作)
- **职责**: 文档写作、内容创作
- **权限**: 读写文件、飞书文档
- **用途**:
  - 写文档
  - 写博客
  - 写报告
  - 内容创作

### 4. **ops** (运维)
- **职责**: 系统运维、监控、部署
- **权限**: 系统命令、日志查看、服务管理
- **用途**:
  - 服务部署
  - 日志分析
  - 系统监控
  - 故障排查

## 🚀 如何使用

### 方法 1: 通过 Web UI
访问: http://127.0.0.1:18789

### 方法 2: 通过命令行
```bash
# 发消息给 dev
openclaw agent --agent dev --message "帮我写个 Python 脚本"

# 发消息给 writer
openclaw agent --agent writer --message "写一份项目文档"

# 发消息给 ops
openclaw agent --agent ops --message "查看系统日志"
```

### 方法 3: 通过飞书
在飞书群里：
```
@dev 帮我写个 API
@writer 写一份使用文档
@ops 查看一下服务状态
```

## 🔧 Agent 协同开发流程

### 场景 1: 开发新功能
1. **main** 接收需求，分析任务
2. **dev** 编写代码实现功能
3. **writer** 编写使用文档
4. **ops** 部署到生产环境

### 场景 2: 修复 Bug
1. **main** 接收 Bug 报告
2. **dev** 定位问题并修复
3. **writer** 更新变更日志
4. **ops** 发布热修复

### 场景 3: 代码审查
1. **writer** 撰写 Review 文档
2. **dev** 进行代码审查
3. **main** 汇总审查意见
4. **ops** 执行合并部署

## 📁 工作区结构

```
~/.openclaw/
├── workspace/          # main 的工作区
├── workspace-dev/      # dev 的工作区
├── workspace-writer/   # writer 的工作区
└── workspace-ops/      # ops 的工作区
```

每个工作区都可以有：
- Skills (技能包)
- 配置文件
- 知识文档
- 会话历史

## 🎨 自定义 Agent

### 创建新 Agent
```bash
openclaw agents add architect --workspace /root/.openclaw/workspace-architect
```

### 删除 Agent
```bash
openclaw agents remove architect
```

### 配置 Agent 权限
编辑 `~/.openclaw/openclaw.json` 中的 agent 配置

## 💡 最佳实践

1. **明确职责**: 每个 Agent 专注一个领域
2. **独立工作区**: 避免文件冲突
3. **权限控制**: dangerous 工具只给需要的 Agent
4. **定期备份**: 重要配置要备份
5. **监控日志**: 定期查看 Agent 运行状态

## 🔍 查看状态

```bash
# 查看所有 Agent
openclaw agents list

# 查看 Agent 会话
openclaw agent --agent dev --sessions

# 查看 Agent 配置
openclaw agent --agent dev --config
```

## 📝 总结

OpenClaw Multi-Agent 让你可以：
- ✅ 创建不同 AI 角色
- ✅ 设置不同权限
- ✅ 使用不同 Skills
- ✅ 独立管理会话
- ✅ 协同完成任务

一个服务器，运行多个 AI 助手！
