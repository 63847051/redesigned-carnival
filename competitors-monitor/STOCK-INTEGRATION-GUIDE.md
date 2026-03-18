# 股票分析系统整合使用指南

**版本**: v1.0  
**整合时间**: 2026-03-18  
**状态**: ✅ 快速集成完成

---

## 🎯 整合方案

### 系统架构

```
daily_stock_analysis (股票分析系统)
    ↓ Webhook
competitors-monitor (通用监控框架)
    ↓ 飞书
用户
```

---

## 📋 准备工作

### 1. 安装 daily_stock_analysis

```bash
# 克隆仓库
git clone https://github.com/ZhuLinsen/daily_stock_analysis.git
cd daily_stock_analysis

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
vim .env

# 启动服务
python main.py --webui
```

### 2. 配置环境变量

在 `daily_stock_analysis/.env` 中添加：

```bash
# Webhook 推送到监控系统
MONITOR_WEBHOOK_URL=http://127.0.0.1:5001/webhook/stock
```

---

## 🚀 启动步骤

### 步骤 1：启动 Webhook 接收端

```bash
cd /root/.openclaw/workspace/competitors-monitor

# 启动接收端
python webhook-receiver.py
```

**输出**:
```
🚀 启动 Webhook 接收端...
📡 Webhook URL: http://0.0.0.0:5001/webhook/stock
📊 报告查询: http://0.0.0.0:5001/webhook/stock/reports
❤️ 健康检查: http://0.0.0.0:5001/health
```

### 步骤 2：启动股票分析系统

```bash
cd /root/.openclaw/workspace/daily_stock_analysis

# 启动 Web UI
python main.py --webui
```

**访问**: http://127.0.0.1:8000

### 步骤 3：测试整合

**测试 1：手动触发股票分析**

1. 访问 http://127.0.0.1:8000
2. 点击「立即分析」
3. 等待分析完成
4. 检查 Webhook 是否接收成功

**测试 2：查看接收的报告**

```bash
curl http://127.0.0.1:5001/webhook/stock/reports
```

**预期输出**:
```json
{
  "status": "success",
  "count": 1,
  "reports": [
    {
      "title": "股票分析报告",
      "content": "...",
      "received_at": "2026-03-18T23:30:00"
    }
  ]
}
```

---

## 📊 使用插件获取分析结果

### 方式 1：直接运行插件

```bash
cd /root/.openclaw/workspace/competitors-monitor

# 运行股票 AI 插件
python plugins/stock-ai.py
```

### 方式 2：通过配置文件

```bash
# 使用配置文件
python scripts/run.py config/stock-ai.json
```

---

## 🔧 配置说明

### stock-ai.json 配置

```json
{
  "monitor_type": "api",
  "name": "股票 AI 分析监控",
  "api_url": "http://127.0.0.1:8000/api/v1/analysis/history",
  "targets": [
    {
      "name": "自选股分析",
      "limit": 10
    }
  ],
  "check_rules": {
    "min_score": 60,
    "check_frequency": "daily"
  },
  "notification": {
    "feishu_webhook": "YOUR_WEBHOOK_URL_HERE",
    "report_time": "18:30"
  }
}
```

**参数说明**:
- `limit`: 获取多少条历史记录
- `min_score`: 最低评分（低于此值告警）
- `check_frequency`: 检查频率（daily/weekly）
- `report_time`: 推送时间

---

## 🎯 工作流程

### 完整流程

1. **股票分析系统** → 分析股票 → 生成报告
2. **Webhook 推送** → 推送到监控系统
3. **监控系统接收** → 保存到数据库
4. **飞书推送** → 推送给用户

### 时序图

```
时间 → 
18:00  股票分析系统自动运行
18:05  分析完成
18:06  Webhook 推送报告
18:07  监控系统接收报告
18:08  推送到飞书
```

---

## 💡 高级用法

### 1. 定时检查股票分析

```bash
# 添加到 crontab
0 18 * * 1-5 cd /root/.openclaw/workspace/competitors-monitor && python plugins/stock-ai.py
```

### 2. 自定义推送规则

修改 `config/stock-ai.json`:

```json
{
  "notification": {
    "feishu_webhook": "YOUR_WEBHOOK_URL",
    "report_time": "18:30",
    "alert_on": {
      "score_below": 50,
      "score_above": 85,
      "recommendation": "buy"
    }
  }
}
```

### 3. 多渠道推送

```json
{
  "notification": {
    "feishu_webhook": "FEISHU_URL",
    "telegram_bot_token": "TELEGRAM_TOKEN",
    "telegram_chat_id": "TELEGRAM_CHAT_ID"
  }
}
```

---

## 🐛 故障排查

### 问题 1：Webhook 推送失败

**检查**:
```bash
# 检查接收端是否运行
curl http://127.0.0.1:5001/health

# 检查股票分析系统配置
cat daily_stock_analysis/.env | grep MONITOR_WEBHOOK_URL
```

### 问题 2：无法获取分析结果

**检查**:
```bash
# 检查股票分析系统是否运行
curl http://127.0.0.1:8000/health

# 检查 API 是否可用
curl http://127.0.0.1:8000/api/v1/analysis/history?limit=1
```

### 问题 3：飞书推送失败

**检查**:
```bash
# 检查 Webhook URL
echo "测试" | curl -X POST -d @- $FEISHU_WEBHOOK_URL
```

---

## 📚 相关文档

- **daily_stock_analysis 完整指南**: https://github.com/ZhuLinsen/daily_stock_analysis/blob/main/docs/full-guide.md
- **通用监控框架使用指南**: `USAGE.md`
- **通用监控框架架构文档**: `ARCHITECTURE.md`

---

## ✅ 整合完成

**功能**:
- ✅ Webhook 接收端运行
- ✅ 股票分析系统运行
- ✅ 数据自动推送
- ✅ 飞书通知

**下一步**:
- 📊 查看分析报告
- 🎯 配置推送规则
- 📈 优化工作流程

---

**整合完成时间**: 2026-03-18 23:35  
**状态**: ✅ 快速集成完成
