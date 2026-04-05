# 🚀 快速开始指南

**项目**: 自主进化系统 v7.0 - TradingAgents 特性集成
**状态**: Phase 1 完成 ✅

---

## 📋 项目概览

本项目旨在将 TradingAgents 的优秀特性集成到我们的自主进化系统中，包括：

- ✅ **配置系统** - 动态配置管理
- ✅ **进度显示** - 实时 Agent 状态跟踪
- ✅ **Agent 注册** - 模块化 Agent 管理
- ⏳ **辩论机制** - 结构化方案辩论（Phase 2）
- ⏳ **分层决策** - 多层级决策系统（Phase 3）
- ⏳ **统一框架** - 完整的 Agent 框架（Phase 4）

---

## 🎯 查看演示

### 方式 1: 运行演示脚本
```bash
bash /root/.openclaw/workspace/projects/tradingagents-study/demo/demo.sh
```

### 方式 2: 单独测试各个组件

**测试配置系统**:
```bash
cd /root/.openclaw/workspace/projects/tradingagents-study
python3 scripts/config-loader.py
```

**测试进度跟踪器**:
```bash
cd /root/.openclaw/workspace/projects/tradingagents-study
python3 scripts/progress-tracker.py
```

**测试 Agent 注册表**:
```bash
cd /root/.openclaw/workspace/projects/tradingagents-study
python3 scripts/agent-registry.py
```

---

## 📂 项目结构

```
tradingagents-study/
├── config/
│   └── system-config.yaml          # 系统配置文件
├── scripts/
│   ├── config-loader.py            # 配置加载器
│   ├── progress-tracker.py         # 进度跟踪器
│   └── agent-registry.py           # Agent 注册表
├── demo/
│   └── demo.sh                     # 演示脚本
├── COMPARISON_ANALYSIS.md          # 对比分析
├── IMPLEMENTATION_PLAN.md          # 实施计划
├── PHASE1-COMPLETE.md              # Phase 1 完成报告
└── QUICKSTART.md                   # 本文档
```

---

## 💡 使用示例

### 1. 修改配置

编辑配置文件：
```bash
vi /root/.openclaw/workspace/projects/tradingagents-study/config/system-config.yaml
```

修改示例：
```yaml
workflow:
  enable_debate: true  # 启用辩论机制
  enable_progress_display: true  # 启用进度显示
  enable_layered_decision: false  # 暂不启用分层决策
```

### 2. 使用配置加载器

```python
from scripts.config_loader import get_config_loader

# 获取配置加载器
loader = get_config_loader()

# 获取 Agent 配置
tech_config = loader.get_agent_config("tech")
print(tech_config["model"])  # opencode/minimax-m2.5-free

# 检查功能开关
if loader.is_debate_enabled():
    print("辩论机制已启用")

# 重新加载配置
loader.reload()
```

### 3. 使用进度跟踪器

```python
from scripts.progress_tracker import ProgressTracker

# 创建进度跟踪器
tracker = ProgressTracker(verbose=True)

# 开始任务
tracker.start("小新", "正在编写代码...")

# 更新进度
tracker.update("小新", "running", "正在编写代码...", 50)

# 完成
tracker.complete("小新", "代码编写完成")

# 获取摘要
summary = tracker.get_summary()
print(f"成功率: {summary['success_rate']*100:.1f}%")
```

### 4. 使用 Agent 注册表

```python
from scripts.agent_registry import get_registry

# 获取注册表
registry = get_registry()

# 注册 Agent
registry.register("my_agent", MyAgentClass, {
    "model": "glm-4.7",
    "role": "我的 Agent",
    "description": "这是一个自定义 Agent"
})

# 获取 Agent
agent_info = registry.get("my_agent")
print(agent_info.config["role"])

# 列出所有 Agent
agents = registry.list_agents()
print(agents)

# 注销 Agent
registry.unregister("my_agent")
```

---

## 🔧 配置参考

### Agents 配置

```yaml
agents:
  leader:
    model: glmcode/glm-4.7
    role: 主控决策
    description: 负责任务分配、协调和最终决策

  tech:
    model: opencode/minimax-m2.5-free
    role: 技术支持
    description: 负责所有编程和技术相关任务

  log:
    model: glmcode/glm-4.5-air
    role: 日志管理
    description: 负责工作日志记录和管理

  design:
    model: glmcode/glm-4.6
    role: 设计专家
    description: 负责所有室内设计相关任务

  challenger:
    model: glmcode/glm-4.7
    role: 方案质疑
    description: 专门负责质疑和挑战方案，发现潜在问题

  review:
    model: glmcode/glm-4.7
    role: 质量审查
    description: 负责审查方案质量，发现问题并提供改进建议
```

### 工作流程配置

```yaml
workflow:
  enable_debate: false              # 是否启用辩论机制
  max_debate_rounds: 2              # 最大辩论轮数
  enable_progress_display: true     # 是否启用进度显示
  enable_layered_decision: false    # 是否启用分层决策
  decision_layers: 5                # 决策层数
```

### 质量控制配置

```yaml
quality:
  require_review: false             # 是否需要质量审查
  auto_fix_errors: true             # 是否自动修复错误
  min_confidence: 0.7               # 最低置信度
  min_quality_score: 70             # 最低质量评分（0-100）
```

### 性能配置

```yaml
performance:
  enable_parallel: false            # 是否启用并行执行
  max_parallel_agents: 3            # 最大并行 Agent 数量
  enable_cache: true                # 是否启用缓存
  cache_size: 128                   # 缓存大小
```

---

## 📊 当前进度

### ✅ Phase 1: 基础设施升级（已完成）
- ✅ 配置系统
- ✅ 进度显示系统
- ✅ Agent 注册表
- ✅ 演示脚本

### ⏳ Phase 2: 辩论机制实现（待开始）
- ⏳ 创建挑战者 Agent
- ⏳ 实现辩论流程
- ⏳ 集成到主流程

### ⏳ Phase 3: 分层决策系统（待开始）
- ⏳ 创建 5 个决策层级
- ⏳ 实现审查 Agent
- ⏳ 集成到主流程

### ⏳ Phase 4: 整合和优化（待开始）
- ⏳ 创建统一框架
- ⏳ 性能优化
- ⏳ 测试和文档

---

## 🎯 下一步行动

### 立即可用
- ✅ 使用配置系统管理 Agent
- ✅ 使用进度跟踪器监控任务
- ✅ 使用 Agent 注册表管理 Agent

### 即将推出
- ⏳ 辩论机制（提高决策质量 30%+）
- ⏳ 分层决策（降低错误率 50%+）
- ⏳ 统一框架（完整集成）

---

## 📚 相关文档

- **对比分析**: `COMPARISON_ANALYSIS.md` - TradingAgents vs 我们的系统
- **实施计划**: `IMPLEMENTATION_PLAN.md` - 完整的实施计划
- **完成报告**: `PHASE1-COMPLETE.md` - Phase 1 完成报告

---

## 💬 反馈和建议

如果你有任何问题或建议，请随时告诉我！

---

**最后更新**: 2026-03-31
**版本**: v7.0 Phase 1
**状态**: ✅ 基础设施完成
