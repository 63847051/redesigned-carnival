# 📊 股票分析系统

**版本**: v1.0
**设计者**: 大领导 🎯
**实现**: OpenCode AI

---

## 🎯 系统简介

一个专业级的股票分析系统，提供实时数据获取、技术分析、基本面分析、风险评估、机器学习预测和回测功能。

---

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行 Web 应用

```bash
streamlit run web/app.py
```

### 运行测试

```bash
bash scripts/run_tests.sh
```

---

## 📁 项目结构

```
stock-analysis-system/
├── README.md                   # 项目说明
├── requirements.txt            # Python 依赖
├── config/
│   └── settings.py             # 配置文件
├── src/
│   ├── data/                   # 数据获取模块
│   ├── analysis/               # 分析模块
│   ├── indicators/             # 技术指标
│   ├── strategies/             # 交易策略
│   ├── backtest/               # 回测系统
│   ├── ml/                     # 机器学习
│   └── utils/                  # 工具函数
├── web/                        # Streamlit 应用
├── api/                        # REST API
├── tests/                      # 测试
└── docs/                       # 文档
```

---

## 🎨 主要功能

### 1. 数据获取
- ✅ 实时股价（多数据源）
- ✅ 历史数据
- ✅ 财务报表
- ✅ 新闻资讯

### 2. 技术分析
- ✅ 移动平均线、MACD、RSI
- ✅ 布林带、KDJ
- ✅ 趋势识别
- ✅ 支撑/阻力位

### 3. 基本面分析
- ✅ 财务分析
- ✅ 估值分析
- ✅ 成长性分析

### 4. 机器学习
- ✅ 价格预测
- ✅ 趋势预测
- ✅ 风险评估

### 5. 回测系统
- ✅ 策略回测
- ✅ 性能评估
- ✅ 参数优化

---

## 📊 使用示例

### 查询股票
```python
from src.data.fetcher import DataFetcher

fetcher = DataFetcher()
df = fetcher.get_historical_data('600318.SS', '1y')
print(df.tail())
```

### 技术分析
```python
from src.analysis.technical import TechnicalAnalysis

ta = TechnicalAnalysis()
df = ta.calculate_indicators(df)
trend = ta.identify_trend(df)
print(f"趋势: {trend}")
```

### 机器学习预测
```python
from src.ml.predictor import MLPredictor

predictor = MLPredictor()
predictor.train('600318.SS')
prediction = predictor.predict('600318.SS', days=7)
print(prediction)
```

---

## 🎯 实施进度

- [x] 项目结构创建
- [ ] 数据获取模块
- [ ] 技术分析模块
- [ ] 基本面分析模块
- [ ] 机器学习模块
- [ ] 回测系统
- [ ] Web UI
- [ ] API 开发

---

## 📝 设计文档

完整设计文档请参阅: [STOCK-ANALYSIS-SYSTEM-DESIGN.md](../STOCK-ANALYSIS-SYSTEM-DESIGN.md)

---

## 🤝 贡献

由大领导 🎯 设计，OpenCode AI 实现。

---

## 📄 许可

MIT License

---

*创建时间: 2026-03-05*
*版本: v1.0*
