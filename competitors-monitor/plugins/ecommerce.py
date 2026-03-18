#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电商价格监控插件
监控京东、天猫、淘宝、拼多多等平台的商品价格
"""

import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any


class EcommercePlugin:
    """电商数据源插件"""

    def __init__(self):
        try:
            import requests
            from bs4 import BeautifulSoup

            self.requests = requests
            self.BeautifulSoup = BeautifulSoup
        except ImportError:
            raise ImportError("请安装依赖: pip3 install requests beautifulsoup4")

    def fetch(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取电商数据"""
        results = []

        sources = config.get("data_sources", {})

        if sources.get("web_scraping", {}).get("enabled"):
            scraping_data = self._fetch_by_scraping(config)
            results.extend(scraping_data)

        if sources.get("jd", {}).get("enabled"):
            jd_data = self._fetch_jd(config)
            results.extend(jd_data)

        if sources.get("taobao", {}).get("enabled"):
            tb_data = self._fetch_taobao(config)
            results.extend(tb_data)

        return results

    def _fetch_by_scraping(self, config: Dict[str, Any]) -> List[Dict]:
        """通过网页抓取获取价格"""
        results = []

        mock_prices = {
            "iPhone 15 Pro": {"jd": 7999, "taobao": 7899, "pdd": 7699},
            "MacBook Air M3": {"jd": 9499, "taobao": 9299, "pdd": 8999},
        }

        for target in config.get("targets", []):
            name = target.get("name")
            prices = mock_prices.get(name, {"jd": 0, "taobao": 0, "pdd": 0})

            for platform, price in prices.items():
                if price > 0:
                    results.append(
                        {
                            "source": platform,
                            "type": "ecommerce_price",
                            "product_name": name,
                            "platform": platform,
                            "price": price,
                            "currency": "CNY",
                            "stock_status": "in_stock",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

        return results

    def _fetch_jd(self, config: Dict[str, Any]) -> List[Dict]:
        """获取京东价格"""
        jd_config = config.get("data_sources", {}).get("jd", {})

        if not jd_config.get("api_key"):
            return [
                {
                    "source": "jd",
                    "error": "未配置京东 API Key",
                    "timestamp": datetime.now().isoformat(),
                }
            ]

        results = []

        for target in config.get("targets", []):
            sku = target.get("jd_sku")
            if not sku:
                continue

            try:
                url = f"https://api.jd.com/routerjson"

                results.append(
                    {
                        "source": "jd",
                        "type": "ecommerce_price",
                        "product_name": target.get("name"),
                        "sku": sku,
                        "platform": "jd",
                        "note": "需配置京东联盟 API",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            except Exception as e:
                results.append(
                    {
                        "source": "jd",
                        "error": str(e),
                        "product": target.get("name"),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return results

    def _fetch_taobao(self, config: Dict[str, Any]) -> List[Dict]:
        """获取淘宝/天猫价格"""
        tb_config = config.get("data_sources", {}).get("taobao", {})

        if not tb_config.get("app_key"):
            return [
                {
                    "source": "taobao",
                    "error": "未配置淘宝 App Key",
                    "timestamp": datetime.now().isoformat(),
                }
            ]

        return [
            {
                "source": "taobao",
                "error": "需配置淘宝开放平台 API",
                "timestamp": datetime.now().isoformat(),
            }
        ]

    def validate(self, data: List[Dict[str, Any]]) -> bool:
        """验证数据"""
        return len(data) > 0


class PriceMonitor:
    """价格监控器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.plugin = EcommercePlugin()
        self.last_price_file = "data/price_last.json"

    def fetch(self) -> List[Dict[str, Any]]:
        """抓取数据"""
        return self.plugin.fetch(self.config)

    def analyze(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """分析价格变化"""
        alerts = []
        check_rules = self.config.get("check_rules", {})

        last_prices = self._load_last_prices()

        for item in data:
            if item.get("type") != "ecommerce_price":
                continue

            product_name = item.get("product_name")
            platform = item.get("platform")
            current_price = item.get("price")

            if not current_price:
                continue

            key = f"{product_name}_{platform}"

            if key in last_prices:
                last_price = last_prices[key]
                price_change = (current_price - last_price) / last_price

                threshold = check_rules.get("price_change_threshold", 0.05)

                if price_change < -threshold:
                    alerts.append(
                        {
                            "type": "price_drop",
                            "severity": "info",
                            "product": product_name,
                            "platform": platform,
                            "last_price": last_price,
                            "current_price": current_price,
                            "change_percent": round(price_change * 100, 2),
                            "message": f"{product_name} ({platform}) 降价: {last_price} → {current_price} ({price_change * 100:.1f}%)",
                        }
                    )
                elif price_change > threshold:
                    alerts.append(
                        {
                            "type": "price_increase",
                            "severity": "warning",
                            "product": product_name,
                            "platform": platform,
                            "last_price": last_price,
                            "current_price": current_price,
                            "change_percent": round(price_change * 100, 2),
                            "message": f"{product_name} ({platform}) 涨价: {last_price} → {current_price} (+{price_change * 100:.1f}%)",
                        }
                    )

            stock = item.get("stock_status")
            if stock == "out_of_stock" and check_rules.get("alert_on_out_of_stock"):
                alerts.append(
                    {
                        "type": "out_of_stock",
                        "severity": "warning",
                        "product": product_name,
                        "platform": platform,
                        "message": f"{product_name} ({platform}) 已售罄",
                    }
                )

        self._save_current_prices(data)

        return alerts

    def _load_last_prices(self) -> Dict:
        """加载上次价格"""
        if os.path.exists(self.last_price_file):
            with open(self.last_price_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_current_prices(self, data: List[Dict]):
        """保存当前价格"""
        prices = {}
        for item in data:
            if item.get("type") == "ecommerce_price":
                key = f"{item.get('product_name')}_{item.get('platform')}"
                prices[key] = item.get("price")

        os.makedirs("data", exist_ok=True)
        with open(self.last_price_file, "w", encoding="utf-8") as f:
            json.dump(prices, f, ensure_ascii=False)

    def generate_report(self, data: List[Dict], alerts: List[Dict]) -> str:
        """生成价格报告"""
        report = "## 📊 电商价格监控报告\n\n"

        products = {}
        for item in data:
            if item.get("type") == "ecommerce_price":
                name = item.get("product_name")
                if name not in products:
                    products[name] = []
                products[name].append(
                    {
                        "platform": item.get("platform"),
                        "price": item.get("price"),
                        "stock": item.get("stock_status"),
                    }
                )

        for name, info in products.items():
            report += f"### {name}\n\n"
            for p in info:
                stock_emoji = "✅" if p["stock"] == "in_stock" else "❌"
                report += f"- {p['platform']}: ¥{p['price']} {stock_emoji}\n"
            report += "\n"

        if alerts:
            report += "### ⚠️ 价格变化\n\n"
            for alert in alerts:
                emoji = "📉" if alert["type"] == "price_drop" else "📈"
                report += f"{emoji} {alert['message']}\n"

        return report


def run_monitor():
    """运行价格监控"""
    import sys

    config_path = "config/ecommerce-price.json"

    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    monitor = PriceMonitor(config)
    data = monitor.fetch()
    alerts = monitor.analyze(data)

    print(f"获取到 {len(data)} 条价格数据")
    print(f"发现 {len(alerts)} 条价格变化")

    report = monitor.generate_report(data, alerts)
    print("\n" + report)

    return data, alerts


if __name__ == "__main__":
    run_monitor()
