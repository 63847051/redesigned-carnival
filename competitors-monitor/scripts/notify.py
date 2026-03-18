#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书推送通知脚本
把报告推送到飞书群
"""

import json
import os
import requests
from datetime import datetime

def load_config():
    """加载配置"""
    config_path = os.path.join(os.path.dirname(__file__), '../config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_report(report_file):
    """加载报告内容"""
    with open(report_file, 'r', encoding='utf-8') as f:
        return f.read()

def send_to_feishu(webhook_url, message):
    """发送消息到飞书"""
    headers = {
        'Content-Type': 'application/json'
    }
    
    data = {
        "msg_type": "text",
        "content": {
            "text": message
        }
    }
    
    try:
        response = requests.post(webhook_url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return True, response.json()
    except Exception as e:
        return False, str(e)

def format_summary_message(report_content, today):
    """格式化摘要消息"""
    # 提取关键信息
    lines = report_content.split('\n')
    
    summary_lines = []
    summary_lines.append(f"📊 竞品监控日报 - {today}")
    summary_lines.append("")
    
    # 找到变化概览
    for i, line in enumerate(lines):
        if '总变化数' in line:
            # 添加下一行的内容
            if i + 1 < len(lines):
                summary_lines.append(lines[i + 1])
            if i + 2 < len(lines):
                summary_lines.append(lines[i + 2])
            if i + 3 < len(lines):
                summary_lines.append(lines[i + 3])
            break
    
    summary_lines.append("")
    
    # 找到关键发现
    for i, line in enumerate(lines):
        if '关键发现' in line:
            if i + 1 < len(lines):
                summary_lines.append("🎯 " + lines[i + 1].strip())
            if i + 2 < len(lines):
                summary_lines.append("💡 " + lines[i + 2].strip())
            break
    
    summary_lines.append("")
    summary_lines.append("📁 完整报告已保存到本地")
    summary_lines.append("⏰ " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    return '\n'.join(summary_lines)

def main():
    """主函数"""
    print("📤 开始推送报告到飞书...")
    
    # 加载配置
    config = load_config()
    webhook_url = config.get('notification', {}).get('feishu_webhook', '')
    
    if not webhook_url or webhook_url == 'YOUR_WEBHOOK_URL_HERE':
        print("⚠️  未配置飞书 Webhook")
        print("💡 请在 config.json 中配置 feishu_webhook")
        print("💡 或者直接运行以下命令查看报告:")
        print("   cat reports/2026-03-18.md")
        return
    
    # 加载报告
    today = datetime.now().strftime('%Y-%m-%d')
    report_file = os.path.join(os.path.dirname(__file__), f'../reports/{today}.md')
    
    if not os.path.exists(report_file):
        print("❌ 找不到报告文件")
        print(f"💡 请先运行: python3 scripts/report.py")
        return
    
    report_content = load_report(report_file)
    
    # 格式化消息
    message = format_summary_message(report_content, today)
    
    print(f"📝 消息内容:")
    print(message)
    print()
    
    # 发送到飞书
    success, result = send_to_feishu(webhook_url, message)
    
    if success:
        print("✅ 推送成功！")
        print(f"📊 飞书响应: {result}")
    else:
        print(f"❌ 推送失败: {result}")
        print("💡 请检查:")
        print("   1. Webhook URL 是否正确")
        print("   2. 网络连接是否正常")
        print("   3. 飞书机器人是否有权限")

if __name__ == '__main__':
    main()
