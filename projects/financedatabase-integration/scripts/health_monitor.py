#!/usr/bin/env python3
"""
系统健康度监控脚本
基于 FinanceToolkit 计算系统健康度指标
"""

import json
import logging
import os
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

try:
    from financetoolkit import Toolkit
except ImportError:
    pass

LOG_DIR = Path("/root/.openclaw/workspace/logs")
MEMORY_DIR = Path("/root/.openclaw/workspace/memory")
HEALTH_REPORT_PATH = Path("/root/.openclaw/workspace/data/health-report.json")


class SystemHealthMonitor:
    """系统健康度监控器"""

    def __init__(self):
        self.metrics = {}
        self.thresholds = {
            "cpu_critical": 90,
            "cpu_warning": 70,
            "memory_critical": 90,
            "memory_warning": 70,
            "disk_critical": 90,
            "disk_warning": 80,
        }

    def collect_metrics(self):
        """收集系统指标"""
        self.metrics = {
            "timestamp": datetime.now().isoformat(),
            "system": self._get_system_metrics(),
            "memory": self._get_memory_metrics(),
            "disk": self._get_disk_metrics(),
            "logs": self._get_log_metrics(),
            "agent": self._get_agent_metrics(),
        }

    def _get_system_metrics(self):
        """获取系统指标 (CPU, uptime)"""
        metrics = {"cpu": 0, "uptime_hours": 0}
        try:
            result = subprocess.run(
                ["cat", "/proc/loadavg"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                load = result.stdout.strip().split()
                metrics["cpu"] = float(load[0])
        except Exception:
            pass
        try:
            result = subprocess.run(
                ["uptime", "-p"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                metrics["uptime_hours"] = self._parse_uptime(result.stdout)
        except Exception:
            pass
        return metrics

    def _parse_uptime(self, uptime_str):
        """解析 uptime 输出为小时"""
        hours = 0
        match = re.search(r"(\d+)\s*hour", uptime_str)
        if match:
            hours += int(match.group(1))
        match = re.search(r"(\d+)\s*day", uptime_str)
        if match:
            hours += int(match.group(1)) * 24
        return hours

    def _get_memory_metrics(self):
        """获取内存指标"""
        metrics = {"total_mb": 0, "used_mb": 0, "percent": 0}
        try:
            result = subprocess.run(
                ["free", "-m"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if len(lines) >= 2:
                    mem = lines[1].split()
                    metrics["total_mb"] = int(mem[1])
                    metrics["used_mb"] = int(mem[2])
                    metrics["percent"] = round(
                        metrics["used_mb"] / metrics["total_mb"] * 100, 1
                    )
        except Exception:
            pass
        return metrics

    def _get_disk_metrics(self):
        """获取磁盘指标"""
        metrics = {"total_gb": 0, "used_gb": 0, "percent": 0}
        try:
            result = subprocess.run(
                ["df", "-BG", "/"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if len(lines) >= 2:
                    disk = lines[1].split()
                    metrics["used_gb"] = int(disk[2].replace("G", ""))
                    metrics["total_gb"] = int(disk[3].replace("G", ""))
                    metrics["percent"] = int(disk[4].replace("%", ""))
        except Exception:
            pass
        return metrics

    def _get_log_metrics(self):
        """获取日志指标"""
        metrics = {"error_count": 0, "warning_count": 0, "info_count": 0}
        try:
            syslog = "/var/log/syslog"
            if os.path.exists(syslog):
                with open(syslog, "r", errors="ignore") as f:
                    lines = f.readlines()
                    recent = lines[-1000:] if len(lines) > 1000 else lines
                    for line in recent:
                        line_lower = line.lower()
                        if "error" in line_lower:
                            metrics["error_count"] += 1
                        elif "warning" in line_lower:
                            metrics["warning_count"] += 1
                        elif "info" in line_lower:
                            metrics["info_count"] += 1
        except Exception:
            pass
        return metrics

    def _get_agent_metrics(self):
        """获取 Agent 运行状态"""
        metrics = {"active_sessions": 0, "memory_files": 0}
        try:
            result = subprocess.run(
                ["ls", "-la", str(MEMORY_DIR)],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                metrics["memory_files"] = len(result.stdout.split("\n")) - 1
        except Exception:
            pass
        return metrics

    def calculate_health_score(self):
        """计算健康度分数"""
        if not self.metrics:
            return 0

        score = 100

        cpu = self.metrics.get("system", {}).get("cpu", 0)
        if cpu > self.thresholds["cpu_critical"]:
            score -= 30
        elif cpu > self.thresholds["cpu_warning"]:
            score -= 15

        mem_percent = self.metrics.get("memory", {}).get("percent", 0)
        if mem_percent > self.thresholds["memory_critical"]:
            score -= 25
        elif mem_percent > self.thresholds["memory_warning"]:
            score -= 10

        disk_percent = self.metrics.get("disk", {}).get("percent", 0)
        if disk_percent > self.thresholds["disk_critical"]:
            score -= 20
        elif disk_percent > self.thresholds["disk_warning"]:
            score -= 10

        error_count = self.metrics.get("logs", {}).get("error_count", 0)
        if error_count > 10:
            score -= 15
        elif error_count > 5:
            score -= 5

        self.metrics["health_score"] = max(0, score)
        return score

    def generate_report(self):
        """生成健康报告"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "health_score": self.metrics.get("health_score", 0),
            "metrics": self.metrics,
            "status": self._get_status(self.metrics.get("health_score", 0)),
        }
        HEALTH_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(HEALTH_REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return report

    def _get_status(self, score):
        """根据分数获取状态"""
        if score >= 80:
            return "良好"
        elif score >= 60:
            return "警告"
        else:
            return "危险"


def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("开始系统健康度检查...")

    monitor = SystemHealthMonitor()
    monitor.collect_metrics()
    score = monitor.calculate_health_score()
    report = monitor.generate_report()

    print(f"\n{'=' * 40}")
    print(f"📊 系统健康度报告")
    print(f"{'=' * 40}")
    print(f"健康分数: {score}/100 ({report['status']})")
    print(f"\nCPU 负载: {monitor.metrics.get('system', {}).get('cpu', 0):.2f}")
    print(f"内存使用: {monitor.metrics.get('memory', {}).get('percent', 0)}%")
    print(f"磁盘使用: {monitor.metrics.get('disk', {}).get('percent', 0)}%")
    print(f"错误日志: {monitor.metrics.get('logs', {}).get('error_count', 0)}")
    print(f"\n报告已保存到: {HEALTH_REPORT_PATH}")
    print(f"{'=' * 40}\n")


if __name__ == "__main__":
    main()
