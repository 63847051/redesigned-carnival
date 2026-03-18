#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
竞品报告汇总脚本
分析变化数据，生成 Markdown 报告
"""

import json
import os
from datetime import datetime
from collections import defaultdict

def load_json(file_path):
    """加载 JSON 文件"""
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_summary(changes):
    """生成报告摘要"""
    if not changes:
        return "✨ 今天竞品没有明显变化"
    
    new_count = len([c for c in changes if c['type'] == 'new'])
    updated_count = len([c for c in changes if c['type'] == 'updated'])
    deleted_count = len([c for c in changes if c['type'] == 'deleted'])
    
    summary = f"## 📊 变化概览\n\n"
    summary += f"- **总变化数**: {len(changes)}\n"
    summary += f"- **新增页面**: {new_count}\n"
    summary += f"- **更新页面**: {updated_count}\n"
    summary += f"- **删除页面**: {deleted_count}\n"
    
    return summary

def generate_competitor_sections(changes):
    """按竞品分组生成报告"""
    # 按竞品分组
    competitor_changes = defaultdict(list)
    for change in changes:
        competitor_changes[change['competitor']].append(change)
    
    sections = []
    
    for competitor, comp_changes in competitor_changes.items():
        section = f"\n## 🏢 {competitor}\n\n"
        
        # 统计该竞品的变化
        new_count = len([c for c in comp_changes if c['type'] == 'new'])
        updated_count = len([c for c in comp_changes if c['type'] == 'updated'])
        deleted_count = len([c for c in comp_changes if c['type'] == 'deleted'])
        
        section += f"**变化统计**: 新增 {new_count} | 更新 {updated_count} | 删除 {deleted_count}\n\n"
        
        # 新增页面
        new_pages = [c for c in comp_changes if c['type'] == 'new']
        if new_pages:
            section += "### ➕ 新增页面\n\n"
            for change in new_pages:
                section += f"- **{change['page_type']}**: [{change['url']}]({change['url']})\n"
                if change.get('title'):
                    section += f"  - 标题: {change['title']}\n"
            section += "\n"
        
        # 更新页面
        updated_pages = [c for c in comp_changes if c['type'] == 'updated']
        if updated_pages:
            section += "### 🔄 更新页面\n\n"
            
            # 按字段分组
            field_changes = defaultdict(list)
            for change in updated_pages:
                field_changes[change['field']].append(change)
            
            # 标题变化
            if 'title' in field_changes:
                section += "#### 标题变化\n\n"
                for change in field_changes['title']:
                    section += f"- **{change['page_type']}**\n"
                    section += f"  - 旧: {change['old']}\n"
                    section += f"  - 新: {change['new']}\n"
                    section += f"  - 链接: [{change['url']}]({change['url']})\n\n"
            
            # 内容变化
            if 'content' in field_changes:
                section += "#### 内容变化\n\n"
                for change in field_changes['content']:
                    section += f"- **{change['page_type']}**\n"
                    section += f"  - 相似度: {change.get('similarity', 0):.2%}\n"
                    section += f"  - 链接: [{change['url']}]({change['url']})\n"
                    
                    # 如果相似度很低，说明是重大更新
                    if change.get('similarity', 1.0) < 0.5:
                        section += f"  - ⚠️ **重大更新**: 内容变化较大\n"
                    section += "\n"
            
            # 价格变化
            if 'price' in field_changes:
                section += "#### 价格/促销变化\n\n"
                for change in field_changes['price']:
                    section += f"- **{change['page_type']}**\n"
                    section += f"  - 旧: {change['old_price']}\n"
                    section += f"  - 新: {change['new_price']}\n"
                    section += f"  - 链接: [{change['url']}]({change['url']})\n\n"
        
        # 删除页面
        deleted_pages = [c for c in comp_changes if c['type'] == 'deleted']
        if deleted_pages:
            section += "### ➖ 删除页面\n\n"
            for change in deleted_pages:
                section += f"- **{change['page_type']}**: [{change['url']}]({change['url']})\n"
            section += "\n"
        
        sections.append(section)
    
    return sections

def generate_trend_analysis(changes):
    """生成趋势分析"""
    if not changes:
        return "\n## 📈 趋势分析\n\n今天没有明显变化，系统运行正常。"
    
    analysis = "\n## 📈 趋势分析\n\n"
    
    # 统计各类变化
    updated_pages = [c for c in changes if c['type'] == 'updated']
    
    # 内容变化分析
    content_changes = [c for c in updated_pages if c['field'] == 'content']
    if content_changes:
        avg_similarity = sum([c.get('similarity', 0) for c in content_changes]) / len(content_changes)
        
        if avg_similarity < 0.5:
            analysis += "### 🎯 关键发现\n\n"
            analysis += f"- **平均内容相似度**: {avg_similarity:.2%}\n"
            analysis += "- **结论**: 竞品正在积极更新产品/内容，建议密切关注\n\n"
    
    # 价格变化分析
    price_changes = [c for c in updated_pages if c['field'] == 'price']
    if price_changes:
        analysis += "### 💰 价格动态\n\n"
        analysis += f"- **价格变化数量**: {len(price_changes)}\n"
        analysis += "- **建议**: 竞品正在调整价格策略，可能影响市场定位\n\n"
    
    # 新增页面分析
    new_pages = [c for c in changes if c['type'] == 'new']
    if new_pages:
        analysis += "### 🆕 新产品动向\n\n"
        analysis += f"- **新增页面数量**: {len(new_pages)}\n"
        analysis += "- **建议**: 竞品可能正在扩展产品线或增加营销页面\n\n"
    
    if not (content_changes or price_changes or new_pages):
        analysis += "今天的变化主要是小幅调整，没有明显趋势。\n"
    
    return analysis

def generate_report(changes, today):
    """生成完整报告"""
    report = f"# 竞品监控日报\n\n"
    report += f"**日期**: {today}\n"
    report += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += f"**监控范围**: {len(set([c['competitor'] for c in changes]))} 个竞品\n\n"
    report += "---\n\n"
    
    # 摘要
    report += generate_summary(changes)
    
    # 趋势分析
    report += generate_trend_analysis(changes)
    
    # 竞品详情
    report += "---\n\n"
    report += "## 📋 详细变化\n\n"
    
    sections = generate_competitor_sections(changes)
    report += "\n".join(sections)
    
    # 页脚
    report += "\n---\n\n"
    report += "## 📝 说明\n\n"
    report += "- 本报告由 OpenClaw 竞品监控系统自动生成\n"
    report += "- 相似度低于 90% 的内容会被标记为更新\n"
    report += "- 重大更新定义为相似度低于 50%\n"
    report += "- 建议每天查看报告，及时了解竞品动态\n\n"
    report += f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    return report

def save_report(report, reports_dir, today):
    """保存报告"""
    os.makedirs(reports_dir, exist_ok=True)
    
    output_file = os.path.join(reports_dir, f'{today}.md')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return output_file

def main():
    """主函数"""
    print("📝 开始生成竞品监控报告...")
    
    # 获取目录
    data_dir = os.path.join(os.path.dirname(__file__), '../data')
    reports_dir = os.path.join(os.path.dirname(__file__), '../reports')
    
    # 加载变化数据
    today = datetime.now().strftime('%Y-%m-%d')
    diff_file = os.path.join(data_dir, f'diff-{today}.json')
    
    changes = load_json(diff_file)
    
    if not changes:
        print("❌ 找不到变化数据文件")
        print(f"💡 请先运行: python3 scripts/diff.py")
        return
    
    print(f"📅 日期: {today}")
    print(f"📊 变化数量: {len(changes)}")
    
    # 生成报告
    report = generate_report(changes, today)
    
    # 保存报告
    output_file = save_report(report, reports_dir, today)
    
    print(f"\n✅ 报告生成完成！")
    print(f"📁 文件保存到: {output_file}")
    
    # 统计信息
    if changes:
        new_count = len([c for c in changes if c['type'] == 'new'])
        updated_count = len([c for c in changes if c['type'] == 'updated'])
        deleted_count = len([c for c in changes if c['type'] == 'deleted'])
        
        print(f"\n📊 报告统计:")
        print(f"  ➕ 新增: {new_count}")
        print(f"  🔄 更新: {updated_count}")
        print(f"  ➖ 删除: {deleted_count}")
    
    return output_file

if __name__ == '__main__':
    main()
