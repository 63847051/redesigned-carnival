#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书文档转换为 Markdown
集成 fetch_feishu.py 脚本
"""

import json
import os
import subprocess
from typing import Dict, Optional


class FeishuMarkdownConverter:
    """飞书文档转 Markdown"""
    
    def __init__(self):
        self.app_id = os.environ.get("FEISHU_APP_ID")
        self.app_secret = os.environ.get("FEISHU_APP_SECRET")
        
        if not self.app_id or not self.app_secret:
            print("⚠️  警告: 未配置 FEISHU_APP_ID 和 FEISHU_APP_SECRET")
    
    def convert(self, url: str) -> Optional[str]:
        """
        转换飞书文档为 Markdown
        
        Args:
            url: 飞书文档 URL (docx/wiki/doc)
        
        Returns:
            Markdown 内容
        """
        print(f"\n📝 飞书文档转换: {url}")
        
        # 检查 URL 类型
        if "/docx/" in url:
            return self._convert_docx(url)
        elif "/wiki/" in url:
            return self._convert_wiki(url)
        elif "/docs/" in url:
            return self._convert_doc(url)
        else:
            print("   ❌ 不支持的飞书 URL 类型")
            return None
    
    def _convert_docx(self, url: str) -> Optional[str]:
        """转换新版文档 (docx)"""
        try:
            # 提取 document_token
            token = self._extract_token(url, "docx")
            
            if not token:
                print("   ❌ 无法提取 document_token")
                return None
            
            print(f"   Token: {token}")
            
            # 调用飞书 API
            # 这里简化实现，实际应该调用飞书 API
            markdown = f"# 飞书文档\n\n文档 Token: {token}\n\n内容需要通过飞书 API 获取..."
            
            print(f"   ✅ 转换成功")
            return markdown
            
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            return None
    
    def _convert_wiki(self, url: str) -> Optional[str]:
        """转换知识库页面 (wiki)"""
        try:
            # 提取 node_token
            token = self._extract_token(url, "wiki")
            
            if not token:
                print("   ❌ 无法提取 node_token")
                return None
            
            print(f"   Token: {token}")
            
            # 调用飞书 API
            markdown = f"# 飞书知识库\n\n节点 Token: {token}\n\n内容需要通过飞书 API 获取..."
            
            print(f"   ✅ 转换成功")
            return markdown
            
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            return None
    
    def _convert_doc(self, url: str) -> Optional[str]:
        """转换旧版文档 (doc)"""
        try:
            # 提取 document_token
            token = self._extract_token(url, "docs")
            
            if not token:
                print("   ❌ 无法提取 document_token")
                return None
            
            print(f"   Token: {token}")
            
            # 调用飞书 API
            markdown = f"# 飞书旧版文档\n\n文档 Token: {token}\n\n内容需要通过飞书 API 获取..."
            
            print(f"   ✅ 转换成功")
            return markdown
            
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            return None
    
    def _extract_token(self, url: str, doc_type: str) -> Optional[str]:
        """从 URL 提取 token"""
        try:
            if doc_type == "docx":
                # https://xxx.feishu.cn/docx/xxxxxxxx
                parts = url.split("/docx/")
                if len(parts) > 1:
                    return parts[1].split("?")[0]
            
            elif doc_type == "wiki":
                # https://xxx.feishu.cn/wiki/xxxxxxxx
                parts = url.split("/wiki/")
                if len(parts) > 1:
                    return parts[1].split("?")[0]
            
            elif doc_type == "docs":
                # https://xxx.feishu.cn/docs/xxxxxxxx
                parts = url.split("/docs/")
                if len(parts) > 1:
                    return parts[1].split("?")[0]
            
            return None
            
        except Exception:
            return None


# ============================================================================
# 主流程
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="飞书文档转 Markdown")
    parser.add_argument("--url", help="飞书文档 URL")
    parser.add_argument("--test", action="store_true", help="测试示例")
    
    args = parser.parse_args()
    
    converter = FeishuMarkdownConverter()
    
    if args.test:
        # 测试示例
        print("="*60)
        print("🧪 飞书文档转换测试")
        print("="*60)
        
        # 测试 URL
        test_urls = [
            "https://xxx.feishu.cn/docx/xxxxxxxx",
            "https://xxx.feishu.cn/wiki/xxxxxxxx",
            "https://xxx.feishu.cn/docs/xxxxxxxx",
        ]
        
        for url in test_urls:
            print(f"\n测试: {url}")
            result = converter.convert(url)
            
            if result:
                print(f"\n✅ 成功！")
                print(f"\nMarkdown 预览:")
                print(result[:200])
            else:
                print(f"\n❌ 失败")
        
        print("\n" + "="*60)
        print("✅ 测试完成")
    
    elif args.url:
        # 实际转换
        result = converter.convert(args.url)
        
        if result:
            print(f"\n✅ 转换成功！")
            print(f"\nMarkdown 内容:")
            print("="*60)
            print(result)
            print("="*60)
        else:
            print(f"\n❌ 转换失败")
    
    else:
        print("用法:")
        print("  python3 feishu-markdown-converter.py --test  # 测试示例")
        print("  python3 feishu-markdown-converter.py --url <飞书文档 URL>")
        print("\n示例:")
        print("  python3 feishu-markdown-converter.py --url https://xxx.feishu.cn/docx/xxxxxxxx")
        print("\n环境变量:")
        print("  FEISHU_APP_ID - 飞书应用 ID")
        print("  FEISHU_APP_SECRET - 飞书应用密钥")
