#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户交互优化系统 - 简化版
- 智能确认机制
- 风险评估
"""

import re
import sys

def assess_risk(task_description: str):
    """
    评估任务风险等级
    返回: (风险等级, 原因)
    """
    task_lower = task_description.lower()
    
    # 低风险: 常规任务
    low_risk_patterns = [
        r"写个|创建.*脚本|代码|文章",
        r"查询|搜索|查找|读取|分析",
        r"设计.*图|平面图|海报",
        r"测试|验证|检查",
    ]
    
    for pattern in low_risk_patterns:
        if re.search(pattern, task_lower):
            return "low", "常规任务，无系统修改风险"
    
    # 中风险: 涉及配置修改
    medium_risk_patterns = [
        r"配置|修改|更改|设置|调整",
        r"部署|发布|推送|git push",
        r"数据|备份|恢复|迁移",
    ]
    
    for pattern in medium_risk_patterns:
        if re.search(pattern, task_lower):
            return "medium", "涉及系统或数据修改，需要确认"
    
    # 高风险: 删除、破坏性操作
    high_risk_patterns = [
        r"删除|移除|卸载|清理|清除",
        r"停止|关闭|禁用",
        r"重置|恢复出厂|清空|格式化",
    ]
    
    for pattern in high_risk_patterns:
        if re.search(pattern, task_lower):
            return "high", "破坏性操作，必须详细确认"
    
    # 默认中等风险
    return "medium", "未识别的任务，建议确认"

def test_risk_assessment():
    """测试风险评估"""
    print("="*60)
    print("风险评估测试")
    print("="*60)
    
    test_tasks = [
        "写个 Python 脚本",
        "配置系统设置",
        "删除所有文件",
        "查询今天的天气",
        "优化性能",
    ]
    
    for task in test_tasks:
        risk, reason = assess_risk(task)
        
        if risk == "low":
            status = "✅"
        elif risk == "medium":
            status = "⚠️"
        else:  # high
            status = "🔴"
        
        print(f"{status} {task}")
        print(f"   风险: {risk}")
        print(f"   原因: {reason}")
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test-risk":
        test_risk_assessment()
    else:
        print("请使用 --test-risk 参数测试")
