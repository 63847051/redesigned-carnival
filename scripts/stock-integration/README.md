# 股票分析集成脚本

**版本**: 1.0.0
**创建时间**: 2026-03-27
**状态**: ✅ 已创建

---

## 🎯 功能

自动配合 A 股 MCP 服务和 daily_stock_analysis，生成综合分析报告。

### 集成流程

```
1. A 股 MCP 服务 → 获取实时数据
2. daily_stock_analysis → AI 深度分析
3. 集成脚本 → 生成综合报告
4. 保存到文件 → 方便查看
```

---

## 🚀 使用方法

### 基础使用

```bash
cd /root/.openclaw/workspace/scripts/stock-integration
python3 integrated_analysis.py SH600000
```

### 示例

```bash
# 浦发银行
python3 integrated_analysis.py SH600000

# 贵州茅台
python3 integrated_analysis.py SH600519

# 腾讯控股
python3 integrated_analysis.py SZ00700
```

---

## 📊 输出报告

报告包含：

1. **实时数据**（A 股 MCP 服务）
   - 基本信息
   - 交易数据
   - 资金流向
   - 换手率

2. **AI 分析**（daily_stock_analysis）
   - 技术指标
   - 趋势分析
   - 投资建议

3. **保存位置**
   - 目录: `/root/.openclaw/workspace/stock-reports/`
   - 格式: `{股票代码}_{时间戳}.md`

---

## ⚙️ 配置

### MCP 服务

```python
MCP_URL = "http://82.156.17.205/cnstock/mcp"
```

### daily_stock_analysis

```python
DAILY_STOCK_API = "http://127.0.0.1:8000"
```

---

## 🔧 依赖

```bash
pip install httpx
```

---

## 💡 使用场景

### 场景 1：每日复盘

```bash
# 分析自选股
python3 integrated_analysis.py SH600000
python3 integrated_analysis.py SH600519
python3 integrated_analysis.py SZ00700
```

### 场景 2：选股辅助

```bash
# 批量分析
for stock in SH600000 SH600519 SZ00700; do
    python3 integrated_analysis.py $stock
done
```

### 场景 3：定时任务

```bash
# 添加到 crontab
# 每天早上 9 点分析
0 9 * * * cd /root/.openclaw/workspace/scripts/stock-integration && python3 integrated_analysis.py SH600000
```

---

## ⚠️ 注意事项

1. **daily_stock_analysis 必须运行**
   - 检查: `ps aux | grep daily_stock_analysis`
   - 启动: `cd /root/.openclaw/workspace/daily_stock_analysis && python3 webui.py`

2. **网络连接**
   - MCP 服务需要外网访问
   - daily_stock_analysis 是本地服务

3. **股票代码格式**
   - 上海: SH + 6位数字
   - 深圳: SZ + 6位数字

---

## 🎉 特性

- ✅ 自动集成两个系统
- ✅ 生成结构化报告
- ✅ 自动保存到文件
- ✅ 支持 Markdown 格式
- ✅ 错误处理和提示

---

## 📝 版本历史

**v1.0.0** (2026-03-27)
- ✅ 初始版本
- ✅ MCP + daily_stock_analysis 集成
- ✅ 自动报告生成
