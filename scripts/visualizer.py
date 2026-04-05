#!/usr/bin/env python3
# -*- coding: HTML -*-
"""
可视化界面生成器 - Karpathy 风格
自动生成知识库可视化页面
"""

import json
from pathlib import Path
from datetime import datetime

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
COMPILED_DIR = WORKSPACE / "knowledge-compiled"
OUTPUT_DIR = WORKSPACE / "knowledge-visual"
KNOWLEDGE_FILE = COMPILED_DIR / "knowledge.json"
OUTPUT_FILE = OUTPUT_DIR / "index.html"


class Visualizer:
    """可视化界面生成器"""
    
    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True)
    
    def generate(self) -> str:
        """生成可视化界面"""
        print("🎨 生成可视化界面...")
        
        # 加载知识库
        if not KNOWLEDGE_FILE.exists():
            print("   ⚠️ 知识库不存在，先运行编译器")
            return ""
        
        with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 生成 HTML
        html = self._generate_html(data)
        
        # 保存
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"   ✅ 已生成: {OUTPUT_FILE}")
        print(f"   🔗 访问: file://{OUTPUT_FILE}")
        
        return str(OUTPUT_FILE)
    
    def _generate_html(self, data: Dict) -> str:
        """生成 HTML"""
        
        compiled = data.get('compiled', [])
        index = data.get('index', {})
        stats = data.get('stats', {})
        
        # 构建页面
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>知识库可视化</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .stat h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            color: #666;
        }}
        .stat .value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        .section {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .section h2 {{
            margin: 0 0 20px 0;
            color: #333;
            font-size: 24px;
        }}
        .item {{
            padding: 10px;
            border-left: 3px solid #667eea;
            margin-bottom: 10px;
            background: #f9f9f9;
            padding-left: 15px;
        }}
        .item-title {{
            font-weight: bold;
            color: #333;
        }}
        .item-path {{
            color: #666;
            font-size: 14px;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 50px;
            padding: 20px;
            border-top: 1px solid #ddd;
        }}
        .search-box {{
            margin: 30px 0;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 8px;
        }}
        #search-input {{
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }}
        #search-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }}
        #search-btn:hover {{
            background: #5568d3;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📚 知识库可视化</h1>
        <p>让 LLM 驱动的知识库，像 Wiki 一样浏览</p>
    </div>
    
    <div class="stats">
        <div class="stat">
            <h3>总文档数</h3>
            <div class="value">{stats.get('total', 0)}</div>
        </div>
        <div class="stat">
            <h3>关键词数</h3>
            <div class="value">{len(index.get('keywords', {}))}</div>
        </div>
        <div class="stat">
            <h3>概念数</h3>
            <div class="value">{len(index.get('concepts', {}))}</div>
        </div>
        <div class="stat">
            <h3>更新时间</h3>
            <div class="value" style="font-size: 14px;">{stats.get('compiled_at', '未知')}</div>
        </div>
    </div>
    
    <div class="search-box">
        <input type="text" id="search-input" placeholder="搜索关键词..." onkeypress="if(event.key === 'Enter') searchKnowledge()">
        <button id="search-btn" onclick="searchKnowledge()">🔍 搜索</button>
    </div>
    
    <div id="results"></div>
    
    <div class="section">
        <h2>📚 最新文档</h2>
        <div id="documents">
"""
        
        # 添加最新文档（前 10 个）
        for item in compiled[:10]:
            item_path = item.get('path', 'unknown')
            item_summary = item.get('summary', '无摘要')
            
            html += f"""
            <div class="item">
                <div class="item-title">{item.get('title', item_path)}</div>
                <div class="item-path">{item_path}</div>
                <div class="item-summary">{item_summary[:100]}...</div>
            </div>
            """
        
        html += """
        </div>
    </div>
    
    <div class="section">
        <h2🏷 关键词索引</h2>
        <div class="keywords">
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px;">
"""
        
        # 添加关键词（前 20 个）
        for kw, paths in list(index.get('keywords', {}).items())[:20]:
            html += f"""
                <div style="background: #f9f9f9; padding: 10px; border-radius: 4px;">
                    <strong>{kw}</strong>
                    <p style="margin: 0; font-size: 12px; color: #666;">
                        {', '.join(paths[:3])}
                    </p>
                </div>
                """
        
        html += """
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        <p>Powered by OpenClaw + Claude Code 原则</p>
    </div>
    
    <script>
        function searchKnowledge() {{
            const input = document.getElementById('search-input').value;
            const results = document.getElementById('results');
            
            if (!input) {{
                return;
            }}
            
            // TODO: 实际搜索功能
            results.innerHTML = `
                <p>搜索功能开发中...</p>
                <p>搜索: <strong>${input}</strong></p>
            `;
        }}
        
        // 自动聚焦搜索框
        document.getElementById('search-input').focus();
    </script>
</body>
</html>
"""
        
        return html


def main():
    """主函数"""
    visualizer = Visualizer()
    
    print("🎨 生成可视化界面...")
    url = visualizer.generate()
    
    print("")
    print("✅ 可视化界面已生成！")
    print(f"🔗 访问: {url}")
    print("")
    print("💡 使用方法:")
    print("   在浏览器中打开上面的 URL")
    print("   可以像浏览 Wiki 一样查看知识库")


if __name__ == "__main__":
    main()
