#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用监控框架 - 报告生成
"""

from datetime import datetime
from typing import List, Dict, Any


class Reporter:
    """通用报告生成"""
    
    def __init__(self):
        pass
    
    def generate(self, changes: List[Dict], config: Dict) -> str:
        """生成报告"""
        report_type = config.get('monitor_type', 'webpage')
        report_name = config.get('name', '监控报告')
        
        if report_type == 'webpage':
            return self._generate_webpage_report(changes, report_name)
        elif report_type == 'api':
            return self._generate_api_report(changes, report_name)
        else:
            return self._generate_generic_report(changes, report_name)
    
    def _generate_webpage_report(self, changes: List[Dict], name: str) -> str:
        """生成网页监控报告"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        report = f"# {name}\n\n"
        report += f"**日期**: {today}\n"
        report += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += "---\n\n"
        
        # 统计
        new_count = len([c for c in changes if c['type'] == 'new'])
        updated_count = len([c for c in changes if c['type'] == 'updated'])
        
        report += "## 📊 变化概览\n\n"
        report += f"- **总变化数**: {len(changes)}\n"
        report += f"- **新增**: {new_count}\n"
        report += f"- **更新**: {updated_count}\n\n"
        
        # 详细变化
        report += "## 📋 详细变化\n\n"
        
        for change in changes:
            report += f"- {change['message']}\n"
        
        report += "\n---\n\n"
        report += "## 📝 说明\n\n"
        report += "本报告由通用监控框架自动生成\n\n"
        
        return report
    
    def _generate_api_report(self, changes: List[Dict], name: str) -> str:
        """生成 API 监控报告"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        report = f"# {name}\n\n"
        report += f"**日期**: {today}\n"
        report += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += "---\n\n"
        
        report += "## 📊 数据变化\n\n"
        
        for change in changes:
            report += f"- {change['message']}\n"
        
        return report
    
    def _generate_generic_report(self, changes: List[Dict], name: str) -> str:
        """生成通用报告"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        report = f"# {name}\n\n"
        report += f"**日期**: {today}\n\n"
        report += "---\n\n"
        report += "## 📊 变化\n\n"
        
        for change in changes:
            report += f"- {change.get('message', 'Unknown change')}\n"
        
        return report
    
    def save(self, report: str, output_dir: str, date: str) -> str:
        """保存报告"""
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f'{date}.md')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return output_file
