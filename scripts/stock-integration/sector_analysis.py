#!/usr/bin/env python3
"""
综合板块分析工具
分析5大热门板块：AI、新能源、半导体、医药生物、消费升级
预测下周（2026-03-31 ~ 2026-04-04）表现
"""

import asyncio
import httpx
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import sys

sys.path.insert(0, "/root/.openclaw/workspace/daily_stock_analysis")
sys.path.insert(0, "/root/.openclaw/workspace/scripts/stock-integration")

MCP_URL = "http://82.156.17.205/cnstock/mcp"

SECTOR_STOCKS = {
    "人工智能": ["SZ000998", "SH688777", "SH688395", "SZ300750", "SH603259"],
    "新能源": ["SH600438", "SH600011", "SH600905", "SZ002594", "SZ002466"],
    "半导体": ["SH688981", "SH688008", "SZ002475", "SH688126", "SH688396"],
    "医药生物": ["SH600276", "SZ300760", "SZ002727", "SH600566", "SZ300529"],
    "消费升级": ["SH600519", "SZ000568", "SH603288", "SZ002594", "SH600754"],
}


class SectorAnalyzer:
    def __init__(self):
        self.mcp_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }

    async def get_full_data(self, symbol: str) -> dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": "full", "arguments": {"symbol": symbol}},
                "id": 1,
            }
            try:
                response = await client.post(
                    MCP_URL, json=payload, headers=self.mcp_headers
                )
                if response.status_code == 200:
                    lines = response.text.split("\n")
                    for line in lines:
                        if line.startswith("data: "):
                            data = json.loads(line[6:])
                            if "result" in data:
                                result = data["result"]
                                if "content" in result:
                                    for item in result["content"]:
                                        if item.get("type") == "text":
                                            return {
                                                "success": True,
                                                "data": item["text"],
                                            }
                return {"success": False, "error": "解析失败"}
            except Exception as e:
                return {"success": False, "error": str(e)}

    def parse_technical_indicators(self, data: str) -> dict:
        indicators = {}

        price_match = re.search(r"- 当日: ([\d.]+) 最高: ([\d.]+) 最低: ([\d.]+)", data)
        if price_match:
            indicators["price"] = {
                "current": float(price_match.group(1)),
                "high": float(price_match.group(2)),
                "low": float(price_match.group(3)),
            }

        change_match = re.search(r"- 当日: ([\-\d.]+)%", data)
        if change_match:
            indicators["change"] = float(change_match.group(1))

        lines = data.split("\n")
        for line in lines:
            if "| 2026-" in line and "|10." in line:
                parts = line.split("|")
                if len(parts) >= 18:
                    try:
                        indicators["kdj"] = {
                            "K": float(parts[7].strip()),
                            "D": float(parts[8].strip()),
                            "J": float(parts[9].strip()),
                        }
                        indicators["macd"] = {
                            "DIF": float(parts[10].strip()),
                            "DEA": float(parts[11].strip()),
                        }
                        indicators["rsi"] = {
                            "RSI6": float(parts[12].strip()),
                            "RSI12": float(parts[13].strip()),
                            "RSI24": float(parts[14].strip()),
                        }
                        indicators["bollinger"] = {
                            "upper": float(parts[15].strip()),
                            "middle": float(parts[16].strip()),
                            "lower": float(parts[17].strip()),
                        }
                        indicators["ma"] = {
                            "MA5": float(parts[2].strip()),
                            "MA10": float(parts[3].strip()),
                            "MA30": float(parts[4].strip()),
                            "MA60": float(parts[5].strip()),
                            "MA120": float(parts[6].strip()),
                        }
                        break
                    except (ValueError, IndexError):
                        continue

        return indicators

    def analyze_consecutive_factor(self, indicators: dict) -> tuple:
        change = indicators.get("change", 0)
        if change > 3:
            return ("down", 0.4)
        elif change > 1:
            return ("down", 0.45)
        elif change > -1:
            return ("up", 0.55)
        elif change > -3:
            return ("up", 0.6)
        else:
            return ("up", 0.65)

    def analyze_weekday_factor(self) -> tuple:
        weekday = datetime.now().weekday()
        if weekday == 0:
            return ("up", 0.52)
        elif weekday == 4:
            return ("down", 0.52)
        else:
            return ("neutral", 0.5)

    def analyze_monthly_factor(self) -> tuple:
        day = datetime.now().day
        if day <= 5:
            return ("up", 0.53)
        elif day >= 25:
            return ("down", 0.53)
        else:
            return ("neutral", 0.5)

    def analyze_extreme_factor(self, indicators: dict) -> tuple:
        change = indicators.get("change", 0)
        if abs(change) > 5:
            if change > 5:
                return ("down", 0.6)
            else:
                return ("up", 0.6)
        else:
            return ("neutral", 0.5)

    def analyze_technical_factor(self, indicators: dict) -> tuple:
        signals = []

        if "kdj" in indicators:
            kdj = indicators["kdj"]
            if kdj["K"] > 80:
                signals.append(("down", 0.6))
            elif kdj["K"] < 20:
                signals.append(("up", 0.6))

        if "macd" in indicators:
            macd = indicators["macd"]
            if macd["DIF"] > macd["DEA"]:
                signals.append(("up", 0.55))
            else:
                signals.append(("down", 0.55))

        if "rsi" in indicators:
            rsi = indicators["rsi"]
            if rsi["RSI6"] > 70:
                signals.append(("down", 0.6))
            elif rsi["RSI6"] < 30:
                signals.append(("up", 0.6))

        if "bollinger" in indicators and "price" in indicators:
            bb = indicators["bollinger"]
            price = indicators["price"]["current"]
            if price > bb["upper"]:
                signals.append(("down", 0.6))
            elif price < bb["lower"]:
                signals.append(("up", 0.6))

        if signals:
            up_prob = sum(s[1] if s[0] == "up" else (1 - s[1]) for s in signals) / len(
                signals
            )
            direction = "up" if up_prob > 0.5 else "down"
            return (direction, up_prob)
        else:
            return ("neutral", 0.5)

    def analyze_ma_factor(self, indicators: dict) -> tuple:
        if "ma" not in indicators or "price" not in indicators:
            return ("neutral", 0.5)

        ma = indicators["ma"]
        price = indicators["price"]["current"]

        up_count = 0
        if price > ma["MA5"]:
            up_count += 1
        if ma["MA5"] > ma["MA10"]:
            up_count += 1
        if ma["MA10"] > ma["MA30"]:
            up_count += 1
        if ma["MA30"] > ma["MA60"]:
            up_count += 1

        if up_count >= 4:
            return ("up", 0.65)
        elif up_count >= 2:
            return ("up", 0.55)
        elif up_count >= 1:
            return ("neutral", 0.5)
        else:
            return ("down", 0.55)

    def calculate_sector_score(self, indicators: dict) -> dict:
        weights = {
            "consecutive": 0.15,
            "weekday": 0.15,
            "monthly": 0.10,
            "extreme": 0.10,
            "technical": 0.25,
            "ma": 0.25,
        }

        factors = {}
        factors["consecutive"] = self.analyze_consecutive_factor(indicators)
        factors["weekday"] = self.analyze_weekday_factor()
        factors["monthly"] = self.analyze_monthly_factor()
        factors["extreme"] = self.analyze_extreme_factor(indicators)
        factors["technical"] = self.analyze_technical_factor(indicators)
        factors["ma"] = self.analyze_ma_factor(indicators)

        total_prob = 0
        total_weight = 0

        for name, (direction, prob) in factors.items():
            weight = weights[name]
            if direction == "up":
                num_prob = prob
            elif direction == "down":
                num_prob = 1 - prob
            else:
                num_prob = 0.5
            total_prob += num_prob * weight
            total_weight += weight

        final_prob = total_prob / total_weight if total_weight > 0 else 0.5

        if final_prob > 0.52:
            direction = "UP"
            confidence = min((final_prob - 0.5) * 2, 1.0)
        elif final_prob < 0.48:
            direction = "DOWN"
            confidence = min((0.5 - final_prob) * 2, 1.0)
        else:
            direction = "NEUTRAL"
            confidence = 0.2

        return {
            "direction": direction,
            "probability": final_prob,
            "confidence": confidence,
            "factors": factors,
            "indicators": indicators,
        }

    async def analyze_stock(self, symbol: str) -> dict:
        result = await self.get_full_data(symbol)
        if not result["success"]:
            return {"success": False, "error": result["error"]}

        indicators = self.parse_technical_indicators(result["data"])
        score = self.calculate_sector_score(indicators)

        return {
            "success": True,
            "symbol": symbol,
            "indicators": indicators,
            "score": score,
        }

    async def analyze_sector(self, sector_name: str, stocks: List[str]) -> dict:
        print(f"\n{'=' * 60}")
        print(f"📊 分析板块: {sector_name}")
        print(f"{'=' * 60}")

        stock_results = []
        for symbol in stocks:
            print(f"  🔍 {symbol}...", end=" ")
            result = await self.analyze_stock(symbol)
            if result["success"]:
                stock_results.append(result)
                print(f"✓ (方向: {result['score']['direction']})")
            else:
                print(f"✗ ({result.get('error', 'error')})")

        if not stock_results:
            return {"success": False, "sector": sector_name}

        avg_prob = sum(r["score"]["probability"] for r in stock_results) / len(
            stock_results
        )
        avg_conf = sum(r["score"]["confidence"] for r in stock_results) / len(
            stock_results
        )

        up_count = sum(1 for r in stock_results if r["score"]["direction"] == "UP")
        down_count = sum(1 for r in stock_results if r["score"]["direction"] == "DOWN")

        if up_count > down_count:
            direction = "UP"
        elif down_count > up_count:
            direction = "DOWN"
        else:
            direction = "NEUTRAL"

        return {
            "success": True,
            "sector": sector_name,
            "stocks": stocks,
            "results": stock_results,
            "summary": {
                "direction": direction,
                "probability": avg_prob,
                "confidence": avg_conf,
                "up_count": up_count,
                "down_count": down_count,
                "total": len(stock_results),
            },
        }


async def main():
    analyzer = SectorAnalyzer()

    print("\n" + "=" * 60)
    print("🚀 综合板块分析 - 预测下周热门板块 (2026-03-31 ~ 2026-04-04)")
    print("=" * 60)

    all_results = []

    for sector_name, stocks in SECTOR_STOCKS.items():
        result = await analyzer.analyze_sector(sector_name, stocks)
        if result["success"]:
            all_results.append(result)
            print(f"\n  📈 板块评分: {result['summary']['direction']}")
            print(f"  📊 上涨概率: {result['summary']['probability'] * 100:.1f}%")
            print(
                f"  📉 看涨/看跌: {result['summary']['up_count']}/{result['summary']['down_count']}"
            )

    print("\n\n" + "=" * 60)
    print("📋 板块评分排序 (按上涨概率)")
    print("=" * 60)

    sorted_results = sorted(
        all_results, key=lambda x: x["summary"]["probability"], reverse=True
    )

    for i, result in enumerate(sorted_results, 1):
        s = result["summary"]
        emoji = (
            "🔴"
            if s["direction"] == "UP"
            else ("🟢" if s["direction"] == "DOWN" else "⚪")
        )
        print(f"\n{i}. {emoji} {result['sector']}")
        print(
            f"   方向: {s['direction']} | 概率: {s['probability'] * 100:.1f}% | 置信度: {s['confidence'] * 100:.1f}%"
        )
        print(
            f"   看涨: {s['up_count']} | 看跌: {s['down_count']} | 总计: {s['total']}"
        )

    print("\n\n" + "=" * 60)
    print("💡 推荐买入清单")
    print("=" * 60)

    all_stocks = []
    for result in sorted_results:
        for stock_result in result["results"]:
            if stock_result["score"]["direction"] == "UP":
                all_stocks.append(
                    {
                        "sector": result["sector"],
                        "symbol": stock_result["symbol"],
                        "direction": stock_result["score"]["direction"],
                        "probability": stock_result["score"]["probability"],
                        "confidence": stock_result["score"]["confidence"],
                    }
                )

    all_stocks.sort(key=lambda x: (x["probability"], x["confidence"]), reverse=True)

    print("\n推荐股票（按上涨概率排序）:")
    print("-" * 60)
    for i, stock in enumerate(all_stocks[:10], 1):
        print(
            f"{i:2d}. {stock['symbol']:12s} | {stock['sector']:8s} | 概率: {stock['probability'] * 100:5.1f}% | 置信度: {stock['confidence'] * 100:5.1f}%"
        )

    print("\n\n" + "=" * 60)
    print("⚠️ 风险提示")
    print("=" * 60)
    print("""
1. 本分析仅供参考，不构成投资建议
2. 量化预测存在不确定性，请控制仓位
3. 市场充满风险，入市需谨慎
4. 建议设置止损位，注意风险控制
5. 过往表现不代表未来收益
    """)

    print("\n✅ 分析完成！")

    return sorted_results


if __name__ == "__main__":
    asyncio.run(main())
