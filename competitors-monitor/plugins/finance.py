#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财务报表分析插件
解析 PDF 财务报表，计算财务指标，分析公司健康状况
"""

import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any


class PDFParser:
    """简单 PDF 解析器（文本提取）"""

    def __init__(self):
        try:
            import PyPDF2

            self.pyPdf = PyPDF2
        except ImportError:
            self.pyPdf = None

    def parse(self, file_path: str) -> str:
        """解析 PDF 文件"""
        if self.pyPdf is None:
            return "PDF 解析需要安装 PyPDF2: pip3 install PyPDF2"

        if not os.path.exists(file_path):
            return f"文件不存在: {file_path}"

        try:
            text = ""
            with open(file_path, "rb") as f:
                reader = self.pyPdf.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"解析错误: {str(e)}"

    def extract_financial_data(self, text: str) -> Dict:
        """从文本提取财务数据"""
        data = {}

        patterns = {
            "revenue": r"(营业收入|销售收入|总收入).*?(\d+\.?\d*)\s*(万|亿|元)?",
            "net_profit": r"(净利润|纯利润).*?(\d+\.?\d*)\s*(万|亿|元)?",
            "gross_margin": r"(毛利率|毛利率).*?(\d+\.?\d*)\s*%?",
            "assets": r"(总资产).*?(\d+\.?\d*)\s*(万|亿|元)?",
            "liabilities": r"(总负债).*?(\d+\.?\d*)\s*(万|亿|元)?",
            "equity": r"(股东权益|净资产).*?(\d+\.?\d*)\s*(万|亿|元)?",
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                try:
                    value = float(match.group(2))
                    if match.group(3) == "亿":
                        value *= 100000000
                    elif match.group(3) == "万":
                        value *= 10000
                    data[key] = value
                except:
                    pass

        return data


class FinancialAnalyzer:
    """财务分析器"""

    def calculate_metrics(self, financial_data: Dict) -> Dict:
        """计算财务指标"""
        metrics = {}

        revenue = financial_data.get("revenue", 0)
        net_profit = financial_data.get("net_profit", 0)
        assets = financial_data.get("assets", 1)
        liabilities = financial_data.get("liabilities", 0)
        equity = financial_data.get("equity", 1)

        if revenue > 0:
            metrics["net_margin"] = net_profit / revenue

        if assets > 0:
            metrics["roa"] = net_profit / assets

        if equity > 0:
            metrics["roe"] = net_profit / equity

        if assets > 0:
            metrics["debt_ratio"] = liabilities / assets

        if liabilities > 0:
            metrics["debt_to_equity"] = liabilities / equity

        return metrics

    def compare_with_benchmark(self, metrics: Dict, benchmark: Dict) -> List[Dict]:
        """与基准对比"""
        comparisons = []

        if "roe" in metrics and "roe" in benchmark:
            if metrics["roe"] < benchmark["roe"]:
                comparisons.append(
                    {
                        "metric": "roe",
                        "actual": metrics["roe"],
                        "benchmark": benchmark["roe"],
                        "status": "below",
                        "message": f"ROE ({metrics['roe'] * 100:.1f}%) 低于基准 ({benchmark['roe'] * 100:.1f}%)",
                    }
                )

        if "gross_margin" in metrics and "gross_margin" in benchmark:
            if metrics["gross_margin"] < benchmark["gross_margin"]:
                comparisons.append(
                    {
                        "metric": "gross_margin",
                        "actual": metrics["gross_margin"],
                        "benchmark": benchmark["gross_margin"],
                        "status": "below",
                        "message": f"毛利率 ({metrics['gross_margin'] * 100:.1f}%) 低于基准 ({benchmark['gross_margin'] * 100:.1f}%)",
                    }
                )

        if "debt_ratio" in metrics and "debt_ratio" in benchmark:
            if metrics["debt_ratio"] > benchmark["debt_ratio"]:
                comparisons.append(
                    {
                        "metric": "debt_ratio",
                        "actual": metrics["debt_ratio"],
                        "benchmark": benchmark["debt_ratio"],
                        "status": "above",
                        "message": f"负债率 ({metrics['debt_ratio'] * 100:.1f}%) 高于基准 ({benchmark['debt_ratio'] * 100:.1f}%)",
                    }
                )

        return comparisons

    def detect_anomalies(self, metrics: Dict, thresholds: Dict) -> List[Dict]:
        """检测异常"""
        anomalies = []

        debt_ratio = metrics.get("debt_ratio", 0)
        if debt_ratio > thresholds.get("debt_ratio_high", 0.70):
            anomalies.append(
                {
                    "type": "high_debt",
                    "severity": "warning",
                    "value": debt_ratio,
                    "threshold": thresholds["debt_ratio_high"],
                    "message": f"负债率过高: {debt_ratio * 100:.1f}%",
                }
            )

        current_ratio = metrics.get("current_ratio", 1.5)
        if current_ratio < thresholds.get("current_ratio_low", 1.0):
            anomalies.append(
                {
                    "type": "low_liquidity",
                    "severity": "warning",
                    "value": current_ratio,
                    "threshold": thresholds["current_ratio_low"],
                    "message": f"流动性不足: 流动比率 {current_ratio:.2f}",
                }
            )

        return anomalies


class FinanceReportAnalyzer:
    """财务报表分析器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.parser = PDFParser()
        self.analyzer = FinancialAnalyzer()

    def analyze(self) -> Dict:
        """执行分析"""
        results = {"companies": [], "alerts": []}

        for company in self.config.get("companies", []):
            company_result = self._analyze_company(company)
            results["companies"].append(company_result)
            results["alerts"].extend(company_result.get("alerts", []))

        return results

    def _analyze_company(self, company: Dict) -> Dict:
        """分析单个公司"""
        result = {
            "name": company.get("name"),
            "stock_code": company.get("stock_code"),
            "fiscal_year": company.get("fiscal_year"),
            "metrics": {},
            "alerts": [],
            "comparisons": [],
        }

        financial_data = self._get_financial_data(company)

        if not financial_data:
            result["note"] = "使用模拟数据进行分析"
            financial_data = self._generate_mock_data()

        result["raw_data"] = financial_data

        metrics = self.analyzer.calculate_metrics(financial_data)
        result["metrics"] = metrics

        if company.get("benchmark"):
            comparisons = self.analyzer.compare_with_benchmark(
                metrics, company["benchmark"]
            )
            result["comparisons"] = comparisons

            for comp in comparisons:
                result["alerts"].append(
                    {
                        "type": "benchmark_breach",
                        "severity": "warning",
                        "company": company.get("name"),
                        **comp,
                    }
                )

        thresholds = self.config.get("thresholds", {})
        anomalies = self.analyzer.detect_anomalies(metrics, thresholds)
        result["alerts"].extend(anomalies)

        return result

    def _get_financial_data(self, company: Dict) -> Dict:
        """获取财务数据"""
        pdf_folder = self.config.get("data_sources", {}).get("pdf_folder", "")

        if not pdf_folder or not os.path.exists(pdf_folder):
            return {}

        company_name = company.get("name", "")

        for filename in os.listdir(pdf_folder):
            if filename.endswith(".pdf") and company_name in filename:
                text = self.parser.parse(os.path.join(pdf_folder, filename))
                return self.parser.extract_financial_data(text)

        return {}

    def _generate_mock_data(self) -> Dict:
        """生成模拟数据"""
        return {
            "revenue": 1000000000,
            "net_profit": 150000000,
            "gross_margin": 0.35,
            "assets": 5000000000,
            "liabilities": 2500000000,
            "equity": 2500000000,
        }

    def generate_report(self, results: Dict) -> str:
        """生成分析报告"""
        report = "## 📊 财务报表分析报告\n\n"

        for company in results.get("companies", []):
            report += f"### {company.get('name')} ({company.get('stock_code')})\n\n"
            report += f"**财年**: {company.get('fiscal_year')}\n\n"

            metrics = company.get("metrics", {})
            if metrics:
                report += "#### 财务指标\n\n"
                report += f"| 指标 | 数值 |\n"
                report += f"|------|------|\n"

                if "net_margin" in metrics:
                    report += f"| 净利率 | {metrics['net_margin'] * 100:.2f}% |\n"
                if "roe" in metrics:
                    report += f"| ROE | {metrics['roe'] * 100:.2f}% |\n"
                if "roa" in metrics:
                    report += f"| ROA | {metrics['roa'] * 100:.2f}% |\n"
                if "debt_ratio" in metrics:
                    report += f"| 负债率 | {metrics['debt_ratio'] * 100:.2f}% |\n"

                report += "\n"

            alerts = company.get("alerts", [])
            if alerts:
                report += "#### ⚠️ 告警\n\n"
                for alert in alerts:
                    emoji = "🔴" if alert.get("severity") == "warning" else "🟡"
                    report += f"{emoji} {alert.get('message')}\n"
                report += "\n"

        return report


def run_analyzer():
    """运行财务分析"""
    import sys

    config_path = "config/finance.json"

    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    analyzer = FinanceReportAnalyzer(config)
    results = analyzer.analyze()

    print(f"分析了 {len(results.get('companies', []))} 家公司")
    print(f"发现 {len(results.get('alerts', []))} 条告警")

    report = analyzer.generate_report(results)
    print("\n" + report)

    return results


if __name__ == "__main__":
    run_analyzer()
