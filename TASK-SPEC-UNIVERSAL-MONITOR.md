# 通用监控框架改造 - 任务说明

**分配给**: 小新（opencode/minimax-m2.5-free）
**任务类型**: 系统架构改造
**预计时间**: 2-3 小时
**优先级**: 高

---

## 🎯 任务目标

将 `/root/.openclaw/workspace/competitors-monitor/` 从专用竞品监控系统改造成**通用监控框架**。

**核心价值**: 一次搭建，随处可用

---

## 📋 现有系统分析

### 当前结构
```
competitors-monitor/
├── scripts/
│   ├── scrape.py      # 网页抓取（硬编码）
│   ├── diff.py        # 变化检测（通用性好）
│   ├── report.py      # 报告生成（通用性好）
│   └── notify.py      # 飞书推送（通用性好）
├── config.json        # 配置文件（竞品专用）
└── data/              # 数据目录
```

### 核心流程
```
抓取网页 → 对比 HTML → 生成报告 → 推送飞书
```

### 问题
- ❌ scrape.py 只能抓取网页
- ❌ config.json 只能配置竞品
- ❌ 要监控股票需要重新写代码

---

## ✨ 目标架构

### 新结构
```
universal-monitor/
├── core/
│   ├── __init__.py
│   ├── monitor.py       # 核心监控引擎
│   ├── detector.py      # 通用变化检测
│   ├── reporter.py      # 通用报告生成
│   └── notifier.py      # 通用推送通知
├── plugins/
│   ├── __init__.py
│   ├── base.py          # 插件基类
│   ├── webpage.py       # 网页抓取插件
│   ├── api.py           # API 调用插件
│   └── database.py      # 数据库查询插件
├── config/
│   ├── competitor.json  # 竞品监控配置
│   ├── stock.json       # 股票监控配置
│   └── database.json    # 数据库监控配置
├── scripts/
│   ├── run.py           # 主运行脚本
│   └── setup.py         # 安装脚本
└── data/
    ├── raw/             # 原始数据
    ├── diff/            # 变化数据
    └── reports/         # 监控报告
```

### 核心流程
```
选择插件 → 抓取数据 → 检测变化 → 生成报告 → 推送通知
```

---

## 🔧 详细实现步骤

### Step 1: 创建插件基类（30 分钟）

**文件**: `plugins/base.py`

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class DataSourcePlugin(ABC):
    """数据源插件基类"""
    
    @abstractmethod
    def fetch(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        抓取数据
        
        Args:
            config: 配置字典
            
        Returns:
            数据列表，格式: [{"key": "value", ...}, ...]
        """
        pass
    
    @abstractmethod
    def validate(self, data: List[Dict[str, Any]]) -> bool:
        """
        验证数据
        
        Args:
            data: 待验证的数据
            
        Returns:
            是否有效
        """
        pass
```

---

### Step 2: 实现网页抓取插件（30 分钟）

**文件**: `plugins/webpage.py`

```python
from .base import DataSourcePlugin
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

class WebpagePlugin(DataSourcePlugin):
    """网页抓取插件"""
    
    def fetch(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """抓取网页"""
        results = []
        
        for target in config.get('targets', []):
            # 抓取逻辑（从现有 scrape.py 迁移）
            url = target['url']
            # ... 抓取代码
            
            results.append({
                'source': target.get('name'),
                'type': 'webpage',
                'url': url,
                'title': title,
                'content': content,
                'timestamp': datetime.now().isoformat()
            })
        
        return results
    
    def validate(self, data: List[Dict[str, Any]]) -> bool:
        """验证数据"""
        return len(data) > 0 and all('url' in d for d in data)
```

---

### Step 3: 实现 API 调用插件（30 分钟）

**文件**: `plugins/api.py`

```python
from .base import DataSourcePlugin
import requests
from typing import List, Dict, Any

class APIPlugin(DataSourcePlugin):
    """API 调用插件"""
    
    def fetch(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """调用 API"""
        results = []
        
        for target in config.get('targets', []):
            # API 调用逻辑
            api_url = config['api_url']
            params = self._build_params(target, config)
            
            response = requests.get(api_url, params=params)
            data = response.json()
            
            results.append({
                'source': target.get('name'),
                'type': 'api',
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
        
        return results
    
    def _build_params(self, target: Dict, config: Dict) -> Dict:
        """构建 API 参数"""
        # 根据不同的 API 类型构建参数
        pass
```

---

### Step 4: 创建核心监控引擎（45 分钟）

**文件**: `core/monitor.py`

```python
from typing import Dict, Any
from ..plugins.base import DataSourcePlugin

class Monitor:
    """通用监控引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.plugin = self._load_plugin()
    
    def _load_plugin(self) -> DataSourcePlugin:
        """加载插件"""
        plugin_type = self.config.get('monitor_type')
        
        if plugin_type == 'webpage':
            from ..plugins.webpage import WebpagePlugin
            return WebpagePlugin()
        elif plugin_type == 'api':
            from ..plugins.api import APIPlugin
            return APIPlugin()
        # ... 其他插件
        else:
            raise ValueError(f"Unknown plugin type: {plugin_type}")
    
    def fetch(self) -> List[Dict[str, Any]]:
        """抓取数据"""
        return self.plugin.fetch(self.config)
    
    def validate(self, data: List[Dict[str, Any]]) -> bool:
        """验证数据"""
        return self.plugin.validate(data)
```

---

### Step 5: 抽象检测和报告逻辑（30 分钟）

**文件**: `core/detector.py`

```python
from typing import List, Dict, Any

class Detector:
    """通用变化检测"""
    
    def detect(self, today_data: List[Dict], yesterday_data: List[Dict]) -> List[Dict]:
        """检测变化"""
        # 从现有 diff.py 迁移
        # 保持通用性
        pass
```

**文件**: `core/reporter.py`

```python
from typing import List, Dict, Any

class Reporter:
    """通用报告生成"""
    
    def generate(self, changes: List[Dict], config: Dict) -> str:
        """生成报告"""
        # 从现有 report.py 迁移
        # 根据数据类型调整报告格式
        pass
```

---

### Step 6: 设计通用配置格式（30 分钟）

**竞品监控配置**: `config/competitor.json`

```json
{
  "monitor_type": "webpage",
  "name": "竞品监控",
  "targets": [
    {
      "name": "Apple",
      "url": "https://www.apple.com",
      "pages": [
        {"name": "首页", "url": "https://www.apple.com", "type": "homepage"}
      ]
    }
  ],
  "check_rules": {
    "content_similarity_threshold": 0.9
  },
  "notification": {
    "feishu_webhook": "YOUR_WEBHOOK_URL",
    "report_time": "09:00"
  }
}
```

**股票监控配置**: `config/stock.json`

```json
{
  "monitor_type": "api",
  "name": "股票监控",
  "api_url": "https://api.example.com/stock",
  "targets": [
    {
      "name": "贵州茅台",
      "code": "600519",
      "fields": ["price", "volume", "change"]
    }
  ],
  "check_rules": {
    "price_change_threshold": 0.05
  },
  "notification": {
    "feishu_webhook": "YOUR_WEBHOOK_URL"
  }
}
```

---

### Step 7: 创建主运行脚本（15 分钟）

**文件**: `scripts/run.py`

```python
#!/usr/bin/env python3
import sys
import json
from core.monitor import Monitor
from core.detector import Detector
from core.reporter import Reporter
from core.notifier import Notifier

def main():
    # 加载配置
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'config/competitor.json'
    with open(config_file) as f:
        config = json.load(f)
    
    # 1. 抓取数据
    monitor = Monitor(config)
    today_data = monitor.fetch()
    
    # 2. 检测变化
    detector = Detector()
    changes = detector.detect(today_data, yesterday_data)
    
    # 3. 生成报告
    reporter = Reporter()
    report = reporter.generate(changes, config)
    
    # 4. 推送通知
    notifier = Notifier()
    notifier.send(report, config)

if __name__ == '__main__':
    main()
```

---

## ✅ 验收标准

### 功能完整性
- ✅ 现有竞品监控功能完全兼容
- ✅ 新增股票监控功能
- ✅ 新增数据库监控功能（可选）

### 代码质量
- ✅ 代码结构清晰，易于维护
- ✅ 插件接口简洁，易于扩展
- ✅ 详细注释和文档

### 测试验证
- ✅ 测试竞品监控（原有功能）
- ✅ 测试股票监控（新功能）
- ✅ 测试配置切换

---

## 📝 交付物

1. **代码文件**
   - core/ 目录（核心引擎）
   - plugins/ 目录（插件系统）
   - config/ 目录（配置示例）
   - scripts/run.py（主运行脚本）

2. **文档**
   - README.md（使用说明）
   - MIGRATION.md（迁移指南）
   - ARCHITECTURE.md（架构说明）

3. **测试报告**
   - 测试多种场景
   - 性能对比
   - 问题记录

---

## 🚀 开始工作

请按照以上步骤，逐步改造系统。

**重要提醒**:
1. 保持现有功能完全兼容
2. 代码要清晰、注释要详细
3. 遇到问题随时问我
4. 每完成一个 Step 告诉我进度

**开始吧！** 🚀
