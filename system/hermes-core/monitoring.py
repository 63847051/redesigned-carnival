"""
Hermes Agent Monitoring System - 监控系统

功能：
- 性能指标收集
- 错误追踪
- 健康检查
- 监控仪表板
"""

import os
import time
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque
import psutil


@dataclass
class Metric:
    """指标数据"""
    name: str
    value: float
    unit: str
    timestamp: str
    tags: Dict[str, str]
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ErrorEvent:
    """错误事件"""
    error_id: str
    error_type: str
    error_message: str
    stack_trace: str
    timestamp: str
    context: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return asdict(self)


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, max_metrics: int = 10000):
        """初始化指标收集器"""
        self.max_metrics = max_metrics
        self.metrics: deque = deque(maxlen=max_metrics)
        
    def record(self, name: str, value: float, unit: str = "", tags: Dict = None):
        """记录指标"""
        metric = Metric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now().isoformat(),
            tags=tags or {}
        )
        self.metrics.append(metric)
    
    def get_metrics(self, name: str = None, 
                   since: datetime = None,
                   limit: int = 100) -> List[Metric]:
        """获取指标"""
        filtered = self.metrics
        
        if name:
            filtered = [m for m in filtered if m.name == name]
        
        if since:
            since_str = since.isoformat()
            filtered = [m for m in filtered if m.timestamp >= since_str]
        
        return list(filtered)[-limit:]
    
    def get_latest(self, name: str) -> Optional[Metric]:
        """获取最新指标"""
        for metric in reversed(self.metrics):
            if metric.name == name:
                return metric
        return None
    
    def get_aggregated(self, name: str, 
                      since: datetime = None) -> Dict[str, float]:
        """获取聚合统计"""
        metrics = self.get_metrics(name, since)
        
        if not metrics:
            return {}
        
        values = [m.value for m in metrics]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "sum": sum(values)
        }


class ErrorTracker:
    """错误追踪器"""
    
    def __init__(self, max_errors: int = 1000):
        """初始化错误追踪器"""
        self.max_errors = max_errors
        self.errors: deque = deque(maxlen=max_errors)
        self.error_counts: Dict[str, int] = {}
        
    def track(self, error: Exception, context: Dict = None):
        """追踪错误"""
        import traceback
        import uuid
        
        error_id = str(uuid.uuid4())
        error_type = type(error).__name__
        error_message = str(error)
        stack_trace = traceback.format_exc()
        
        error_event = ErrorEvent(
            error_id=error_id,
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            timestamp=datetime.now().isoformat(),
            context=context or {}
        )
        
        self.errors.append(error_event)
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
    
    def get_recent_errors(self, limit: int = 10) -> List[ErrorEvent]:
        """获取最近的错误"""
        return list(self.errors)[-limit:]
    
    def get_error_stats(self) -> Dict[str, Any]:
        """获取错误统计"""
        return {
            "total_errors": len(self.errors),
            "error_counts": self.error_counts,
            "most_common": sorted(self.error_counts.items(), 
                                key=lambda x: x[1], 
                                reverse=True)[:10]
        }


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        """初始化健康检查器"""
        self.checks = {}
        
    def register_check(self, name: str, check_func: callable):
        """注册健康检查"""
        self.checks[name] = check_func
    
    def run_checks(self) -> Dict[str, Any]:
        """运行所有健康检查"""
        results = {}
        overall_healthy = True
        
        for name, check_func in self.checks.items():
            try:
                result = check_func()
                results[name] = result
                
                if not result.get("healthy", True):
                    overall_healthy = False
                    
            except Exception as e:
                results[name] = {
                    "healthy": False,
                    "error": str(e)
                }
                overall_healthy = False
        
        return {
            "overall_healthy": overall_healthy,
            "checks": results,
            "timestamp": datetime.now().isoformat()
        }


class HermesMonitor:
    """Hermes 监控系统（主接口）"""
    
    def __init__(self, data_dir: str = "/root/.openclaw/workspace/data/monitoring"):
        """初始化监控系统"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics = MetricsCollector()
        self.errors = ErrorTracker()
        self.health = HealthChecker()
        
        # 注册默认健康检查
        self._register_default_checks()
        
        # 设置日志
        self._setup_logging()
    
    def _register_default_checks(self):
        """注册默认健康检查"""
        def check_disk_space():
            """检查磁盘空间"""
            usage = psutil.disk_usage('/')
            free_percent = (usage.free / usage.total) * 100
            return {
                "healthy": free_percent > 10,  # 至少 10% 空闲
                "free_percent": free_percent,
                "free_gb": usage.free / (1024**3)
            }
        
        def check_memory():
            """检查内存"""
            mem = psutil.virtual_memory()
            return {
                "healthy": mem.available > 100 * 1024 * 1024,  # 至少 100MB
                "available_mb": mem.available / (1024**2),
                "percent": mem.percent
            }
        
        def check_database_files():
            """检查数据库文件"""
            db_files = [
                "/root/.openclaw/workspace/data/knowledge.db",
                "/root/.openclaw/workspace/data/honcho.db"
            ]
            
            for db_file in db_files:
                if Path(db_file).exists():
                    size = Path(db_file).stat().st_size
                    if size > 100 * 1024 * 1024:  # 超过 100MB
                        return {"healthy": False, "error": f"{db_file} too large"}
            
            return {"healthy": True}
        
        self.health.register_check("disk_space", check_disk_space)
        self.health.register_check("memory", check_memory)
        self.health.register_check("database_files", check_database_files)
    
    def _setup_logging(self):
        """设置日志"""
        log_file = self.data_dir / "hermes_monitor.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("HermesMonitor")
    
    def record_metric(self, name: str, value: float, unit: str = "", tags: Dict = None):
        """记录指标"""
        self.metrics.record(name, value, unit, tags)
        self.logger.debug(f"Metric: {name} = {value} {unit}")
    
    def track_error(self, error: Exception, context: Dict = None):
        """追踪错误"""
        self.errors.track(error, context)
        self.logger.error(f"Error: {type(error).__name__}: {error}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        return self.health.run_checks()
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取监控仪表板数据"""
        # 最近 1 小时的指标
        since = datetime.now() - timedelta(hours=1)
        
        return {
            "health": self.get_health_status(),
            "metrics": {
                "knowledge_operations": self.metrics.get_aggregated("knowledge_ops", since),
                "snapshot_operations": self.metrics.get_aggregated("snapshot_ops", since),
                "cache_hit_rate": self.metrics.get_aggregated("cache_hit_rate", since)
            },
            "errors": self.errors.get_error_stats(),
            "recent_errors": [e.to_dict() for e in self.errors.get_recent_errors(5)],
            "timestamp": datetime.now().isoformat()
        }
    
    def save_report(self, path: str = None):
        """保存监控报告"""
        if path is None:
            path = self.data_dir / f"monitor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = self.get_dashboard_data()
        
        with open(path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"监控报告已保存: {path}")
        return path


if __name__ == "__main__":
    # 测试监控系统
    monitor = HermesMonitor()
    
    # 记录一些指标
    for i in range(10):
        monitor.record_metric("test_metric", i * 10, "units", {"test": "value"})
    
    # 测试健康检查
    health = monitor.get_health_status()
    print(f"系统健康: {health['overall_healthy']}")
    
    # 生成报告
    report_path = monitor.save_report()
    print(f"报告已保存: {report_path}")
