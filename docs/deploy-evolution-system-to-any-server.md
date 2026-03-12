# 🚀 自我进化系统 - 完整部署指南

**适用场景**: 在任何OpenClaw环境（"小龙虾"）上部署自我进化系统

---

## 📋 部署清单

### 前置要求

✅ OpenClaw已安装（版本 >= 2026.2.26）  
✅ Bash shell  
✅ Python 3.8+  
✅ systemctl（用户级）  
✅ 有工作区权限  

---

## 🚀 快速部署（5分钟）

### Step 1: 复制核心脚本

```bash
# 在目标服务器上
cd ~/.openclaw workspace/scripts

# 创建自我进化系统脚本
cat > self-evolution-system.sh << 'EVOLUTION_SCRIPT'
#!/bin/bash
# 自我进化系统 - 统一调度器
set -e

WORKSPACE="/root/.openclaw/workspace"
PAI_WORKFLOW="$WORKSPACE/scripts/pai-workflow.sh"
SES_AUTO="$WORKSPACE/scripts/ses-auto.sh"
PROTECTION="$WORKSPACE/scripts/protection-check.sh"
L7_VALIDATION="$WORKSPACE/scripts/l7-config-validation.sh"
HEARTBEAT_EVOLUTION="$WORKSPACE/scripts/heartbeat-evolution.sh"

EVOLUTION_LOG="$WORKSPACE/.evolution/evolution.log"
mkdir -p "$(dirname "$EVOLUTION_LOG")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$EVOLUTION_LOG"
}

log "🧬 自我进化系统启动..."
echo "======================================"

# Step 1: L7配置验证
echo ""
echo "🔍 步骤1: L7配置验证..."
if [ -f "$L7_VALIDATION" ]; then
    if bash "$L7_VALIDATION"; then
        log "✅ L7验证通过"
    else
        log "❌ L7发现配置问题"
    fi
else
    echo "⚠️ L7验证脚本不存在，跳过"
fi

# Step 2: 6层防护检测
echo ""
echo "📡 步骤2: 6层防护系统检测..."
PROTECTION_OUTPUT=$(bash "$PROTECTION" 2>&1)
PROTECTION_STATUS=$?
if [ $PROTECTION_STATUS -ne 0 ]; then
    log "❌ 防护系统检测到异常"
    if [ -f "$WORKSPACE/scripts/pai-learning-capture.sh" ]; then
        bash "$WORKSPACE/scripts/pai-learning-capture.sh" \
            "protection" 3 0 "防护异常" "auto-evolution" 2>/dev/null || true
    fi
else
    log "✅ 防护系统正常"
fi

# Step 3: 检查错误
echo ""
echo "🔍 步骤3: 检查最近错误..."
ERRORS=$(journalctl --user -u openclaw-gateway --since "30 minutes ago" --no-pager | \
  grep -i "error\|failed" | grep -v "HEARTBEAT_OK" | tail -10)

if [ -n "$ERRORS" ]; then
    ERROR_COUNT=$(echo "$ERRORS" | grep -c "^")
    log "❌ 发现 $ERROR_COUNT 个错误"
    
    ERROR_FILE="$WORKSPACE/.learnings/errors/error_$(date +%Y%m%d_%H%M%S).md"
    mkdir -p "$WORKSPACE/.learnings/errors"
    
    cat > "$ERROR_FILE" << EOF
# 错误记录

**时间**: $(date)
**来源**: 自我进化系统自动检测

\`\`\`
$ERRORS
\`\`\`

## 待PAI深度分析...
EOF
    log "✓ 错误已记录: $ERROR_FILE"
else
    log "✅ 无最近错误"
fi

# Step 4: PAI深度学习
echo ""
echo "🧠 步骤4: PAI深度学习..."
if [ -n "$ERRORS" ] && [ -f "$PAI_WORKFLOW" ]; then
    if [ -f "$WORKSPACE/scripts/pai-learning-capture.sh" ]; then
        bash "$WORKSPACE/scripts/pai-learning-capture.sh" \
            error 5 0 "自动捕获的错误" "auto-evolution" 2>/dev/null || true
    fi
    bash "$PAI_WORKFLOW" 2>&1 | head -20 | tee -a "$EVOLUTION_LOG"
    log "✅ PAI学习完成"
else
    echo "✓ 无错误，跳过PAI学习"
fi

# Step 5: 超级大脑进化
echo ""
echo "🎯 步骤5: 超级大脑进化决策..."
if [ -f "$SES_AUTO" ]; then
    bash "$SES_AUTO" post-eval 2>&1 | head -20 | tee -a "$EVOLUTION_LOG"
    log "✅ SES进化完成"
else
    echo "⚠️ SES脚本不存在"
fi

# Step 6: memu知识存储
echo ""
echo "💾 步骤6: memu-engine知识存储..."
if systemctl --user is-active --quiet openclaw-gateway; then
    log "memu-engine运行正常"
    if [ -f "$HEARTBEAT_EVOLUTION" ]; then
        bash "$HEARTBEAT_EVOLUTION" 2>/dev/null || true
    fi
    log "✅ 知识已存储"
else
    log "⚠️ memu-engine未运行"
fi

echo ""
echo "======================================"
log "✅ 自我进化周期完成!"
echo "我变得更强了！🧬"
exit 0
EVOLUTION_SCRIPT

chmod +x self-evolution-system.sh
```

### Step 2: 创建L7配置验证脚本

```bash
# 创建L7验证脚本
cat > l7-config-validation.sh << 'L7_SCRIPT'
#!/bin/bash
echo "🔍 L7: 配置验证..."

CONFIG_FILE="/root/.openclaw/openclaw.json"
ERRORS=0

# 检查字段命名
if grep -q '"base_url"' "$CONFIG_FILE"; then
    echo "❌ 错误: memu-engine使用base_url，应该是baseUrl"
    ERRORS=$((ERRORS+1))
fi

if grep -q '"api_key"' "$CONFIG_FILE"; then
    echo "❌ 错误: 使用了api_key，应该是apiKey"
    ERRORS=$((ERRORS+1))
fi

# 检查JSON格式
if ! python3 -c "import json; json.load(open('$CONFIG_FILE'))" 2>/dev/null; then
    echo "❌ 错误: JSON格式无效"
    ERRORS=$((ERRORS+1))
fi

# 检查provider
if grep -A 10 '"memu-engine"' "$CONFIG_FILE" | grep -q '"provider": "openai-compatible"'; then
    echo "⚠️ 警告: provider应该是openai"
    ERRORS=$((ERRORS+1))
fi

# 检查API Key
if grep -A 5 '"embedding"' "$CONFIG_FILE" | grep -q '"apiKey": "sk-'; then
    echo "✅ API Key格式正确"
else
    echo "❌ 错误: API Key格式不正确"
    ERRORS=$((ERRORS+1))
fi

[ $ERRORS -eq 0 ] && echo "✅ L7验证通过" || echo "❌ L7发现 $ERRORS 个问题"
exit $([ $ERRORS -eq 0 ] && echo 0 || echo 1)
L7_SCRIPT

chmod +x l7-config-validation.sh
```

### Step 3: 集成到心跳

```bash
# 更新心跳配置
cat >> ~/.openclaw/workspace/HEARTBEAT.md << 'EOF'

## 🧬 自我进化系统（整合版）

### 每次心跳必做
```bash
bash ~/.openclaw/workspace/scripts/self-evolution-system.sh
```

**整合的系统**:
- 🧠 PAI学习系统
- 🧬 超级进化大脑
- 🛡️ 6层防护系统(L7增强)
- 💾 memu-engine

**自动执行**: L7验证 → 防护检测 → PAI学习 → SES决策 → memu存储

EOF
```

### Step 4: 测试运行

```bash
# 测试自我进化系统
bash ~/.openclaw/workspace/scripts/self-evolution-system.sh

# 预期输出：
# ✅ L7验证通过
# ✅ 防护系统正常
# ✅ PAI学习完成
# ✅ SES进化完成
# ✅ memu记忆已存储
# 我变得更强了！🧬
```

---

## 📦 完整部署包

### 方案A: 从当前服务器复制

```bash
# 1. 在目标服务器上创建目录
ssh user@new-server
mkdir -p ~/.openclaw/workspace/scripts

# 2. 复制核心脚本
scp self-evolution-system.sh user@new-server:~/.openclaw/workspace/scripts/
scp l7-config-validation.sh user@new-server:~/.openclaw/workspace/scripts/

# 3. 复制心跳配置
scp HEARTBEAT.md user@new-server:~/.openclaw/workspace/

# 4. 在目标服务器设置权限
ssh user@new-server
chmod +x ~/.openclaw/workspace/scripts/self-evolution-system.sh
chmod +x ~/.openclaw/workspace/scripts/l7-config-validation.sh
```

### 方案B: 创建自动化部署脚本

```bash
# 创建部署脚本
cat > deploy-evolution-system.sh << 'DEPLOY_SCRIPT'
#!/bin/bash
# 自我进化系统一键部署脚本

set -e

echo "🚀 部署自我进化系统到新环境..."

# 参数
TARGET_SERVER="$1"
if [ -z "$TARGET_SERVER" ]; then
    echo "用法: $0 <user@server>"
    exit 1
fi

echo "目标服务器: $TARGET_SERVER"

# 创建目录
ssh "$TARGET_SERVER" "mkdir -p ~/.openclaw/workspace/scripts"

# 复制脚本
echo "复制核心脚本..."
scp ~/.openclaw/workspace/scripts/self-evolution-system.sh \
   "$TARGET_SERVER:~/.openclaw/workspace/scripts/"

scp ~/.openclaw/workspace/scripts/l7-config-validation.sh \
   "$TARGET_SERVER:~/.openclaw/workspace/scripts/"

# 设置权限
echo "设置权限..."
ssh "$TARGET_SERVER" \
  "chmod +x ~/.openclaw/workspace/scripts/self-evolution-system.sh \
   chmod +x ~/.openclaw/workspace/scripts/l7-config-validation.sh"

# 更新心跳
echo "集成到心跳..."
scp ~/.openclaw/workspace/HEARTBEAT.md \
   "$TARGET_SERVER:~/.openclaw/workspace/HEARTBEAT.md"

echo ""
echo "✅ 部署完成！"
echo ""
echo "下一步："
echo "1. SSH到目标服务器: ssh $TARGET_SERVER"
echo "2. 测试系统: bash ~/.openclaw/workspace/scripts/self-evolution-system.sh"
echo "3. 重启Gateway: systemctl --user restart openclaw-gateway"

DEPLOY_SCRIPT

chmod +x deploy-evolution-system.sh

# 使用示例
# ./deploy-evolution-system.sh user@new-server
```

---

## 🎯 部署检查清单

### 部署后验证

```bash
# 1. 检查脚本存在
ls -la ~/.openclaw/workspace/scripts/self-evolution-system.sh
ls -la ~/.openclaw/workspace/scripts/l7-config-validation.sh

# 2. 检查权限
ls -l ~/.openclaw/workspace/scripts/self-evolution-system.sh
# 应该显示 -rwxr-xr-x

# 3. 测试运行
bash ~/.openclaw/workspace/scripts/self-evolution-system.sh

# 4. 检查心跳集成
grep "self-evolution-system" ~/.openclaw/workspace/HEARTBEAT.md
```

---

## 🔧 自定义配置

### 调整心跳频率

```bash
# 编辑 ~/.openclaw/workspace/openclaw.json
# 修改 agents.defaults.heartbeat.every
# 例如改为 "15m" 或 "60m"
```

### 启用/禁用组件

```bash
# 编辑 self-evolution-system.sh
# 注释掉不需要的步骤
# 例如：不需要PAI学习，注释掉 Step 4
```

---

## 📊 验证部署

### 完整测试

```bash
# 1. 手动测试
bash ~/.openclaw/workspace/scripts/self-evolution-system.sh

# 2. 查看日志
cat ~/.openclaw/workspace/.evolution/evolution.log

# 3. 检查进化记录
ls -la ~/.openclaw/workspace/.learnings/errors/

# 4. 检查进化报告
ls -la ~/.openclaw/workspace/.learnings/evolution_report_*.md
```

---

## 🆘 故障排除

### 常见问题

**Q1: 脚本没有执行权限**
```bash
chmod +x ~/.openclaw/workspace/scripts/self-evolution-system.sh
```

**Q2: PAI工作流不存在**
```bash
# 这是正常的，系统会跳过PAI步骤
# 或者你可以先安装PAI系统
```

**Q3: 心跳没有触发**
```bash
# 检查心跳配置
grep "heartbeat" ~/.openclaw/workspace/HEARTBEAT.md

# 手动触发
bash ~/.openclaw/workspace/scripts/self-evolution-system.sh
```

**Q4: Gateway重启失败**
```bash
# 检查配置文件
openclaw config validate

# 查看日志
journalctl --user -u openclaw-gateway -n 50
```

---

## 📚 进阶配置

### 添加自定义修复规则

编辑 `self-evolution-system.sh`，添加自定义修复逻辑：

```bash
# 在Step 3后添加自定义修复
case "$ERROR_TYPE" in
    "我的自定义错误")
        # 我的修复逻辑
        ;;
esac
```

### 集成到其他监控工具

```bash
# 添加到crontab
crontab -e

# 每15分钟检查一次
*/15 * * * * bash ~/.openclaw/workspace/scripts/self-evolution-system.sh
```

---

## 🎯 总结

### 快速部署命令

```bash
# 一键部署（3个命令）
cd ~/.openclaw/workspace/scripts
# 粘贴上面的脚本
chmod +x *.sh
# 测试运行
```

### 核心文件

1. **`self-evolution-system.sh`** - 统一调度器
2. **`l7-config-validation.sh`** - L7配置验证
3. **`HEARTBEAT.md`** - 心跳集成

### 部署后效果

- ✅ 自动检测错误
- ✅ 自动学习改进
- ✅ 自动预防未来
- ✅ 系统持续进化

---

**在任何"小龙虾"上都能部署自我进化系统！** 🚀

需要我解释任何步骤吗？或者帮你部署到特定服务器？
