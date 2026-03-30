#!/usr/bin/env python3
"""
股票查询脚本 - 最终版
直接从标题提取数据
"""

import httpx
from datetime import datetime

def fetch_market_data():
    """获取A股三大指数"""
    urls = {
        "上证指数": "https://r.jina.ai/https://quote.eastmoney.com/unify/r/1.000001",
        "深证成指": "https://r.jina.ai/https://quote.eastmoney.com/unify/r/0.399001",
        "创业板指": "https://r.jina.ai/https://quote.eastmoney.com/unify/r/399006"
    }
    
    results = {}
    
    for name, url in urls.items():
        try:
            response = httpx.get(url, timeout=10)
            response.raise_for_status()
            
            # 从标题提取数据
            # 格式: 上证指数 3923.29 9.57(0.24%)
            title = response.text
            
            # 提取所有数字
            import re
            numbers = re.findall(r'[\d.]+', title)
            
            if len(numbers) >= 3:
                index_code = numbers[0]  # 指数代码
                price = numbers[1]      # 当前价格
                change = numbers[2]     # 涨跌
                percent = numbers[3]    # 涨跌幅
                
                is_up = change[0] != '-'
                
                results[name] = {
                    "index_code": index_code,
                    "price": price,
                    "change": change,
                    "percent": percent,
                    "is_up": is_up
                }
            else:
                results[name] = {"error": "无法解析数据"}
                
        except Exception as e:
            results[name] = {"error": str(e)}
    
    return results


def main():
    print("📊 A股三大指数行情")
    print("=" * 50)
    print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = fetch_market_data()
    
    # 输出结果
    for name, data in results.items():
        if "error" in data:
            print(f"{name}: ❌ {data['error']}")
        else:
            emoji = "📈" if data["is_up"] else "📉"
            change_symbol = "+" if data["is_up"] else ""
            
            print(f"{emoji} {name:8} {data['price']:>10} ({change_symbol}{data['change']}, {data['percent']}%)")
    
    print()
    print("数据来源: 东方财富网 (via Jina Reader)")


if __name__ == "__main__":
    main()
