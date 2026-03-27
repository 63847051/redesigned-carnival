# 股票分析集成系统 - 快速开始

**版本**: 1.0.0
**创建时间**: 2026-03-27

---

## 🎯 系统概述

这个集成系统自动配合：
- **A 股 MCP 服务**：提供实时数据
- **daily_stock_analysis**：提供 AI 深度分析

---

## 🚀 快速开始

### 方式 1：使用快捷脚本（推荐）⭐

```bash
# 分析单只股票
/root/.openclaw/workspace/analyze-stock.sh SH600000

# 批量分析
/root/.openclaw/workspace/analyze-stock.sh SH600000 SH600519 SZ00700
```

### 方式 2：使用 Python 脚本

```bash
cd /root/.openclaw/workspace/scripts/stock-integration
/root/.openclaw/workspace/mcp-cn-a-stock/venv/bin/python3 integrated_analysis.py SH600000
```

---

## 📊 报告示例

运行后会生成 Markdown 报告：

```markdown
# 📊 SH600000 集成分析报告

**生成时间**: 2026-03-27 21:35:46

---

## 📡 实时数据（A 股 MCP 服务）

- 股票代码: SH600000
- 股票名称: 浦发银行
- 当日: 10.020 元
- 市盈率: 6.94
- ...

---

## 🤖 AI 深度分析（daily_stock_analysis）

- 技术指标分析
- 趋势判断
- 投资建议
- ...
```

---

## 📁 报告位置

所有报告保存在：
```
/root/.openclaw/workspace/stock-reports/
```

文件名格式：
```
{股票代码}_{时间戳}.md
```

例如：
```
SH600000_20260327_213546.md
SH600519_20260327_213600.md
```

---

## 💡 使用场景

### 场景 1：每日复盘

```bash
# 每天早上分析自选股
/root/.openclaw/workspace/analyze-stock.sh SH600000 SH600519 SZ00700
```

### 场景 2：选股辅助

```bash
# 批量分析银行股
/root/.openclaw/workspace/analyze-stock.sh SH600000 SH600036 SH601398 SH601939
```

### 场景 3：定时任务

```bash
# 添加到 crontab
crontab -e

# 每天早上 9 点执行
0 9 * * * /root/.openclaw/workspace/analyze-stock.sh SH600000 >> /root/.openclaw/workspace/stock-analysis.log 2>&1
```

---

## ⚙️ 系统要求

### 必需服务

1. **A 股 MCP 服务**
   - 状态：✅ 已配置
   - 地址：http://82.156.17.205/cnstock/mcp

2. **daily_stock_analysis**
   - 状态：需要运行
   - 检查：`ps aux | grep daily_stock_analysis`
   - 启动：`cd /root/.openclaw/workspace/daily_stock_analysis && python3 webui.py`

### Python 环境

```bash
# 虚拟环境
/root/.openclaw/workspace/mcp-cn-a-stock/venv/

# 依赖
pip install httpx
```

---

## ⚠️ 注意事项

1. **daily_stock_analysis 可选**
   - 如果不运行，只会显示 MCP 数据
   - 不影响基本功能

2. **网络连接**
   - MCP 服务需要外网访问
   - 如果失败会提示错误

3. **股票代码格式**
   - 上海: SH + 6位数字
   - 深圳: SZ + 6位数字

---

## 🎉 特性

- ✅ 一键分析
- ✅ 自动保存报告
- ✅ 支持批量分析
- ✅ Markdown 格式
- ✅ 错误处理
- ✅ 时间戳记录

---

## 📝 常用股票代码

### 银行股

- SH600000 - 浦发银行
- SH600036 - 招商银行
- SH601398 - 工商银行
- SH601939 - 建设银行
- SH601288 - 农业银行

### 科技股

- SH600519 - 贵州茅台
- SZ000858 - 五粮液
- SZ00700 - 腾讯控股
- SZ002594 - 比亚迪

### 指数

- SH000001 - 上证指数
- SZ399001 - 深证成指
- SZ399006 - 创业板指

---

## 🔧 故障排除

### 问题 1：MCP 服务不可用

```
❌ MCP 查询失败: Connection refused
```

**解决**：
- 检查网络连接
- 确认 MCP 服务地址正确

### 问题 2：daily_stock_analysis 不可用

```
⚠️  AI 分析不可用: All connection attempts failed
```

**解决**：
- 检查服务是否运行：`ps aux | grep daily_stock_analysis`
- 启动服务：`cd /root/.openclaw/workspace/daily_stock_analysis && python3 webui.py`

### 问题 3：报告目录不存在

```
❌ 分析失败: No such file or directory
```

**解决**：
- 创建目录：`mkdir -p /root/.openclaw/workspace/stock-reports`

---

## 📞 获取帮助

```bash
# 查看使用说明
/root/.openclaw/workspace/analyze-stock.sh

# 查看详细文档
cat /root/.openclaw/workspace/scripts/stock-integration/README.md
```

---

**最后更新**: 2026-03-27 21:35
**版本**: 1.0.0
**状态**: ✅ 可用
