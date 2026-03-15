#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FinanceDatabase 高级筛选器
实现多维度、灵活的数据筛选功能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class FilterOperator(Enum):
    """筛选操作符"""
    EQ = "eq"          # 等于
    NE = "ne"          # 不等于
    GT = "gt"          # 大于
    GTE = "gte"        # 大于等于
    LT = "lt"          # 小于
    LTE = "lte"        # 小于等于
    CONTAINS = "contains"  # 包含
    STARTS_WITH = "starts_with"  # 开头是
    ENDS_WITH = "ends_with"      # 结尾是
    IN = "in"          # 在列表中
    NOT_IN = "not_in"  # 不在列表中
    BETWEEN = "between"  # 在范围内
    IS_NULL = "is_null"    # 为空
    IS_NOT_NULL = "is_not_null"  # 不为空


class LogicalOperator(Enum):
    """逻辑操作符"""
    AND = "and"
    OR = "or"
    NOT = "not"


@dataclass
class FilterCondition:
    """筛选条件"""
    field: str
    operator: FilterOperator
    value: Any = None
    value2: Any = None  # 用于 BETWEEN 操作


@dataclass
class FilterGroup:
    """筛选条件组（支持嵌套）"""
    conditions: List[FilterCondition]
    logical_operator: LogicalOperator = LogicalOperator.AND
    sub_groups: List['FilterGroup'] = None


class AdvancedFilter:
    """高级筛选器"""

    def __init__(self):
        self.operators_map = {
            FilterOperator.EQ: lambda df, field, val: df[field] == val,
            FilterOperator.NE: lambda df, field, val: df[field] != val,
            FilterOperator.GT: lambda df, field, val: df[field] > val,
            FilterOperator.GTE: lambda df, field, val: df[field] >= val,
            FilterOperator.LT: lambda df, field, val: df[field] < val,
            FilterOperator.LTE: lambda df, field, val: df[field] <= val,
            FilterOperator.CONTAINS: self._contains,
            FilterOperator.STARTS_WITH: self._starts_with,
            FilterOperator.ENDS_WITH: self._ends_with,
            FilterOperator.IN: lambda df, field, val: df[field].isin(val),
            FilterOperator.NOT_IN: lambda df, field, val: ~df[field].isin(val),
            FilterOperator.BETWEEN: self._between,
            FilterOperator.IS_NULL: lambda df, field, val: df[field].isna(),
            FilterOperator.IS_NOT_NULL: lambda df, field, val: df[field].notna()
        }

    def _contains(self, df: pd.DataFrame, field: str, value: str) -> pd.Series:
        """字符串包含"""
        return df[field].astype(str).str.contains(value, na=False)

    def _starts_with(self, df: pd.DataFrame, field: str, value: str) -> pd.Series:
        """字符串开头"""
        return df[field].astype(str).str.startswith(value, na=False)

    def _ends_with(self, df: pd.DataFrame, field: str, value: str) -> pd.Series:
        """字符串结尾"""
        return df[field].astype(str).str.endswith(value, na=False)

    def _between(self, df: pd.DataFrame, field: str, value: tuple) -> pd.Series:
        """范围查询"""
        min_val, max_val = value
        return (df[field] >= min_val) & (df[field] <= max_val)

    def apply_condition(self, df: pd.DataFrame, condition: FilterCondition) -> pd.DataFrame:
        """应用单个筛选条件"""
        if condition.field not in df.columns:
            raise ValueError(f"Field '{condition.field}' not found in DataFrame")

        operator_func = self.operators_map.get(condition.operator)
        if not operator_func:
            raise ValueError(f"Operator {condition.operator} not supported")

        if condition.operator in [FilterOperator.BETWEEN]:
            mask = operator_func(df, condition.field, (condition.value, condition.value2))
        elif condition.operator in [FilterOperator.IS_NULL, FilterOperator.IS_NOT_NULL]:
            mask = operator_func(df, condition.field, None)
        else:
            mask = operator_func(df, condition.field, condition.value)

        return df[mask]

    def apply_filter_group(self, df: pd.DataFrame, filter_group: FilterGroup) -> pd.DataFrame:
        """应用筛选条件组"""
        result_mask = pd.Series([True] * len(df), index=df.index)

        # 处理子组
        if filter_group.sub_groups:
            for sub_group in filter_group.sub_groups:
                sub_mask = self._get_group_mask(df, sub_group)

                if filter_group.logical_operator == LogicalOperator.AND:
                    result_mask &= sub_mask
                elif filter_group.logical_operator == LogicalOperator.OR:
                    result_mask |= sub_mask
                elif filter_group.logical_operator == LogicalOperator.NOT:
                    result_mask &= ~sub_mask

        # 处理当前组的条件
        group_mask = self._get_conditions_mask(df, filter_group.conditions)

        if filter_group.logical_operator == LogicalOperator.AND:
            result_mask &= group_mask
        elif filter_group.logical_operator == LogicalOperator.OR:
            result_mask |= group_mask
        elif filter_group.logical_operator == LogicalOperator.NOT:
            result_mask &= ~group_mask

        return df[result_mask]

    def _get_conditions_mask(self, df: pd.DataFrame, conditions: List[FilterCondition]) -> pd.Series:
        """获取条件的掩码"""
        if not conditions:
            return pd.Series([True] * len(df), index=df.index)

        mask = pd.Series([True] * len(df), index=df.index)
        for condition in conditions:
            condition_mask = self._get_condition_mask(df, condition)
            mask &= condition_mask

        return mask

    def _get_condition_mask(self, df: pd.DataFrame, condition: FilterCondition) -> pd.Series:
        """获取单个条件的掩码"""
        operator_func = self.operators_map.get(condition.operator)
        if not operator_func:
            raise ValueError(f"Operator {condition.operator} not supported")

        if condition.operator == FilterOperator.BETWEEN:
            return operator_func(df, condition.field, (condition.value, condition.value2))
        elif condition.operator in [FilterOperator.IS_NULL, FilterOperator.IS_NOT_NULL]:
            return operator_func(df, condition.field, None)
        else:
            return operator_func(df, condition.field, condition.value)

    def _get_group_mask(self, df: pd.DataFrame, group: FilterGroup) -> pd.Series:
        """获取组的掩码"""
        conditions_mask = self._get_conditions_mask(df, group.conditions)
        result_mask = conditions_mask

        if group.sub_groups:
            for sub_group in group.sub_groups:
                sub_mask = self._get_group_mask(df, sub_group)

                if group.logical_operator == LogicalOperator.AND:
                    result_mask &= sub_mask
                elif group.logical_operator == LogicalOperator.OR:
                    result_mask |= sub_mask
                elif group.logical_operator == LogicalOperator.NOT:
                    result_mask &= ~sub_mask

        return result_mask


class PresetFilters:
    """预设筛选器"""

    @staticmethod
    def high_growth_companies(df: pd.DataFrame, revenue_growth_threshold: float = 15.0) -> pd.DataFrame:
        """高增长公司筛选"""
        if 'revenue_growth' not in df.columns:
            return df

        return df[df['revenue_growth'] > revenue_growth_threshold].copy()

    @staticmethod
    def value_stocks(df: pd.DataFrame, pe_max: float = 15.0, pb_max: float = 2.0) -> pd.DataFrame:
        """价值股筛选（低PE、低PB）"""
        conditions = []
        if 'pe_ratio' in df.columns:
            conditions.append(df['pe_ratio'] > 0)
            conditions.append(df['pe_ratio'] <= pe_max)

        if 'pb_ratio' in df.columns:
            conditions.append(df['pb_ratio'] > 0)
            conditions.append(df['pb_ratio'] <= pb_max)

        if conditions:
            combined = conditions[0]
            for condition in conditions[1:]:
                combined &= condition
            return df[combined].copy()

        return df

    @staticmethod
    def quality_stocks(df: pd.DataFrame, roe_min: float = 15.0, debt_to_equity_max: float = 0.5) -> pd.DataFrame:
        """优质股筛选（高ROE、低负债）"""
        conditions = []
        if 'roe' in df.columns:
            conditions.append(df['roe'] >= roe_min)

        if 'debt_to_equity' in df.columns:
            conditions.append(df['debt_to_equity'] <= debt_to_equity_max)

        if conditions:
            combined = conditions[0]
            for condition in conditions[1:]:
                combined &= condition
            return df[combined].copy()

        return df

    @staticmethod
    def dividend_stocks(df: pd.DataFrame, dividend_yield_min: float = 3.0) -> pd.DataFrame:
        """高股息股筛选"""
        if 'dividend_yield' not in df.columns:
            return df

        return df[df['dividend_yield'] >= dividend_yield_min].copy()

    @staticmethod
    def low_volatility(df: pd.DataFrame, volatility_max: float = 20.0) -> pd.DataFrame:
        """低波动率筛选"""
        if 'volatility' not in df.columns:
            return df

        return df[df['volatility'] <= volatility_max].copy()

    @staticmethod
    def momentum_stocks(df: pd.DataFrame, momentum_threshold: float = 0.0) -> pd.DataFrame:
        """动量股筛选（正收益动量）"""
        if 'momentum' not in df.columns:
            return df

        return df[df['momentum'] > momentum_threshold].copy()


class FilterBuilder:
    """筛选器构建器（链式API）"""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.conditions = []
        self.advanced_filter = AdvancedFilter()

    def filter_by(self, field: str, operator: FilterOperator, value: Any = None, value2: Any = None) -> 'FilterBuilder':
        """添加筛选条件"""
        condition = FilterCondition(field=field, operator=operator, value=value, value2=value2)
        self.conditions.append(condition)
        return self

    def eq(self, field: str, value: Any) -> 'FilterBuilder':
        """等于"""
        return self.filter_by(field, FilterOperator.EQ, value)

    def gt(self, field: str, value: Any) -> 'FilterBuilder':
        """大于"""
        return self.filter_by(field, FilterOperator.GT, value)

    def gte(self, field: str, value: Any) -> 'FilterBuilder':
        """大于等于"""
        return self.filter_by(field, FilterOperator.GTE, value)

    def lt(self, field: str, value: Any) -> 'FilterBuilder':
        """小于"""
        return self.filter_by(field, FilterOperator.LT, value)

    def lte(self, field: str, value: Any) -> 'FilterBuilder':
        """小于等于"""
        return self.filter_by(field, FilterOperator.LTE, value)

    def contains(self, field: str, value: str) -> 'FilterBuilder':
        """包含"""
        return self.filter_by(field, FilterOperator.CONTAINS, value)

    def between(self, field: str, min_value: Any, max_value: Any) -> 'FilterBuilder':
        """范围"""
        return self.filter_by(field, FilterOperator.BETWEEN, min_value, max_value)

    def in_list(self, field: str, values: List[Any]) -> 'FilterBuilder':
        """在列表中"""
        return self.filter_by(field, FilterOperator.IN, values)

    def execute(self) -> pd.DataFrame:
        """执行筛选"""
        result = self.df.copy()
        for condition in self.conditions:
            result = self.advanced_filter.apply_condition(result, condition)
        return result

    def reset(self) -> 'FilterBuilder':
        """重置条件"""
        self.conditions = []
        return self


def demo_usage():
    """演示使用"""
    # 创建示例数据
    data = pd.DataFrame({
        'symbol': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM'],
        'sector': ['Technology', 'Technology', 'Technology', 'Consumer',
                  'Technology', 'Technology', 'Technology', 'Financial'],
        'pe_ratio': [25.5, 28.3, 22.1, 45.6, 85.3, 18.2, 65.4, 11.5],
        'pb_ratio': [35.2, 11.8, 5.4, 8.9, 12.3, 3.4, 18.6, 1.5],
        'roe': [145.6, 38.2, 25.4, 15.8, 32.1, 28.9, 56.7, 15.2],
        'debt_to_equity': [1.85, 0.45, 0.23, 0.65, 1.12, 0.18, 0.45, 1.25],
        'dividend_yield': [0.5, 0.8, 0.0, 0.0, 0.0, 0.0, 0.0, 2.5],
        'revenue_growth': [8.5, 12.3, 15.6, 12.1, 35.6, 18.9, 206.4, 5.6],
        'market_cap': [2500, 2300, 1800, 1500, 800, 750, 1800, 400]  # Billion
    })

    print("=== 高级筛选器演示 ===\n")

    # 演示 1: 链式筛选
    print("1. 链式筛选: 科技板块 + PE < 30 + ROE > 20")
    builder = FilterBuilder(data)
    result = builder.eq('sector', 'Technology').lt('pe_ratio', 30).gt('roe', 20).execute()
    print(result[['symbol', 'sector', 'pe_ratio', 'roe']])
    print()

    # 演示 2: 预设筛选器
    print("2. 预设筛选: 优质股（高ROE + 低负债）")
    result = PresetFilters.quality_stocks(data, roe_min=20, debt_to_equity_max=0.5)
    print(result[['symbol', 'roe', 'debt_to_equity']])
    print()

    # 演示 3: 范围筛选
    print("3. 范围筛选: 市值 800-2000 亿")
    builder = FilterBuilder(data)
    result = builder.between('market_cap', 800, 2000).execute()
    print(result[['symbol', 'market_cap']])
    print()

    # 演示 4: 复合筛选
    print("4. 复合筛选: 科技板块 + (PE < 30 OR 高增长)")
    tech_stocks = data[data['sector'] == 'Technology']
    builder = FilterBuilder(tech_stocks)
    result = builder.filter_by(
        'pe_ratio',
        FilterOperator.LT,
        30
    ).execute()
    print(result[['symbol', 'sector', 'pe_ratio', 'revenue_growth']])


if __name__ == "__main__":
    demo_usage()
