# 🧠 SKILLS.md - 技能仓库

这里记录所有已掌握的技能及其使用方法。

**更新时间**: 2026-03-02

---

## 📋 技能列表

### 1. 自主项目管理

**来源**: GitHub awesome-openclaw-usecases
**文件**: `/root/.openclaw/workspace/SKILLS/project-management-usage.md`
**快速参考**: `/root/.openclaw/workspace/SKILLS/project-management-quickref.md`

**功能**: 让 AI 代理像项目经理一样管理多个项目

**触发方式**:
- "创建项目: <项目名>, PM: pm-xxx"
- "项目状态报告"
- "给 <项目名> 添加任务: <任务描述>"
- "暂停/恢复 <项目>"

**工作原理**:
- 主代理(CEO 模式)只做协调
- PM 子代理负责具体执行
- 通过 STATE.yaml 文件协调
- 并行处理多个项目

**使用场景**:
- 管理飞书 Gateway 监控
- 管理 EvoMap 节点
- 管理仪表板维护
- 学习新技能

---

### 2. EvoMap 进化资产市场

**来源**: https://evomap.ai/skill.md
**项目**: EvoMap 节点管理项目的一部分

**功能**:
- 发布 Gene + Capsule + EvolutionEvent 资产包
- 赚取积分
- 认领和完成任务
- 参与进化协作

**我的节点**: `node_3cfe84b91a567bd4`
**当前声誉**: 54.35
**当前积分**: 500

**准备发布的资产**:
- Gene: `gene_feishu_gateway_auto_recovery` v2
- Capsule: `capsule_feishu_gateway_auto_recovery` v2
- EvolutionEvent: `event_feishu_gateway_auto_recovery` v2

**进化机制**:
- **Gene**: 进化策略的抽象(修复/优化/创新)
- **Capsule**: 具体实现(代码、脚本、配置)
- **Event**: 进化审计日志(完整追踪)

**已吸收**:
- ✅ GEP-A2A 协议
- ✅ Gene/Capsule/Event 模式
- ✅ 安全约束机制
- ✅ 验证和回滚流程

**详细说明**: `/root/.openclaw/workspace/SKILLS/evomap-evolution-absorbed.md`

**状态**: 等待 Hub 恢复后发布

---

### 3. 动态仪表板

**来源**: https://github.com/hesamsheikh/awesome-openclaw-usecases
**项目**: dashboard-monitor

**功能**:
- 可视化监控界面
- 实时图表和趋势
- 告警面板
- 自动刷新(30 秒)

**访问地址**: http://43.134.63.176

**监控内容**:
- 飞书 Gateway 状态
- EvoMap 节点信息
- 内存使用趋势
- 系统资源概览

**服务器**: 运行在 80 端口,PID: 1983922

---

### 4. 飞书 Gateway 管理

**项目**: feishu-gateway

**功能**:
- 飞书 Gateway 配置
- 连接监控
- 自动恢复脚本
- 心跳循环管理

**关键脚本**:
- `/root/.openclaw/workspace/scripts/backup-before-update.sh` - 快速备份
- `/root/.openclaw/workspace/scripts/safe-upgrade.sh` - 安全升级
- `/root/.openclaw/workspace/scripts/restore-pairing.sh` - 恢复飞书配对
- `/root/.openclaw/workspace/scripts/heartbeat-evolution.sh` - 心跳进化
- `/root/.openclaw/workspace/scripts/check-upgrade-compatibility.sh` - 兼容性检查

**状态**:
- 服务状态: ✅ active
- 内存使用: 44.8%
- 重启次数: 5 次（正常）
- 最近错误: 无

---

### 5. 系统监控

**来源**: https://github.com/hesamsheikh/awesome-openclaw-usecases

**功能**:
- 系统健康检查
- 资源监控
- 日志分析
- 自动告警

**Heartbeat 配置**: `HEARTBEAT.md`

**当前检查项**:
- Gateway 状态
- 内存使用
- 错误日志
- 配置文件修改时间

---

### 6. 防护机制

**来源**: 系统经验 + 崩溃学习

**功能**:
- 6 层崩溃防护系统
- 自动恢复机制
- Token 溢出防护
- 内存监控
- 配置保护

**防护级别**:
- L1: 心跳循环监控
- L2: 内存使用监控
- L3: 自动告警
- L4: 安全重启脚本
- L5: 会话压缩
- L6: Gateway 自动重启

**防护历史**:
- 崩溃次数: 1 次（2026-03-01）
- 恢复成功率: 100%
- 防护版本: v2.1

**学习文档**: `/root/.openclaw/workspace/memory/crash-learning.md`
**详细说明**: `/root/.openclaw/workspace/SKILLS/protection-mechanisms.md`

---

### 7. 飞书云文档操作

**来源**: OpenClaw 内置功能

**功能**:
- 读取飞书文档
- 创建和更新文档
- 多维表格操作
- 知识库管理

**已接入项目**:
- 蓝色光标上海办公室工作日志
- 知识库链接: https://ux7aumj3ud.feishu.cn/wiki/KSlQwODcAidSqVkuiLzcOLlrnug

**操作记录**:
- ✅ 成功读取工作日志（10 条记录）
- ✅ 解析多维表格结构
- ✅ 分析任务状态和类型

---

### 8. 团队协作管理

**来源**: 内置能力

**功能**:
- 任务分配给专业团队成员
- 协调多个专家并行工作
- 监督执行质量
- 统筹项目进度

**团队成员**:
- 🏠 **室内设计专家** - 负责所有室内设计相关任务
- 💻 **技术支持专家** - 负责所有编程和技术相关任务
- 📋 **工作日志管理专家** - 负责工作日志记录和管理

**触发关键词**:
- 设计类任务 → 室内设计专家
- 技术类任务 → 技术支持专家
- 日志类任务 → 工作日志管理专家

---

### 9. 备份和恢复系统

**来源**: 系统经验

**功能**:
- 自动备份配置和工作区
- 安全升级流程
- 一键恢复系统
- 飞书配对保护

**备份脚本**:
- `backup-before-update.sh` - 快速备份
- `safe-upgrade.sh` - 安全升级
- `restore-pairing.sh` - 恢复飞书配对

**备份指南**: `/root/.openclaw/workspace/BACKUP-GUIDE.md`
**重装指南**: `/root/.openclaw/workspace/REINSTALL-GUIDE.md`

---

## 📚 ClawHub 已安装技能（18 个）

### 生产力工具
- **ai-meeting-notes** (1.0.3) - 会议记录整理
- **obsidian** (1.0.0) - 笔记管理
- **daily-rhythm** (1.0.0) - 日常规划
- **para-second-brain** (2.0.1) - PARA 知识管理
- **reflect-learn** (2.1.0) - 反思学习
- **self-improving-agent** (1.0.11) - 自我改进

### 开发工具
- **agent-browser** (0.2.0) - 浏览器自动化
- **automation-workflows** (0.1.0) - 工作流自动化
- **agent-builder** (1.0.0) - AI 代理构建
- **github** (1.0.0) - GitHub 集成
- **find-skills** (0.1.0) - 技能查找

### 集成工具
- **notion** (1.0.0) - Notion API
- **airtable-automation** (0.1.0) - Airtable 自动化
- **summarize** (1.0.0) - 内容总结
- **tavily-search** (1.0.0) - Tavily AI 搜索

### 监控工具
- **stock-monitor-skill** (0.1.0) - 股票监控
- **weather** (1.0.0) - 天气查询

---

## 🔄 技能之间的协作

```
主控 Agent（大领导 🎯）
    │
    ├── 团队协作管理 → 分配任务给专家
    │
    ├── 自主项目管理 → 协调多个项目
    │
    ├── EvoMap → 发布资产到市场
    │
    ├── 动态仪表板 → 可视化状态
    │
    ├── 飞书管理 → 维护连接
    │
    ├── 系统监控 → 健康检查
    │
    ├── 防护机制 → 6 层保护
    │
    └── 备份恢复 → 数据安全
```

---

## 🎓 如何添加新技能

1. 学习新的 GitHub awesome-openclaw-usecases
2. 创建对应的技能文件
3. 记录到 SKILLS.md
4. 更新相关配置
5. 测试新功能

---

**这个 SKILLS.md 是我的"大脑"🧠,记录所有学到的技能!**

**总技能数**: 24 个（9 个内置 + 18 个 ClawHub - 3 个重复）
