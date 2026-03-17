---
name: 安全审查
description: 运行安全扫描并生成报告
type: command
agent: 安全审查专家
---

# /security-scan - 安全扫描

## 功能
运行全面的安全扫描，检查敏感信息、权限、注入风险等。

## 使用方法
```
/security-scan
```

## 扫描内容

### 1. Secrets 检测
- API Keys (sk-, ghp_, AKIA patterns)
- 密码和凭证
- Token 和证书

### 2. 文件权限
- .env, .key, .pem 文件
- 配置文件权限
- 凭证文件安全

### 3. 代码安全
- 命令注入风险
- SQL 注入风险
- XSS 漏洞
- CSRF 保护

### 4. Hook 安全
- Hook 脚本审计
- Hook 配置验证
- 动态代码执行检查

## 输出
- 安全报告（Markdown）
- 风险评级（A-F）
- 修复建议
- 优先级排序

## 自动修复
```
/security-scan --fix
```

自动修复安全的问题：
- 移除硬编码密钥
- 修复文件权限
- 更新配置

## CI 集成
```
npm run security-scan
```

集成到 CI/CD 流程。

## 参考标准
- OWASP Top 10
- CWE Top 25
- 安全编码最佳实践
