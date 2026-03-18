#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用监控框架 - 主运行脚本
"""

import sys
import json
import os
from datetime import datetime, timedelta

# 添加 core 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.monitor import Monitor
from core.detector import Detector
from core.reporter import Reporter
from core.notifier import Notifier


def main():
    """主函数"""
    # 加载配置
    if len(sys.argv) < 2:
        print("用法: python3 run.py <配置文件>")
        print("示例: python3 run.py config/competitor.json")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print(f"🚀 启动通用监控框架 v2.0")
    print(f"📋 监控类型: {config.get('monitor_type')}")
    print(f"📝 监控名称: {config.get('name', '未命名')}")
    print()
    
    # 获取目录
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data/raw')
    diff_dir = os.path.join(base_dir, 'data/diff')
    reports_dir = os.path.join(base_dir, 'data/reports')
    
    # 1. 抓取数据
    print("📡 [1/4] 正在抓取数据...")
    monitor = Monitor(config)
    today_data = monitor.fetch()
    
    if not monitor.validate(today_data):
        print("❌ 数据验证失败")
        return
    
    print(f"✅ 抓取完成，共 {len(today_data)} 条数据")
    
    # 保存今天的数据
    today = datetime.now().strftime('%Y-%m-%d')
    today_file = monitor.save(today_data, data_dir)
    print(f"📁 数据已保存到: {today_file}")
    
    # 2. 检测变化
    print()
    print("🔍 [2/4] 正在检测变化...")
    detector = Detector()
    
    # 加载昨天的数据
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    yesterday_data = detector.load_data(data_dir, yesterday)
    
    # 检测变化
    changes = detector.detect(today_data, yesterday_data)
    
    # 保存变化数据
    if changes and changes[0].get('type') != 'first_run':
        diff_file = detector.save(changes, diff_dir, today)
        print(f"✅ 检测到 {len(changes)} 个变化")
        print(f"📁 变化数据已保存到: {diff_file}")
    else:
        print("ℹ️  " + changes[0].get('message', '无变化'))
        changes = []
    
    # 3. 生成报告
    print()
    print("📝 [3/4] 正在生成报告...")
    reporter = Reporter()
    report = reporter.generate(changes, config)
    
    # 保存报告
    report_file = reporter.save(report, reports_dir, today)
    print(f"✅ 报告已生成")
    print(f"📁 报告已保存到: {report_file}")
    
    # 4. 推送通知
    print()
    print("📤 [4/4] 正在推送通知...")
    notifier = Notifier()
    success = notifier.send(report, config)
    
    if not success:
        print("💡 提示: 配置飞书 Webhook 后可自动推送")
    
    print()
    print("=" * 50)
    print("✅ 监控完成！")
    print("=" * 50)
    
    # 显示简要统计
    if changes:
        print(f"📊 今日统计:")
        new_count = len([c for c in changes if c['type'] == 'new'])
        updated_count = len([c for c in changes if c['type'] == 'updated'])
        print(f"  ➕ 新增: {new_count}")
        print(f"  🔄 更新: {updated_count}")
    else:
        print("📊 今日统计: 无变化")


if __name__ == '__main__':
    main()
