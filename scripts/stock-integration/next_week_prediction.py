#!/usr/bin/env python3
"""
下周股票预测
基于量化分析模型推荐
"""

import asyncio
from datetime import datetime
from pathlib import Path

# 导入量化分析器
import sys
sys.path.append('/root/.openclaw/workspace/scripts/stock-integration')
from quantitative_analysis import QuantitativeAnalyzer


class NextWeekPredictor:
    """下周预测器"""

    def __init__(self):
        self.analyzer = QuantitativeAnalyzer()

        # 热门股票池（蓝筹股）
        self.stock_pool = [
            ('SH600000', '浦发银行'),
            ('SH600036', '招商银行'),
            ('SH600519', '贵州茅台'),
            ('SH600887', '伊利股份'),
            ('SZ000001', '平安银行'),
            ('SZ000002', '万科A'),
            ('SZ000333', '美的集团'),
            ('SZ000858', '五粮液'),
        ]

    async def analyze_single(self, symbol: str, name: str) -> dict:
        """分析单个股票"""
        try:
            result = await self.analyzer.analyze(symbol)
            if result['success']:
                pred = result['prediction']
                sug = result['suggestions']
                indicators = result['indicators']

                # 计算得分
                score = 0

                # 技术面得分（40分）
                if 'kdj' in indicators:
                    kdj = indicators['kdj']
                    if kdj['K'] < 20:  # 超卖
                        score += 20
                    elif kdj['K'] < 40:  # 偏低
                        score += 10
                    elif kdj['K'] > 80:  # 超买
                        score -= 10

                # MACD 金叉死叉（20分）
                if 'macd' in indicators:
                    macd = indicators['macd']
                    if macd['DIF'] > macd['DEA']:
                        score += 20
                    else:
                        score -= 10

                # RSI 强弱（15分）
                if 'rsi' in indicators:
                    rsi = indicators['rsi']
                    if rsi['RSI6'] < 30:  # 超卖
                        score += 15
                    elif rsi['RSI6'] < 50:  # 偏弱
                        score += 5
                    elif rsi['RSI6'] > 70:  # 超买
                        score -= 10

                # 布林带位置（15分）
                if 'bollinger' in indicators and 'price' in indicators:
                    bb = indicators['bollinger']
                    price = indicators['price']['current']
                    if price < bb['lower']:  # 跌破下轨
                        score += 15
                    elif price < bb['middle']:  # 低于中轨
                        score += 5
                    elif price > bb['upper']:  # 突破上轨
                        score -= 10

                # 均线排列（10分）
                if 'ma' in indicators:
                    ma = indicators['ma']
                    if ma['MA5'] > ma['MA10'] > ma['MA30']:  # 多头排列
                        score += 10
                    elif ma['MA5'] < ma['MA10'] < ma['MA30']:  # 空头排列
                        score -= 5

                return {
                    'symbol': symbol,
                    'name': name,
                    'success': True,
                    'score': score,
                    'prediction': pred,
                    'suggestions': sug,
                    'indicators': indicators
                }
            else:
                return {
                    'symbol': symbol,
                    'name': name,
                    'success': False,
                    'error': result.get('error')
                }
        except Exception as e:
            return {
                'symbol': symbol,
                'name': name,
                'success': False,
                'error': str(e)
            }

    async def predict_next_week(self):
        """预测下周机会"""
        print("=" * 80)
        print("📊 下周股票机会预测")
        print("=" * 80)
        print(f"预测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"预测周期: 下周（{self.get_next_week_range()}）")
        print("=" * 80)
        print()

        # 分析所有股票
        results = []
        for symbol, name in self.stock_pool:
            print(f"🔍 分析 {name}（{symbol}）...")
            result = await self.analyze_single(symbol, name)
            results.append(result)
            print(f"   ✅ 完成（得分: {result.get('score', 0)}）" if result['success'] else f"   ❌ 失败")
            print()

        # 按得分排序
        successful = [r for r in results if r['success']]
        successful.sort(key=lambda x: x['score'], reverse=True)

        # 生成报告
        self.generate_report(successful)

    def get_next_week_range(self) -> str:
        """获取下周日期范围"""
        # 今天是 2026-03-27 周五
        # 下周一是 2026-03-31
        return "2026-03-31 至 2026-04-04"

    def generate_report(self, results: list):
        """生成预测报告"""
        print()
        print("=" * 80)
        print("📈 推荐股票排名")
        print("=" * 80)
        print()

        # 推荐（得分 > 20）
        recommended = [r for r in results if r['score'] > 20]

        if recommended:
            print("🌟 强烈推荐（得分 > 20）：")
            print()
            for i, r in enumerate(recommended[:3], 1):
                pred = r['prediction']
                sug = r['suggestions']
                indicators = r['indicators']

                print(f"{i}. {r['name']}（{r['symbol']}）- 得分: {r['score']}")
                print(f"   预测: {pred['direction'].upper()} (概率: {pred['probability']*100:.1f}%, 置信度: {pred['confidence']*100:.1f}%)")
                print(f"   仓位建议: {sug['position']}")
                print(f"   技术信号: {sug['signal']}")

                # 关键指标
                if 'kdj' in indicators:
                    kdj = indicators['kdj']
                    print(f"   KDJ: K={kdj['K']:.1f} ({'超卖' if kdj['K'] < 20 else '偏低' if kdj['K'] < 40 else '中性' if kdj['K'] < 60 else '偏高' if kdj['K'] < 80 else '超买'})")

                if 'macd' in indicators:
                    macd = indicators['macd']
                    signal = '金叉' if macd['DIF'] > macd['DEA'] else '死叉'
                    print(f"   MACD: {signal} (DIF={macd['DIF']:.2f}, DEA={macd['DEA']:.2f})")

                if 'price' in indicators and 'bollinger' in indicators:
                    price = indicators['price']['current']
                    bb = indicators['bollinger']
                    if price < bb['lower']:
                        position = '跌破下轨（超卖）'
                    elif price < bb['middle']:
                        position = '低于中轨'
                    elif price > bb['upper']:
                        position = '突破上轨（超买）'
                    else:
                        position = '中轨附近'
                    print(f"   位置: {position}")

                print()
        else:
            print("⚠️ 本周无强烈推荐股票")
            print()

        # 观望（得分 0-20）
        watch = [r for r in results if 0 <= r['score'] <= 20]

        if watch:
            print("👀 可以关注（得分 0-20）：")
            print()
            for i, r in enumerate(watch[:3], 1):
                print(f"{i}. {r['name']}（{r['symbol']}）- 得分: {r['score']}")
                pred = r['prediction']
                print(f"   预测: {pred['direction'].upper()} (概率: {pred['probability']*100:.1f}%)")
            print()

        # 风险提示
        print("=" * 80)
        print("⚠️ 风险提示")
        print("=" * 80)
        print()
        print("1. **量化预测不是保证**: 历史概率不代表未来结果")
        print("2. **市场充满不确定性**: 突发事件可能导致预测失效")
        print("3. **控制仓位**: 不要全仓，建议分散投资")
        print("4. **设置止损**: 跌破支撑位及时止损")
        print("5. **自己做决定**: 不要盲目相信任何预测，包括 AI")
        print()
        print("=" * 80)
        print("📊 报告结束")
        print("=" * 80)
        print()
        print("*本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。*")


async def main():
    """主函数"""
    predictor = NextWeekPredictor()
    await predictor.predict_next_week()


if __name__ == "__main__":
    asyncio.run(main())
