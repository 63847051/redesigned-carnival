#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动摄入系统 - Karpathy 风格
自动从多个来源收集知识
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import requests
from bs4 import BeautifulSoup

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
RAW_DIR = WORKSPACE / "knowledge-raw"
COMPILED_DIR = WORKSPACE / "knowledge-compiled"


class AutoIngestor:
    """自动摄入器"""
    
    def __init__(self):
        self.raw_dir = RAW_DIR
        self.raw_dir.mkdir(exist_ok=True)
        
        # 创建子目录
        (self.raw_dir / "articles").mkdir(exist_ok=True)
        (self.raw_dir / "papers").mkdir(exist_ok=True)
        (self.raw_dir / "repos").mkdir(exist_ok=True)
        (self.raw_dir / "images").mkdir(exist_ok=True)
    
    def ingest_url(self, url: str) -> Dict:
        """
        摄入 URL（文章）
        """
        print(f"📥 摄入 URL: {url}")
        
        try:
            # 获取网页内容
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取标题
            title = soup.title.string or "未知标题"
            
            # 提取正文
            content = ''
            if soup.article:
                article = soup.find('div', class_='_resizeObserver_')
                if article:
                    content = article.get_text(separator='\n', strip=True)
            else:
                content = soup.get_text(separator='\n', strip=True)
            
            # 保存为 Markdown
            filename = self._safe_filename(title)
            filepath = self.raw_dir / "articles" / f"{filename}.md"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n")
                f.write(f"> 来源: {url}\n\n")
                f.write(content)
            
            print(f"   ✅ 已保存: {filename}")
            return {
                'source': url,
                'title': title,
                'file': str(filepath),
                'size': len(content)
            }
            
        except Exception as e:
            print(f"   ❌ 摄入失败: {e}")
            return {}
    
    def ingest_github_repo(self, repo_url: str) -> Dict:
        """
        摄入 GitHub 仓库（README）
        """
        print(f"📥 摄入 GitHub: {repo_url}")
        
        try:
            # 提取 repo 信息
            parts = repo_url.rstrip('/').split('/')
            repo_name = parts[-1]
            
            # 克隆或拉取
            repo_path = self.raw_dir / "repos" / repo_name
            if repo_path.exists():
                subprocess.run(
                    ['git', 'pull'],
                    cwd=repo_path,
                    capture_output=True
                )
            else:
                subprocess.run(
                    ['git', 'clone', repo_url],
                    cwd=self.raw_dir / "repos",
                    capture_output=True
                )
            
            print(f"   ✅ 已克隆: {repo_name}")
            return {
                'source': repo_url,
                'name': repo_name,
                'path': str(repo_path),
                'files': len(list(repo_path.glob('*')))
            
        except Exception as e:
            print(f"   ❌ 摄入失败: {e}")
            return {}
    
    def _safe_filename(self, title: str) -> str:
        """生成安全的文件名"""
        # 移除特殊字符
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))
        return safe_title[:50]  # 限制长度


def main():
    """主函数"""
    ingestor = AutoIngestor()
    
    print("🤖 自动摄入系统 - Karpathy 风格")
    print("=" * 60)
    print("")
    
    # 示例：摄入 URL
    url = "https://github.com/openclaw/openclaw"
    
    print(f"📥 测试摄入: {url}")
    result = ingestor.ingest_url(url)
    
    if result:
        print(f"   来源: {result['source']}")
        print(f"   标题: {result['title']}")
        print(f"   文件: {result['file']}")
        print(f"   大小: {result['size']} 字符")
    
    print("")
    print("✅ 自动摄入系统准备完成！")
    print("")
    print("🚀 使用方法:")
    print("   python3 scripts/auto-ingestor.py")


if __name__ == "__main__":
    main()
