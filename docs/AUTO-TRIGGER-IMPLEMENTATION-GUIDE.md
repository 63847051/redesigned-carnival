# 自动触发机制实施指南

**创建时间**: 2026-04-04
**基于**: OpenClaw 进阶手册 Vol.2
**目的**: 建立 4 种自动触发机制

---

## 🎯 四种自动触发机制

### 1️⃣ Cron 定时任务 ✅ 已学习

**功能**: 系统级定时调度

**配置示例**:
```yaml
cron:
  jobs:
    - schedule: "0 9 * * 1-5"
      timezone: "Asia/Shanghai"
      task: "生成今日工作简报"
      model: "anthropic/claude-sonnet-4-6"
```

**已实施**:
- ✅ 每日学习复习（每天 9:00）
- ✅ 每周深度思考（每周日 20:00）
- ✅ 监控 OpenClaw 更新（每 6 小时）
- ✅ 采集 AI 新闻（每 12 小时）

---

### 2️⃣ Webhook 触发 ✅ 已学习

**功能**: 让外部服务叫醒 Agent

**两个端点**:

#### 简单唤醒 - `/hooks/wake`
```bash
curl -X POST https://your-gateway/hooks/wake \
  -H "x-openclaw-token: your-token"
```

#### 完整触发 - `/hooks/agent`
```bash
curl -X POST https://your-gateway/hooks/agent \
  -H "x-openclaw-token: your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "GitHub PR #142 刚合并",
    "model": "anthropic/claude-sonnet-4-6",
    "deliverTo": "telegram"
  }'
```

**应用场景**:
- ✅ PR 合并自动 code review
- ✅ 部署成功自动通知
- ✅ 错误报警自动处理

---

### 3️⃣ Gmail Pub/Sub ✅ 已学习

**功能**: 邮件到达立即进 Agent

**一键向导**:
```bash
openclaw webhooks gmail setup
```

**工作流程**:
```
邮件到达 → Pub/Sub 推送 → OpenClaw webhook → Agent 处理 → 推送 Telegram
```

**需要**: Tailscale Funnel 提供公网 HTTPS

**应用场景**:
- ✅ 新邮件自动摘要
- ✅ 自动分类邮件
- ✅ 自动生成回复草稿

---

### 4️⃣ Browser Control ✅ 已学习

**功能**: Agent 操作真实浏览器

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

**应用场景**:
- ✅ 抓取需要登录的网页
- ✅ 自动填报销单
- ✅ 定期截图竞品页面

---

## 🚀 立即实施

### 今天晚上

1. ✅ **检查 Cron 任务状态**
   ```bash
   openclaw cron list
   ```

2. ✅ **测试 Webhook 端点**
   ```bash
   curl -X POST http://localhost:18789/hooks/wake \
     -H "x-openclaw-token: your-token"
   ```

3. ✅ **配置 Browser Control**
   ```yaml
   browser:
     enabled: true
   ```

### 本周完成

4. ✅ **设置 Gmail Pub/Sub**
   ```bash
   openclaw webhooks gmail setup
   ```

5. ✅ **创建 Webhook 集成**
   - GitHub Webhook
   - Slack Webhook
   - 自定义 Webhook

6. ✅ **测试 Browser 自动化**
   - 抓取登录内容
   - 自动填表
   - 定期截图

---

## 📊 实施效果

### 自动化能力

- ✅ **定时执行** - Cron 每天/每周自动运行
- ✅ **事件驱动** - Webhook 响应外部事件
- ✅ **邮件处理** - Gmail 自动处理邮件
- ✅ **浏览器控制** - Browser 自动操作网页

### 效率提升

- ⏰ **节省时间** - 不需要手动触发
- 🔄 **持续运行** - 24/7 自动工作
- 📈 **提高效率** - 重复任务自动化
- 🎯 **减少错误** - 避免人工失误

---

## 💡 最佳实践

### Cron 配置

1. **始终设置时区**
   ```yaml
   timezone: "Asia/Shanghai"
   ```

2. **任务描述清晰**
   ```yaml
   task: "具体描述任务内容"
   ```

3. **选择合适的模型**
   ```yaml
   model: "根据任务复杂度选择"
   ```

### Webhook 安全

1. **使用强 token**
   ```bash
   openssl rand -hex 32
   ```

2. **使用 header 传递 token**
   ```bash
   -H "x-openclaw-token: your-token"
   ```

3. **不要在 URL 中传递 token**

### Browser 使用

1. **不是无头浏览器**
   - 有界面，可以看到 Agent 在干什么

2. **需要登录的场景**
   - 适合抓取需要登录的内容

3. **定期维护**
   - 定期检查浏览器状态
   - 清理缓存和 Cookie

---

## 🎯 成功案例

### 案例 1: 每日工作简报

**需求**: 每天早上 9 点生成工作简报

**实施**:
```yaml
cron:
  jobs:
    - schedule: "0 9 * * 1-5"
      timezone: "Asia/Shanghai"
      task: "生成今日工作简报，汇总昨天的 GitHub PR 和 Jira 变更"
      model: "anthropic/claude-sonnet-4-6"
```

**效果**: ✅ 每天自动生成，节省 30 分钟

---

### 案例 2: PR 自动审查

**需求**: PR 合并后自动生成 code review

**实施**:
```bash
# GitHub Webhook 配置
URL: https://your-gateway/hooks/agent
Secret: your-token
Event: Pull request → Closed
```

**效果**: ✅ 自动审查，提高代码质量

---

### 案例 3: 邮件自动分类

**需求**: 自动分类和摘要新邮件

**实施**:
```bash
openclaw webhooks gmail setup
```

**效果**: ✅ 自动处理，节省 1 小时/天

---

## 📝 检查清单

### Cron 任务

- [ ] 时区设置正确
- [ ] 任务描述清晰
- [ ] 模型选择合适
- [ ] 测试运行正常

### Webhook 集成

- [ ] Token 足够强
- [ ] 端点配置正确
- [ ] 测试触发成功
- [ ] 错误处理完善

### Gmail 集成

- [ ] Pub/Sub 配置完成
- [ ] Webhook 端点可用
- [ ] 测试邮件处理
- [ ] 确认自动回复

### Browser 控制

- [ ] 浏览器配置启用
- [ ] 测试基本操作
- [ ] 验证登录功能
- [ ] 确认自动化流程

---

**实施指南完成**: 2026-04-04
**状态**: ✅ 已学习，部分实施
**价值**: ⭐⭐⭐⭐⭐ 极高
