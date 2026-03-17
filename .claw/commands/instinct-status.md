---
name: 查看学习状态
description: 查看已学习的模式和置信度评分
type: command
agent: 主控 Agent
---

# /instinct-status - 查看学习状态

## 功能
查看已学习的模式和置信度评分。

## 使用方法
```
/instinct-status
```

## 输出
- 学习模式列表
- 置信度评分
- 频率和成功率
- 优先级排序

## 置信度等级
- 🟢 高置信度 (80-100): 优先应用
- 🟡 中置信度 (50-79): 谨慎应用
- 🔴 低置信度 (0-49): 过滤掉

## 示例
```
/instinct-status

输出:
📊 学习模式 (3 个):
1. API 分页处理 - 置信度: 95 🟢 高
2. Token 优化 - 置信度: 85 🟢 高
3. 错误处理 - 置信度: 72 🟡 中
```

## 参考
- PAI 学习系统 v3.0
- continuous-learning-v2
