# 安全规则：文件权限检查

**类型**: 安全规则
**优先级**: 高
**版本**: 1.0.0

---

## 规则内容

### ✅ 应该做
- 设置正确的文件权限
- `.env` 文件权限应为 `600` (仅所有者可读写)
- `.key` 文件权限应为 `600`
- `.pem` 文件权限应为 `600`
- 脚本文件权限应为 `700` 或 `755`

### ❌ 不应该做
- 使用过于宽松的权限（如 777）
- 将敏感文件设置为可被其他用户读取
- 忽略文件权限检查

## 检查标准

### 敏感文件权限要求

| 文件类型 | 最小权限 | 推荐权限 |
|---------|---------|---------|
| `.env` | 600 | 600 |
| `.key` | 600 | 600 |
| `.pem` | 600 | 600 |
| `.cert` | 644 | 644 |
| `config.json` | 600 | 600 |
| 脚本文件 | 700 | 755 |

## 检测方法

### 检查文件权限
```bash
# 检查敏感文件权限
find . -name ".env" -o -name "*.key" -o -name "*.pem" | xargs ls -la

# 查找权限过宽的文件
find . -type f \( -name ".env" -o -name "*.key" -o -name "*.pem" \) -perm /o+r
```

### 自动修复
```bash
# 修复文件权限
chmod 600 .env
chmod 600 *.key
chmod 600 *.pem
```

## 示例

### ❌ 错误示例
```
-rw-r--r-- 1 user user 123 Mar 17 22:00 .env
```
权限过于宽松，其他用户可读取。

### ✅ 正确示例
```
-rw------- 1 user user 123 Mar 17 22:00 .env
```
权限正确，仅所有者可读写。

## 审查命令
```bash
# 完整权限检查
find . -type f \( -name ".env" -o -name "*.key" -o -name "*.pem" \) -exec ls -la {} \;

# 查找权限问题
find . -type f -name ".env" ! -perm 600
```

## 参考
- CWE-732: Incorrect Permission Assignment for Critical Resource
- OWASP A01:2021 - Broken Access Control
- POSIX File Permissions

---

*规则版本: 1.0.0*
*最后更新: 2026-03-17*
