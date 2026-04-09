#!/usr/bin/env python3
"""
报告生成器 - 多格式数据导出
支持 CSV、Excel、JSON、PDF 格式
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except ImportError:
    pass

WORKSPACE_DIR = Path("/root/.openclaw/workspace")
DATA_DIR = WORKSPACE_DIR / "data"
REPORTS_DIR = DATA_DIR / "reports"


class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        self.reports_dir = REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_daily_report(
        self,
        include_metrics: bool = True,
        include_charts: bool = True,
    ) -> Dict[str, Any]:
        """
        生成每日报告

        参数:
            include_metrics: 是否包含指标
            include_charts: 是否包含图表

        返回:
            报告数据
        """
        # 加载健康度数据
        health_data = self._load_health_data()

        # 加载记忆索引
        memory_index = self._load_memory_index()

        # 生成报告
        report = {
            "generated_at": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "health": health_data,
            "memory": memory_index.get("statistics", {}) if memory_index else {},
            "summary": self._generate_summary(health_data, memory_index),
        }

        # 保存 JSON
        json_path = self.reports_dir / f"daily-report-{datetime.now().strftime('%Y%m%d')}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return report

    def _load_health_data(self) -> Optional[Dict[str, Any]]:
        """加载健康度数据"""
        health_path = DATA_DIR / "health-report.json"
        if health_path.exists():
            with open(health_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def _load_memory_index(self) -> Optional[Dict[str, Any]]:
        """加载记忆索引"""
        index_path = DATA_DIR / "memory-index.json"
        if index_path.exists():
            with open(index_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def _generate_summary(
        self,
        health_data: Optional[Dict[str, Any]],
        memory_index: Optional[Dict[str, Any]],
    ) -> str:
        """生成摘要"""
        summary_parts = []

        # 健康度摘要
        if health_data:
            health_score = health_data.get("health_score", 0)
            status = health_data.get("status", "未知")
            summary_parts.append(f"系统健康度: {health_score}/100 ({status})")

            # 添加关键指标
            metrics = health_data.get("metrics", {})
            if "memory" in metrics:
                mem_percent = metrics["memory"].get("percent", 0)
                summary_parts.append(f"内存使用: {mem_percent}%")
            if "disk" in metrics:
                disk_percent = metrics["disk"].get("percent", 0)
                summary_parts.append(f"磁盘使用: {disk_percent}%")

        # 记忆摘要
        if memory_index:
            stats = memory_index.get("statistics", {})
            total_scenes = stats.get("total_scenes", 0)
            total_memories = stats.get("total_memories", 0)
            summary_parts.append(f"场景记忆: {total_scenes}")
            summary_parts.append(f"日志记忆: {total_memories}")

        return " | ".join(summary_parts) if summary_parts else "无数据"

    def export_data(
        self,
        data: Dict[str, Any],
        format: str = "csv",
        destination: Optional[Path] = None,
    ) -> Path:
        """
        导出数据

        参数:
            data: 要导出的数据
            format: 导出格式 (csv, excel, json)
            destination: 目标目录

        返回:
            导出文件的路径
        """
        if destination is None:
            destination = self.reports_dir

        destination.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "csv":
            return self._export_csv(data, destination, timestamp)
        elif format == "excel":
            return self._export_excel(data, destination, timestamp)
        elif format == "json":
            return self._export_json(data, destination, timestamp)
        else:
            raise ValueError(f"不支持的格式: {format}")

    def _export_csv(self, data: Dict[str, Any], destination: Path, timestamp: str) -> Path:
        """导出为 CSV"""
        output_path = destination / f"report-{timestamp}.csv"

        # 扁平化数据
        flat_data = self._flatten_dict(data)

        # 写入 CSV
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Key", "Value"])
            for key, value in flat_data.items():
                writer.writerow([key, value])

        return output_path

    def _export_excel(self, data: Dict[str, Any], destination: Path, timestamp: str) -> Path:
        """导出为 Excel"""
        if pd is None:
            raise ImportError("需要安装 pandas: pip install pandas openpyxl")

        output_path = destination / f"report-{timestamp}.xlsx"

        # 扁平化数据
        flat_data = self._flatten_dict(data)

        # 创建 DataFrame
        df = pd.DataFrame(list(flat_data.items()), columns=["Key", "Value"])

        # 保存为 Excel
        df.to_excel(output_path, index=False)

        return output_path

    def _export_json(self, data: Dict[str, Any], destination: Path, timestamp: str) -> Path:
        """导出为 JSON"""
        output_path = destination / f"report-{timestamp}.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return output_path

    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
        """扁平化字典"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def generate_pdf_report(
        self,
        report_data: Dict[str, Any],
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        生成 PDF 报告

        参数:
            report_data: 报告数据
            output_path: 输出路径

        返回:
            PDF 文件路径
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.reports_dir / f"report-{timestamp}.pdf"

        # 创建 PDF
        doc = SimpleDocTemplate(str(output_path), pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # 标题
        title = Paragraph("系统每日报告", styles["Title"])
        story.append(title)
        story.append(Spacer(1, 0.3 * inch))

        # 生成时间
        date = Paragraph(f"生成时间: {report_data.get('generated_at', 'N/A')}", styles["Normal"])
        story.append(date)
        story.append(Spacer(1, 0.2 * inch))

        # 摘要
        summary = Paragraph(f"摘要: {report_data.get('summary', 'N/A')}", styles["Normal"])
        story.append(summary)
        story.append(Spacer(1, 0.3 * inch))

        # 健康度表格
        if "health" in report_data and report_data["health"]:
            health_title = Paragraph("系统健康度", styles["Heading2"])
            story.append(health_title)
            story.append(Spacer(1, 0.1 * inch))

            health_data = report_data["health"]
            health_table_data = [
                ["指标", "数值"],
                ["健康分数", str(health_data.get("health_score", "N/A"))],
                ["状态", health_data.get("status", "N/A")],
            ]

            # 添加详细指标
            metrics = health_data.get("metrics", {})
            if "memory" in metrics:
                mem = metrics["memory"]
                health_table_data.extend([
                    ["内存使用", f"{mem.get('percent', 0)}%"],
                    ["已用/总计", f"{mem.get('used_mb', 0)}MB / {mem.get('total_mb', 0)}MB"],
                ])
            if "disk" in metrics:
                disk = metrics["disk"]
                health_table_data.extend([
                    ["磁盘使用", f"{disk.get('percent', 0)}%"],
                    ["已用/总计", f"{disk.get('used_gb', 0)}GB / {disk.get('total_gb', 0)}GB"],
                ])

            health_table = Table(health_table_data)
            health_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 14),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(health_table)
            story.append(Spacer(1, 0.3 * inch))

        # 记忆统计表格
        if "memory" in report_data and report_data["memory"]:
            memory_title = Paragraph("记忆统计", styles["Heading2"])
            story.append(memory_title)
            story.append(Spacer(1, 0.1 * inch))

            memory_data = report_data["memory"]
            memory_table_data = [
                ["项目", "数量"],
                ["场景记忆", str(memory_data.get("total_scenes", 0))],
                ["日志记忆", str(memory_data.get("total_memories", 0))],
                ["标签数量", str(memory_data.get("unique_tags", 0))],
                ["分类数量", str(memory_data.get("unique_categories", 0))],
            ]

            memory_table = Table(memory_table_data)
            memory_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 14),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(memory_table)

        # 生成 PDF
        doc.build(story)

        return output_path


def main():
    """主函数 - 演示用法"""
    generator = ReportGenerator()

    print("=" * 50)
    print("报告生成器演示")
    print("=" * 50)

    # 生成每日报告
    print("\n📊 生成每日报告...")
    report = generator.generate_daily_report(include_metrics=True, include_charts=True)

    print(f"✅ JSON 报告已生成")
    print(f"   摘要: {report['summary']}")

    # 导出为 CSV
    print("\n📄 导出为 CSV...")
    csv_path = generator.export_data(report, format="csv")
    print(f"✅ CSV 文件已保存: {csv_path}")

    # 导出为 JSON
    print("\n📋 导出为 JSON...")
    json_path = generator.export_data(report, format="json")
    print(f"✅ JSON 文件已保存: {json_path}")

    # 尝试生成 PDF
    try:
        print("\n📕 生成 PDF 报告...")
        pdf_path = generator.generate_pdf_report(report)
        print(f"✅ PDF 文件已保存: {pdf_path}")
    except NameError:
        print("⚠️  PDF 生成需要安装 reportlab: pip install reportlab")

    print("\n✅ 所有报告生成完成！")


if __name__ == "__main__":
    main()
