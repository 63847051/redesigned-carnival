#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用监控框架 - 推送通知
"""

import os
from datetime import datetime
from typing import Dict


class Notifier:
    """通用推送通知"""
    
    def __init__(self):
        pass
    
    def format_message(self, report: str, config: Dict) -> str:
        """格式化消息"""
        name = config.get('name', '监控报告')
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 提取摘要
        lines = report.split('\n')
        summary_lines = []
        
        summary_lines.append(f"📊 {name} - {today}")
        summary_lines.append("")
        
        # 找到变化概览
        for i, line in enumerate(lines):
            if '总变化数' in line or '数据变化' in line:
                if i + 1 < len(lines):
                    summary_lines.append(lines[i + 1])
                break
        
        summary_lines.append("")
        summary_lines.append(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return '\n'.join(summary_lines)
    
    def send(self, report: str, config: Dict) -> bool:
        """发送通知"""
        # 获取通知配置
        notification = config.get('notification', {})
        webhook_url = notification.get('feishu_webhook', '')
        
        if not webhook_url or webhook_url == 'YOUR_WEBHOOK_URL_HERE':
            print("⚠️  未配置飞书 Webhook")
            print("💡 报告已保存到本地")
            return False
        
        # 格式化消息
        message = self.format_message(report, config)
        
        # 发送到飞书
        try:
            import requests
            
            headers = {'Content-Type': 'application/json'}
            data = {
                "msg_type": "text",
                "content": {"text": message}
            }
            
            response = requests.post(webhook_url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            print("✅ 推送成功！")
            return True
            
        except Exception as e:
            print(f"❌ 推送失败: {e}")
            return False
