# 学习助手系统 - 使用指南

## 概述

学习助手系统帮助您管理知识图谱、追踪学习进度、智能安排复习计划。基于间隔重复算法 (SM-2) 自动安排复习时间。

## 功能特性

- **知识图谱**: 可视化知识点及其依赖关系
- **学习计划**: 智能生成每日学习计划
- **间隔重复**: 自动计算最佳复习时间
- **进度追踪**: 实时掌握学习进度和掌握度

## 配置说明

编辑 `config/learning.json`:

```json
{
  "user_profile": {
    "name": "学习者",
    "level": "intermediate",
    "daily_study_time_minutes": 60
  },
  "subjects": [
    {
      "name": "Python 编程",
      "topics": [
        {"name": "基础语法", "priority": 1, "mastery": 0.8},
        {"name": "函数", "priority": 2, "mastery": 0.7}
      ]
    }
  ],
  "spaced_repetition": {
    "enabled": true,
    "review_intervals_days": [1, 3, 7, 14, 30]
  }
}
```

## 运行方式

```bash
cd /root/.openclaw/workspace/competitors-monitor
python3 plugins/learning.py
```

## 输出示例

```
今日学习计划: 3 个新主题, 0 个复习
进度分析: 2 条

## 📚 学习助手报告

**日期**: 2026-03-18
**学习时长**: 60 分钟

### 📖 今日学习计划

**新内容**:

- Python 编程 - 面向对象 (当前: 50%)
- Python 编程 - 数据分析 (当前: 30%)
- Python 编程 - Web 开发 (当前: 20%)

### 📊 进度分析

📝 面向对象 掌握度较低 (50%)
📝 数据分析 掌握度较低 (30%)

知识图谱: 8 个节点
```

## 核心概念

### 知识点优先级

| 优先级 | 说明 |
|--------|------|
| 1 | 基础内容，必须掌握 |
| 2 | 进阶内容 |
| 3 | 高级内容 |

### 掌握度 (Mastery)

- 0.0 - 0.3: 初学
- 0.3 - 0.6: 理解
- 0.6 - 0.8: 熟悉
- 0.8 - 1.0: 掌握

### 间隔重复

系统使用 SM-2 算法自动安排复习:
- 第1次复习: 1天后
- 第2次复习: 3天后
- 第3次复习: 7天后
- 第4次复习: 14天后
- 第5次复习: 30天后

## 更新学习进度

复习完一个主题后，系统会自动更新下次复习时间:

```python
# 计算下次复习（示例）
# quality: 0-5 分，3分以上算通过
next_review = sr.calculate_next_review("函数", quality=4)
```

## 告警类型

| 类型 | 说明 |
|------|------|
| low_mastery | 掌握度过低 |
| review_due | 待复习 |
| goal_achieved | 达成学习目标 |
