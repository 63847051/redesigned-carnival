#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票 AI 分析插件
从 daily_stock_analysis 系统获取分析结果
"""

import requests
from typing import List, Dict, Any
from datetime import datetime


class StockAIPlugin:
    """股票 AI 分析插件"""
    
    def __init__(self):
        self.api_base = "http://127.0.0.1:8000"
        self.timeout = 30
    
    def fetch(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从 daily_stock_analysis 获取分析结果"""
        results = []
        
        try:
            # 调用 API 获取历史分析记录
            response = requests.get(
                f"{self.api_base}/api/v1/analysis/history",
                params={
                    "limit": config.get("limit", 10),
                    "offset": 0
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("records", [])
                
                # 添加获取时间
                for item in results:
                    item["fetched_at"] = datetime.now().isoformat()
                    
        except requests.exceptions.RequestException as e:
            print(f"获取股票分析数据失败: {e}")
        except Exception as e:
            print(f"处理股票分析数据时出错: {e}")
        
        return results
    
    def validate(self, data: List[Dict[str, Any]]) -> bool:
        """验证数据格式"""
        if not data:
            return False
        
        # 检查必需字段
        required_fields = ["stock_code", "stock_name", "analysis_result"]
        for item in data:
            if not all(field in item for field in required_fields):
                return False
        
        return True


if __name__ == "__main__":
    # 测试插件
    plugin = StockAIPlugin()
    
    config = {
        "limit": 5
    }
    
    results = plugin.fetch(config)
    
    print(f"获取到 {len(results)} 条股票分析记录")
    
    for item in results[:3]:
        print(f"\n股票: {item.get('stock_name')} ({item.get('stock_code')})")
        print(f"分析结果: {item.get('analysis_result', 'N/A')}")
