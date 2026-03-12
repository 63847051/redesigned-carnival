# 🕒 PAI 自动化执行配置

## Cron 任务配置

### 方式 1: 每小时自动运行
```bash
# 每小时的第 0 分钟执行
0 * * * * bash /root/.openclaw/workspace/scripts/pai-auto-exec.sh
```

### 方式 2: 每 6 小时运行（推荐）
```bash
# 每 6 小时的第 0 分钟执行
0 */6 * * * bash /root/.openclaw/workspace/scripts/pai-auto-exec.sh
```

### 方式 3: 每天运行（早上 8 点）
```bash
# 每天早上 8 点执行
0 8 * * * bash /root/.openclaw/workspace/scripts/pai-auto-exec.sh
```

## 如何设置 Cron 任务

### 步骤 1: 编辑 crontab
```bash
crontab -e
```

### 步骤 2: 添加以下行（选择一个频率）
```bash
# 每 6 小时自动运行 PAI 系统
0 */6 * * * bash /root/.openclaw/workspace/scripts/pai-auto-exec.sh >> /root/.openclaw/workspace/.pai-learning/cron.log 2>&1
```

### 步骤 3: 保存并退出

### 步骤 4: 验证 cron 任务
```bash
# 查看 cron 任务列表
crontab -l

# 查看 cron 日志
tail -f /root/.openclaw/workspace/.pai-learning/cron.log
```

## 临时测试（立即执行一次）
```bash
bash /root/.openclaw/workspace/scripts/pai-auto-exec.sh
```

## 手动设置 Cron 任务
```bash
# 创建临时 cron 文件
cat > /tmp/pai-cron << 'EOF'
# 每 6 小时自动运行 PAI 系统
0 */6 * * * bash /root/.openclaw/workspace/scripts/pai-auto-exec.sh >> /root/.openclaw/workspace/.pai-learning/cron.log 2>&1
EOF

# 安装 cron 任务
crontab /tmp/pai-cron
rm /tmp/pai-cron

# 验证
crontab -l
```
