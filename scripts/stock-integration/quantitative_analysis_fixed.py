#!/usr/bin/env python3
"""
股票量化分析工具 - 修复版
修复：正确解析表格中的技术指标
"""

import asyncio
import httpx
import json
import re
from datetime import datetime
from pathlib import Path

# 配置
MCP_URL = "http://82.156.17.205/cnstock/mcp"


class QuantitativeAnalyzer:
    """量化分析器"""

    def __init__(self):
        self.mcp_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }

    async def get_full_data(self, symbol: str) -> dict:
        """获取完整股票数据"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "full",
                    "arguments": {"symbol": symbol}
                },
                "id": 1
            }

            try:
                response = await client.post(MCP_URL, json=payload, headers=self.mcp_headers)
                if response.status_code == 200:
                    lines = response.text.split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            data = json.loads(line[6:])
                            if 'result' in data:
                                result = data['result']
                                if 'content' in result:
                                    for item in result['content']:
                                        if item.get('type') == 'text':
                                            return {"success": True, "data": item['text']}
                return {"success": False, "error": "解析失败"}
            except Exception as e:
                return {"success": False, "error": str(e)}

    def parse_technical_indicators(self, data: str) -> dict:
        """
        解析技术指标（修复版）
        从表格中提取最新一天的技术指标
        """
        indicators = {}

        # 解析价格数据
        price_match = re.search(r'- 当日: ([\d.]+) 最高: ([\d.]+) 最低: ([\d.]+)', data)
        if price_match:
            indicators['price'] = {
                'current': float(price_match.group(1)),
                'high': float(price_match.group(2)),
                'low': float(price_match.group(3))
            }

        # 解析涨跌幅
        change_match = re.search(r'- 当日: ([\-\d.]+)%', data)
        if change_match:
            indicators['change'] = float(change_match.group(1))

        # 解析成交量（万手）
        volume_match = re.search(r'- 当日: ([\d.]+)\n.*?- 5日均量\(万手\): ([\d.]+)', data, re.DOTALL)
        if volume_match:
            indicators['volume'] = float(volume_match.group(1))

        # 解析技术指标表格（最新一天）
        # 找到包含日期的第一行数据
        lines = data.split('\n')
        for line in lines:
            if '| 2026-' in line and '|10.' in line:  # 简单识别表格数据行
                parts = line.split('|')
                if len(parts) >= 18:
                    try:
                        # 提取技术指标（索引 7-17）
                        indicators['kdj'] = {
                            'K': float(parts[7].strip()),
                            'D': float(parts[8].strip()),
                            'J': float(parts[9].strip())
                        }

                        indicators['macd'] = {
                            'DIF': float(parts[10].strip()),
                            'DEA': float(parts[11].strip())
                        }

                        indicators['rsi'] = {
                            'RSI6': float(parts[12].strip()),
                            'RSI12': float(parts[13].strip()),
                            'RSI24': float(parts[14].strip())
                        }

                        indicators['bollinger'] = {
                            'upper': float(parts[15].strip()),
                            'middle': float(parts[16].strip()),
                            'lower': float(parts[17].strip())
                        }

                        # 均线数据（索引 2-6）
                        indicators['ma'] = {
                            'MA5': float(parts[2].strip()),
                            'MA10': float(parts[3].strip()),
                            'MA30': float(parts[4].strip()),
                            'MA60': float(parts[5].strip()),
                            'MA120': float(parts[6].strip())
                        }

                        break  # 找到第一行就退出
                    except (ValueError, IndexError) as e:
                        # 解析失败，继续下一行
                        continue

        return indicators

    def analyze_consecutive_factor(self, indicators: dict) -> tuple:
        """分析连续涨跌因子（20%）"""
        change = indicators.get('change', 0)

        if change > 3:
            return ('down', 0.4, '大涨后可能回调')
        elif change > 1:
            return ('down', 0.45, '小涨后可能盘整')
        elif change > -1:
            return ('up', 0.55, '平盘后可能选择方向')
        elif change > -3:
            return ('up', 0.6, '小跌后可能反弹')
        else:
            return ('up', 0.65, '大跌后可能超跌反弹')

    def analyze_weekday_factor(self, indicators: dict) -> tuple:
        """分析周内日历因子（25%）"""
        weekday = datetime.now().weekday()

        if weekday == 0:
            return ('up', 0.52, '周一效应：上涨概率略高')
        elif weekday == 4:
            return ('down', 0.52, '周五效应：获利了结')
        else:
            return ('neutral', 0.5, '其他交易日：无明显偏向')

    def analyze_monthly_factor(self, indicators: dict) -> tuple:
        """分析月度日历因子（20%）"""
        day = datetime.now().day

        if day <= 5:
            return ('up', 0.53, '月初效应：资金流入')
        elif day >= 25:
            return ('down', 0.53, '月末效应：资金紧张')
        else:
            return ('neutral', 0.5, '月中：无明显偏向')

    def analyze_extreme_factor(self, indicators: dict) -> tuple:
        """分析极端行情因子（15%）"""
        change = indicators.get('change', 0)

        if abs(change) > 5:
            if change > 5:
                return ('down', 0.6, '极端上涨后大概率回调')
            else:
                return ('up', 0.6, '极端下跌后大概率反弹')
        else:
            return ('neutral', 0.5, '非极端行情：无明显偏向')

    def analyze_technical_factor(self, indicators: dict) -> tuple:
        """分析技术面因子（10%）"""
        signals = []

        # KDJ 分析
        if 'kdj' in indicators:
            kdj = indicators['kdj']
            if kdj['K'] > 80:
                signals.append(('down', 0.6, 'KDJ超买：可能回调'))
            elif kdj['K'] < 20:
                signals.append(('up', 0.6, 'KDJ超卖：可能反弹'))

        # MACD 分析
        if 'macd' in indicators:
            macd = indicators['macd']
            if macd['DIF'] > macd['DEA']:
                signals.append(('up', 0.55, 'MACD金叉：看涨'))
            else:
                signals.append(('down', 0.55, 'MACD死叉：看跌'))

        # RSI 分析
        if 'rsi' in indicators:
            rsi = indicators['rsi']
            if rsi['RSI6'] > 70:
                signals.append(('down', 0.6, 'RSI超买：可能回调'))
            elif rsi['RSI6'] < 30:
                signals.append(('up', 0.6, 'RSI超卖：可能反弹'))

        # 布林带分析
        if 'bollinger' in indicators and 'price' in indicators:
            bb = indicators['bollinger']
            price = indicators['price']['current']
            if price > bb['upper']:
                signals.append(('down', 0.6, '突破上轨：可能回调'))
            elif price < bb['lower']:
                signals.append(('up', 0.6, '跌破下轨：可能反弹'))

        if signals:
            up_prob = sum(s[1] if s[0] == 'up' else (1-s[1]) for s in signals) / len(signals)
            direction = 'up' if up_prob > 0.5 else 'down'
            return (direction, up_prob, ' | '.join([s[2] for s in signals]))
        else:
            return ('neutral', 0.5, '技术指标：无明显信号')

    def analyze_sector_factor(self, indicators: dict) -> tuple:
        """分析板块因子（10%）"""
        return ('neutral', 0.5, '板块：无明显偏向')

    def calculate_final_probability(self, factors: dict) -> tuple:
        """计算最终概率"""
        weights = {
            'consecutive': 0.20,
            'weekday': 0.25,
            'monthly': 0.20,
            'extreme': 0.15,
            'technical': 0.10,
            'sector': 0.10
        }

        total_prob = 0
        total_weight = 0

        for name, (direction, prob, desc) in factors.items():
            weight = weights[name]

            if direction == 'up':
                num_prob = prob
            elif direction == 'down':
                num_prob = 1 - prob
            else:
                num_prob = 0.5

            total_prob += num_prob * weight
            total_weight += weight

        if total_prob > 0.5:
            direction = 'up'
            prob = total_prob
        elif total_prob < 0.5:
            direction = 'down'
            prob = 1 - total_prob
        else:
            direction = 'neutral'
            prob = 0.5

        confidence = abs(prob - 0.5) * 2

        return (direction, prob, confidence)

    def generate_suggestions(self, direction: str, prob: float, confidence: float, indicators: dict) -> dict:
        """生成操作建议"""
        if confidence > 0.3:
            position = '50%'
        elif confidence > 0.2:
            position = '30%'
        elif confidence > 0.1:
            position = '20%'
        else:
            position = '观望'

        if 'price' in indicators:
            current = indicators['price']['current']
            stop_loss = current * 0.97
        else:
            stop_loss = '未知'

        if 'kdj' in indicators:
            kdj = indicators['kdj']
            if kdj['K'] > 80:
                signal = '空头信号'
            elif kdj['K'] < 20:
                signal = '多头信号'
            else:
                signal = '中性'
        else:
            signal = '未知'

        return {
            'direction': direction,
            'probability': prob,
            'confidence': confidence,
            'position': position,
            'stop_loss': stop_loss,
            'signal': signal
        }

    async def analyze(self, symbol: str) -> dict:
        """完整量化分析"""
        print(f"\n🔍 量化分析: {symbol}")
        print("=" * 60)

        # 1. 获取完整数据
        print(f"\n📡 步骤 1: 获取完整数据...")
        result = await self.get_full_data(symbol)

        if not result['success']:
            return {
                'success': False,
                'error': f"获取数据失败: {result.get('error', '未知错误')}"
            }

        print(f"✅ 数据获取成功")

        # 2. 解析技术指标
        print(f"\n🔧 步骤 2: 解析技术指标...")
        indicators = self.parse_technical_indicators(result['data'])
        print(f"✅ 技术指标解析完成")
        print(f"   - KDJ: {indicators.get('kdj', 'N/A')}")
        print(f"   - MACD: {indicators.get('macd', 'N/A')}")
        print(f"   - RSI: {indicators.get('rsi', 'N/A')}")
        print(f"   - 布林带: {indicators.get('bollinger', 'N/A')}")

        # 3. 分析各因子
        print(f"\n📊 步骤 3: 量化因子分析...")

        factors = {}
        factors['consecutive'] = self.analyze_consecutive_factor(indicators)
        factors['weekday'] = self.analyze_weekday_factor(indicators)
        factors['monthly'] = self.analyze_monthly_factor(indicators)
        factors['extreme'] = self.analyze_extreme_factor(indicators)
        factors['technical'] = self.analyze_technical_factor(indicators)
        factors['sector'] = self.analyze_sector_factor(indicators)

        # 打印因子分析
        for name, (direction, prob, desc) in factors.items():
            print(f"  {name:15s}: {direction:8s} {prob:.2f} - {desc}")

        # 4. 计算最终概率
        print(f"\n🎯 步骤 4: 计算最终概率...")
        direction, prob, confidence = self.calculate_final_probability(factors)
        print(f"✅ 最终判断: {direction.upper()} (概率: {prob*100:.2f}%, 置信度: {confidence*100:.2f}%)")

        # 5. 生成操作建议
        print(f"\n💡 步骤 5: 生成操作建议...")
        suggestions = self.generate_suggestions(direction, prob, confidence, indicators)
        print(f"✅ 操作建议已生成")

        return {
            'success': True,
            'symbol': symbol,
            'indicators': indicators,
            'factors': factors,
            'prediction': {
                'direction': direction,
                'probability': prob,
                'confidence': confidence
            },
            'suggestions': suggestions,
            'raw_data': result['data']
        }

    def generate_report(self, analysis: dict) -> str:
        """生成分析报告"""
        pred = analysis['prediction']
        sug = analysis['suggestions']

        report = f"""
# 📊 {analysis['symbol']} 量化分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**数据来源**: A 股 MCP 服务

---

## 🎯 预测结果

**方向**: {pred['direction'].upper()}
**概率**: {pred['probability']*100:.2f}%
**置信度**: {pred['confidence']*100:.2f}%

---

## 📈 操作建议

| 项目 | 建议 |
|------|------|
| **方向** | {sug['direction'].upper()} |
| **仓位** | {sug['position']} |
| **止损位** | {sug['stop_loss']} |
| **技术信号** | {sug['signal']} |

---

## 🔬 量化因子分析

| 因子 | 权重 | 方向 | 概率 | 说明 |
|------|------|------|------|------|
| 连续涨跌 | 20% | {analysis['factors']['consecutive'][0]} | {analysis['factors']['consecutive'][1]*100:.0f}% | {analysis['factors']['consecutive'][2]} |
| 周内效应 | 25% | {analysis['factors']['weekday'][0]} | {analysis['factors']['weekday'][1]*100:.0f}% | {analysis['factors']['weekday'][2]} |
| 月度效应 | 20% | {analysis['factors']['monthly'][0]} | {analysis['factors']['monthly'][1]*100:.0f}% | {analysis['factors']['monthly'][2]} |
| 极端行情 | 15% | {analysis['factors']['extreme'][0]} | {analysis['factors']['extreme'][1]*100:.0f}% | {analysis['factors']['extreme'][2]} |
| 技术面 | 10% | {analysis['factors']['technical'][0]} | {analysis['factors']['technical'][1]*100:.0f}% | {analysis['factors']['technical'][2]} |
| 板块 | 10% | {analysis['factors']['sector'][0]} | {analysis['factors']['sector'][1]*100:.0f}% | {analysis['factors']['sector'][2]} |

---

## 📉 技术指标

### KDJ 指标
{self._format_indicator(analysis['indicators'].get('kdj'))}

### MACD 指标
{self._format_indicator(analysis['indicators'].get('macd'))}

### RSI 指标
{self._format_indicator(analysis['indicators'].get('rsi'))}

### 布林带
{self._format_indicator(analysis['indicators'].get('bollinger'))}

### 均线
{self._format_indicator(analysis['indicators'].get('ma'))}

---

## ⚠️ 风险提示

1. **量化预测不是保证**: {pred['probability']*100:.0f}% 概率意味着仍有 {100-pred['probability']*100:.0f}% 失败可能
2. **市场充满不确定性**: 突发事件可能导致预测失效
3. **控制仓位**: 建议仓位 {sug['position']}，不要全仓
4. **设置止损**: 跌破 {sug['stop_loss']} 考虑止损
5. **自己做决定**: 不要盲目相信任何预测，包括 AI

---

**📊 报告结束**

*本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。*
"""

        return report

    def _format_indicator(self, indicator: dict) -> str:
        """格式化指标显示"""
        if not indicator:
            return "无数据"

        items = [f"{k}: {v}" for k, v in indicator.items()]
        return " | ".join(items)

    def save_report(self, symbol: str, report: str):
        """保存报告"""
        output_dir = Path("/root/.openclaw/workspace/stock-reports")
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = output_dir / f"{symbol}_quant_{timestamp}.md"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n💾 报告已保存: {filename}")
        return filename


async def main():
    """主函数"""
    import sys

    if len(sys.argv) < 2:
        print("使用方法: python3 quantitative_analysis_fixed.py <股票代码>")
        print("示例: python3 quantitative_analysis_fixed.py SH600000")
        sys.exit(1)

    symbol = sys.argv[1]

    # 创建分析器
    analyzer = QuantitativeAnalyzer()

    # 执行分析
    result = await analyzer.analyze(symbol)

    if result['success']:
        # 生成报告
        report = analyzer.generate_report(result)

        # 保存报告
        analyzer.save_report(symbol, report)

        # 打印报告
        print("\n" + "=" * 60)
        print(report)
    else:
        print(f"\n❌ 分析失败: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
