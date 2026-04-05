# Feature Flags 系统使用指南

**版本**: 1.0.0
**创建时间**: 2026-04-01
**作者**: 大领导 🎯

---

## 📖 什么是 Feature Flags？

Feature Flags（功能开关）是一种允许我们在不修改代码的情况下启用或禁用功能的机制。

**核心优势**:
- ✅ 安全地测试新功能
- ✅ 快速回滚有问题的功能
- ✅ 灰度发布和 A/B 测试
- ✅ 减少部署风险

---

## 🚀 快速开始

### 1. 命令行使用

#### 列出所有功能
```bash
bash /root/.openclaw/workspace/scripts/feature-flags.sh list
```

#### 检查功能是否启用
```bash
bash /root/.openclaw/workspace/scripts/feature-flags.sh check TASK_AGENT_LOOP
```

#### 启用功能
```bash
bash /root/.openclaw/workspace/scripts/feature-flags.sh enable PROACTIVE_MODE
```

#### 禁用功能
```bash
bash /root/.openclaw/workspace/scripts/feature-flags.sh disable PROACTIVE_MODE
```

#### 获取功能详细信息
```bash
bash /root/.openclaw/workspace/scripts/feature-flags.sh info MEMORY_SEARCH
```

#### 按组列出功能
```bash
# 实验性功能
bash /root/.openclaw/workspace/scripts/feature-flags.sh group experimental

# 稳定功能
bash /root/.openclaw/workspace/scripts/feature-flags.sh group stable

# 优化功能
bash /root/.openclaw/workspace/scripts/feature-flags.sh group optimization
```

---

### 2. Python 代码使用

#### 基本使用
```python
from scripts.feature_flags import is_feature_enabled

# 检查功能是否启用
if is_feature_enabled('TASK_AGENT_LOOP'):
    # 启用任务内部 Agent Loop
    pass
```

#### 使用便捷函数
```python
from scripts.feature_flags import (
    is_task_agent_loop_enabled,
    is_proactive_mode_enabled,
    is_memory_search_enabled,
    is_auto_compression_enabled
)

# 检查任务内部 Agent Loop
if is_task_agent_loop_enabled():
    print("任务内部 Agent Loop 已启用")

# 检查主动模式
if is_proactive_mode_enabled():
    print("主动模式已启用")

# 检查记忆搜索
if is_memory_search_enabled():
    print("记忆搜索已启用")

# 检查自动压缩
if is_auto_compression_enabled():
    print("自动压缩已启用")
```

#### 使用 FeatureFlags 类
```python
from scripts.feature_flags import FeatureFlags

# 创建实例
ff = FeatureFlags()

# 检查功能
if ff.is_enabled('TASK_AGENT_LOOP'):
    print("功能已启用")

# 获取功能信息
info = ff.get_flag('TASK_AGENT_LOOP')
print(f"描述: {info['description']}")
print(f"状态: {info['code_status']}")

# 列出所有功能
all_flags = ff.list_flags()
for name, info in all_flags.items():
    print(f"{name}: {info['description']}")

# 启用/禁用功能
ff.enable('PROACTIVE_MODE')
ff.disable('PROACTIVE_MODE')
```

---

## 📋 当前功能列表

### 实验性功能 (experimental)
| 功能 | 状态 | 描述 | 风险 |
|------|------|------|------|
| **PROACTIVE_MODE** | ⚪ 未启用 | 主动模式 - Agent 主动发现问题并提出建议 | 中 |
| **KAIROS_SCHEDULER** | ⚪ 未启用 | 择时而动 - 自主守护进程 | 高 |
| **DAEMON_MODE** | ⚪ 未启用 | 永不下班 - 24小时后台待命 | 高 |

### 稳定功能 (stable)
| 功能 | 状态 | 描述 | 风险 |
|------|------|------|------|
| **TASK_AGENT_LOOP** | ✅ 已启用 | 任务内部的 Agent Loop - 微观层面循环推进 | 低 |
| **AUTO_COMPRESSION** | ✅ 已启用 | 自动压缩 - 对话太长时自动压缩上下文 | 低 |
| **MEMORY_SEARCH** | ✅ 已启用 | 记忆搜索 - 智能记忆搜索系统 | 低 |

### 优化功能 (optimization)
| 功能 | 状态 | 描述 | 风险 |
|------|------|------|------|
| **CLEAN_DESTROY_MODE** | ⚪ 未启用 | 完全销毁模式 - 子 Agent 用完即毁 | 中 |
| **LOOP_TRACKER** | ⚪ 未启用 | 循环路径记录 - 记录 Agent Loop 的执行路径 | 低 |
| **FAST_MICRO_LOOP** | ⚪ 未启用 | 快速微观循环 - 秒级循环速度 | 中 |
| **OPTIMIZED_CACHE** | ⚪ 未启用 | 优化缓存 - 工具排序优化 | 低 |

---

## 🎯 使用场景

### 场景 1: 开发新功能
```python
# 在代码中检查功能开关
from scripts.feature_flags import is_feature_enabled

def my_new_feature():
    """新功能"""
    if not is_feature_enabled('MY_NEW_FEATURE', default=False):
        print("功能未启用")
        return
    
    # 执行新功能逻辑
    print("执行新功能...")
```

### 场景 2: 灰度发布
```bash
# 先启用小范围测试
bash feature-flags.sh enable MY_NEW_FEATURE

# 观察效果，如果有问题立即禁用
bash feature-flags.sh disable MY_NEW_FEATURE
```

### 场景 3: A/B 测试
```python
# 随机启用功能（A/B 测试）
import random
from scripts.feature_flags import FeatureFlags

ff = FeatureFlags()
flag_name = 'NEW_UI_DESIGN'

if random.random() < 0.5:  # 50% 概率启用
    ff.enable(flag_name)
else:
    ff.disable(flag_name)
```

---

## ⚙️ 配置文件结构

```json
{
  "flags": {
    "FEATURE_NAME": {
      "enabled": true,
      "description": "功能描述",
      "code_status": "implemented",
      "risk_level": "low",
      "notes": "备注信息"
    }
  },
  "groups": {
    "experimental": {
      "description": "实验性功能",
      "flags": ["PROACTIVE_MODE", "KAIROS_SCHEDULER"]
    }
  },
  "metadata": {
    "total_flags": 10,
    "enabled_count": 3,
    "disabled_count": 7
  }
}
```

---

## 🔧 添加新功能开关

### 步骤 1: 编辑配置文件
```bash
vi /root/.openclaw/workspace/feature-flags.json
```

### 步骤 2: 添加新功能
```json
{
  "flags": {
    "YOUR_NEW_FEATURE": {
      "enabled": false,
      "description": "你的新功能描述",
      "code_status": "planned",
      "risk_level": "low",
      "notes": "实现计划"
    }
  }
}
```

### 步骤 3: 在代码中使用
```python
from scripts.feature_flags import is_feature_enabled

if is_feature_enabled('YOUR_NEW_FEATURE'):
    # 执行新功能
    pass
```

---

## 📊 最佳实践

### 1. 功能命名
- 使用大写字母和下划线
- 例如：`TASK_AGENT_LOOP`, `MEMORY_SEARCH`

### 2. 风险评估
- **low**: 低风险，可以安全启用
- **medium**: 中等风险，需要测试
- **high**: 高风险，需要谨慎

### 3. 代码状态
- **planned**: 计划中
- **in_development**: 开发中
- **ready**: 就绪
- **implemented**: 已实现
- **deprecated**: 已废弃

### 4. 启用流程
1. 先在开发环境测试
2. 确认无问题后启用
3. 观察生产环境效果
4. 有问题立即禁用

---

## 🎯 总结

**Feature Flags 系统**已成功部署！

**核心文件**:
- 配置: `/root/.openclaw/workspace/feature-flags.json`
- Shell: `/root/.openclaw/workspace/scripts/feature-flags.sh`
- Python: `/root/.openclaw/workspace/scripts/feature_flags.py`

**当前状态**:
- ✅ 10 个功能开关
- ✅ 3 个功能已启用
- ⚪ 7 个功能未启用

**下一步**:
1. ✅ Feature Flags 系统已完成
2. 🔄 开始实施任务内部 Agent Loop

---

**文档生成**: 大领导 🎯
**创建时间**: 2026-04-01 17:02
