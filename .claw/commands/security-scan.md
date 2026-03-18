---
name: 安全审查
description: 运行安全扫描并生成报告
type: command
agent: 安全审查专家
version: 2.0.0
---

# /security-scan - 安全审查

## 功能
运行安全扫描，检测敏感信息泄露、安全漏洞、配置问题。

## 使用方法
\`\`\`
/security-scan
\`\`\`

或

\`\`\`
/security-scan "path/to/scan"
\`\`\`

## 输入规范

### 可选参数
- **target**: 扫描目标（字符串）
  - 默认: 当前目录
  - 支持文件或目录
  - 示例: "src/" 或 ".env"

- **scan_type**: 扫描类型（字符串）
  - full: 完整扫描
  - quick: 快速扫描
  - secrets: 只扫描敏感信息
  - config: 只扫描配置问题
  - 默认: quick

## 输出规范

### 1. 扫描摘要（对象）
- **total_files**: 扫描文件数
- **issues_found**: 发现问题数
- **critical_issues**: 严重问题数
- **scan_duration**: 扫描耗时（秒）

### 2. 问题列表（数组）
每个问题包含：
- **id**: 唯一标识符
- **severity**: 严重程度（critical/high/medium/low）
- **category**: 类别（secrets/config/dependencies/code）
- **file**: 文件路径
- **line**: 行号
- **rule_id**: 规则ID
- **message**: 问题描述
- **recommendation**: 修复建议

### 3. 风险评级（对象）
- **overall_risk**: 总体风险等级（A/B/C/D/F）
- **risk_factors**: 风险因素列表

### 4. 修复建议（数组）
- 优先级排序的修复建议
- 具体实施步骤

## 预期输出格式

\`\`\`markdown
# 安全扫描报告

## 扫描摘要
- 扫描文件: 45个
- 发现问题: 3个
- 严重问题: 0个 ✅
- 扫描耗时: 2.3秒

## 风险评级
**总体风险: B (良好)**

风险因素:
- 发现1个中级问题
- 发现2个低级问题
- 无严重问题

## 问题列表（按严重程度）

### 🚨 严重问题 (0个)
✅ 未发现严重问题

### ⚠️ 高级问题 (0个)
✅ 未发现高级问题

### 📝 中级问题 (1个)
1. [secrets] .env:3 - 可能的API密钥
   \`\`\`bash
   API_KEY=sk_live_1234567890abcdef
   \`\`\`
   **建议**: 使用环境变量或密钥管理服务
   **规则**: GITHUB_TOKEN_PATTERN

### 💡 低级问题 (2个)
1. [config] package.json:15 - 依赖版本过宽
   \`\`\`json
   "express": "*"
   \`\`\`
   **建议**: 锁定版本号
2. [code] src/auth.js:23 - 缺少输入验证

## 修复建议（优先级排序）
1. **[P0]** 无严重问题 ✅
2. **[P1]** 移除.env中的API密钥
3. **[P2]** 锁定依赖版本
4. **[P3]** 添加输入验证

## 扫描配置
- 扫描类型: quick
- 排除目录: node_modules/, .git/
- 规则版本: v1.0.0
\`\`\`

## 验证标准
- ✅ 所有问题都有明确位置
- ✅ 所有建议都有可操作步骤
- ✅ 风险评级合理
- ✅ 优先级排序合理

## 边界（不覆盖）
- ❌ 不包含运行时漏洞扫描
- ❌ 不包含网络端口扫描
- ❌ 不包含第三方服务依赖分析

## 扫描规则
- **GITHUB_TOKEN_PATTERN**: GitHub Token检测
- **AWS_KEY_PATTERN**: AWS密钥检测
- **API_KEY_PATTERN**: API密钥检测
- **WIDE_VERSION_PATTERN**: 宽版本依赖检测
- **HARDCODED_SECRET**: 硬编码密钥检测

## 示例

### 输入
\`\`\`
/security-scan
\`\`\`

### 输出
\`\`\`markdown
# 安全扫描报告
[详见上文]
\`\`\`

---

**版本**: 2.0.0
**最后更新**: 2026-03-17
**状态**: ✅ 规范明确
