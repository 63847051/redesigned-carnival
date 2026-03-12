#!/bin/bash
# =============================================================================
# 🤖 使用 OpenCode 完善股票分析系统
# =============================================================================

echo "🤖 使用 OpenCode 完善股票分析系统"
echo "======================================"
echo ""

# 检查 OpenCode
if ! command -v opencode &> /dev/null; then
    echo "❌ OpenCode 未安装"
    echo "请先运行: curl -fsSL https://opencode.ai/install | bash"
    exit 1
fi

echo "✅ OpenCode 已安装"
echo ""

# 进入项目目录
cd "$(dirname "$0")"

echo "📂 当前项目: $(pwd)"
echo ""

echo "🚀 启动 OpenCode..."
echo ""
echo "----------------------------------------"
echo "📝 OpenCode 使用指南"
echo "----------------------------------------"
echo ""
echo "1. OpenCode 将自动启动"
echo "2. 按 Tab 切换 Build/Plan 模式"
echo "3. 输入任务或复制下面的提示词"
echo ""
echo "📋 推荐任务顺序："
echo ""
echo "✅ 任务 1: 基本面分析模块"
echo '请创建 src/analysis/fundamental.py 文件，实现基本面分析功能。'
echo ""
echo "✅ 任务 2: 风险评估模块"
echo '请创建 src/analysis/risk.py 文件，实现风险评估功能。'
echo ""
echo "✅ 任务 3: 技术指标"
echo '请创建 src/indicators/ 目录，添加 KDJ、Williams %R、ATR、OBV 等指标。'
echo ""
echo "✅ 任务 4: 机器学习预测"
echo '请创建 src/ml/predictor.py，使用 LSTM 和 XGBoost 进行股价预测。'
echo ""
echo "✅ 任务 5: 回测系统"
echo '请创建 src/backtest/engine.py，实现策略回测功能。'
echo ""
echo "----------------------------------------"
echo "📚 详细任务清单: OPENCODE-TASKS.md"
echo "----------------------------------------"
echo ""
echo "⏳ 5 秒后启动 OpenCode..."
sleep 5

# 启动 OpenCode
opencode
