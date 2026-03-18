---
name: 代码审查
description: 审查代码质量、安全性和可维护性
type: command
agent: 代码审查专家
version: 2.0.0
---

# /code-review - 代码审查

## 功能
全面审查代码质量、安全性、可维护性，提供改进建议。

## 使用方法
\`\`\`
/code-review "path/to/file.py"
\`\`\`

或

\`\`\`
/code-review
（审查最近修改的文件）
\`\`\`

## 输入规范

### 必需参数
- **file_path**: 文件路径（字符串）
  - 相对或绝对路径
  - 支持通配符（*.py）
  - 示例: "src/auth.py" 或 "src/*.py"

### 可选参数
- **focus**: 审查重点（数组）
  - quality: 代码质量
  - security: 安全性
  - performance: 性能
  - maintainability: 可维护性
  - 默认: 全部

- **severity**: 严重程度过滤（字符串）
  - critical: 只显示严重问题
  - high: 高级及以上
  - medium: 中级及以上
  - all: 全部
  - 默认: medium

## 输出规范

### 1. 总体评分（对象）
- **quality_score**: 质量评分（0-100）
- **security_score**: 安全评分（0-100）
- **maintainability_score**: 可维护性评分（0-100）
- **overall_score**: 综合评分（0-100）

### 2. 问题列表（数组）
每个问题包含：
- **id**: 唯一标识符
- **severity**: 严重程度（critical/high/medium/low）
- **category**: 类别（quality/security/performance/maintainability）
- **line**: 行号
- **message**: 问题描述
- **suggestion**: 改进建议
- **code_snippet**: 问题代码片段

### 3. 统计信息（对象）
- **total_issues**: 总问题数
- **critical_count**: 严重问题数
- **high_count**: 高级问题数
- **medium_count**: 中级问题数
- **low_count**: 低级问题数

### 4. 改进建议（数组）
- 优先级排序的改进建议
- 具体实施步骤

## 预期输出格式

\`\`\`markdown
# 代码审查报告: [文件名]

## 总体评分
- 质量评分: 85/100
- 安全评分: 72/100
- 可维护性评分: 78/100
- **综合评分: 78/100**

## 问题列表（按严重程度）

### 🚨 严重问题 (1个)
1. [security] 第45行: SQL注入风险
   \`\`\`python
   query = f"SELECT * FROM users WHERE id={user_id}"
   \`\`\`
   **建议**: 使用参数化查询
   \`\`\`python
   query = "SELECT * FROM users WHERE id=?"
   cursor.execute(query, (user_id,))
   \`\`\`

### ⚠️ 高级问题 (2个)
1. [quality] 第23行: 函数过长（50行）
   **建议**: 拆分为多个小函数
2. [performance] 第67行: 循环内查询数据库
   **建议**: 使用批量查询

### 📝 中级问题 (3个)
1. [maintainability] 第12行: 缺少文档字符串
2. [quality] 第34行: 魔法数字
3. [security] 第89行: 硬编码密钥

## 统计信息
- 总问题: 6个
- 严重: 1个 ⚠️
- 高级: 2个
- 中级: 3个

## 改进建议（优先级排序）
1. **[P0]** 修复SQL注入风险（第45行）
2. **[P1]** 优化数据库查询（第67行）
3. **[P2]** 添加函数文档
\`\`\`

## 验证标准
- ✅ 所有问题都有明确位置
- ✅ 所有建议都有可操作步骤
- ✅ 评分合理且有依据
- ✅ 优先级排序合理

## 边界（不覆盖）
- ❌ 不包含代码自动修复
- ❌ 不包含性能基准测试
- ❌ 不包含安全漏洞扫描（使用 /security-scan）

## 示例

### 输入
\`\`\`
/code-review "src/auth.py"
\`\`\`

### 输出
\`\`\`markdown
# 代码审查报告: src/auth.py

## 总体评分
- 质量评分: 85/100
- 安全评分: 72/100
- 可维护性评分: 78/100
- **综合评分: 78/100**

## 问题列表
[详见上文]
\`\`\`

---

**版本**: 2.0.0
**最后更新**: 2026-03-17
**状态**: ✅ 规范明确
