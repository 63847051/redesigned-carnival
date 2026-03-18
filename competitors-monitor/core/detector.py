#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用监控框架 - 变化检测
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import difflib


class Detector:
    """通用变化检测"""
    
    def __init__(self):
        pass
    
    def load_data(self, data_dir: str, date: str) -> List[Dict[str, Any]]:
        """加载指定日期的数据"""
        file_path = os.path.join(data_dir, f'{date}.json')
        
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def compare_text(self, text1: str, text2: str) -> Dict[str, Any]:
        """对比两段文本"""
        if not text1 or not text2:
            return None
        
        seq = difflib.SequenceMatcher(None, text1, text2)
        similarity = seq.ratio()
        
        if similarity < 0.9:
            return {
                'similarity': similarity,
                'changed': True
            }
        
        return {'similarity': similarity, 'changed': False}
    
    def detect(self, today_data: List[Dict], yesterday_data: List[Dict]) -> List[Dict[str, Any]]:
        """检测变化"""
        if not yesterday_data:
            return [{
                'type': 'first_run',
                'message': '首次运行，没有历史数据对比'
            }]
        
        changes = []
        
        # 构建昨天的数据字典
        yesterday_dict = {}
        for item in yesterday_data:
            key = self._get_key(item)
            yesterday_dict[key] = item
        
        # 对比今天的数据
        for item in today_data:
            key = self._get_key(item)
            
            if key not in yesterday_dict:
                changes.append({
                    'type': 'new',
                    'source': item.get('source'),
                    'page_type': item.get('page_type'),
                    'url': item.get('url'),
                    'message': f"新增: {item.get('source')} - {item.get('page_type')}"
                })
            else:
                yesterday_item = yesterday_dict[key]
                
                # 对比内容
                if 'content' in item and 'content' in yesterday_item:
                    diff = self.compare_text(
                        yesterday_item.get('content', ''),
                        item.get('content', '')
                    )
                    if diff and diff.get('changed'):
                        changes.append({
                            'type': 'updated',
                            'field': 'content',
                            'source': item.get('source'),
                            'page_type': item.get('page_type'),
                            'similarity': diff['similarity'],
                            'message': f"内容变化: {item.get('source')} - {item.get('page_type')} ({diff['similarity']:.2%})"
                        })
        
        return changes
    
    def _get_key(self, item: Dict[str, Any]) -> str:
        """生成唯一标识"""
        return f"{item.get('source', '')}_{item.get('page_type', '')}"
    
    def save(self, changes: List[Dict], output_dir: str, date: str) -> str:
        """保存变化数据"""
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f'diff-{date}.json')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(changes, f, ensure_ascii=False, indent=2)
        
        return output_file
