# 飞书推送通知 Skill

**Skill 名称**: `feishu-notifier`

**版本**: v1.0

---

## description

当用户要求推送报告到飞书、发送监控结果、通知竞品变化时使用此技能。

不适用于：非飞书平台推送、非报告类消息。

---

## 触发条件

- 用户要求推送报告到飞书
- 报告生成 Agent 完成后自动触发
- 用户说"推送飞书"、"发送通知"等

---

## 工作流程

### 1. 加载配置

- 读取 `config.json`
- 获取飞书 Webhook URL

### 2. 验证配置

- 检查 Webhook URL 是否配置
- 如果未配置，提示用户配置

### 3. 加载报告

- 读取今天的 Markdown 报告
- 提取关键信息

### 4. 格式化消息

- 提取变化概览
- 提取关键发现
- 生成简短摘要（避免消息过长）

### 5. 发送到飞书

- 使用 Webhook 发送消息
- 处理发送结果

### 6. 输出结果

- 成功：显示飞书响应
- 失败：显示错误信息和排查建议

---

## 消息格式

### 摘要消息示例

```
📊 竞品监控日报 - 2026-03-18

- **总变化数**: 6
- **新增页面**: 1
- **更新页面**: 5
- **删除页面**: 0

🎯 - **平均内容相似度**: 27.81%
💡 - **结论**: 竞品正在积极更新产品/内容，建议密切关注

📁 完整报告已保存到本地
⏰ 2026-03-18 11:35:00
```

---

## 配置说明

### config.json 配置

```json
{
  "notification": {
    "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
    "report_time": "09:00",
    "timezone": "Asia/Shanghai"
  }
}
```

### 如何获取飞书 Webhook

1. 在飞书群中添加机器人
2. 获取 Webhook URL
3. 复制到 `config.json`

---

## 需要的环境变量

无（所有配置在 `config.json` 中）

---

## 使用的脚本

- `scripts/notify.py` - 推送通知脚本

---

## 注意事项

### 消息长度
- ⚠️ 飞书消息有长度限制
- 💡 只发送摘要，完整报告保存到本地

### Webhook 安全
- ⚠️ 不要在公开代码中暴露 Webhook URL
- 💡 使用环境变量或配置文件

### 发送频率
- ⚠️ 避免频繁发送（每天 1 次即可）
- 💡 可以设置定时任务

### 错误处理
- ✅ 发送失败时给出明确提示
- ✅ 提供排查建议

---

## 输出示例

### 场景 1：配置正确

**用户输入**:
```
推送报告到飞书
```

**Agent 输出**:
```
收到，正在推送报告到飞书...

📝 消息内容:
📊 竞品监控日报 - 2026-03-18

- **总变化数**: 6
- **新增页面**: 1
- **更新页面**: 5
...

✅ 推送成功！
📊 飞书响应: {"code": 0, "msg": "success"}
```

---

### 场景 2：未配置 Webhook

**Agent 输出**:
```
⚠️  未配置飞书 Webhook
💡 请在 config.json 中配置 feishu_webhook
💡 或者直接运行以下命令查看报告:
   cat reports/2026-03-18.md
```

---

### 场景 3：发送失败

**Agent 输出**:
```
❌ 推送失败: Connection timeout
💡 请检查:
   1. Webhook URL 是否正确
   2. 网络连接是否正常
   3. 飞书机器人是否有权限
```

---

## 与其他 Agent 的协作

### 上游 Agent
- **competitor-reporter**（报告汇总 Agent）
  - 读取其输出的 Markdown 报告
  - 作为输入数据

### 触发方式
- 上游 Agent 完成后，自动触发本 Agent
- 或用户手动触发

---

## 数据结构

### 输入数据
```markdown
# 竞品监控日报

**日期**: 2026-03-18
...

（完整的 Markdown 报告）
```

### 输出数据
```json
{
  "code": 0,
  "msg": "success"
}
```

---

## 飞书 Webhook API

### 请求格式

```json
POST https://open.feishu.cn/open-apis/bot/v2/hook/xxx
Content-Type: application/json

{
  "msg_type": "text",
  "content": {
    "text": "文本消息内容"
  }
}
```

### 响应格式

```json
{
  "code": 0,
  "msg": "success"
}
```

---

## 定时任务

### 使用 cron

```bash
# 每天早上 9:00 推送报告
0 9 * * * cd /root/.openclaw/workspace/competitors-monitor && python3 scripts/scrape.py && python3 scripts/diff.py && python3 scripts/report.py && python3 scripts/notify.py
```

### 使用 systemd timer

创建 `/etc/systemd/system/competitor-monitor.service`:
```ini
[Unit]
Description=Competitor Monitor Service

[Service]
Type=oneshot
WorkingDirectory=/root/.openclaw/workspace/competitors-monitor
ExecStart=/usr/bin/python3 scripts/scrape.py && /usr/bin/python3 scripts/diff.py && /usr/bin/python3 scripts/report.py && /usr/bin/python3 scripts/notify.py
```

创建 `/etc/systemd/system/competitor-monitor.timer`:
```ini
[Unit]
Description=Competitor Monitor Timer

[Timer]
OnCalendar=daily
OnCalendar=09:00
Persistent=true

[Install]
WantedBy=timers.target
```

启用：
```bash
sudo systemctl enable competitor-monitor.timer
sudo systemctl start competitor-monitor.timer
```

---

**Skill 版本**: v1.0
**创建时间**: 2026-03-18
**作者**: 大领导 🎯
