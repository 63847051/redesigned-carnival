# -*- coding: utf-8 -*-
"""
数据处理模块
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional

class DataProcessor:
    """数据处理类"""
    
    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        清洗数据
        
        参数:
            df: 原始数据
        
        返回:
            清洗后的数据
        """
        # 删除缺失值
        df = df.dropna()
        
        # 去重
        df = df.drop_duplicates()
        
        # 排序
        df = df.sort_index()
        
        return df
    
    @staticmethod
    def add_returns(df: pd.DataFrame) -> pd.DataFrame:
        """
        添加收益率列
        
        参数:
            df: 价格数据
        
        返回:
            添加收益率的数据
        """
        # 日收益率
        df['daily_return'] = df['Close'].pct_change()
        
        # 累计收益率
        df['cumulative_return'] = (1 + df['daily_return']).cumprod()
        
        return df
    
    @staticmethod
    def resample_data(
        df: pd.DataFrame, 
        freq: str = 'W'
    ) -> pd.DataFrame:
        """
        重采样数据
        
        参数:
            df: 原始数据
            freq: 频率（D=日, W=周, M=月）
        
        返回:
            重采样后的数据
        """
        return df.resample(freq).last()
    
    @staticmethod
    def normalize(df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化数据
        
        参数:
            df: 原始数据
        
        返回:
            标准化后的数据
        """
        return (df - df.mean()) / df.std()
