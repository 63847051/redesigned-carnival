# 飞书通知配置指南

## 🎯 功能说明

飞书通知系统可以实时发送系统告警到飞书，无需主动查看日志。

## 📋 支持的告警类型

1. **内存告警** - 内存使用超过阈值时通知
2. **服务告警** - 服务停止时通知
3. **进化完成** - 进化学习完成时通知
4. **健康检查** - 定期健康检查报告

## 🔧 配置步骤

### 步骤 1: 创建飞书机器人

1. 在飞书中创建一个群聊
2. 添加"自定义机器人"
3. 获取 Webhook URL

### 步骤 2: 配置环境变量

```bash
# 方式 1: 临时配置（当前会话）
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"

# 方式 2: 永久配置（推荐）
echo 'export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"' >> /root/.bashrc
source /root/.bashrc

# 方式 3: 系统配置（最稳定）
cat > /etc/profile.d/feishu-notify.sh << 'EOF'
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
EOF
chmod +x /etc/profile.d/feishu-notify.sh
source /etc/profile.d/feishu-notify.sh
```

### 步骤 3: 测试通知

```bash
# 测试内存告警
bash /root/.openclaw/workspace/scripts/feishu-notify.sh memory "85" "80"

# 测试服务告警
bash /root/.openclaw/workspace/scripts/feishu-notify.sh service "Dashboard" "stopped"

# 测试自定义消息
bash /root/.openclaw/workspace/scripts/feishu-notify.sh "测试标题" "测试内容"
```

## 📱 通知样式

### 内存告警
```
⚠️ 内存使用告警

内存使用过高

当前使用: 85%
告警阈值: 80%

请及时检查系统状态！

服务器: VM-0-8-opencloudos | 时间: 2026-03-13 20:35:00
```

### 服务告警
```
🚨 服务状态告警

Dashboard 状态异常

当前状态: stopped

请及时检查服务状态！

服务器: VM-0-8-opencloudos | 时间: 2026-03-13 20:35:00
```

### 进化完成
```
🧬 进化学习完成

系统进化完成

✅ L7验证通过
✅ 防护系统正常
✅ PAI学习已执行

系统已变得更强大！✨

服务器: VM-0-8-opencloudos | 时间: 2026-03-13 20:35:00
```

## 🔍 故障排查

### 问题 1: 未收到通知

**检查**:
```bash
# 1. 检查环境变量
echo $FEISHU_WEBHOOK_URL

# 2. 检查脚本权限
ls -la /root/.openclaw/workspace/scripts/feishu-notify.sh

# 3. 手动测试
bash /root/.openclaw/workspace/scripts/feishu-notify.sh "测试" "测试内容"
```

### 问题 2: Webhook 失败

**原因**: Webhook URL 错误或已过期

**解决**: 重新创建机器人，更新 URL

### 问题 3: 消息格式错误

**检查**: 查看脚本日志

## 💡 使用建议

1. **创建专门的告警群聊**
   - 不要打扰工作群
   - 方便查看历史告警

2. **设置合理的阈值**
   - 内存: 80-85%
   - 磁盘: 85-90%

3. **定期测试**
   - 每周测试一次通知
   - 确保 Webhook 有效

4. **添加群组成员**
   - 运维人员
   - 开发人员
   - 相关负责人

## 🚀 高级功能

### 自定义告警

```bash
# 在你的脚本中使用
bash /root/.openclaw/workspace/scripts/feishu-notify.sh \
  "自定义标题" \
  "**自定义内容**

支持 Markdown 格式

- 列表项 1
- 列表项 2"
```

### 集成到现有脚本

```bash
# 在任何脚本中添加
if [ -n "$FEISHU_WEBHOOK_URL" ]; then
  bash /root/.openclaw/workspace/scripts/feishu-notify.sh \
    "任务完成" \
    "**任务名称**: 备份数据\n**状态**: 成功\n**耗时**: 2 分钟"
fi
```

## 📚 相关文档

- 飞书机器人文档: https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ATO24yNxkjN
- 脚本位置: `/root/.openclaw/workspace/scripts/feishu-notify.sh`

---

*配置完成后，你将实时收到系统告警！* 🎉
