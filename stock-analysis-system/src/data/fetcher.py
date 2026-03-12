# -*- coding: utf-8 -*-
"""
数据获取模块
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class DataFetcher:
    """数据获取类"""
    
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    def get_realtime_price(self, symbol: str) -> Dict:
        """
        获取实时股价
        
        参数:
            symbol: 股票代码（如 600318.SS）
        
        返回:
            实时股价数据字典
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            return {
                "symbol": symbol,
                "price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "change": info.get("regularMarketChange"),
                "change_percent": info.get("regularMarketChangePercent"),
                "volume": info.get("regularMarketVolume"),
                "high": info.get("dayHigh"),
                "low": info.get("dayLow"),
                "open": info.get("regularMarketOpen"),
                "previous_close": info.get("previousClose"),
                "market_cap": info.get("marketCap"),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_historical_data(
        self, 
        symbol: str, 
        period: str = "1y",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        获取历史数据
        
        参数:
            symbol: 股票代码
            period: 时间周期（1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max）
            interval: 数据间隔（1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo）
        
        返回:
            历史数据 DataFrame
        """
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period=period, interval=interval)
            return df
        except Exception as e:
            print(f"获取历史数据失败: {e}")
            return pd.DataFrame()
    
    def get_financials(self, symbol: str) -> Dict:
        """
        获取财务数据
        
        参数:
            symbol: 股票代码
        
        返回:
            财务数据字典
        """
        try:
            stock = yf.Ticker(symbol)
            
            return {
                "income_stmt": stock.income_stmt,
                "balance_sheet": stock.balance_sheet,
                "cashflow": stock.cashflow,
                "info": stock.info
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_stock_info(self, symbol: str) -> Dict:
        """
        获取股票基本信息
        
        参数:
            symbol: 股票代码
        
        返回:
            股票信息字典
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            return {
                "symbol": symbol,
                "name": info.get("longName"),
                "industry": info.get("industry"),
                "sector": info.get("sector"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "pb_ratio": info.get("priceToBook"),
                "dividend_yield": info.get("dividendYield"),
                "beta": info.get("beta"),
                "description": info.get("longBusinessSummary")
            }
        except Exception as e:
            return {"error": str(e)}
    
    def batch_get_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        批量获取股价
        
        参数:
            symbols: 股票代码列表
        
        返回:
            股价数据字典
        """
        results = {}
        for symbol in symbols:
            results[symbol] = self.get_realtime_price(symbol)
        return results
