#!/usr/bin/env python3
"""
抖音视频信息提取脚本（简化版）
"""

import subprocess
import json
import sys


def extract_douyin_video_info(url):
    """提取抖音视频信息"""
    try:
        cmd = [
            'yt-dlp',
            '--dump-json',
            '--skip-download',
            '-o', '/tmp/douyin',
            url
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr,
                "url": url
            }
        
        # 读取 JSON 文件
        import os
        json_file = '/tmp/douyin.info.json'
        
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 清理临时文件
            os.remove(json_file)
            
            return {
                "success": True,
                "url": url,
                "title": data.get('title', ''),
                "uploader": data.get('uploader', ''),
                "view_count": data.get('view_count', 0),
                "like_count": data.get('like_count', 0),
                "comment_count": data.get('comment_count', 0),
                "raw_data": data
            }
        
        return {
            "success": False,
            "error": "无法解析视频信息",
            "url": url
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url
        }


def main():
    if len(sys.argv) < 2:
        print("用法: python3 extract_douyin.py <抖音视频链接>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    print("🔄 正在提取抖音视频信息...")
    info = extract_douyin_video_info(url)
    
    if info.get("success"):
        data = info.get("raw_data", {})
        print("\n✅ 提取成功！")
        print("=" * 60)
        print("📺 标题:", data.get('title', '未知'))
        print("👤 UP 主:", data.get('uploader', '未知'))
        print("📅 发布时间:", data.get('upload_date', '未知'))
        print("👁 观看次数:", data.get('view_count', 0))
        print("👍 点赞数:", data.get('like_count', 0))
        print("💬 评论数:", data.get('comment_count', 0))
        print("🔗 链接:", url)
        
        if data.get('description'):
            print("\n📝 描述:")
            print("   ", data.get('description', ''))
        
        if data.get('tags'):
            print("\n🏷️ 标签:")
            for tag in data.get('tags', []):
                print("   -", tag)
    else:
        print("\n❌ 提取失败")
        print("错误:", info.get('error', '未知错误'))


if __name__ == '__main__':
    main()
