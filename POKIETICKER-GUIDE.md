# 📊 PokieTicker 安装和配置指南

**项目**: https://github.com/owengetinfo-design/PokieTicker
**安装时间**: 2026-03-28 12:17
**状态**: ✅ 安装中

---

## 🎯 项目概述

**PokieTicker** 是一个股票新闻分析工具，结合了：

- 📊 **K线图可视化** - D3.js 交互式图表
- 📰 **新闻事件分析** - 新闻点标注在K线图上
- 🤖 **AI 解释价格波动** - Claude AI 分析
- 📈 **XGBoost 预测模型** - 31个特征的预测系统

### 核心功能

1. **News on the chart**
   - K线图上的点代表新闻
   - 点击任何点查看当天的新闻

2. **Filter by impact type**
   - 按影响类型过滤（市场、财报、产品、政策、竞争、管理）

3. **Find similar events**
   - 发现具有相似新闻模式的历史日期

4. **AI explains price moves**
   - 选择日期范围，询问 AI 为什么股票下跌或上涨

5. **Predict trends**
   - 基于过去30天的新闻事件预测未来价格方向

---

## 🚀 技术栈

### 前端
- React
- TypeScript
- Vite
- D3.js

### 后端
- FastAPI
- SQLite (WAL mode)
- Pydantic

### AI
- Claude Haiku 4.5（批量情感分析）
- Claude Sonnet（深度分析）

### ML
- XGBoost（预测）
- Cosine similarity（模式匹配）

### 数据
- Polygon.io REST API

---

## 📦 安装步骤

### 1. 克隆项目

```bash
cd /root/.openclaw/workspace
git clone https://github.com/owengetinfo-design/PokieTicker.git
cd PokieTicker
```

### 2. 解压数据库和模型

```bash
# 解压数据库
gunzip -k pokieticker.db.gz

# 解压模型
tar xzf models.tar.gz -C backend/ml/
```

### 3. 安装后端依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 安装前端依赖

```bash
cd frontend
npm install
cd ..
```

### 5. 启动服务

**方法 1: 使用启动脚本（推荐）**

```bash
bash /root/.openclaw/workspace/scripts/start-pokieticker.sh
```

**方法 2: 手动启动**

```bash
# Terminal 1: 后端
source venv/bin/activate
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: 前端
cd frontend
npm run dev -- --host 0.0.0.0 --port 7777
```

---

## 🌐 访问地址

### 前端界面
```
http://43.134.63.176:7777/PokieTicker/
```

### 后端 API 文档
```
http://43.134.63.176:8000/docs
```

---

## 🔧 配置（可选）

如果需要获取最新股票数据和运行 AI 分析，配置 API keys：

```bash
cp .env.example .env
# 编辑 .env 并填写你的 keys
```

### API Keys

| Key | 来源 | 成本 |
|-----|------|------|
| POLYGON_API_KEY | [polygon.io](https://polygon.io/) | Free tier |
| ANTHROPIC_API_KEY | [console.anthropic.com](https://console.anthropic.com/) | Pay-as-you-go |

---

## 📊 数据更新

### 获取最新数据

```bash
# 获取最新 OHLC + 新闻
python -m backend.bulk_fetch

# 运行 AI 分析
python -m backend.batch_submit --top 50
python -m backend.batch_collect <batch_id>
```

### 每周增量更新

```bash
# 获取自上次更新以来的最新 OHLC + 新闻
python -m backend.weekly_update

# 对新文章运行 AI 分析
python -m backend.batch_submit --top 50
python -m backend.batch_collect <batch_id>
```

---

## 💰 成本估算

| 项目 | 成本 |
|------|------|
| Polygon 数据（免费层）| $0 |
| Layer 1 Batch API（每1000篇文章）| ~$0.35 |
| Layer 2 按需（每篇文章）| ~$0.003 |
| 每周增量更新 | ~$1-2 |

---

## 🎯 使用场景

1. **学习股票市场**
   - 理解K线图背后的故事
   - 了解新闻如何影响价格

2. **事件驱动思维**
   - 理解每次价格变动的原因
   - 发现历史相似事件

3. **AI 辅助分析**
   - AI 解释价格波动
   - 预测未来趋势

---

## 📁 项目结构

```
PokieTicker/
├── backend/
│   ├── api/
│   │   └── main.py          # FastAPI 应用
│   ├── ml/
│   │   ├── features.py      # 31个特征工程
│   │   ├── model.py         # XGBoost 训练
│   │   └── inference.py     # 预测生成
│   ├── pipeline/
│   │   ├── layer0.py        # 规则过滤器
│   │   ├── layer1.py        # Claude Haiku 批量分析
│   │   └── layer2.py        # Claude Sonnet 深度分析
│   └── bulk_fetch.py        # 批量下载
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── CandlestickChart.tsx    # D3.js 图表
│       │   ├── NewsPanel.tsx           # 新闻面板
│       │   └── PredictionPanel.tsx     # 预测面板
│       └── App.tsx
├── pokieticker.db          # SQLite 数据库
└── models.tar.gz           # XGBoost 模型
```

---

## 🔍 故障排除

### 问题 1: 后端启动失败

**检查日志**:
```bash
cat /tmp/pokie-backend-server.log
```

**常见原因**:
- 虚拟环境未激活
- 依赖未安装
- 端口 8000 被占用

### 问题 2: 前端无法连接后端

**检查后端是否运行**:
```bash
curl http://localhost:8000/docs
```

**检查 CORS 配置**

### 问题 3: 数据库未找到

**确认数据库已解压**:
```bash
ls -la pokieticker.db
```

---

## 📞 获取帮助

- **GitHub**: https://github.com/owengetinfo-design/PokieTicker
- **Issues**: https://github.com/owengetinfo-design/PokieTicker/issues
- **Live Demo**: https://mitrui.com/PokieTicker/

---

## ⚠️ 免责声明

这是一个用于学习的实验性工具，不构成财务建议。市场是复杂的，没有模型能捕捉所有因素。

---

**状态**: ✅ 安装中
**下一步**: 等待后端依赖安装完成
**版本**: Latest
**更新**: 2026-03-28 12:17
