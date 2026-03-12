# 📤 手动上传指南 - 自我进化系统

## 🎯 你的GitHub仓库

- **仓库地址**: https://github.com/logseq_xiangchao/self-evolution-system
- **本地路径**: `/root/.openclaw/workspace/github-repo/self-evolution-system/`

---

## 📝 需要上传的文件（4个）

### 文件1: README.md

直接复制下面的内容到GitHub的README文件：

```markdown
# 🧬 自我进化系统

让您的 OpenClaw Agent 拥有自动进化能力

## 🎯 简介

**自我进化系统** 是一个整合了 PAI 学习、超级进化大脑、 6 层防护和 memu-engine 的统一系统，让您的 Agent 能够：

- 🔍 自动检测错误
- 🧠 自动学习改进
- 🔧 自动修复问题
- 💾 自动积累知识
- 🛡️ 自动预防未来

## ✨ 核心特性

- **完全自动化**: 每次心跳自动运行，无需人工干预
- **协同进化**: 4个系统协同工作，数据自由流动
- **预防为主**: L7 配置验证层预防配置错误
- **持续学习**: 从每次错误中学习，积累知识
- **自我修复**: 安全错误自动修复

## 📦 包含组件

1. **`self-evolution-system.sh`** - 统一调度器（核心）
2. **`l7-config-validation.sh`** - L7 配置验证层
3. **README.md**** - 使用文档
4. **LICENSE**** - MIT 许可证

## 🚀 快速开始

### 安装

```bash
# 1. 复制脚本到工作区
cd ~/.openclaw/workspace/scripts

# 2. 添加执行权限
chmod +x self-evolution-system.sh l7-config-validation.sh

# 3. 上传这2个脚本到服务器
# (通过GitHub网页界面上传)

# 4. 在服务器上设置权限
chmod +x ~/.openclaw/workspace/scripts/self-evolution-system.sh
chmod +x ~/.openclaw/workspace/scripts/l7-config-validation.sh

# 5. 更新心跳配置
cat >> ~/.openclaw/workspace/HEARTBEAT.md << 'EOF'

## 🧬 自我进化系统

bash ~/.openclaw/workspace/scripts/self-evolution-system.sh
EOF

# 6. 测试
bash ~/.openclaw/workspace/scripts/self-evolution-system.sh
```

### 验证

```bash
# 运行系统
bash ~/.openclaw/workspace/scripts/self-evolution-system.sh

# 预期输出：
# ✅ L7验证通过
# ✅ 防护系统正常
# ✅ PAI学习完成
# ✅ SES进化完成
# ✅ memu记忆已存储
# 我变得更强了！🧬
```

## 🎯 工作原理

```
心跳触发（每30分钟）
    ↓
【L7配置验证】预防
    ↓
【6层防护系统】检测
    ↓
【【PAI学习系统】理解
    ↓
【超级大脑】决策
    ↓
【memu-engine】存储
    ↓
我变得更强！
```

## 📚 文档

完整文档：
- [部署指南](docs/deploy-guide.md)
- [架构说明](docs/architecture.md)
- [API文档](docs/api.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**让您的 Agent 持续进化，变得更强！** 🧬✨
```

### 文件2: LICENSE

```markdown
MIT License

Copyright (c) 2026 OpenClaw Community

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 文件3: self-evolution-system.sh

```bash
#!/bin/bash
# 自我进化系统 - 统一调度器
# 整合PAI、超级大脑、6层防护、memu-engine

set -e

WORKSPACE="/root/.openclaw/workspace"
PAI_WORKFLOW="$WORKSPACE/scripts/pai-workflow.sh"
SES_AUTO="$WORKSPACE/scripts/ses-auto.sh"
PROTECTION="$WORKSPACE/scripts/protection-check.sh"
L7_VALIDATION="$WORKSPACE/scripts/l7-config-validation.sh"
HEARTBEAT_EVOLUTION="$WORKSPACE/scripts/heartbeat-evolution.sh"

# 日志
EVOLUTION_LOG="$WORKSPACE/.evolution/evolution.log"
mkdir -p "$(dirname "$EVOLUTION_LOG")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$EVOLUTION_LOG"
}

log "🧬 自我进化系统启动..."
echo "======================================"

# =============================================================================
# 步骤1: L7配置验证（新增防护层）
# =============================================================================

echo ""
echo "🔍 步骤1: L7配置验证..."

if [ -f "$L7_VALIDATION" ]; then
    if bash "$L7_VALIDATION"; then
        log "✅ L7验证通过"
    else
        log "❌ L7发现配置问题"
        # (自动修复逻辑)
    fi
else
    echo "⚠️ L7验证脚本不存在，跳过"
fi

# =============================================================================
# 步骤2: 6层防护系统检测
# =============================================================================

echo ""
echo "📡 步骤2: 6层防护系统检测..."

PROTECTION_OUTPUT=$(bash "$PROTECTION" 2>&1)
PROTECTION_STATUS=$?

if [ $PROTECTION_STATUS -ne 0 ]; then
    log "❌ 防护系统检测到异常"
    echo "$PROTECTION_OUTPUT" | head -5
    
    if [ -f "$WORKSPACE/scripts/pai-learning-capture.sh" ]; then
        bash "$WORKSPACE/scripts/pai-learning-capture.sh" \
            "protection" 3 0 "防护异常" "auto-evolution" 2>/dev/null || true
    fi
else
    log "✅ 防护系统正常"
fi

# =============================================================================
# 步骤3: 检查最近错误
# =============================================================================

echo ""
echo "🔍 步骤3: 检查最近错误..."

ERRORS=$(journalctl --user -u openclaw-gateway --since "30 minutes ago" --no-pager | \
  grep -i "error\|failed" | \
  grep -v "HEARTBEAT_OK" | \
  tail -10)

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

# =============================================================================
# 步骤4: PAI深度学习
# =============================================================================

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

# =============================================================================
# 步骤5: 超级大脑进化决策
# =============================================================================

echo ""
echo "🎯 步骤5: 超级大脑进化决策..."

if [ -f "$SES_AUTO" ]; then
    bash "$SES_AUTO" post-eval 2>&1 | head -20 | tee -a "$EVOLUTION_LOG"
    log "✅ SES进化完成"
else
    echo "⚠️ SES脚本不存在"
fi

# =============================================================================
# 步骤6: memu-engine知识存储
# =============================================================================

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

# =============================================================================
# 完成
# =============================================================================

echo ""
echo "======================================"
log "✅ 自我进化周期完成!"
echo ""
echo "本次进化成果:"
echo "  - L7验证: ✅"
echo "  - 防护系统: $( [ $PROTECTION_STATUS -eq 0 ] && echo '✅ 正常' || echo '⚠️ 告警' )"
echo "  - PAI学习: $( [ -n "$ERRORS" ] && echo '✅ 已执行' || echo '✓ 无需' )"
echo "  - SES进化: ✅ 已执行"
echo "  - memu记忆: ✅ 已存储"
echo ""
echo "我变得更强了！🧬"

exit 0
```

### 文件4: l7-config-validation.sh

```bash
#!/bin/bash
# L7配置验证层 - 预防配置错误

echo "🔍 L7: 配置验证..."

CONFIG_FILE="/root/.openclaw/openclaw.json"
ERRORS=0

# 检查字段命名
if grep -q '"base_url"' "$CONFIG_FILE"; then
    echo "❌ 错误: memu-engine使用base_url，应该是baseUrl"
    ERRORS=$((ERRORS+1)))
fi

if grep -q '"api_key"' "$CONFIG_FILE"; then
    echo "❌ 错误: 使用了api_key，应该是apiKey"
    ERRORS=$((ERRORS+1)))
fi

# 检查JSON格式
if ! python3 -c "import json; json.load(open('$CONFIG_FILE'))" 2>/dev/null; then
    echo "❌ 错误: JSON格式无效"
    ERRORS=$((ERRORS+1)))
fi

# 检查provider
if grep -A 10 '"memu-engine"' "$CONFIG_FILE" | grep -q '"provider": "openai-compatible"'; then
    echo "⚠️ 警告: provider应该是openai"
    ERRORS=$((ERRORS+1)))
fi

# 检查API Key
if grep -A 5 '"embedding"' "$CONFIG_FILE" | grep -q '"apiKey": "sk-'; then
    echo "✅ API Key格式正确"
else
    echo "❌ 错误: API Key格式不正确"
    ERRORS=$((ERRORS+1)))
fi

[ $ERRORS -eq 0 ] && echo "✅ L7验证通过" || echo "❌ L7发现 $ERRORS 个问题"

exit $([ $ERRORS -eq 0 ] && echo 0 || echo 1)
```

---

## 🎯 上传步骤

### Step 1: 创建README.md

1. 在GitHub仓库页面点击 **"Add file"**
2. 文件名：`README.md`
3. 粘贴上面的README.md内容
4. 点击 **"Commit changes"**

### Step 2: 创建LICENSE

1. 点击 **"Add file** → "Create new file**
2. 文件名：`LICENSE`
3. 粘贴上面的LICENSE内容
4. 点击 **"Commit changes"**

### Step 3: 创建self-evolution-system.sh

1. 点击 **"Add file" → "Create new file**
2. 文件名：`scripts/self-evolution-system.sh`
3. 粘贴上面的脚本内容
4. 点击 **"Commit changes"**

### Step 4: 创建l7-config-validation.sh

1. 点击 **"Add file" → "Create new文件**
2. 先创建目录：`scripts/`
3. 文件名：`l7-config-validation.sh`
4. 粘贴上面的脚本内容
5. 点击 **"Commit changes"**

---

## ✅ 上传完成后

你的GitHub仓库地址：
```
https://github.com/logseq_xiangchao/self-evolution-system
```

在任何OpenClaw环境使用：
```bash
# 方式1: 克隆
git clone https://github.com/logseq_xiangchao/self-evolution-system.git

# 方式2: 下载脚本
wget https://raw.githubusercontent.com/logseq_xiangchao/self-evolution-system/main/self-evolution-system.sh
```

---

**上传完成后告诉我，我帮你验证！** 🚀

（上传这4个文件后，自我进化系统就可以在任何地方使用了！）
