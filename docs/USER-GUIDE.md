# 📘 OpenClaw 优化系统使用指南

**版本**: v1.0
**更新**: 2026-04-07
**状态**: ✅ 生产就绪

---

## 🎯 系统概览

本系统整合了 **8 个核心优化组件**，提供完整的可靠性、一致性、安全性保障。

### 核心组件

| 组件 | 功能 | 优先级 | 状态 |
|------|------|--------|------|
| **AutoDream v0.4** | 熔断器增强 | 高 | ✅ |
| **Session Memory v0.2** | 思考-输出分离 | 高 | ✅ |
| **记忆新鲜度 v1.0** | 自然语言时间戳 | 高 | ✅ |
| **记忆召回降级 v1.0** | 三层防御 | 高 | ✅ |
| **API 不变量保护** | 熔断器 + 重试 | 中 | ✅ |
| **缓存一致性管理** | 版本控制 + 失效 | 中 | ✅ |
| **Feature Flag 控制** | 安全发布 + A/B | 中 | ✅ |
| **API 健康监控** | 失败分析 | 中 | ✅ |

---

## 🚀 快速开始

### 1. API 不变量保护

**用途**: 保护 API 调用，避免雪崩效应

**基本使用**:
```bash
# 测试 API 调用
bash /root/.openclaw/workspace/scripts/api-invariant-guard.sh test

# 查看熔断器状态
bash /root/.openclaw/workspace/scripts/api-invariant-guard.sh status

# 重置熔断器
bash /root/.openclaw/workspace/scripts/api-invariant-guard.sh reset
```

**状态输出**:
```
📊 熔断器状态:
  - 失败计数: 0/3
  - 熔断器状态: closed
  - 上次失败: 0
```

**何时使用**:
- ✅ API 调用失败率 > 1%
- ✅ 需要自动重试
- ✅ 避免雪崩效应

---

### 2. 缓存一致性管理

**用途**: 确保缓存数据的一致性和完整性

**基本使用**:
```bash
# 测试缓存功能
bash /root/.openclaw/workspace/scripts/cache-consistency-manager.sh test

# 清理过期缓存
bash /root/.openclaw/workspace/scripts/cache-consistency-manager.sh cleanup

# 查看缓存统计
bash /root/.openclaw/workspace/scripts/cache-consistency-manager.sh stats

# 失效指定缓存
bash /root/.openclaw/workspace/scripts/cache-consistency-manager.sh invalidate <cache_key>
```

**统计输出**:
```
📊 缓存统计:

总体:
  - 缓存条目: 5
  - 缓存大小: 2MB
  - 最大限制: 100MB

健康状态:
  ✅ 无过期缓存
```

**何时使用**:
- ✅ 缓存数据不一致
- ✅ 缓存占用空间过大
- ✅ 需要清理过期数据

---

### 3. Feature Flag 控制

**用途**: 安全地发布新功能，支持 A/B 测试

**基本使用**:
```bash
# 创建新 Flag
bash /root/.openclaw/workspace/scripts/feature-flag-controller.sh create \\
  "new-feature" \\
  "新功能描述" \\
  true  # 默认启用

# 启用 Flag
bash /root/.openclaw/workspace/scripts/feature-flag-controller.sh enable "new-feature"

# 禁用 Flag
bash /root/.openclaw/workspace/scripts/feature-flag-controller.sh disable "new-feature"

# 删除 Flag
bash /root/.openclaw/workspace/scripts/feature-flag-controller.sh delete "new-feature"

# 列出所有 Flag
bash /root/.openclaw/workspace/scripts/feature-flag-controller.sh list

# 查看 Flag 详情
bash /root/.openclaw/workspace/scripts/feature-flag-controller.sh show "new-feature"
```

**Flag 列表输出**:
```
🚩 Feature Flag 列表:

  ✅ new-feature: 新功能描述
  ❌ old-feature: 旧功能描述

总计: 2 个 Flag
```

**何时使用**:
- ✅ 发布新功能
- ✅ A/B 测试
- ✅ 快速回滚
- ✅ 灰度发布

---

### 4. 记忆系统组件

#### 记忆新鲜度系统

**用途**: 自动标注记忆的新鲜度

**基本使用**:
```bash
# 更新所有记忆的新鲜度标注
bash /root/.openclaw/workspace/scripts/memory-freshness-system-v1.sh
```

**效果**:
- "刚刚"（< 60秒）
- "今天"（< 24小时）
- "昨天"（24-48小时）
- "X 天前"（< 7天）
- "YYYY-MM-DD"（≥ 7天）

#### 记忆召回降级策略

**用途**: 三层防御确保总能找到相关信息

**基本使用**:
```bash
# 搜索记忆（三层降级）
bash /root/.openclaw/workspace/scripts/memory-recall-fallback-v1.sh "查询词"
```

**输出**:
```
🔍 第一层：keyword 搜索（快速）
✅ 第一层找到 151 条结果
```

---

### 5. AutoDream v0.4

**用途**: 自动记忆整理，带熔断器保护

**基本使用**:
```bash
# 手动触发 AutoDream
bash /root/.openclaw/workspace/scripts/auto-dream-v4-circuit-breaker.sh
```

**熔断器保护**:
- ✅ 连续失败 3 次自动熔断
- ✅ 避免资源浪费
- ✅ 自动恢复机制

---

### 6. 集成测试

**用途**: 验证所有组件协同工作

**基本使用**:
```bash
# 运行完整集成测试
bash /root/.openclaw/workspace/scripts/integration-test.sh
```

**测试输出**:
```
🧪 集成测试开始

🔍 测试 1: API 不变量保护
  ✅ API 调用成功
  ✅ 状态查询正常

...

📈 测试总结

  总测试数: 15
  通过: 15
  失败: 0

  通过率: 100.0%

🎉 所有测试通过！系统运行正常！
```

**何时使用**:
- ✅ 部署后验证
- ✅ 定期健康检查
- ✅ 故障排查

---

## 📊 监控和告警

### 系统健康检查

**每日检查**:
```bash
# 1. 检查 Gateway 状态
systemctl --user is-active openclaw-gateway

# 2. 检查内存使用
free | awk '/Mem/{printf("%.1f%"), $3/$2*100}'

# 3. 检查配置文件
python3 -c "import json; json.load(open('/root/.openclaw/openclaw.json'))"

# 4. 运行集成测试
bash /root/.openclaw/workspace/scripts/integration-test.sh
```

### 日志位置

- **API 保护日志**: `/root/.openclaw/workspace/.api-guard-state/`
- **缓存管理日志**: `/root/.openclaw/workspace/logs/cache-consistency.log`
- **Feature Flag 日志**: `/root/.openclaw/workspace/logs/feature-flags.log`
- **集成测试日志**: `/root/.openclaw/workspace/logs/api-health.log`

---

## 🛠️ 故障排查

### 问题 1: API 调用失败

**症状**: API 调用频繁失败

**排查步骤**:
```bash
# 1. 检查熔断器状态
bash /root/.openclaw/workspace/scripts/api-invariant-guard.sh status

# 2. 如果熔断器打开，重置
bash /root/.openclaw/workspace/scripts/api-invariant-guard.sh reset

# 3. 测试 API 连接
curl -s -o /dev/null -w "%{http_code}" -X POST \\
  https://open.bigmodel.cn/api/anthropic/v1/messages \\
  -H "Content-Type: application/json" \\
  -H "x-api-key: YOUR_API_KEY" \\
  -H "anthropic-version: 2023-06-01" \\
  -d '{"model":"glm-4.7","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
```

### 问题 2: 缓存占用过高

**症状**: 缓存目录占用大量空间

**排查步骤**:
```bash
# 1. 查看缓存统计
bash /root/.openclaw/workspace/scripts/cache-consistency-manager.sh stats

# 2. 清理过期缓存
bash /root/.openclaw/workspace/scripts/cache-consistency-manager.sh cleanup

# 3. 检查缓存大小
du -sh /root/.openclaw/workspace/memory/.cache
```

### 问题 3: Feature Flag 不生效

**症状**: 修改 Flag 后没有生效

**排查步骤**:
```bash
# 1. 检查 Flag 状态
bash /root/.openclaw/workspace/scripts/feature-flag-controller.sh show "flag-name"

# 2. 查看版本号
jq '.flags."flag-name".version' /root/.openclaw/workspace/.feature-flags/feature-flags.json

# 3. 检查启用状态
jq '.flags."flag-name".enabled' /root/.openclaw/workspace/.feature-flags/feature-flags.json
```

---

## 🎯 最佳实践

### 1. 定期维护

**每周**:
- 运行集成测试
- 检查内存使用
- 清理过期缓存

**每月**:
- 审查 Feature Flags
- 删除未使用的 Flags
- 归档旧日志

### 2. 监控指标

**关键指标**:
- API 成功率 > 99%
- 内存使用 < 85%
- 缓存命中率 > 80%
- 集成测试通过率 = 100%

### 3. 安全建议

- ✅ 定期备份配置文件
- ✅ 使用版本控制
- ✅ 记录重要变更
- ✅ 定期安全审计

---

## 📚 相关文档

- **集成测试报告**: `/root/.openclaw/workspace/docs/INTEGRATION-TEST-REPORT.md`
- **高优先级优化**: `/root/.openclaw/workspace/docs/DEEP-OPTIMIZATION-COMPLETE.md`
- **中优先级优化**: `/root/.openclaw/workspace/docs/MEDIUM-OPTIMIZATION-COMPLETE.md`
- **API 失败分析**: `/root/.openclaw/workspace/docs/API-FAILURE-ANALYSIS.md`

---

## 🆘 获取帮助

**遇到问题？**
1. 查看故障排查部分
2. 检查日志文件
3. 运行集成测试
4. 查看相关文档

**贡献**:
- 报告 Bug
- 提交改进建议
- 分享使用经验

---

**祝你使用愉快！** 😊

**系统已优化，性能卓越！** 🚀
