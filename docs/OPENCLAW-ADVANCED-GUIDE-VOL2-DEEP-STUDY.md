# OpenClaw 进阶手册 Vol.2 深度学习

**创建时间**: 2026-04-04 21:25
**文章**: 《OpenClaw 进阶手册 Vol.2：让它真的自己跑起来》
**来源**: 微信公众号 - 请致天下.AI
**字数**: 11,850 字符
**状态**: ✅ 完整学习

---

## 🎯 文章概览

### 核心价值
**30 个技巧，7 个主题**，从基础到进阶的完整指南

### 目标读者
- ✅ 读完 Vol.1 的用户
- ✅ 想让 Agent 自己跑的用户
- ✅ 关注生产安全的用户
- ✅ 需要多 Agent 协作的用户

---

## 📚 七大主题

### 第一章：自动触发（01-05）

#### Tip 01: Cron 的正确写法 ⭐⭐⭐

**两个常踩的坑**:

1. **时区问题**
   ```yaml
   schedule: "0 9 * * 1-5"  # UTC 时间早 9 点
   timezone: "Asia/Shanghai"  # ✅ 加上这个
   ```

2. **proactive-agent vs Cron**
   - proactive-agent: 对话里自主触发
   - Cron: 系统级定时（无对话也跑）
   - 可以同时用

**示例配置**:
```yaml
cron:
  jobs:
    - schedule: "0 9 * * 1-5"
      timezone: "Asia/Shanghai"
      task: "生成今日工作简报，汇总昨天的 GitHub PR 和 Jira 变更"
      model: "anthropic/claude-sonnet-4-6"
    - schedule: "0 17 * * 5"
      timezone: "Asia/Shanghai"
      task: "生成本周总结，输出到 Notion"
      model: "anthropic/claude-opus-4-6"
```

#### Tip 02: Webhook 唤醒 Agent ⭐⭐⭐

**两个端点**:

1. **简单唤醒** - `/hooks/wake`
   ```bash
   curl -X POST https://your-gateway/hooks/wake \
     -H "x-openclaw-token: your-token"
   ```

2. **完整触发** - `/hooks/agent`
   ```bash
   curl -X POST https://your-gateway/hooks/agent \
     -H "x-openclaw-token: your-token" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "GitHub PR #142 刚合并，请生成 code review 摘要",
       "model": "anthropic/claude-sonnet-4-6",
       "deliverTo": "telegram"
     }'
   ```

**应用场景**: PR 合并自动 code review

#### Tip 03: Gmail Pub/Sub ⭐⭐

**一键向导**:
```bash
openclaw webhooks gmail setup
```

**工作流程**:
```
邮件到达 → Pub/Sub 推送 → OpenClaw webhook → Agent 处理 → 推送 Telegram
```

**需要**: Tailscale Funnel 提供公网 HTTPS

#### Tip 04: Browser Control ⭐⭐⭐

**配置**:
```yaml
browser:
  enabled: true
  color: "#FF4500"
```

**可用操作**:
- `browser_snapshot` - 截取页面结构
- `browser_navigate` - 跳转到 URL
- `browser_click` - 点击元素
- `browser_fill` - 填写表单
- `browser_type` - 追加文字

**用途**:
- 抓取需要登录的网页
- 自动填报销单
- 定期截图竞品页面

**特点**: 不是无头浏览器，有界面

#### Tip 05: Webhook Token ⭐⭐⭐

**正确生成**:
```bash
openssl rand -hex 32
# 输出: a3f8b2c1d4e5...（64位十六进制）
```

**错误生成**:
```bash
"my-secret-token-2026"  # ❌ 不要这样
```

**两件事不要做**:
1. ❌ 把带 token 的 webhook URL 发进群聊
2. ❌ 在日志里打印 token

---

### 第二章：多频道管理（06-10）

#### Tip 06: DM Pairing 默认值变化 ⭐⭐⭐

**2026.1 之前**: `dmPolicy: open`（开放）
**2026.1 之后**: `dmPolicy: pairing`（配对）

**查看配对请求**:
```bash
openclaw pairing list
```

**批准用户**:
```bash
openclaw pairing approve telegram abc123
```

**恢复开放模式**:
```yaml
channels:
  telegram:
    dmPolicy: open
    allowFrom: ["*"]
```

⚠️ **不推荐这样做**（除非你清楚风险）

#### Tip 07: 群组路由：默认拒绝 ⭐⭐⭐

**配置**:
```yaml
channels:
  telegram:
    groups:
      "-1001234567890":
        requireMention: true
      "*": false
```

**关键**: `requireMention: true`
- 防止 Bot 响应所有消息
- 避免被当做刷量机器人举报

#### Tip 08: 一个 Gateway 管所有频道 ⭐⭐

**配置**:
```yaml
channels:
  telegram:
    botToken: "..."
    allowFrom: ["your_telegram_id"]
  slack:
    botToken: "xoxb-..."
    appToken: "xapp-..."
```

**特点**:
- 同一条指令发到任意频道都处理
- 结果默认回到发消息的频道
- 可以用 `deliverTo` 指定送到别的地方

#### Tip 09: sessions_send vs sessions_spawn ⭐⭐⭐

| | sessions_spawn | sessions_send |
|----------------|----------------|---------------|
| 场景 | 下发任务，等结果 | 向另一个 Agent 发消息 |
| 同步 | 异步，spawn 后不等 | 可以等对方回复 |
| 默认开关 | 默认开启 | 默认关闭，需要配置 |

**开启 sessions_send**:
```yaml
agents:
  agentToAgent: true
```

**用途**: 前台 Agent（对话）+ 后台 Agent（数据处理）

#### Tip 10: openclaw doctor ⭐⭐⭐

**每次改完配置，跑一遍**:
```bash
openclaw doctor
```

**检查内容**:
- DM 策略是否有暴露风险
- Gateway token 强度
- allowFrom 是否过于宽松
- 频道连接状态
- 常见配置冲突

**经典场景**: `dmPolicy` 改成 `pairing`，但 `allowFrom` 还是 `["*"]`

---

### 第三章：Agent 间通信（11-14）

#### Tip 11: sessions_list + sessions_history ⭐⭐⭐

**查看所有活跃 session**:
```python
sessions_list()
# 返回: session ID、label、状态、开始时间、模型
```

**查看完整对话记录**:
```python
sessions_history(session_id="q4-sales-analysis-2026")
# 返回: 完整 transcript
```

**用途**:
- `sessions_list` ≈ `ps aux`
- `sessions_history` ≈ `tail -f logfile`

#### Tip 12: 三种拓扑架构 ⭐⭐⭐

**星型（Fan-Out）**:
- 主 Agent 分发，子 Agent 并行独立跑
- 互不通信
- 适合任务之间没有依赖关系

**流水线**:
```
A → B → C
```
- 用 `sessions_send` 实现
- 适合顺序依赖的任务（研究→分析→撰写）

**广播**:
- 主 Agent 把同一个消息发给多个专项 Agent
- 用多个 `sessions_spawn` 或 `sessions_send`
- 适合「通知型」场景

#### Tip 13: A2A Secure（实验性）⚠️

**功能**:
- Agent 间 Ed25519 签名认证
- Trust Registry 管理信任
- Dead Letter Queue 保障投递

**状态**: 实验性，API 随时可能变
**建议**: 实验环境可以了解，生产环境等 stable release

#### Tip 14: 画拓扑图 ⭐⭐⭐

**示例**:
```
用户(Telegram)
  ↓
前台 Agent (sessions_send ←→ 后台 Agent)
  ├── sessions_spawn → 数据采集子 Agent
  ├── sessions_spawn → 分析子 Agent
  └── sessions_spawn → 生成子 Agent
  ↓
结果回 Telegram
```

**原则**: 画出来再写代码（30分钟 vs 调试2天）

---

### 第四章：远程部署与生产安全（15-20）

#### Tip 15: 不要在主力机跑 Gateway ⭐⭐⭐

**原因**: 主力机有代码、文档、密码、SSH key

**专用部署选项**:
- Mac Mini（闲置的那台）
- Raspberry Pi 5（€3.79/月，ARM，够用）
- Hetzner VPS（CAX11，€3.79/月，ARM，够用）
- DigitalOcean Droplet（$4/月起）

**本地运行**: 至少锁定 bind 地址
```yaml
gateway:
  bind: "127.0.0.1"  # 只监听本地回环
```

#### Tip 16: Tailscale 安全访问 ⭐⭐⭐

**serve 模式**（日常使用）:
```yaml
gateway:
  bind: loopback
  tailscale:
    mode: serve  # 只有 tailnet 设备能访问
```

**funnel 模式**（公网访问）:
```yaml
gateway:
  auth:
    mode: password
  tailscale:
    mode: funnel  # 必须开密码保护
```

**特点**:
- TLS 证书自动管理
- 不需要 Let's Encrypt

#### Tip 17: Docker Sandbox 隔离 ⭐⭐⭐

**必做项**（ClawHavoc 事件之后）:
```yaml
agents:
  defaults:
    sandbox:
      mode: non-main  # 群组消息在容器中
```

**含义**:
- main session（直接对话）: 不隔离
- 群组、频道、webhook: 独立 Docker 容器

**作用**: 恶意 Skill 只能影响容器，碰不到宿主机

#### Tip 18: Gateway Token 保护 ⭐⭐⭐

**生成**:
```bash
openssl rand -hex 32
```

**配置**:
```yaml
gateway:
  token: "你生成的64位token"
```

**不要放在**:
- ❌ 代码里（用环境变量替代）
- ❌ 群聊截图里
- ❌ 公开的 GitHub 仓库里

#### Tip 19: openclaw security audit ⭐⭐⭐

**基础审计**:
```bash
openclaw security audit
```

**深度审计**:
```bash
openclaw security audit --deep
```

**检查问题**:
- Gateway 绑在 0.0.0.0
- token 太弱
- allowFrom 过宽
- 浏览器控制暴露在公网
- 文件系统权限过松

**频率**: 上线前跑，升级后也跑

#### Tip 20: 升级策略 ⭐⭐⭐

**查看当前版本**:
```bash
openclaw --version
```

**升级到 stable 最新**:
```bash
openclaw update --channel stable
```

**升级前备份（重要！）**:
```bash
cp -r ~/.openclaw ~/.openclaw-backup.$(date +%Y%m%d)/
```

**按版本逐步升**，每次跑 `openclaw doctor`

---

### 第五章：Voice + Canvas（21-24）

#### Tip 21: Voice Wake ⭐⭐

**配置**:
```yaml
voice:
  wake:
    enabled: true
    phrase: "hey openclaw"
```

**特点**:
- macOS: 菜单栏 App 后台监听
- 语音处理优先在本地（隐私保护）
- iOS/Android: 通过 Companion Node

**场景**: 开车问路、做饭查菜谱、走路记事项

#### Tip 22: Talk Mode ⭐⭐

**配置**:
```yaml
voice:
  talk:
    enabled: true
```

**特点**:
- 用 ElevenLabs 做语音合成
- 可以说话打断
- 需要 ElevenLabs API Key（额外费用）
- 不适合长文本（800字读出来体验差）

**建议**: 在 SOUL.md 里加上「语音模式下回复控制在 3 句以内」

#### Tip 23: Canvas + A2UI ⭐⭐⭐

**Canvas 操作**:
- `canvas.navigate` - 跳转到指定内容
- `canvas.eval` - 执行 JavaScript
- `canvas.snapshot` - 截图当前状态

**A2UI（Abstract to UI）**:
- 基于 Canvas 的抽象层
- 生成动态表单、图表、交互界面
- 不需要写前端代码

**用途**: 项目状态仪表盘、对比图表

#### Tip 24: Companion 节点 ⭐⭐⭐

**架构**:
- Gateway: 远程 Linux 服务器（推理）
- 节点: macOS/iOS/Android（感知和输出）

**macOS 节点提供**:
- `system.run` - 执行命令
- `system.notify` - 发送通知
- `camera.snap` - 拍照
- `screen.record` - 截屏

**iOS 节点提供**:
- Canvas 渲染
- 语音（麦克风 + 扬声器）
- 摄像头

**示例**: 手机上说「帮我看看桌上这张纸写的什么」→ iOS 节点拍照 → 模型识别 → 结果回 Telegram

---

### 第六章：ECC 深度功能（25-28）

#### Tip 25: contexts/ 目录 ⭐⭐⭐

**三个文件**:
- `contexts/dev.md` - 开发模式（代码质量 + 测试）
- `contexts/review.md` - 审查模式（批判性分析）
- `contexts/research.md` - 研究模式（全面探索）

**使用**:
```markdown
# CLAUDE.md
Current mode: development
@contexts/dev.md
```

**作用**: 切换 AI 的「心态」，不用每次重新说明

#### Tip 26: Memory Persistence Hooks ⭐⭐⭐

**功能**:
- SessionStart hook: 自动加载 `~/.claude/projects/<project-hash>/memory.md`
- SessionEnd hook: 提取决策和模式，追加进 memory 文件

**作用**: 下次打开同一个项目，AI 记得上次定的架构决策、踩过的坑

**特点**: ECC 安装完自动开启

#### Tip 27: Continuous Learning v2 ⭐⭐⭐⭐⭐

**查看学到了什么**:
```bash
/instinct-status
```

**输出示例**:
```
✓ [0.92] 这个项目用 pnpm，不用 npm
✓ [0.87] 数据库列名用 snake_case
? [0.61] 偏好函数式写法（置信度偏低，仍在学习）
```

**三个命令**:
```bash
/instinct-status    # 查看学到了什么
/instinct-export    # 导出成文件分享
/instinct-evolve    # 智能聚类，生成 Skill
```

**价值**: 一个人踩过的坑，导出后发给团队，所有人都规避了

#### Tip 28: Verification Loops ⭐⭐⭐

**两种模式**:

1. **checkpoint-based**（线性任务）
   - 定期打快照
   - 发现偏差立即回滚
   - 适合大文件重构

2. **continuous**（探索性任务）
   - 持续评估输出质量
   - 适合探索性任务

**使用**:
```bash
# 开始重构之前，打一个 checkpoint
/checkpoint

# 让 AI 继续工作

# 50 行之后，验证是否在预期轨道上
/verify
```

---

### 第七章：工作流进化（29-30）

#### Tip 29: Git Worktrees ⭐⭐⭐

**真正的并行，不是假的**:
```bash
# 创建两个独立工作目录
git worktree add ../project-bugfix bugfix/memory-leak
git worktree add ../project-feature feature/export-api

# 同时工作，共享历史，文件不冲突
cd ../project-bugfix && claude
cd ../project-feature && claude
```

**ECC 的 Longform Guide 叫这个「Cascade Method」**

**流程**:
1. 主分支的 Agent 做规划和架构决策
2. Spawn 到各个 feature 分支并行实现

#### Tip 30: /skill-create ⭐⭐⭐⭐⭐

**从 git 历史提炼 Skill**:
```bash
/skill-create --instincts
```

**功能**:
- 分析当前仓库的 git 历史
- 找出重复出现的多文件变更序列
- 生成 SKILL.md

**示例**: 「每次加新 API 都要改 routes.ts + schema.ts + tests/ 里三个文件」

**适用**: 超过 10k commits 的大仓库
**更深层**: `ecc.tools` GitHub App（自动开 PR）

---

## 🎯 核心价值

### 最有价值的技巧（Top 5）

**1. Tip 27 - Continuous Learning v2** ⭐⭐⭐⭐⭐
- 团队级别的 AI 进化
- 自动从历史学习
- 带置信度评分
- 自动生成和分享 Skill

**2. Tip 30 - /skill-create** ⭐⭐⭐⭐⭐
- 从 git 历史提炼 Skill
- 自动识别重复模式
- 生成可复用工作流

**3. Tip 28 - Verification Loops** ⭐⭐⭐
- 线性任务：定期快照
- 探索性任务：持续评估
- 避免走偏

**4. Tip 29 - Git Worktrees** ⭐⭐⭐
- 真正的并行
- 不同目录，共享历史
- 文件不冲突

**5. Tip 14 - 画拓扑图** ⭐⭐⭐
- 画出来再写代码
- 30 分钟 vs 调试 2 天
- 清晰的架构设计

---

## 🚀 立即可用的改进

### 1. 应用 Verification Loops

```bash
# 创建检查点脚本
cat > /root/.openclaw/workspace/scripts/verify-checkpoint.sh << 'EOF'
#!/bin/bash
echo "🔍 创建检查点..."
checkpoint_dir="/root/.openclaw/workspace/checkpoints/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$checkpoint_dir"
echo "✅ 检查点已创建: $checkpoint_dir"
echo "📝 继续任务，50 步后验证..."
EOF

chmod +x /root/.openclaw/workspace/scripts/verify-checkpoint.sh
```

### 2. 学习 Git Worktrees

```bash
# 创建工作树
git worktree add ../project-bugfix bugfix/
git worktree add ../project-feature feature/

# 同时工作，共享历史
cd ../project-bugfix && claude
cd ../project-feature && claude
```

### 3. 尝试 TinyClaw

- 60 秒部署
- 预置生产配置
- 参考：https://tinyclaw.dev

---

## 💡 文章价值

**极其有价值！** ⭐⭐⭐⭐⭐

- **30 个实用技巧**
- **7 个核心主题**
- **11,850 字符的深度内容**
- **从基础到进阶的完整指南**

**对比今天的学习**:

| | Open-ClaudeCode 源码 | OpenClaw 进阶手册 Vol.2 |
|---|---|---|
| 深度 | 源码级深度 | 实战技巧 |
| 价值 | 设计思想 | 即用即学 |
| 适用 | 理解原理 | 快速上手 |
| 难度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

**两篇文章都极其有价值！** 🧠✨

---

**最后更新**: 2026-04-04 21:25
**状态**: ✅ 完整学习
**价值**: ⭐⭐⭐⭐⭐ 极高
**推荐**: 必读！
