#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FinanceDatabase 集成模块 - 完整功能测试
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("=" * 60)
print("FinanceDatabase 集成模块 - 完整功能测试")
print("=" * 60)
print()

# 测试计数
tests_passed = 0
tests_total = 0

def test_section(name):
    print(f"\n{'=' * 60}")
    print(f"测试: {name}")
    print('=' * 60)

def test_result(name, passed):
    global tests_passed, tests_total
    tests_total += 1
    if passed:
        tests_passed += 1
        print(f"✅ {name}: 通过")
    else:
        print(f"❌ {name}: 失败")
    return passed

# ===========================
# 1. 测试健康度计算模块
# ===========================
test_section("健康度计算模块")

try:
    from health_metrics import FinancialHealthCalculator, TrendAnalyzer

    # 创建测试数据
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

    # 测试健康度计算
    calculator = FinancialHealthCalculator()
    report = calculator.generate_health_report(test_data)

    test_result("模块导入", True)
    test_result("健康度计算", 'overall_rating' in report)
    test_result("评分系统", 'scores' in report)
    test_result("建议生成", 'overall_advice' in report)

    print(f"\n总体评分: {report['overall_rating']}")
    print(f"总分: {report.get('scores', {}).get('overall', 'N/A')}")

except Exception as e:
    test_result("健康度模块", False)
    print(f"错误: {e}")

# ===========================
# 2. 测试高级筛选器模块
# ===========================
test_section("\n高级筛选器模块")

try:
    from advanced_filter import FilterBuilder, PresetFilters, FilterOperator, LogicalOperator

    # 创建测试数据
    test_stocks = pd.DataFrame({
        'symbol': ['AAPL', 'MSFT', 'GOOGL', 'TSLA'],
        'sector': ['Technology', 'Technology', 'Technology', 'Technology'],
        'pe_ratio': [25.5, 28.3, 22.1, 85.3],
        'roe': [145.6, 38.2, 25.4, 32.1],
        'debt_to_equity': [1.85, 0.45, 0.23, 1.12],
        'market_cap': [2500, 2300, 1800, 800]
    })

    # 测试链式筛选
    builder = FilterBuilder(test_stocks)
    result = builder.lt('pe_ratio', 30).gt('roe', 20).execute()

    test_result("模块导入", True)
    test_result("链式筛选", len(result) > 0)
    test_result("FilterBuilder", isinstance(builder, FilterBuilder))

    # 测试预设筛选器
    quality = PresetFilters.quality_stocks(test_stocks, roe_min=20, debt_to_equity_max=0.5)
    test_result("预设筛选器", len(quality) > 0)

    print(f"\n链式筛选结果: {len(result)} 只股票")
    print(f"优质股筛选: {len(quality)} 只股票")

except Exception as e:
    test_result("高级筛选器模块", False)
    print(f"错误: {e}")

# ===========================
# 3. 测试报告生成器模块
# ===========================
test_section("\n报告生成器模块")

try:
    from report_generator import (
        CSVReportGenerator,
        JSONReportGenerator,
        ExcelReportGenerator,
        ComprehensiveReportGenerator
    )

    # 创建测试数据
    test_report_data = pd.DataFrame({
        'symbol': ['AAPL', 'MSFT', 'GOOGL'],
        'price': [175.5, 378.2, 141.8],
        'pe_ratio': [25.5, 28.3, 22.1]
    })

    # 测试 CSV 生成
    csv_gen = CSVReportGenerator()
    csv_path = csv_gen.generate(test_report_data, "test_csv")
    test_result("模块导入", True)
    test_result("CSV 生成", csv_path.endswith('.csv'))

    # 测试 JSON 生成
    json_gen = JSONReportGenerator()
    json_path = json_gen.generate(test_report_data, "test_json")
    test_result("JSON 生成", json_path.endswith('.json'))

    # 测试 Excel 生成
    excel_gen = ExcelReportGenerator()
    excel_path = excel_gen.generate(test_report_data, "test_excel")
    test_result("Excel 生成", excel_path.endswith('.xlsx'))

    # 测试综合生成器
    comp_gen = ComprehensiveReportGenerator()
    all_reports = comp_gen.generate_all_formats(test_report_data, "test_comprehensive")
    test_result("综合生成器", len(all_reports) >= 3)

    print(f"\n生成报告数量: {len(all_reports)}")
    for format_type, path in all_reports.items():
        print(f"  - {format_type.upper()}: {path}")

except Exception as e:
    test_result("报告生成器模块", False)
    print(f"错误: {e}")

# ===========================
# 4. 集成测试
# ===========================
test_section("\n集成测试")

try:
    from health_metrics import FinancialHealthCalculator
    from advanced_filter import FilterBuilder
    from report_generator import ComprehensiveReportGenerator

    # 创建完整测试数据
    np.random.seed(42)
    full_data = pd.DataFrame({
        'symbol': [f'STOCK{i}' for i in range(10)],
        'sector': ['Tech'] * 5 + ['Finance'] * 5,
        'pe_ratio': np.random.uniform(10, 50, 10),
        'roe': np.random.uniform(5, 30, 10),
        'debt_to_equity': np.random.uniform(0.2, 1.5, 10),
        'current_ratio': np.random.uniform(1.0, 3.0, 10),
        'net_margin': np.random.uniform(5, 20, 10)
    })

    # 筛选 + 健康度计算 + 报告生成
    filtered = FilterBuilder(full_data).eq('sector', 'Tech').execute()

    calculator = FinancialHealthCalculator()
    health_report = calculator.generate_health_report(filtered)

    generator = ComprehensiveReportGenerator()
    final_reports = generator.generate_all_formats(filtered, "integration_test")

    test_result("完整工作流", True)
    test_result("数据筛选", len(filtered) == 5)
    test_result("健康度报告", 'overall_rating' in health_report)
    test_result("多格式报告", len(final_reports) >= 3)

    print(f"\n筛选后数据: {len(filtered)} 条")
    print(f"健康度: {health_report['overall_rating']}")
    print(f"生成报告: {len(final_reports)} 种格式")

except Exception as e:
    test_result("集成测试", False)
    print(f"错误: {e}")

# ===========================
# 最终总结
# ===========================
print("\n" + "=" * 60)
print("测试总结")
print("=" * 60)
print(f"总测试数: {tests_total}")
print(f"通过数: {tests_passed}")
print(f"失败数: {tests_total - tests_passed}")
print(f"通过率: {tests_passed / tests_total * 100:.1f}%")

if tests_passed == tests_total:
    print("\n🎉 所有测试通过！模块可以投入使用！")
    exit(0)
else:
    print(f"\n⚠️  有 {tests_total - tests_passed} 个测试失败，请检查！")
    exit(1)
