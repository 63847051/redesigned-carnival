#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用监控框架 - 核心引擎
支持多种数据源：网页、API、数据库
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
from abc import ABC, abstractmethod


class DataSourcePlugin(ABC):
    """数据源插件基类"""
    
    @abstractmethod
    def fetch(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """抓取数据"""
        pass
    
    @abstractmethod
    def validate(self, data: List[Dict[str, Any]]) -> bool:
        """验证数据"""
        pass


class WebpagePlugin(DataSourcePlugin):
    """网页抓取插件"""
    
    def __init__(self):
        try:
            import requests
            from bs4 import BeautifulSoup
            self.requests = requests
            self.BeautifulSoup = BeautifulSoup
        except ImportError:
            raise ImportError("请安装依赖: pip3 install requests beautifulsoup4")
    
    def fetch(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """抓取网页"""
        results = []
        
        for target in config.get('targets', []):
            for page in target.get('pages', []):
                try:
                    headers = {'User-Agent': config.get('user_agent', 'Mozilla/5.0')}
                    response = self.requests.get(page['url'], headers=headers, timeout=30)
                    response.raise_for_status()
                    
                    soup = self.BeautifulSoup(response.text, 'html.parser')
                    
                    results.append({
                        'source': target['name'],
                        'page_type': page['type'],
                        'url': page['url'],
                        'title': soup.find('title').get_text().strip() if soup.find('title') else '',
                        'content': soup.get_text()[:500],
                        'timestamp': datetime.now().isoformat()
                    })
                except Exception as e:
                    results.append({
                        'source': target['name'],
                        'page_type': page.get('type', 'unknown'),
                        'url': page.get('url', ''),
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
        
        return results
    
    def validate(self, data: List[Dict[str, Any]]) -> bool:
        """验证数据"""
        return len(data) > 0


class APIPlugin(DataSourcePlugin):
    """API 调用插件"""
    
    def __init__(self):
        try:
            import requests
            self.requests = requests
        except ImportError:
            raise ImportError("请安装依赖: pip3 install requests")
    
    def fetch(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """调用 API"""
        results = []
        
        api_url = config.get('api_url')
        headers = config.get('headers', {})
        
        for target in config.get('targets', []):
            try:
                params = self._build_params(target, config)
                response = self.requests.get(api_url, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                results.append({
                    'source': target.get('name'),
                    'type': 'api',
                    'code': target.get('code'),
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                results.append({
                    'source': target.get('name'),
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        return results
    
    def _build_params(self, target: Dict, config: Dict) -> Dict:
        """构建 API 参数"""
        params = {}
        
        # 股票代码
        if 'code' in target:
            params['symbol'] = target['code']
        
        # 字段列表
        if 'fields' in target:
            params['fields'] = ','.join(target['fields'])
        
        return params
    
    def validate(self, data: List[Dict[str, Any]]) -> bool:
        """验证数据"""
        return len(data) > 0


class Monitor:
    """通用监控引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.plugin = self._load_plugin()
    
    def _load_plugin(self) -> DataSourcePlugin:
        """加载插件"""
        plugin_type = self.config.get('monitor_type', 'webpage')
        
        if plugin_type == 'webpage':
            return WebpagePlugin()
        elif plugin_type == 'api':
            return APIPlugin()
        else:
            raise ValueError(f"未知的插件类型: {plugin_type}")
    
    def fetch(self) -> List[Dict[str, Any]]:
        """抓取数据"""
        return self.plugin.fetch(self.config)
    
    def validate(self, data: List[Dict[str, Any]]) -> bool:
        """验证数据"""
        return self.plugin.validate(data)
    
    def save(self, data: List[Dict[str, Any]], output_dir: str) -> str:
        """保存数据"""
        os.makedirs(output_dir, exist_ok=True)
        
        today = datetime.now().strftime('%Y-%m-%d')
        output_file = os.path.join(output_dir, f'{today}.json')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return output_file
