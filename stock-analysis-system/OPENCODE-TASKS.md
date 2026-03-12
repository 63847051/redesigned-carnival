# 📋 OpenCode 完善任务清单

**项目**: 股票分析系统
**位置**: /root/.openclaw/workspace/stock-analysis-system

---

## 🎯 任务目标

完善股票分析系统，添加以下功能：

---

## 📝 需要完成的任务

### 1. 基本面分析模块 (src/analysis/fundamental.py)

**功能要求**:
- 分析财务报表（收入、利润、现金流）
- 计算财务指标（ROE、ROA、毛利率、净利率）
- 估值分析（PE、PB、PS、PEG）
- 成长性分析（营收增长、利润增长）
- 与同行对比

**接口设计**:
```python
class FundamentalAnalysis:
    def analyze_financials(symbol: str) -> Dict
    def calculate_ratios(symbol: str) -> Dict
    def get_valuation(symbol: str) -> Dict
    def score_stock(symbol: str) -> int
```

---

### 2. 风险评估模块 (src/analysis/risk.py)

**功能要求**:
- 计算波动率
- 计算最大回撤
- 计算 VaR（风险价值）
- 计算夏普比率
- 风险等级评估

**接口设计**:
```python
class RiskAssessment:
    def calculate_volatility(df: DataFrame) -> float
    def calculate_max_drawdown(df: DataFrame) -> Dict
    def calculate_var(df: DataFrame, confidence: float) -> float
    def assess_risk_level(symbol: str) -> str
```

---

### 3. 增强的技术指标 (src/indicators/)

**需要添加的指标**:
- KDJ 随机指标
- 威廉指标 (Williams %R)
- ATR 真实波幅
- OBV 能量潮
- CCI 顺势指标

**文件结构**:
```
indicators/
├── __init__.py
├── kdj.py
├── williams.py
├── atr.py
├── obv.py
└── cci.py
```

---

### 4. 机器学习预测模块 (src/ml/predictor.py)

**功能要求**:
- 使用 LSTM 预测股价
- 使用 XGBoost 预测趋势
- 特征工程
- 模型训练和评估

**接口设计**:
```python
class StockPredictor:
    def train(symbol: str, days: int = 30)
    def predict(symbol: str, future_days: int) -> DataFrame
    def predict_trend(symbol: str) -> str
    def evaluate(symbol: str) -> Dict
```

---

### 5. 回测系统 (src/backtest/engine.py)

**功能要求**:
- 策略回测
- 计算收益率
- 计算最大回撤
- 计算夏普比率
- 生成回测报告

**接口设计**:
```python
class BacktestEngine:
    def run(strategy, symbol: str, period: str) -> Dict
    def calculate_metrics(df: DataFrame) -> Dict
    def generate_report() -> str
```

---

### 6. 增强 Web UI (web/app.py)

**需要添加的页面**:
- 基本面分析页面
- 风险评估页面
- 预测页面
- 回测页面

**功能增强**:
- 添加多股票对比
- 添加自选股功能
- 添加数据导出
- 优化图表展示

---

### 7. 测试文件 (tests/)

**需要创建的测试**:
```
tests/
├── __init__.py
├── test_fetcher.py
├── test_technical.py
├── test_fundamental.py
└── test_ml.py
```

---

## 🎯 优先级

### 高优先级（必须）
1. ✅ 基本面分析模块
2. ✅ 风险评估模块
3. ✅ 增强的技术指标

### 中优先级（重要）
4. ✅ 机器学习预测模块
5. ✅ 回测系统

### 低优先级（可选）
6. ✅ 增强 Web UI
7. ✅ 测试文件

---

## 📝 使用指南

### 启动 OpenCode
```bash
cd /root/.openclaw/workspace/stock-analysis-system
opencode
```

### 初始化项目
```
/init
```

### 提示词示例

#### 任务 1: 创建基本面分析模块
```
请创建 src/analysis/fundamental.py 文件，实现基本面分析功能。

功能包括：
1. 分析财务报表（收入、利润、现金流）
2. 计算财务指标（ROE、ROA、毛利率、净利率）
3. 估值分析（PE、PB、PS、PEG）
4. 成长性分析

使用 yfinance 获取财务数据。
参考现有的 src/analysis/technical.py 的代码风格。
```

#### 任务 2: 创建风险评估模块
```
请创建 src/analysis/risk.py 文件，实现风险评估功能。

功能包括：
1. 计算历史波动率
2. 计算最大回撤
3. 计算 VaR（风险价值）
4. 风险等级评估

参考现有的技术分析模块的代码风格。
```

#### 任务 3: 添加更多技术指标
```
请创建 src/indicators/ 目录，并添加以下指标：
1. KDJ 随机指标
2. 威廉指标 (Williams %R)
3. ATR 真实波幅
4. OBV 能量潮

每个指标单独一个文件，参考 technical.py 的实现方式。
```

#### 任务 4: 创建机器学习预测模块
```
请创建 src/ml/predictor.py 文件，实现股价预测功能。

要求：
1. 使用 LSTM 进行时间序列预测
2. 使用 XGBoost 进行趋势分类
3. 包含特征工程
4. 模型训练和评估函数

使用 scikit-learn 和 tensorflow/keras。
```

#### 任务 5: 创建回测系统
```
请创建 src/backtest/engine.py 文件，实现回测功能。

功能包括：
1. 策略回测引擎
2. 性能指标计算（收益率、回撤、夏普比率）
3. 回测报告生成
```

---

## 🔧 技术要求

### 代码风格
- 遵循 PEP 8 规范
- 添加类型注解
- 添加文档字符串
- 添加错误处理

### 测试
- 每个模块都要有对应的测试文件
- 测试覆盖率 > 80%

### 文档
- 每个函数都要有文档字符串
- 包含使用示例

---

## 📂 项目结构

```
stock-analysis-system/
├── src/
│   ├── analysis/
│   │   ├── technical.py       ✅ 已有
│   │   ├── fundamental.py     🆕 待创建
│   │   └── risk.py            🆕 待创建
│   ├── indicators/
│   │   ├── kdj.py             🆕 待创建
│   │   ├── williams.py         🆕 待创建
│   │   ├── atr.py             🆕 待创建
│   │   └── obv.py             🆕 待创建
│   ├── ml/
│   │   └── predictor.py       🆕 待创建
│   └── backtest/
│       └── engine.py          🆕 待创建
├── web/
│   └── app.py                 ✅ 已有，需增强
└── tests/                     🆕 待创建
```

---

## 🎯 成功标准

- [ ] 所有模块创建完成
- [ ] 代码通过测试
- [ ] Web UI 正常运行
- [ ] 文档完整

---

*创建时间: 2026-03-05*
*任务文件: OPENCODE-TASKS.md*
