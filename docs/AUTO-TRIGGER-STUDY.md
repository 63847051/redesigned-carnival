# 自动触发机制学习文档

**创建时间**: 2026-04-04 18:45
**最后更新**: 2026-04-04 19:30
**预计学习时间**: 2-3 小时
**状态**: ✅ 已完成

---

## 🎯 学习目标

掌握 OpenClaw 的 4 种自动触发机制：
1. ✅ Cron 定时任务
2. ✅ Webhook 触发
3. ✅ Gmail Pub/Sub 集成
4. ✅ Browser Control 自动化

---

## 📚 学习模块

### ✅ 模块 1: Cron 定时任务

#### 核心概念
- **三种调度类型**：
  - `--every <duration>`: 每隔一段时间（如 `10m`, `1h`, `30d`）
  - `--at <when>`: 指定时间执行（如 `2026-04-04 09:00` 或 `+10m`）
  - `--cron <expr>`: Cron 表达式（如 `0 9 * * 1-5`）

- **四种执行模式**：
  - `main`: 主会话
  - `isolated`: 隔离会话（默认）
  - `current`: 当前会话
  - `custom session`: 自定义会话

#### 实战测试 ✅

**测试 1: 创建任务**
```bash
openclaw cron add \
  --every "10m" \
  --name "测试心跳任务" \
  --message "Read HEARTBEAT.md..."
```
**结果**: ✅ 成功

**测试 2: 列出任务**
```bash
openclaw cron list
```
**结果**: ✅ 成功

**测试 3: 删除任务**
```bash
openclaw cron remove <job-id>
```
**结果**: ✅ 成功

---

### ✅ 模块 2: Webhook 触发

#### 核心发现 ⭐

**Bug: gateway.hooks 配置悖论**
- **问题**: v2026.4.2 文档提到 `gateway.hooks` 配置
- **实际**: Gateway 后端不支持这个配置
- **行为**: Gateway 启动时自动删除"未知字段"
- **解决**: 使用 `openclaw hooks` 命令管理

#### Hooks 命令 ✅

**列出所有 hooks**:
```bash
openclaw hooks list
```

**查看 hook 详情**:
```bash
openclaw hooks info <hook-name>
```

**启用/禁用 hook**:
```bash
openclaw hooks enable <hook-name>
openclaw hooks disable <hook-name>
```

**检查 hook 状态**:
```bash
openclaw hooks check
```

#### 内置 Hooks（4 个）

根据 Gateway 日志，系统加载了 4 个内部 hook handlers：
1. Session Memory Hook
2. Agent Lifecycle Hook
3. Task Flow Hook
4. Custom Event Hook

---

### ✅ 模块 3: Gmail Pub/Sub 集成

#### 原理

**Gmail Pub/Sub** 是什么？
- Google Cloud Pub/Sub 是一个消息传递服务
- Gmail 可以通过 Pub/Sub 实时推送新邮件通知
- 无需轮询，即时响应

**工作流程**:
```
新邮件 → Gmail API → Pub/Sub Topic → Subscription → Gateway Webhook → 触发 Agent
```

#### 配置方式

**方式 1: Wizard 自动设置** ⭐ 推荐
```bash
openclaw wizard gmail
```

Wizard 会自动：
1. 检查 Google Cloud 项目
2. 创建 Pub/Sub topic
3. 设置 Gmail API push notification
4. 配置 Gateway webhook
5. 测试连接

**方式 2: 手动配置**

**Step 1: 在 Google Cloud Console 创建 Pub/Sub topic**
```bash
gcloud pubsub topics create gmail-notifications
```

**Step 2: 在 Gmail API 设置 push notification**
```yaml
{
  "topicName": "projects/your-project/topics/gmail-notifications"
}
```

**Step 3: 创建 subscription**
```bash
gcloud pubsub subscriptions create gmail-subscription \
  --topic=gmail-notifications \
  --push-endpoint=http://your-gateway.com/hooks/gmail \
  --push-auth-service-account=your-service-account
```

**Step 4: 配置 OpenClaw**
```yaml
channels:
  gmail:
    enabled: true
    pubsub:
      enabled: true
      projectId: "my-gcp-project"
      subscriptionName: "gmail-subscription"
```

#### 配置示例

```yaml
channels:
  gmail:
    enabled: true
    # Pub/Sub 配置
    pubsub:
      enabled: true
      projectId: "my-gcp-project"
      subscriptionName: "openclaw-gmail"

    # 邮件过滤器
    filters:
      - from: "boss@company.com"
        subject: "[任务]"
        action: "转发给大领导处理"

      - from: "*@github.com"
        subject: "[GitHub]"
        action: "记录到工作日志"

    # 标签过滤
    labels:
      - "INBOX"
      - "IMPORTANT"
      - "STARRED"
```

#### CLI 命令

```bash
# 检查 Gmail 配置
openclaw channels status gmail

# 测试 Gmail 连接
openclaw channels test gmail

# 启用 Gmail 通道
openclaw channels enable gmail
```

---

### ✅ 模块 4: Browser Control 自动化

#### 当前配置 ✅

```json
{
  "enabled": true,
  "executablePath": "/root/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome",
  "noSandbox": true,
  "defaultProfile": "user",
  "profiles": {
    "user": {
      "cdpUrl": "http://localhost:9222",
      "driver": "existing-session",
      "attachOnly": true,
      "color": "#4285F4",
      "userDataDir": "/root/.openclaw/browser-existing-session"
    }
  }
}
```

**浏览器状态**: ✅ Chrome 145.0.7632.6 正在运行

#### 原理

Browser Control 允许 OpenClaw 控制浏览器（Chromium），进行网页自动化操作。

**CDP (Chrome DevTools Protocol)**:
- 通过 CDP 协议与浏览器通信
- 支持导航、截图、点击、输入等操作
- 可以使用现有的浏览器会话

#### CLI 命令

```bash
# 列出标签页
openclaw browser tabs

# 快照（获取可交互元素）
openclaw browser snapshot --refs aria

# 截图
openclaw browser screenshot

# 导航
openclaw browser navigate https://example.com

# 点击元素
openclaw browser click --ref "button[name='Login']"

# 输入文本
openclaw browser type --ref "input[name='email']" --text "user@example.com"

# 执行 JavaScript
openclaw browser eval --js "document.title"

# 等待元素
openclaw browser wait --selector ".loaded"
```

#### 实战示例

**示例 1: 每日检查网页**
```bash
openclaw cron add \
  --every "1h" \
  --name "检查网页更新" \
  --message "使用浏览器检查 https://example.com 是否有更新"
```

**示例 2: 自动化登录**
```bash
# 导航到登录页
openclaw browser navigate https://example.com/login

# 输入邮箱
openclaw browser type --ref "input[name='email']" --text "user@example.com"

# 输入密码
openclaw browser type --ref "input[name='password']" --text "password"

# 点击登录按钮
openclaw browser click --ref "button[type='submit']"

# 等待跳转
openclaw browser wait --selector ".dashboard"
```

**示例 3: 定期截图**
```bash
openclaw cron add \
  --every "30m" \
  --name "监控网站" \
  --message "访问 https://status.example.com 并截图"
```

---

## 🎯 实战示例

### 示例 1: 每日工作报告 ✅
```bash
openclaw cron add \
  --cron "0 21 * * *" \
  --tz "Asia/Shanghai" \
  --name "每日工作报告" \
  --message "大领导，生成今日工作报告"
```

### 示例 2: Hooks 管理 ✅
```bash
# 列出所有 hooks
openclaw hooks list

# 启用一个 hook
openclaw hooks enable session-memory

# 检查 hook 状态
openclaw hooks check
```

### 示例 3: Gmail 邮件触发
```yaml
channels:
  gmail:
    enabled: true
    filters:
      - from: "boss@company.com"
        subject: "[任务]"
        action: "转发给大领导处理"
```

### 示例 4: 浏览器自动化 ✅
```bash
# 每天检查网页更新
openclaw cron add \
  --every "1h" \
  --name "检查网页更新" \
  --message "使用浏览器检查 https://example.com 是否有更新"
```

---

## 📋 学习检查清单

### 模块 1: Cron ✅
- [x] 理解 Cron 表达式语法
- [x] 掌握时区处理
- [x] 测试 `--at`、`--every`、`--cron`
- [x] 理解四种执行模式

### 模块 2: Webhook ✅
- [x] 理解 Webhook 原理
- [x] 发现 gateway.hooks Bug
- [x] 学习 openclaw hooks 命令
- [x] 了解 4 个内置 hooks

### 模块 3: Gmail ✅
- [x] 理解 Pub/Sub 原理
- [x] 学习 Wizard 配置
- [x] 了解手动配置流程
- [x] 掌握邮件过滤器使用

### 模块 4: Browser ✅
- [x] 检查 Browser Control 配置
- [x] 验证浏览器运行状态
- [x] 学习基本命令
- [x] 创建自动化示例

---

## 🎓 产出物

1. ✅ **Cron 配置示例**（已完成）
2. ✅ **Webhook 学习笔记**（已完成）
3. ✅ **Gmail 配置示例**（已完成）
4. ✅ **Browser 配置示例**（已完成）
5. ✅ **学习文档**（本文档）

---

## 📊 学习进度

- ✅ 模块 1: Cron 定时任务（100%）
- ✅ 模块 2: Webhook 触发（100%）
- ✅ 模块 3: Gmail Pub/Sub 集成（100%）
- ✅ 模块 4: Browser Control 自动化（100%）

**总进度**: 100% (4/4) ✅

---

## 🚨 重要发现

### Bug: gateway.hooks 配置悖论 ⭐

**问题**:
- v2026.4.2 文档提到 `gateway.hooks` 配置
- Gateway 后端不支持这个配置
- Gateway 启动时自动删除"未知字段"

**解决**:
- 使用 `openclaw hooks` 命令管理
- 不依赖配置文件

**影响**:
- 模块 2 学习方式需要调整
- 需要熟悉 CLI 命令而非配置文件

---

## 💡 核心收获

### 1. Cron 定时任务 ✅
- 三种调度类型（every、at、cron）
- 四种执行模式（main、isolated、current、custom）
- 时区处理（--tz 参数）

### 2. Webhook 触发 ✅
- Hooks 通过 CLI 命令管理
- 4 个内置 hooks（session-memory、agent-lifecycle、task-flow、custom-event）
- 不依赖配置文件

### 3. Gmail Pub/Sub ✅
- 实时邮件推送，无需轮询
- Wizard 自动配置
- 支持邮件过滤器

### 4. Browser Control ✅
- CDP 协议控制浏览器
- 支持现有会话
- 丰富的自动化命令

---

## 🎯 下一步行动

### 立即可用
1. ✅ 使用 Cron 创建定时任务
2. ✅ 使用 `openclaw hooks` 管理 hooks
3. ✅ 配置 Gmail Pub/Sub（如需要）
4. ✅ 使用 Browser Control 自动化

### 深入学习
1. ⬜ Task Flow 系统（v2026.4.2 新功能）
2. ⬜ before_agent_reply 钩子
3. ⬜ 高级 Browser 自动化

---

**最后更新**: 2026-04-04 19:30
**状态**: ✅ 完成
**总学习时间**: ~2 小时
