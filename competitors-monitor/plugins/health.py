#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康管理助手插件
监控健康指标变化，提供健康建议和预警
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any


class HealthDataPlugin:
    """健康数据源插件"""

    def __init__(self):
        self.last_data_file = "data/health_last.json"

    def fetch(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取健康数据"""
        results = []

        sources = config.get("data_sources", {})

        if sources.get("manual_input", {}).get("enabled"):
            manual_data = self._fetch_manual_input(config)
            results.extend(manual_data)

        if sources.get("apple_health", {}).get("enabled"):
            apple_data = self._fetch_apple_health(config)
            results.extend(apple_data)

        if sources.get("google_fit", {}).get("enabled"):
            fit_data = self._fetch_google_fit(config)
            results.extend(fit_data)

        return results

    def _fetch_manual_input(self, config: Dict[str, Any]) -> List[Dict]:
        """获取手动输入的健康数据"""
        manual_config = config.get("data_sources", {}).get("manual_input", {})
        last_values = manual_config.get("last_values", {})

        return [
            {
                "source": "manual_input",
                "type": "health_metrics",
                "weight": last_values.get("weight"),
                "blood_pressure_systolic": last_values.get("blood_pressure_systolic"),
                "blood_pressure_diastolic": last_values.get("blood_pressure_diastolic"),
                "heart_rate": last_values.get("heart_rate"),
                "sleep_hours": last_values.get("sleep_hours"),
                "steps": last_values.get("steps"),
                "water_intake_ml": last_values.get("water_intake"),
                "timestamp": datetime.now().isoformat(),
            }
        ]

    def _fetch_apple_health(self, config: Dict[str, Any]) -> List[Dict]:
        """获取 Apple Health 数据"""
        export_path = (
            config.get("data_sources", {}).get("apple_health", {}).get("export_path")
        )

        if not export_path or not os.path.exists(export_path):
            return [
                {
                    "source": "apple_health",
                    "error": "Apple Health 导出路径未配置或不存在",
                    "timestamp": datetime.now().isoformat(),
                }
            ]

        return [
            {
                "source": "apple_health",
                "type": "health_export",
                "note": "需使用 Apple Health Export 等工具导出 XML 数据",
                "timestamp": datetime.now().isoformat(),
            }
        ]

    def _fetch_google_fit(self, config: Dict[str, Any]) -> List[Dict]:
        """获取 Google Fit 数据"""
        return [
            {
                "source": "google_fit",
                "error": "需配置 Google Fit API 凭证",
                "timestamp": datetime.now().isoformat(),
            }
        ]

    def validate(self, data: List[Dict[str, Any]]) -> bool:
        """验证数据"""
        return len(data) > 0


class HealthMonitor:
    """健康管理监控器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.plugin = HealthDataPlugin()
        self.last_data_file = "data/health_last.json"

    def fetch(self) -> List[Dict[str, Any]]:
        """抓取数据"""
        return self.plugin.fetch(self.config)

    def analyze(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """分析健康数据"""
        alerts = []
        check_rules = self.config.get("check_rules", {})
        goals = self.config.get("goals", {})

        for item in data:
            if item.get("source") != "manual_input":
                continue

            heart_rate = item.get("heart_rate")
            if heart_rate:
                if heart_rate < check_rules.get("heart_rate_abnormal_low", 50):
                    alerts.append(
                        {
                            "type": "abnormal_heart_rate",
                            "severity": "warning",
                            "metric": "heart_rate",
                            "value": heart_rate,
                            "message": f"心率过低: {heart_rate} bpm (正常值: {check_rules['heart_rate_abnormal_low']}-100)",
                        }
                    )
                elif heart_rate > check_rules.get("heart_rate_abnormal_high", 100):
                    alerts.append(
                        {
                            "type": "abnormal_heart_rate",
                            "severity": "warning",
                            "metric": "heart_rate",
                            "value": heart_rate,
                            "message": f"心率过高: {heart_rate} bpm (正常值: 50-{check_rules['heart_rate_abnormal_high']})",
                        }
                    )

            bp_sys = item.get("blood_pressure_systolic")
            bp_dia = item.get("blood_pressure_diastolic")
            if bp_sys and bp_dia:
                if bp_sys > check_rules.get("blood_pressure_systolic_high", 140):
                    alerts.append(
                        {
                            "type": "high_blood_pressure",
                            "severity": "warning",
                            "metric": "blood_pressure",
                            "value": f"{bp_sys}/{bp_dia}",
                            "message": f"血压偏高: {bp_sys}/{bp_dia} mmHg",
                        }
                    )

            sleep = item.get("sleep_hours")
            if sleep and sleep < check_rules.get("sleep_minimum_hours", 6):
                alerts.append(
                    {
                        "type": "poor_sleep",
                        "severity": "info",
                        "metric": "sleep",
                        "value": sleep,
                        "message": f"睡眠不足: {sleep} 小时 (建议: {check_rules['sleep_minimum_hours']}+ 小时)",
                    }
                )

            steps = item.get("steps")
            if steps and steps < check_rules.get("steps_minimum", 5000):
                alerts.append(
                    {
                        "type": "low_activity",
                        "severity": "info",
                        "metric": "steps",
                        "value": steps,
                        "message": f"活动量不足: {steps} 步 (建议: {check_rules['steps_minimum']}+ 步)",
                    }
                )

            water = item.get("water_intake_ml")
            if water and water < check_rules.get("water_minimum_ml", 1500):
                alerts.append(
                    {
                        "type": "low_water",
                        "severity": "info",
                        "metric": "water",
                        "value": water,
                        "message": f"饮水量不足: {water} ml (建议: {check_rules['water_minimum_ml']}+ ml)",
                    }
                )

        return alerts

    def generate_summary(self, data: List[Dict], alerts: List[Dict]) -> str:
        """生成健康摘要"""
        summary = "## 📊 今日健康摘要\n\n"

        for item in data:
            if item.get("source") == "manual_input":
                summary += "### 身体指标\n\n"
                summary += f"- 心率: {item.get('heart_rate', '-')} bpm\n"
                summary += f"- 血压: {item.get('blood_pressure_systolic', '-')}/{item.get('blood_pressure_diastolic', '-')} mmHg\n"
                summary += f"- 睡眠: {item.get('sleep_hours', '-')} 小时\n"
                summary += f"- 步数: {item.get('steps', '-')} 步\n"
                summary += f"- 饮水: {item.get('water_intake_ml', '-')} ml\n"

        if alerts:
            summary += "\n### ⚠️ 健康提醒\n\n"
            for alert in alerts:
                emoji = "🔴" if alert["severity"] == "warning" else "🟡"
                summary += f"{emoji} {alert['message']}\n"
        else:
            summary += "\n### ✅ 健康状态良好\n"

        return summary

    def save_last_data(self, data: List[Dict]):
        """保存上次数据用于对比"""
        os.makedirs("data", exist_ok=True)
        with open(self.last_data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def run_monitor():
    """运行健康管理监控"""
    import sys

    config_path = "config/health.json"

    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    monitor = HealthMonitor(config)
    data = monitor.fetch()
    alerts = monitor.analyze(data)

    print(f"获取到 {len(data)} 条健康数据")
    print(f"发现 {len(alerts)} 条健康提醒")

    for alert in alerts:
        print(f"  [{alert['severity'].upper()}] {alert['message']}")

    summary = monitor.generate_summary(data, alerts)
    print("\n" + summary)

    return data, alerts


if __name__ == "__main__":
    run_monitor()
