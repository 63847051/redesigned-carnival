# 最佳实践 - 2026-03-11

**提取时间**: 2026-03-11 23:11
**来源**: 今天的错误分析和设计模式

---

## 🎯 最佳实践 1: 升级前检查清单

### 升级前必做
- [ ] **备份配置**
  ```bash
  cp /root/.openclaw/openclaw.json /root/.openclaw/backups/
  ```

- [ ] **检查兼容性**
  ```bash
  # 查看版本变更日志
  openclaw --help | grep version
  
  # 查看当前版本
  openclaw --version
  ```

- [ ] **同步包管理器**
  ```bash
  # 检查 npm 版本
  npm list -g openclaw
  
  # 检查 pnpm 版本
  pnpm list -g openclaw
  ```

- [ ] **准备回滚方案**
  ```bash
  # 保存回滚脚本
  cat > rollback.sh <<'EOF'
  npm install -g openclaw@旧版本
  pnpm install -g openclaw@旧版本
  EOF
  ```

### 升级后验证
- [ ] **版本一致性**
  ```bash
  npm list -g openclaw | grep openclaw
  pnpm list -g openclaw | grep openclaw
  ```

- [ ] **功能测试**
  ```bash
  openclaw doctor
  ```

- [ ] **Gateway 状态**
  ```bash
  systemctl --user is-active openclaw-gateway
  ```

---

## 🎯 最佳实践 2: 文件操作安全规范

### 读取文件前
```bash
# 1. 检查路径是否存在
[[ -e "$path" ]] || { echo "路径不存在"; return 1; }

# 2. 检查是文件还是目录
[[ -f "$path" ]] || { echo "不是文件"; return 1; }

# 3. 检查文件可读
[[ -r "$path" ]] || { echo "文件不可读"; return 1; }

# 4. 读取文件
cat "$path"
```

### 写入文件前
```bash
# 1. 检查目录是否存在
dir=$(dirname "$path")
[[ -d "$dir" ]] || mkdir -p "$dir"

# 2. 检查写入权限
[[ -w "$dir" ]] || { echo "目录不可写"; return 1; }

# 3. 备份现有文件
[[ -f "$path" ]] && cp "$path" "${path}.backup"

# 4. 写入文件
echo "内容" > "$path"
```

---

## 🎯 最佳实践 3: 错误处理规范

### 标准错误处理流程
```bash
# 1. 定义错误码
E_FILE_NOT_FOUND=1
E_PERMISSION_DENIED=2
E_INVALID_ARGUMENT=3
E_TIMEOUT=124

# 2. 错误处理函数
handle_error() {
    local code=$1
    local msg=$2
    local context=${3:-"未知"}
    
    echo "❌ [ERROR $code] $msg" >&2
    echo "📍 上下文: $context" >&2
    echo "💡 建议: " >&2
    
    # 记录日志
    log_error "$code" "$msg" "$context"
    
    return $code
}

# 3. 使用示例
if [[ ! -f "$file" ]]; then
    handle_error $E_FILE_NOT_FOUND "文件不存在" "读取文件: $file"
fi
```

### 错误日志格式
```
=== 错误 2026-03-11 23:11:00 ===
错误码: 1
错误信息: 文件不存在
上下文: 读取文件: /path/to/file
调用栈: 
  - script.sh:123
  - main.sh:45
建议: 检查文件路径是否正确
```

---

## 🎯 最佳实践 4: 版本管理规范

### 文件命名规范
```bash
# 主文档
SOUL.md           # 系统灵魂（当前版本）
README.md         # 项目说明

# 版本文档（只保留当前版本）
# ❌ 不要: SOUL-v3.md, SOUL-v5.4.md, CORE-EVOLUTION.md
# ✅ 只要: SOUL.md

# 更新日志
CHANGELOG.md      # 版本变更记录
```

### 版本号规范
```bash
# 主版本.次版本.修订号
5.5.0

# 更新规则
# 主版本：重大变更，不兼容
# 次版本：新功能，向后兼容
# 修订号：bug 修复，小改进
```

### 更新流程
```bash
# 1. 更新 SOUL.md 中的版本号
sed -i 's/版本: .*/版本: 5.5.1/' SOUL.md

# 2. 添加更新日志
cat >> CHANGELOG.md <<EOF
## 5.5.1 (2026-03-11)
### 修复
- 修复文件读取错误
- 修复 Gateway 崩溃问题
EOF

# 3. 删除旧版本文档
find . -name "*v5.*" -o -name "*v6.*" | xargs rm -f

# 4. 验证一致性
grep -r "版本:" *.md | awk '{print $2}' | sort -u
```

---

## 🎯 最佳实践 5: 监控和日志规范

### 日志分级
```bash
# DEBUG: 详细调试信息
log_debug "变量值: $var"

# INFO: 一般信息
log_info "开始执行: $task"

# WARN: 警告信息
log_warn "配置未找到，使用默认值"

# ERROR: 错误信息
log_error "操作失败: $error"
```

### 日志文件组织
```
/root/.openclaw/workspace/logs/
├── errors.log           # 错误日志
├── evolution.log        # 进化日志
├── heartbeat.log        # 心跳日志
└── debug.log           # 调试日志
```

### 监控指标
```bash
# Gateway 状态
systemctl --user is-active openclaw-gateway

# 内存使用
free | awk '/Mem/{printf "%.1f%%", $3/$2*100}'

# 错误数量
journalctl --user -u openclaw-gateway --since "1 hour ago" | grep -i error | wc -l

# 进化报告数量
find /root/.openclaw/workspace/.learnings/evolution_report_* -mtime -1 | wc -l
```

---

## 🎯 最佳实践 6: 脚本编写规范

### 脚本头部
```bash
#!/bin/bash
#
# 脚本名称: safe-read-file.sh
# 功能: 安全读取文件
# 作者: 自主进化系统 5.5
# 创建时间: 2026-03-11
# 版本: 1.0.0
#
# 使用方式:
#   ./safe-read-file.sh /path/to/file.txt
#
# 退出码:
#   0 - 成功
#   1 - 文件不存在
#   2 - 权限不足
#
```

### 参数检查
```bash
# 检查参数数量
if [[ $# -lt 1 ]]; then
    echo "❌ 错误: 缺少参数" >&2
    echo "用法: $0 <文件路径>" >&2
    exit 1
fi

# 检查参数值
file_path="$1"
if [[ -z "$file_path" ]]; then
    echo "❌ 错误: 文件路径为空" >&2
    exit 1
fi
```

### 错误处理
```bash
# 使用 set -e 遇到错误立即退出
set -e

# 使用 trap 捕获错误
trap 'echo "❌ 脚本执行失败，行号: $LINENO"; exit 1' ERR

# 或者使用自定义错误处理
handle_error() {
    local line=$1
    echo "❌ 错误发生在第 $line 行"
    cleanup
    exit 1
}

trap 'handle_error $LINENO' ERR
```

---

## 🎯 最佳实践 7: 测试和验证规范

### 单元测试
```bash
# 测试文件存在
test_file_exists() {
    local file="$1"
    [[ -f "$file" ]] && echo "✅ 测试通过: $file 存在" || echo "❌ 测试失败: $file 不存在"
}

# 测试文件可读
test_file_readable() {
    local file="$1"
    [[ -r "$file" ]] && echo "✅ 测试通过: $file 可读" || echo "❌ 测试失败: $file 不可读"
}

# 运行所有测试
run_tests() {
    test_file_exists "/root/.openclaw/openclaw.json"
    test_file_readable "/root/.openclaw/openclaw.json"
}
```

### 集成测试
```bash
# 测试完整流程
test_upgrade_process() {
    echo "🧪 测试升级流程..."
    
    # 1. 备份
    backup_config || return 1
    
    # 2. 升级
    upgrade_package || return 1
    
    # 3. 验证
    verify_version || return 1
    
    # 4. 清理
    cleanup_backup
    
    echo "✅ 测试通过"
    return 0
}
```

---

## 📊 最佳实践总结

### 安全性
- ✅ 检查所有输入
- ✅ 验证文件类型
- ✅ 处理所有错误
- ✅ 提供默认值

### 可靠性
- ✅ 备份关键数据
- ✅ 验证操作结果
- ✅ 记录详细日志
- ✅ 准备回滚方案

### 可维护性
- ✅ 清晰的命名
- ✅ 详细的注释
- ✅ 统一的风格
- ✅ 完整的文档

### 可追溯性
- ✅ 版本控制
- ✅ 变更日志
- ✅ 错误记录
- ✅ 操作日志

---

## 🚀 实施建议

### 立即实施
1. 使用升级前检查清单
2. 应用文件操作安全规范
3. 使用错误处理规范

### 逐步改进
1. 重构现有脚本
2. 添加单元测试
3. 完善监控日志

### 长期目标
1. 建立完整规范体系
2. 自动化测试
3. 持续优化

---

**这些最佳实践将让系统更稳定、更可靠、更易维护！** 🧬✨

---

*提取时间: 2026-03-11 23:11*
*版本: 自主进化系统 5.5*
