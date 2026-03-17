# 安全规则：API Key 管理

**类型**: 安全规则
**优先级**: 高
**版本**: 1.0.0

---

## 规则内容

### ✅ 应该做
- 将 API Keys 存储在环境变量中
- 使用 `.env` 文件（不提交到 Git）
- 使用密钥管理服务
- 定期轮换密钥
- 使用最小权限原则

### ❌ 不应该做
- 硬编码 API Keys 在代码中
- 将 API Keys 提交到 Git
- 在日志中打印 API Keys
- 在前端代码中暴露 API Keys
- 使用默认密钥

## 检测模式

### 敏感模式（14 种）
1. `sk-` - Stripe API Keys
2. `ghp_` - GitHub Personal Access Tokens
3. `AKIA` - AWS Access Keys
4. `AIza` - Google API Keys
5. `ya29` - OAuth Tokens
6. `xoxb` - Slack Bot Tokens
7. `pk_` - SendGrid Keys
8. `key_` - 通用密钥
9. `secret_` - 通用密钥
10. `password` - 密码字段
11. `token` - Token 字段
12. `.env` - 环境文件
13. `.key` - 私钥文件
14. `.pem` - 证书文件

## 示例

### ❌ 错误示例
```javascript
const apiKey = 'sk_live_1234567890'; // 硬编码
```

### ✅ 正确示例
```javascript
const apiKey = process.env.API_KEY; // 环境变量
```

## 审查命令
```bash
# 检查代码中的硬编码密钥
grep -r "sk_\|ghp_\|AKIA" ./

# 检查环境文件权限
ls -la .env .key .pem
```

## 参考
- OWASP A02:2021 - Cryptographic Failures
- CWE-798: Use of Hard-coded Credentials
- CWE-312: Cleartext Storage of Sensitive Information

---

*规则版本: 1.0.0*
*最后更新: 2026-03-17*
