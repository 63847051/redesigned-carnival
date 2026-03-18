# 安全扫描 Skill

**版本**: v1.0
**创建时间**: 2026-03-19
**作者**: 大领导系统

---

## 📖 概述

**security-scan** 是一个全面的安全扫描 Skill，用于检测和防范各种安全风险。

**核心功能**：
- ✅ 敏感信息泄露检测
- ✅ API Key 安全验证
- ✅ 文件权限审查
- ✅ 命令注入风险检查
- ✅ 凭证文件安全审计
- ✅ Hook 脚本安全验证

---

## 🎯 使用方式

### 命令调用

```bash
# 扫描整个工作区
/security-scan

# 扫描特定文件
/security-scan path/to/file

# 扫描特定目录
/security-scan path/to/directory

# 使用特定规则
/security-scan --rules api-key,secret,injection
```

### 触发词

- "安全扫描"
- "security scan"
- "检查安全"
- "安全检查"
- "扫描风险"

---

## 🔍 扫描类型

### 1️⃣ 敏感信息泄露检测

**检测模式**：
```javascript
const SENSITIVE_PATTERNS = {
  // API Keys
  'API Key': /(?:api[_-]?key|apikey|API[_-]?KEY)\s*[:=]\s*['"]?([a-zA-Z0-9_\-]{20,})['"]?/gi,
  'AWS Access Key': /AKIA[0-9A-Z]{16}/g,
  'GitHub Token': /ghp_[a-zA-Z0-9]{36}/g,
  'Slack Token': /xox[pbar]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32}/g,

  // Secrets & Passwords
  'Secret': /(?:secret|password|passwd|pwd|SECRET|PASSWORD|PASSWD|PWD)\s*[:=]\s*['"]?([^\s'"`]{8,})['"]?/gi,
  'Bearer Token': /Bearer\s+[a-zA-Z0-9_\-\.]{20,}/gi,
  'JWT': /eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+/g,

  // Private Keys
  'RSA Private Key': /-----BEGIN\s+RSA\s+PRIVATE\s+KEY-----/g,
  'Private Key': /-----BEGIN\s+PRIVATE\s+KEY-----/g,
  'SSH Private Key': /-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----/g,

  // Database URLs
  'Database URL': /(?:mongodb|mysql|postgres|redis|sqlite)\+?:\/\/[^\s'"`]+/gi,
  'Connection String': /Server=[^;]+;Database=[^;]+/gi,

  // Internal URLs
  'Internal URL': /https?:\/\/(?:localhost|127\.0\.0\.1|0\.0\.0\.0|10\.|172\.1[6-9]\.|172\.2[0-9]\.|172\.3[0-1]\.|192\.168\)[^\s'"`]*/gi
};
```

**检测文件类型**：
- ✅ Markdown (.md)
- ✅ JavaScript (.js)
- ✅ Python (.py)
- ✅ Shell (.sh, .bash)
- ✅ 配置文件 (.json, .yml, .yaml, .env, .config)
- ✅ 文本文件 (.txt)

**排除目录**：
- ❌ node_modules/
- ❌ .git/
- ❌ venv/
- ❌ __pycache__/
- ❌ .claw/.backups/

---

### 2️⃣ API Key 安全验证

**检查项**：
1. **硬编码检测** - API Key 是否直接写在代码中
2. **环境变量使用** - 是否正确使用环境变量
3. **密钥强度** - 密钥长度和复杂度
4. **密钥轮换** - 是否有过期或需要更新的密钥
5. **权限最小化** - API Key 权限是否符合最小权限原则

**建议**：
- ✅ 使用环境变量存储 API Key
- ✅ 使用 `.env` 文件（不提交到 Git）
- ✅ 使用密钥管理服务（如 AWS Secrets Manager）
- ✅ 定期轮换 API Key
- ✅ 为不同环境使用不同的 API Key

---

### 3️⃣ 文件权限审查

**检查项**：
1. **敏感文件权限** - 凭证文件、配置文件权限
2. **可执行文件** - 脚本文件权限
3. **写入权限** - 重要文件的写权限
4. **组权限** - 组成员是否有过多权限
5. **其他用户权限** - 其他用户是否有权限

**权限标准**：
```bash
# 敏感文件（凭证、密钥）
# 应该: 600 (仅所有者可读写)
credentials/  →  600

# 配置文件
# 应该: 644 (所有者可读写，其他人只读)
*.json, *.yml  →  644

# 可执行脚本
# 应该: 755 (所有者可执行，其他人可读执行)
*.sh, *.js  →  755

# 重要目录
# 应该: 755 (所有者完全控制，其他人可进入)
.claw/, .pai-learning/  →  755
```

---

### 4️⃣ 命令注入风险检查

**检测模式**：
```javascript
const DANGEROUS_PATTERNS = [
  // 直接执行用户输入
  /eval\s*\(/,
  /exec\s*\(/,
  /system\s*\(/,
  /popen\s*\(/,

  // Shell 命令拼接
  /\$\{.*\}/,          // Bash 变量替换
  /`.*`/,              // 命令替换
  /\$\(.*\)/,          // 命令替换

  // 危险函数
  /child_process\.exec/,
  /os\.system/,
  /subprocess\.call/,

  // SQL 注入
  /SELECT.*FROM.*WHERE.*\+/i,
  /UPDATE.*SET.*\+/i,
  /DELETE.*FROM.*\+/i,

  // 路径遍历
  /\.\.\/\.\./,        // 父目录遍历
  /%2e%2e\//,          // URL 编码的父目录
];
```

**风险等级**：
- 🔴 **高危** - 直接执行用户输入
- 🟡 **中危** - 使用外部数据构建命令
- 🟢 **低危** - 使用参数化查询或转义

---

### 5️⃣ 凭证文件安全审计

**审计文件**：
- ✅ `.env` 文件
- ✅ `credentials/` 目录
- ✅ `.claw/credentials/` 目录
- ✅ `openclaw.json`（检查是否有硬编码密钥）
- ✅ `.git/config`（检查凭证存储）

**审计内容**：
1. 文件是否存在
2. 文件权限是否正确
3. 是否包含敏感信息
4. 是否应该提交到 Git（检查 .gitignore）
5. 密钥是否过期或需要更新

---

### 6️⃣ Hook 脚本安全验证

**检查项**：
1. **语法验证** - 所有 Hook 脚本语法是否正确
2. **权限检查** - Hook 脚本是否可执行
3. **安全审查** - Hook 脚本是否有安全风险
4. **依赖检查** - Hook 脚本依赖是否安全
5. **日志审查** - Hook 日志是否泄露敏感信息

**Hook 脚本列表**：
- session-start.js
- session-end.js
- suggest-compact.js
- pre-tool-use.js
- post-tool-use.js
- pre-write.js
- post-write.js
- pre-compact.js
- post-compact.js
- ERROR-HANDLING.js

---

## 📊 扫描报告格式

### 报告结构

```markdown
# 安全扫描报告

**扫描时间**: 2026-03-19 07:15:00
**扫描范围**: /root/.openclaw/workspace
**扫描类型**: 完整扫描

---

## 📊 扫描摘要

- **扫描文件数**: 150
- **发现问题**: 5
- **高危**: 1
- **中危**: 2
- **低危**: 2

---

## 🚨 高危问题

### 1. API Key 泄露

**文件**: `config.js`
**行号**: 15
**问题**: 硬编码 API Key
**建议**: 使用环境变量

---

## ⚠️ 中危问题

### 1. 文件权限过宽

**文件**: `credentials/api-key.txt`
**当前权限**: 644
**建议权限**: 600
**命令**: `chmod 600 credentials/api-key.txt`

---

## 💡 低危问题

### 1. 缺少 .gitignore 条目

**文件**: `.env`
**问题**: 可能被提交到 Git
**建议**: 添加 `.env` 到 .gitignore

---

## ✅ 安全建议

1. 立即修复高危问题
2. 尽快修复中危问题
3. 计划修复低危问题
4. 定期执行安全扫描
5. 建立安全审计流程
```

---

## 🔧 配置选项

### 扫描规则配置

**文件位置**: `.claw/rules/security/config.json`

```json
{
  "scanDepth": "max",
  "excludeDirectories": [
    "node_modules",
    ".git",
    "venv",
    "__pycache__",
    ".claw/.backups"
  ],
  "excludeFiles": [
    "*.log",
    "*.bak",
    "*.tmp"
  ],
  "enabledRules": [
    "sensitive-info",
    "api-key",
    "file-permissions",
    "command-injection",
    "credentials-audit",
    "hook-security"
  ],
  "severityLevel": "all"
}
```

---

## 🎯 最佳实践

### 开发阶段
1. ✅ 使用环境变量存储敏感信息
2. ✅ 不要在代码中硬编码密钥
3. ✅ 使用参数化查询防止注入
4. ✅ 定期更新依赖包
5. ✅ 使用 `.gitignore` 保护敏感文件

### 部署阶段
1. ✅ 设置正确的文件权限
2. ✅ 使用密钥管理服务
3. ✅ 启用日志审计
4. ✅ 定期安全扫描
5. ✅ 建立安全响应流程

### 运维阶段
1. ✅ 定期轮换密钥
2. ✅ 监控异常访问
3. ✅ 审计日志文件
4. ✅ 更新安全规则
5. ✅ 进行安全培训

---

## 📚 参考资料

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [AgentShield (ECC)](https://github.com/prefetch/everything-claude-code)
- [Security Best Practices](https://github.com/OWASP/CheatSheetSeries)

---

## 🔄 版本历史

- **v1.0** (2026-03-19) - 初始版本
  - 敏感信息检测
  - API Key 验证
  - 文件权限审查
  - 命令注入检查
  - 凭证文件审计
  - Hook 安全验证

---

**Skill 文件位置**: `.claw/skills/security-scan/SKILL.md`

**实现脚本**: `.claw/scripts/security-scan.js`

**规则库**: `.claw/rules/security/`
