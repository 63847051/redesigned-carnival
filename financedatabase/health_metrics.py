#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FinanceDatabase 健康度计算模块
集成 FinanceToolkit 实现系统健康度分析
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta


class FinancialHealthCalculator:
    """财务健康度计算器"""

    def __init__(self):
        self.health_categories = {
            'liquidity': {'weight': 0.25, 'name': '流动性健康'},
            'profitability': {'weight': 0.25, 'name': '盈利能力'},
            'solvency': {'weight': 0.25, 'name': '偿债能力'},
            'efficiency': {'weight': 0.25, 'name': '运营效率'}
        }

    def calculate_liquidity_health(self, data: pd.DataFrame) -> float:
        """
        计算流动性健康度 (0-100)
        基于流动比率、速动比率、现金比率
        """
        try:
            if 'current_ratio' in data.columns:
                current_ratio = data['current_ratio'].iloc[-1]
                # 理想范围: 1.5-3.0
                if 1.5 <= current_ratio <= 3.0:
                    return 100
                elif current_ratio >= 1.0:
                    return 70 + (current_ratio - 1.0) * 10
                else:
                    return max(0, current_ratio * 70)
            return 50.0
        except Exception:
            return 50.0

    def calculate_profitability_health(self, data: pd.DataFrame) -> float:
        """
        计算盈利能力健康度 (0-100)
        基于净利润率、ROE、ROA
        """
        try:
            score = 0
            count = 0

            if 'net_margin' in data.columns:
                net_margin = data['net_margin'].iloc[-1]
                # 净利润率 > 15% 为优秀
                score += min(100, net_margin * 6)
                count += 1

            if 'roe' in data.columns:
                roe = data['roe'].iloc[-1]
                # ROE > 15% 为优秀
                score += min(100, roe * 6)
                count += 1

            if 'roa' in data.columns:
                roa = data['roa'].iloc[-1]
                # ROA > 10% 为优秀
                score += min(100, roa * 10)
                count += 1

            return score / count if count > 0 else 50.0
        except Exception:
            return 50.0

    def calculate_solvency_health(self, data: pd.DataFrame) -> float:
        """
        计算偿债能力健康度 (0-100)
        基于资产负债率、利息保障倍数
        """
        try:
            score = 0
            count = 0

            if 'debt_to_equity' in data.columns:
                debt_ratio = data['debt_to_equity'].iloc[-1]
                # 资产负债率 < 60% 为优秀
                if debt_ratio < 0.6:
                    score += 100
                elif debt_ratio < 0.8:
                    score += 70
                else:
                    score += max(0, 100 - debt_ratio * 100)
                count += 1

            if 'interest_coverage' in data.columns:
                coverage = data['interest_coverage'].iloc[-1]
                # 利息保障倍数 > 3 为优秀
                score += min(100, coverage * 30)
                count += 1

            return score / count if count > 0 else 50.0
        except Exception:
            return 50.0

    def calculate_efficiency_health(self, data: pd.DataFrame) -> float:
        """
        计算运营效率健康度 (0-100)
        基于资产周转率、存货周转率、应收账款周转率
        """
        try:
            score = 0
            count = 0

            if 'asset_turnover' in data.columns:
                turnover = data['asset_turnover'].iloc[-1]
                # 资产周转率 > 0.8 为优秀
                score += min(100, turnover * 120)
                count += 1

            if 'inventory_turnover' in data.columns:
                inv_turnover = data['inventory_turnover'].iloc[-1]
                # 存货周转率 > 5 为优秀
                score += min(100, inv_turnover * 18)
                count += 1

            return score / count if count > 0 else 50.0
        except Exception:
            return 50.0

    def calculate_overall_health(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        计算综合健康度评分
        返回各分类评分和总分
        """
        scores = {
            'liquidity': self.calculate_liquidity_health(data),
            'profitability': self.calculate_profitability_health(data),
            'solvency': self.calculate_solvency_health(data),
            'efficiency': self.calculate_efficiency_health(data)
        }

        # 加权平均计算总分
        total_score = sum(
            scores[category] * self.health_categories[category]['weight']
            for category in scores
        )

        scores['overall'] = round(total_score, 2)

        return scores

    def get_health_rating(self, score: float) -> Tuple[str, str]:
        """
        根据分数获取评级和建议
        """
        if score >= 90:
            return "优秀", "财务状况极佳，继续保持"
        elif score >= 75:
            return "良好", "财务状况健康，可适当优化"
        elif score >= 60:
            return "中等", "财务状况一般，需要改善"
        elif score >= 40:
            return "较差", "财务状况不佳，需要重点关注"
        else:
            return "危险", "财务状况危险，需要紧急行动"

    def generate_health_report(self, data: pd.DataFrame) -> Dict:
        """
        生成完整健康度报告
        """
        scores = self.calculate_overall_health(data)

        report = {
            'timestamp': datetime.now().isoformat(),
            'scores': {},
            'overall_rating': None,
            'overall_advice': None,
            'recommendations': []
        }

        # 处理各分类
        for category, score in scores.items():
            if category == 'overall':
                continue

            rating, advice = self.get_health_rating(score)
            report['scores'][category] = {
                'score': round(score, 2),
                'rating': rating,
                'advice': advice,
                'name': self.health_categories[category]['name']
            }

        # 处理总分
        overall_rating, overall_advice = self.get_health_rating(scores['overall'])
        report['overall_rating'] = overall_rating
        report['overall_advice'] = overall_advice

        # 生成建议
        for category, info in report['scores'].items():
            if info['score'] < 60:
                report['recommendations'].append({
                    'category': info['name'],
                    'priority': '高' if info['score'] < 50 else '中',
                    'action': f"改善{info['name']}：{info['advice']}"
                })

        return report


class TrendAnalyzer:
    """趋势分析器"""

    def __init__(self):
        self.periods = {
            'short': 3,   # 短期：3个月/季度
            'medium': 6,  # 中期：6个月/季度
            'long': 12    # 长期：12个月/季度
        }

    def calculate_trend(self, data: pd.Series, period: int) -> Dict[str, float]:
        """
        计算趋势指标
        """
        if len(data) < period:
            return {'trend': 0, 'volatility': 0, 'growth_rate': 0}

        recent_data = data.tail(period)

        # 线性回归计算趋势
        x = np.arange(len(recent_data))
        y = recent_data.values

        # 简单线性回归
        slope = np.polyfit(x, y, 1)[0]
        avg_value = np.mean(y)

        # 趋势方向（标准化）
        trend = (slope / avg_value * 100) if avg_value != 0 else 0

        # 波动率（标准差）
        volatility = np.std(y) / avg_value * 100 if avg_value != 0 else 0

        # 增长率
        if len(recent_data) >= 2:
            growth_rate = (recent_data.iloc[-1] / recent_data.iloc[0] - 1) * 100
        else:
            growth_rate = 0

        return {
            'trend': round(trend, 2),
            'volatility': round(volatility, 2),
            'growth_rate': round(growth_rate, 2)
        }

    def analyze_metric_trend(self, data: pd.DataFrame, metric: str) -> Dict:
        """
        分析单个指标的趋势
        """
        if metric not in data.columns:
            return {}

        metric_data = data[metric].dropna()

        return {
            'short_term': self.calculate_trend(metric_data, self.periods['short']),
            'medium_term': self.calculate_trend(metric_data, self.periods['medium']),
            'long_term': self.calculate_trend(metric_data, self.periods['long'])
        }


def demo_usage():
    """演示使用"""
    # 创建示例数据（12个数据点）
    np.random.seed(42)  # 固定随机种子确保可重复
    dates = pd.date_range(end=datetime.now(), periods=12, freq='ME')
    data = pd.DataFrame({
        'date': dates,
        'current_ratio': np.random.uniform(1.2, 2.5, 12),
        'net_margin': np.random.uniform(8, 18, 12),
        'roe': np.random.uniform(10, 25, 12),
        'roa': np.random.uniform(5, 12, 12),
        'debt_to_equity': np.random.uniform(0.3, 0.7, 12),
        'interest_coverage': np.random.uniform(2, 8, 12),
        'asset_turnover': np.random.uniform(0.5, 1.2, 12),
        'inventory_turnover': np.random.uniform(3, 8, 12)
    })

    # 计算健康度
    calculator = FinancialHealthCalculator()
    report = calculator.generate_health_report(data)

    print("=== 财务健康度报告 ===")
    print(f"总体评分: {report['overall_rating']} ({report['scores'].get('overall', 'N/A')})")
    print(f"总体建议: {report['overall_advice']}")
    print()

    for category, info in report['scores'].items():
        if category == 'overall':
            continue
        print(f"{info['name']}: {info['rating']} ({info['score']})")

    if report['recommendations']:
        print("\n改进建议:")
        for rec in report['recommendations']:
            print(f"- [{rec['priority']}] {rec['action']}")


if __name__ == "__main__":
    # 简单测试
    print("=== 财务健康度计算模块测试 ===")
    print("模块导入成功！")
    print("主要功能:")
    print("- FinancialHealthCalculator: 健康度计算")
    print("- TrendAnalyzer: 趋势分析")
    print()
    print("创建测试数据...")

    # 创建简单的测试数据
    np.random.seed(42)
    test_data = pd.DataFrame({
        'current_ratio': [1.8],
        'net_margin': [15.5],
        'roe': [22.3],
        'roa': [8.5],
        'debt_to_equity': [0.45],
        'interest_coverage': [5.2],
        'asset_turnover': [0.9],
        'inventory_turnover': [6.1]
    })

    calculator = FinancialHealthCalculator()
    report = calculator.generate_health_report(test_data)

    print(f"\n✅ 健康度计算完成!")
    print(f"总体评分: {report['overall_rating']}")
    print(f"总体建议: {report['overall_advice']}")

    print("\n各分类评分:")
    for category, info in report['scores'].items():
        print(f"  {info['name']}: {info['rating']} ({info['score']})")
