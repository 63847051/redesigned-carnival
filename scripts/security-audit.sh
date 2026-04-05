#!/bin/bash
# =============================================================================
# 安全审计脚本 - Security Audit Script
# =============================================================================
# 功能: 检查 OpenClaw 系统的安全配置，发现潜在风险
# 作者: 大领导 🎯
# 创建: 2026-04-02
# =============================================================================

set -euo pipefail

# =============================================================================
# 配置
# =============================================================================

OPENCLAW_DIR="${OPENCLAW_DIR:-/root/.openclaw}"
CONFIG_FILE="${OPENCLAW_DIR}/openclaw.json"
WORKSPACE_DIR="${WORKSPACE_DIR:-/root/.openclaw/workspace}"
REPORT_FILE="${WORKSPACE_DIR}/security-report.md"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# =============================================================================
# 工具函数
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $@"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $@"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $@"
}

log_error() {
    echo -e "${RED}[✗]${NC} $@"
}

# =============================================================================
# 检查函数
# =============================================================================

check_deployment() {
    log_info "检查部署方式..."

    # 检查是否在主力机运行
    if [ -f "$HOME/.ssh/id_rsa" ] || [ -f "$HOME/.ssh/id_ed25519" ]; then
        log_warning "检测到 SSH 密钥，可能是在主力机运行"
    fi

    # 检查是否有代码、文档
    if [ -d "$HOME/Documents" ] || [ -d "$HOME/code" ]; then
        log_warning "检测到文档或代码目录，可能是在主力机"
    fi

    log_success "部署方式检查完成"
}

check_config_file() {
    log_info "检查配置文件..."

    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "配置文件不存在: $CONFIG_FILE"
        return 1
    fi

    # 检查文件权限
    local perms=$(ls -l "$CONFIG_FILE" | awk '{print $1}')
    if [[ "$perms" =~ .*rwx.* ]]; then
        log_warning "配置文件权限过宽: $perms"
    fi

    log_success "配置文件检查完成"
}

check_network_binding() {
    log_info "检查网络绑定..."

    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "配置文件不存在，无法检查"
        return 1
    fi

    # 检查 Gateway 绑定地址
    local bind_addr=$(grep -o '"bind"[[:space:]]*"[^"]*' "$CONFIG_FILE" | cut -d'"' -f 2)

    if [ "$bind_addr" = "0.0.0.0" ] || [ "$bind_addr" = "::" ]; then
        log_error "Gateway 绑定在所有接口（公网暴露）！"
        return 1
    fi

    if [ "$bind_addr" = "127.0.0.1" ] || [ "$bind_addr" = "loopback" ]; then
        log_success "Gateway 绑定在本地回环（安全）"
    else
        log_warning "Gateway 绑定在: $bind_addr"
    fi

    log_success "网络绑定检查完成"
}

check_token_strength() {
    log_info "检查 Gateway Token 强度..."

    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "配置文件不存在，无法检查"
        return 1
    fi

    # 检查 Token
    local token=$(grep -o '"token"[[:space:]]*"[^"]*' "$CONFIG_FILE" | cut -d'"' -f 2)

    if [ -z "$token" ]; then
        log_warning "未设置 Gateway Token"
        return 0
    fi

    # 检查 Token 长度
    local token_len=${#token}

    if [ $token_len -lt 32 ]; then
        log_error "Token 太短（${token_len} 字符），建议使用 64 位十六进制"
        return 1
    fi

    # 检查是否是弱密码
    local weak_patterns=("123456" "password" "openclaw" "token" "admin" "test")

    for pattern in "${weak_patterns[@]}"; do
        if [[ "$token" == *"$pattern"* ]]; then
            log_error "Token 包含弱密码: $pattern"
            return 1
        fi
    done

    log_success "Token 强度检查通过（${token_len} 字符）"
}

check_allow_from() {
    log_info "检查 allowFrom 配置..."

    if [ ! -f "$CONFIG_FILE" ]; then
        return 0
    fi

    # 检查 allowFrom 配置
    local allow_from=$(grep -o '"allowFrom"[[:space:]]*[^]]*' "$CONFIG_FILE" | cut -d'"' -f 2 | head -1)

    if [ "$allow_from" = "[\"*\"]" ] || [ "$allow_from" = "[\"*\"]" ]; then
        log_error "allowFrom 设置为 [*]，允许所有人访问！"
        return 1
    fi

    log_success "allowFrom 配置检查完成"
}

check_dm_policy() {
    log_info "检查 DM Policy..."

    if [ ! -f "$CONFIG_FILE" ]; then
        return 0
    fi

    # 检查 DM Policy
    local dm_policy=$(grep -o '"dmPolicy"[[:space:]]*"[^"}]*' "$CONFIG_FILE" | cut -d'"' -f 2)

    if [ "$dm_policy" = "open" ]; then
        log_error "DM Policy 为 open，陌生人可以直接对话！"
        log_info "建议改为 pairing"
        return 1
    fi

    log_success "DM Policy 检查通过"
}

check_sandbox() {
    log_info "检查 Docker Sandbox 隔离..."

    if [ ! -f "$CONFIG_FILE" ]; then
        return 0
    fi

    # 检查 Sandbox 模式
    local sandbox_mode=$(grep -o '"mode"[[:space:]]*"[^"}]*' "$CONFIG_FILE" | grep -A 5 "sandbox" | grep -o '"mode"[[:space:]]*"[^"}]*' | cut -d'"' -f 2)

    if [ -z "$sandbox_mode" ]; then
        log_warning "未配置 Sandbox 隔离"
        return 0
    fi

    if [ "$sandbox_mode" != "non-main" ]; then
        log_warning "Sandbox 模式不是 non-main，群组消息可能不隔离"
    fi

    log_success "Sandbox 配置检查通过"
}

check_exposed_ports() {
    log_info "检查暴露端口..."

    # 检查 Gateway 监听端口
    local gateway_port=$(grep -o '"port"[[:space:]]*[0-9]+' "$CONFIG_FILE")

    if [ -n "$gateway_port" ]; then
        log_info "Gateway 端口: $gateway_port"

        # 检查端口是否对外开放
        if command -v ss &>/dev/null; then
            local listening=$(ss -tlnp | grep ":$gateway_port" | grep LISTEN)
            if [ -n "$listening" ]; then
                if echo "$listening" | grep -q "0.0.0.0:0"; then
                    log_error "端口在所有接口监听（公网暴露）！"
                else
                    log_warning "端口在监听，需确认是否安全"
                fi
            fi
        fi
    fi

    log_success "端口检查完成"
}

check_file_permissions() {
    log_info "检查文件权限..."

    # 检查敏感文件权限
    local sensitive_files=(
        "$HOME/.ssh/id_rsa"
        "$HOME/.ssh/id_ed25519"
        "$CONFIG_FILE"
    )

    for file in "${sensitive_files[@]}"; do
        if [ -f "$file" ]; then
            local perms=$(ls -l "$file" | awk '{print $1}')
            if [[ "$perms" =~ .*r..* ]]; then
                log_warning "$file 权限过大: $perms"
            fi
        fi
    done

    log_success "文件权限检查完成"
}

# =============================================================================
# 主流程
# =============================================================================

show_usage() {
    cat << EOF
用法: $0 [选项]

选项:
  --quick           快速检查（仅高危项）
  --report          生成审计报告
  --fix             自动修复（谨慎使用）
  --help            显示帮助

示例:
  # 全面审计
  $0

  # 快速检查
  $0 --quick

  # 生成报告
  $0 --report > security-report.md

EOF
}

main() {
    echo ""
    log_info "=========================================="
    log_info "OpenClaw 安全审计"
    log_info "=========================================="
    echo ""

    local quick_mode=false
    local generate_report=false
    local auto_fix=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --quick)
                quick_mode=true
                shift
                ;;
            --report)
                generate_report=true
                shift
                ;;
            --fix)
                auto_fix=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    local failed=0

    # 执行检查
    if [ "$quick_mode" = "false" ]; then
        check_deployment || failed=1
        echo ""
    fi

    check_config_file || failed=1
    echo ""

    check_network_binding || failed=1
    echo ""

    check_token_strength || failed=1
    echo ""

    check_allow_from || failed=1
    echo ""

    check_dm_policy || failed=1
    echo ""

    check_sandbox || failed=1
    echo ""

    check_exposed_ports || failed=1
    echo ""

    check_file_permissions || failed=1
    echo ""

    # 生成报告
    if [ "$generate_report" = "true" ]; then
        generate_security_report
    fi

    # 总结
    echo ""
    log_info "=========================================="
    if [ $failed -eq 0 ]; then
        log_success "安全审计通过"
    else
        log_error "发现 $failed 个安全问题"
    fi
    log_info "=========================================="

    if [ "$auto_fix" = "true" ]; then
        log_info ""
        log_info "自动修复功能开发中..."
    fi
}

# =============================================================================
# 辅助函数
# =============================================================================

generate_security_report() {
    log_info "生成安全审计报告..."

    cat > "$REPORT_FILE" << EOF
# OpenClaw 安全审计报告

**审计时间**: $(date '+%Y-%m-%d %H:%M:%S')
**检查人**: 大领导 🎯

---

## 📊 审计结果摘要

$(if [ $failed -eq 0 ]; then
    echo "✅ 所有检查通过"
else
    echo "⚠️  发现 $failed 个问题"
fi)

---

## 📋 详细检查项

### 1. 部署方式
$(check_deployment 2>&1 | grep -E "检查|✓|!" | sed 's/^/  /')

### 2. 配置文件
$(check_config_file 2>&1 | grep -E "检查|✓|!" | sed 's/^/  /')

### 3. 网络绑定
$(check_network_binding 2>&1 | grep -E "检查|✓|!| Gateway" | sed 's/^/  /')

### 4. Token 强度
$(check_token_strength 2>&1 | grep -E "检查|✓|!| Token" | sed 's/^/  /')

### 5. allowFrom 配置
$(check_allow_from 2>&1 | grep -E "检查|✓|!| allowFrom" | sed 's/^/  /')

### 6. DM Policy
$(check_dm_policy 2>&1 | grep -E "检查|✓|!| DM Policy" | sed 's/^/  /')

### 7. Sandbox 隔离
$(check_sandbox 2>&1 | grep -E "检查|✓|!| Sandbox" | sed 's/^/  /')

### 8. 暴露端口
$(check_exposed_ports 2>&1 | grep -E "检查|✓|!| 端口" | sed 's/^/  /')

### 9. 文件权限
$(check_file_permissions 2>&1 | grep -E "检查|✓|!| 文件权限" | sed 's/^/  /')

---

## 🔧 修复建议

### 高优先级
- [ ] 使用专用部署（VPS / Pi 5）
- [ ] 配置 Tailscale 私有网络
- [ ] 启用 Docker Sandbox（non-main）
- [ ] 生成强 Gateway Token
- [ ] 修复网络绑定（改为 127.0.0.1）

### 中优先级
- [ ] 更新 DM Policy 为 pairing
- [ ] 配置合理的 allowFrom
- [ ] 限制文件权限（600）
- [ ] 移除公网暴露的端口

### 低优先级
- [ ] 定期更新 Token
- [ ] 定期运行 security audit
- [ ] 监控访问日志

---

## 📚 参考资料

- OpenClaw 进阶手册 Vol.2 - Tip 15-20
- OpenClaw 官方文档: docs.openclaw.ai
- 安全检查清单: docs/SECURITY-CHECKLIST.md

---

**报告位置**: \`$REPORT_FILE\`
**下次审计**: 建议每周一次

EOF

    log_success "报告已生成: $REPORT_FILE"
}

# =============================================================================
# 运行主流程
# =============================================================================

main "$@"
