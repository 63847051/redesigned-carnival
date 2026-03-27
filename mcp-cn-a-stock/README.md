# A 股 MCP 代理服务器

**版本**: 1.0.0
**创建时间**: 2026-03-27
**状态**: ✅ 已创建

---

## 🎯 功能

### 工具 1: brief(stock_code)
获取股票基本信息和行情数据

**输入**:
- `stock_code`: 股票代码，例如 "SH600000"（浦发银行）

**输出**:
- 股票名称
- 所属板块
- 当前行情数据

---

### 工具 2: medium(stock_code)
获取股票基本数据 + 财务数据

**输入**:
- `stock_code`: 股票代码，例如 "SH600000"（浦发银行）

**输出**:
- 基本信息
- 近年主要财务数据

---

### 工具 3: full(stock_code)
获取完整股票数据 + 技术指标

**输入**:
- `stock_code`: 股票代码，例如 "SH600000"（浦发银行）

**输出**:
- 所有数据
- 技术指标（KDJ、MACD、RSI、布林带等）

---

## 🚀 使用方式

### 安装依赖
```bash
cd /root/.openclaw/workspace/mcp-cn-a-stock
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 配置 OpenClaw
将 `config.json` 中的内容添加到 `/root/.openclaw/openclaw.json`：

```json
{
  "mcpServers": {
    "cn-a-stock": {
      "command": "python3",
      "args": ["server.py"],
      "cwd": "/root/.openclaw/workspace/mcp-cn-a-stock",
      "env": {}
    }
  }
}
```

### 测试
```bash
# 激活虚拟环境
source venv/bin/activate

# 运行服务器
python3 server.py
```

---

## 📡 远程服务

**原始服务**: http://82.156.17.205/cnstock/mcp
**项目地址**: https://github.com/elsejj/mcp-cn-a-stock

---

## ⚠️ 免责声明

本项目仅作为学习和研究使用。股票数据仅供参考，不构成投资建议。
投资有风险，入市需谨慎。

---

## 📝 注意事项

1. 股票代码格式：
   - 上海证券交易所：SH + 6位数字（如 SH600000）
   - 深圳证券交易所：SZ + 6位数字（如 SZ000001）

2. 数据来源：远程 MCP 服务
3. 免费服务：目前限时免费，可能有限流

---

## 🔧 依赖项

- fastmcp >= 0.11.0
- httpx >= 0.27.0
- Python 3.10+
