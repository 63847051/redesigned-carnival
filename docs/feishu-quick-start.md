# 飞书通知快速配置指南

## 🚀 3 步完成配置

### 步骤 1: 创建飞书机器人（1 分钟）

1. 在飞书群聊中点击右上角 "..."
2. 选择 "群机器人" → "添加机器人" → "自定义机器人"
3. 输入名称（如：系统告警）
4. 点击 "添加"
5. **复制 Webhook URL**（重要！）

### 步骤 2: 运行配置脚本（1 分钟）

```bash
bash /root/.openclaw/workspace/scripts/setup-feishu-notify.sh
```

脚本会提示你输入 Webhook URL，然后自动配置。

### 步骤 3: 测试通知（30 秒）

配置完成后，脚本会自动发送测试消息到飞书群聊。

检查飞书群聊是否收到消息！

---

## ✅ 验证配置

### 检查环境变量

```bash
echo $FEISHU_WEBHOOK_URL
```

应该显示你的 Webhook URL。

### 手动测试

```bash
bash /root/.openclaw/workspace/scripts/feishu-notify.sh "测试" "测试内容"
```

### 查看配置文件

```bash
cat /etc/profile.d/feishu-notify.sh
```

---

## 🎯 配置完成后

### 自动告警功能

配置完成后，以下告警将自动发送到飞书：

1. **内存告警** - 每 10 分钟检查，超过 80% 自动通知
2. **服务告警** - 服务停止时立即通知
3. **进化完成** - 进化学习完成时发送摘要

### 自定义告警

你也可以在自己的脚本中使用：

```bash
# 在任何脚本中
bash /root/.openclaw/workspace/scripts/feishu-notify.sh \
  "任务完成" \
  "**备份任务**\n状态: 成功\n耗时: 2 分钟"
```

---

## 🔧 故障排查

### 问题 1: 未收到通知

**检查**:
```bash
# 1. 确认环境变量已设置
echo $FEISHU_WEBHOOK_URL

# 2. 手动测试
bash /root/.openclaw/workspace/scripts/feishu-notify.sh "测试" "测试"

# 3. 查看 Webhook URL 是否正确
cat /etc/profile.d/feishu-notify.sh
```

### 问题 2: URL 格式错误

**正确格式**:
```
https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**错误格式**:
```
https://open.feishu.cn/open-apis/bot/v2/hook/xxx (缺少部分)
http://open.feishu.cn/... (不是 https)
```

### 问题 3: 机器人被移除

**解决**: 重新创建机器人，更新 Webhook URL

---

## 📱 告警样式

### 内存告警示例
```
⚠️ 内存使用告警

内存使用过高

当前使用: 85%
告警阈值: 80%

请及时检查系统状态！

服务器: VM-0-8-opencloudos | 时间: 2026-03-13 20:35:00
```

### 服务告警示例
```
🚨 服务状态告警

Dashboard 状态异常

当前状态: stopped

请及时检查服务状态！

服务器: VM-0-8-opencloudos | 时间: 2026-03-13 20:35:00
```

---

## 💡 使用建议

1. **创建专门的告警群聊**
   - 不要打扰工作群
   - 方便查看历史告警

2. **添加相关人员**
   - 运维人员
   - 开发人员
   - 相关负责人

3. **定期测试**
   - 每周测试一次
   - 确保 Webhook 有效

4. **设置合理阈值**
   - 内存: 80-85%
   - 磁盘: 85-90%

---

## 🎉 配置完成

配置完成后，你将：
- ✅ 实时收到系统告警
- ✅ 无需主动查看日志
- ✅ 及时发现问题
- ✅ 快速响应故障

---

**开始配置吧！** 🚀
