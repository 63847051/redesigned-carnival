---
name: 导入学习成果
description: 导入他人分享的学习成果
type: command
agent: 主控 Agent
---

# /instinct-import - 导入学习成果

## 功能
导入他人分享的学习成果，合并到当前系统。

## 使用方法
```
/instinct-import learning-export.json
```

## 参数
- `file`: 学习成果文件（JSON 格式）

## 支持的格式
- **JSON 格式**: 从 /instinct-export 导出的文件
- **Markdown 格式**: 从文本导入

## 导入策略
- **合并模式**: 合并到现有学习成果
- **替换模式**: 替换现有学习成果
- **忽略冲突**: 忽略冲突的模式

## 验证
导入前会验证：
- 文件格式
- 模式结构
- 置信度范围

## 示例
```
/instinct-import learning-export-2026-03-17.json

输出:
📥 导入学习成果...
   来源: learning-export-2026-03-17.json
   模式数量: 5
   ✅ 导入成功
```

## 注意事项
- 只导入可信来源的学习成果
- 验证模式的适用性
- 根据实际情况调整置信度

## 参考
- PAI 学习系统 v3.0
- continuous-learning-v2
