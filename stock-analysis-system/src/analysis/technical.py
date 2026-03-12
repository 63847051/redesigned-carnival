# -*- coding: utf-8 -*-
"""
技术分析模块
"""

import pandas as pd
import numpy as np
from typing import Dict, List

class TechnicalAnalysis:
    """技术分析类"""
    
    @staticmethod
    def add_ma(df: pd.DataFrame, periods: List[int] = [5, 10, 20, 50, 200]) -> pd.DataFrame:
        """
        添加移动平均线
        
        参数:
            df: 价格数据
            periods: 周期列表
        
        返回:
            添加 MA 的数据
        """
        for period in periods:
            df[f'MA{period}'] = df['Close'].rolling(window=period).mean()
        return df
    
    @staticmethod
    def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        添加 RSI 指标
        
        参数:
            df: 价格数据
            period: 周期
        
        返回:
            添加 RSI 的数据
        """
        # 计算价格变化
        delta = df['Close'].diff()
        
        # 分离上涨和下跌
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # 计算 RSI
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        return df
    
    @staticmethod
    def add_macd(df: pd.DataFrame, params: tuple = (12, 26, 9)) -> pd.DataFrame:
        """
        添加 MACD 指标
        
        参数:
            df: 价格数据
            params: (快线, 慢线, 信号线)
        
        返回:
            添加 MACD 的数据
        """
        fast, slow, signal = params
        
        # 计算 EMA
        ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
        
        # MACD 线
        df['MACD'] = ema_fast - ema_slow
        
        # 信号线
        df['MACD_Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
        
        # 柱状图
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        return df
    
    @staticmethod
    def add_bollinger_bands(
        df: pd.DataFrame, 
        period: int = 20, 
        std_dev: float = 2
    ) -> pd.DataFrame:
        """
        添加布林带
        
        参数:
            df: 价格数据
            period: 周期
            std_dev: 标准差倍数
        
        返回:
            添加布林带的数据
        """
        # 中轨（移动平均）
        df['BB_Middle'] = df['Close'].rolling(window=period).mean()
        
        # 标准差
        std = df['Close'].rolling(window=period).std()
        
        # 上轨
        df['BB_Upper'] = df['BB_Middle'] + (std * std_dev)
        
        # 下轨
        df['BB_Lower'] = df['BB_Middle'] - (std * std_dev)
        
        return df
    
    @staticmethod
    def identify_trend(df: pd.DataFrame) -> Dict:
        """
        识别趋势
        
        参数:
            df: 价格数据（需包含 MA）
        
        返回:
            趋势分析结果
        """
        latest = df.iloc[-1]
        
        # 均线排列
        ma_list = [f'MA{i}' for i in [5, 10, 20, 50, 200]]
        ma_values = [latest.get(ma) for ma in ma_list if ma in df.columns]
        
        # 判断多头/空头排列
        if len(ma_values) >= 3:
            is_bullish = all(ma_values[i] > ma_values[i+1] for i in range(len(ma_values)-1))
            is_bearish = all(ma_values[i] < ma_values[i+1] for i in range(len(ma_values)-1))
            
            if is_bullish:
                trend = "多头"
            elif is_bearish:
                trend = "空头"
            else:
                trend = "震荡"
        else:
            trend = "未知"
        
        return {
            "trend": trend,
            "current_price": latest['Close'],
            "ma5": latest.get('MA5'),
            "ma20": latest.get('MA20'),
            "ma50": latest.get('MA50')
        }
    
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        计算所有技术指标
        
        参数:
            df: 价格数据
        
        返回:
            添加所有指标的数据
        """
        df = TechnicalAnalysis.add_ma(df)
        df = TechnicalAnalysis.add_rsi(df)
        df = TechnicalAnalysis.add_macd(df)
        df = TechnicalAnalysis.add_bollinger_bands(df)
        
        return df
