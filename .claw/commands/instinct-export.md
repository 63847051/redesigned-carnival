---
name: 导出学习成果
description: 导出已学习的模式和置信度评分
type: command
agent: 主控 Agent
---

# /instinct-export - 导出学习成果

## 功能
导出已学习的模式和置信度评分到文件。

## 使用方法
```
/instinct-export

或

/instinct-export learning-2026-03-17.json
```

## 输出格式
- **JSON 格式**: 包含模式、置信度、元数据
- **Markdown 格式**: 人类可读的学习报告

## 输出文件
- `learning-export-<timestamp>.json`
- `learning-export-<timestamp>.md`

## 示例
```
/instinct-export

输出:
✅ 学习成果已导出:
   - JSON: learning-export-2026-03-17.json
   - Markdown: learning-export-2026-03-17.md
```

## 用途
- 备份学习成果
- 分享给其他人
- 迁移到其他系统

## 参考
- PAI 学习系统 v3.0
- continuous-learning-v2
