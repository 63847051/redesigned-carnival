# 🚀 自我进化系统 v1.0 - 部署和配置指南

**适用场景**: 在新环境或其他服务器上部署自我进化系统

---

## 📋 两种部署方式

### 方式 1: 创建为 Skill（推荐）⭐

**优点**:
- ✅ 可以通过 ClawHub 分享
- ✅ 可以在任何 OpenClaw 环境安装
- ✅ 版本管理方便
- ✅ 更新简单

**实施步骤**:

#### Step 1: 创建 Skill 结构

```bash
# 1. 创建 Skill 目录
mkdir -p ~/.openclaw/skills/self-evolution-system
cd ~/.openclaw/skills/self-evolution-system

# 2. 创建 SKILL.md
cat > SKILL.md << 'EOF'
# 🧬 自我进化系统 v1.0 (Self-Evolution System)

## 简介

完整的自我进化系统，整合 PAI 学习、超级进化大脑、6 层防护和 memu-engine，实现自动错误学习、修复和预防。

## 功能

- 🧠 PAI 深度学习：从错误中提取知识
- 🛡️ 7 层防护系统：预防、检测、修复
- 🔄 自动进化引擎：生成和部署修复
- 💾 统一记忆系统：长期知识积累

## 使用

### 自动模式（推荐）
```bash
# 通过心跳自动运行
# 无需手动干预
```

### 手动模式
```bash
# 触发完整进化流程
evolution-orchestrator.sh --full-evolution

# 只验证配置
evolution-orchestrator.sh --validate-only

# 查看系统状态
evolution-orchestrator.sh --status
```

## 配置

编辑 `~/.openclaw/skills/self-evolution-system/CONFIG.md`

## 依赖

- OpenClaw >= 2026.2.26
- memu-engine 插件
- Bash 4.0+
- Python 3.8+ (可选)

## 文档

完整文档：`docs/self-evolution-system-v1.md`
EOF

# 3. 创建目录结构
mkdir -p {scripts,docs,.evolution-system}
```

#### Step 2: 复制核心脚本

```bash
# 复制核心组件
cp /root/.openclaw/workspace/scripts/evolution-orchestrator.sh ~/.openclaw/skills/self-evolution-system/scripts/
cp /root/.openclaw/workspace/scripts/l7-config-validation.sh ~/.openclaw/skills/self-evolution-system/scripts/
cp /root/.openclaw/workspace/scripts/pai-workflow.sh ~/.openclaw/skills/self-evolution-system/scripts/
cp /root/.openclaw/workspace/scripts/heartbeat-evolution.sh ~/.openclaw/skills/self-evolution-system/scripts/

# 复制文档
cp /root/.openclaw/workspace/docs/self-evolution-system-v1.md ~/.openclaw/skills/self-evolution-system/docs/
cp /root/.openclaw/workspace/docs/self-evolution-validation-report.md ~/.openclaw/skills/self-evolution-system/docs/

# 复制配置
cp /root/.openclaw/workspace/SOUL.md ~/.openclaw/skills/self-evolution-system/.evolution-system/
```

#### Step 3: 创建安装脚本

```bash
cat > ~/.openclaw/skills/self-evolution-system/scripts/install.sh << 'EOF'
#!/bin/bash
# 自我进化系统安装脚本

set -e

INSTALL_DIR="$HOME/.openclaw/skills/self-evolution-system"
WORKSPACE="$HOME/.openclaw/workspace"

echo "🧬 安装自我进化系统 v1.0..."
echo ""

# 1. 创建工作区目录
mkdir -p "$WORKSPACE/.pai-learning"
mkdir -p "$WORKSPACE/.learnings/errors"
mkdir -p "$WORKSPACE/.learnings/design-patterns"
mkdir -p "$WORKSPACE/.learnings/best-practices"
mkdir -p "$WORKSPACE/.evolution-system"

# 2. 复制配置
if [ ! -f "$WORKSPACE/SOUL.md" ]; then
    cp "$INSTALL_DIR/.evolution-system/SOUL.md" "$WORKSPACE/SOUL.md"
    echo "✅ SOUL.md 已创建"
fi

# 3. 设置权限
chmod +x "$INSTALL_DIR/scripts"/*.sh

# 4. 集成到心跳
if ! grep -q "evolution-orchestrator" "$WORKSPACE/HEARTBEAT.md" 2>/dev/null; then
    echo "" >> "$WORKSPACE/HEARTBEAT.md"
    echo "## 🧬 自我进化系统" >> "$WORKSPACE/HEARTBEAT.md"
    echo "bash ~/.openclaw/skills/self-evolution-system/scripts/heartbeat-integration.sh" >> "$WORKSPACE/HEARTBEAT.md"
    echo "✅ 已集成到心跳"
fi

echo ""
echo "✅ 安装完成！"
echo ""
echo "下一步："
echo "1. 编辑配置: vim ~/.openclaw/skills/self-evolution-system/CONFIG.md"
echo "2. 测试系统: bash ~/.openclaw/skills/self-evolution-system/scripts/evolution-orchestrator.sh --test"
echo "3. 启动监控: bash ~/.openclaw/skills/self-evolution-system/scripts/heartbeat-integration.sh"
EOF

chmod +x ~/.openclaw/skills/self-evolution-system/scripts/install.sh
```

#### Step 4: 创建配置文件

```bash
cat > ~/.openclaw/skills/self-evolution-system/CONFIG.md << 'EOF'
# 🧬 自我进化系统配置

## 启用功能

enabled_components:
  pai_learning: true
  super_evolution: true
  protection_system: true
  memu_integration: true
  auto_repair: false  # 谨慎启用

## 进化参数

learning:
  auto_capture: true
  analysis_depth: deep
  evolution_speed: medium  # slow | medium | fast

protection:
  layers: 7  # 使用 7 层防护
  auto_fix: false  # 自动修复（谨慎）
  alert_on_error: true

memory:
  store_in_memu: true
  store_in_pai: true
  retention_days: 90

## 自动化

automation:
  heartbeat_integration: true
  cron_schedule: "*/30 * * * *"  # 每 30 分钟
  auto_deploy: false  # 自动部署（谨慎）

## 高级设置

advanced:
  evolution_orchestration: true
  parallel_analysis: false
  max_concurrent_fixes: 1
  rollback_on_failure: true
EOF
```

#### Step 5: 注册 Skill

```bash
# 编辑 openclaw.json
openclaw config edit

# 添加到 skills.load.paths
{
  "skills": {
    "load": {
      "paths": [
        "~/.openclaw/skills/self-evolution-system"
      ]
    }
  }
}
```

#### Step 6: 重启 Gateway

```bash
openclaw gateway restart
```

---

### 方式 2: 直接部署到工作区

**适用场景**: 不想创建 Skill，直接在工作区使用

#### Step 1: 复制文件

```bash
# 在目标服务器上
cd ~/.openclaw/workspace

# 创建目录
mkdir -p docs scripts .evolution-system

# 从源服务器复制
scp user@source-server:/root/.openclaw/workspace/docs/self-evolution-*.md docs/
scp user@source-server:/root/.openclaw/workspace/scripts/evolution-*.sh scripts/
scp user@source-server:/root/.openclaw/workspace/scripts/l7-*.sh scripts/
```

#### Step 2: 初始化

```bash
# 运行初始化脚本
bash scripts/evolution-orchestrator.sh --init
```

#### Step 3: 配置心跳

```bash
# 添加到 HEARTBEAT.md
echo "" >> HEARTBEAT.md
echo "## 🧬 自我进化系统" >> HEARTBEAT.md
echo "bash ~/.openclaw/workspace/scripts/evolution-orchestrator.sh --auto" >> HEARTBEAT.md
```

---

## 🔧 配置验证

### 验证安装

```bash
# 运行测试
bash ~/.openclaw/skills/self-evolution-system/scripts/evolution-orchestrator.sh --test
```

**预期输出**:
```
🧬 自我进化系统 v1.0
=====================================

✅ 组件检查:
  ✅ PAI 学习系统: 运行中
  ✅ 超级进化大脑: 运行中
  ✅ 6 层防护系统: 运行中
  ✅ memu-engine: 运行中
  ✅ L7 配置验证: 就绪

✅ 依赖检查:
  ✅ OpenClaw: 2026.2.26
  ✅ Bash: 5.1.0
  ✅ Python: 3.11

✅ 配置检查:
  ✅ 配置文件: 有效
  ✅ 工作区: 可写
  ✅ 日志目录: 可写

🎯 系统就绪！
```

---

## 🌍 分享给其他人

### 发布到 ClawHub

```bash
# 1. 初始化 Git 仓库
cd ~/.openclaw/skills/self-evolution-system
git init
git add .
git commit -m "Initial commit: Self-Evolution System v1.0"

# 2. 推送到 GitHub
git remote add origin https://github.com/YOUR_USERNAME/self-evolution-system.git
git push -u origin main

# 3. 发布到 ClawHub
openclaw skill publish https://github.com/YOUR_USERNAME/self-evolution-system
```

### 其他人安装

```bash
# 任何人都可以安装
openclaw skill install self-evolution-system

# 或从 GitHub 安装
openclaw skill install https://github.com/YOUR_USERNAME/self-evolution-system
```

---

## 📦 完整包结构

### 作为 Skill 发布

```
self-evolution-system/
├── SKILL.md                    # Skill 文档
├── CONFIG.md                   # 配置文件
├── README.md                   # 使用说明
├── install.sh                  # 安装脚本
├── scripts/
│   ├── evolution-orchestrator.sh
│   ├── l7-config-validation.sh
│   ├── pai-workflow.sh
│   ├── heartbeat-integration.sh
│   └── install.sh
├── docs/
│   ├── self-evolution-system-v1.md
│   └── self-evolution-validation-report.md
└── .evolution-system/
    ├── SOUL.md
    └── templates/
        └── ...
```

---

## 🎯 快速部署命令

### 一键安装

```bash
# 从 ClawHub 安装（一旦发布）
openclaw skill install self-evolution-system

# 或从 GitHub 安装
openclaw skill install https://github.com/your-repo/self-evolution-system

# 然后运行安装脚本
bash ~/.openclaw/skills/self-evolution-system/install.sh
```

### 手动安装

```bash
# 克隆仓库
git clone https://github.com/your-repo/self-evolution-system.git ~/.openclaw/skills/self-evolution-system

# 运行安装
cd ~/.openclaw/skills/self-evolution-system
bash install.sh
```

---

## 🔧 自定义配置

### 环境变量

```bash
# ~/.openclaw/skills/self-evolution-system/.env
EVOLUTION_SYSTEM_HOME="$HOME/.openclaw/skills/self-evolution-system"
EVOLUTION_WORKSPACE="$HOME/.openclaw/workspace"
EVOLUTION_AUTO_FIX=false  # 谨慎启用
EVOLUTION_LOG_LEVEL=info  # debug | info | warn | error
```

### 配置文件

```bash
# ~/.openclaw/skills/self-evolution-system/CONFIG.md
# (见上文配置示例)
```

---

## 🚀 启动系统

### 手动启动

```bash
# 完整进化流程
bash ~/.openclaw/skills/self-evolution-system/scripts/evolution-orchestrator.sh --full

# 只监控不修复
bash ~/.openclaw/skills/self-evolution-system/scripts/evolution-orchestrator.sh --monitor-only

# 一次性验证
bash ~/.openclaw/skills/self-evolution-system/scripts/evolution-orchestrator.sh --validate
```

### 自动启动（推荐）

```bash
# 添加到心跳
echo "bash ~/.openclaw/skills/self-evolution-system/scripts/heartbeat-integration.sh" >> ~/.openclaw/workspace/HEARTBEAT.md

# 或添加到 cron
crontab -e

# 添加行：
*/30 * * * * bash ~/.openclaw/skills/self-evolution-system/scripts/evolution-orchestrator.sh --auto >> /var/log/evolution.log 2>&1
```

---

## 📊 监控和维护

### 查看状态

```bash
# 系统状态
bash ~/.openclaw/skills/self-evolution-system/scripts/evolution-orchestrator.sh --status

# 查看日志
tail -f ~/.openclaw/workspace/.evolution-system/evolution.log

# 查看进化统计
bash ~/.openclaw/skills/self-evolution-system/scripts/evolution-orchestrator.sh --stats
```

### 更新系统

```bash
# 更新 Skill
openclaw skill update self-evolution-system

# 或手动更新
cd ~/.openclaw/skills/self-evolution-system
git pull origin main
bash install.sh
```

---

## 💡 最佳实践

1. **首次使用**: 先用 `--monitor-only` 模式观察
2. **生产环境**: 禁用 `auto_fix`，保持人工监督
3. **测试环境**: 可以启用 `auto_fix` 进行实验
4. **定期检查**: 每周查看进化报告
5. **备份配置**: 定期备份 `.evolution-system/` 目录

---

## 🆘 故障排除

### 常见问题

**Q: 安装后无法使用？**
```bash
# 检查权限
ls -la ~/.openclaw/skills/self-evolution-system/scripts/
chmod +x ~/.openclaw/skills/self-evolution-system/scripts/*.sh
```

**Q: 心跳没有触发？**
```bash
# 检查 HEARTBEAT.md
cat ~/.openclaw/workspace/HEARTBEAT.md | grep evolution
```

**Q: 配置不生效？**
```bash
# 验证配置
bash ~/.openclaw/skills/self-evolution-system/scripts/evolution-orchestrator.sh --validate-config
```

---

## 📞 支持

- 文档：`docs/self-evolution-system-v1.md`
- 问题反馈：GitHub Issues
- 讨论：OpenClaw Discord

---

*最后更新: 2026-03-08*
*版本: v1.0*
*状态: ✅ 可部署*
