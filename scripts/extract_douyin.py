#!/usr/bin/env python3
"""
抖音视频信息提取脚本
使用 yt-dlp 提取视频信息
"""

import subprocess
import json
import sys
from typing import Dict, Any, Optional


def extract_douyin_video_info(url: str) -> Dict[str, Any]:
    """
    提取抖音视频信息
    
    Args:
        url: 抖音视频分享链接
    
    Returns:
        视频信息字典
    """
    try:
        # 使用 yt-dlp 提取视频信息
        cmd = [
            'yt-dlp',
            '--dump-json',
            '--skip-download',  # 不下载视频
            '--write-info-json',  # 写入 info.json
            '-o', '/tmp/douyin_video',  # 输出文件前缀
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
        
        # 读取生成的 JSON 文件
        import os
        json_file = '/tmp/douyin_video.info.json'
        
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 清理临时文件
            os.remove(json_file)
            if os.path.exists('/tmp/douyin_video.json'):
                os.remove('/tmp/douyin_video.json')
            
            return {
                "success": True,
                "url": url,
                "title": data.get('title', ''),
                "description": data.get('description', ''),
                "uploader": data.get('uploader', ''),
                "upload_date": data.get('upload_date', ''),
                "view_count": data.get('view_count', 0),
                "like_count": data.get('like_count', 0),
                "comment_count": data.get('comment_count', 0),
                "share_count": data.get('share_count', 0),
                "duration": data.get('duration', ''),
                "tags": data.get('tags', []),
                "raw_data": data
            }
        else:
            return {
                "success": False,
                "error": "无法解析视频信息",
                "url": url
            }
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "请求超时",
            "url": url
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url
        }


def format_video_info(info: Dict[str, Any]) -> str:
    """
    格式化视频信息输出
    
    Args:
        info: 视频信息字典
    
    Returns:
        格式化的文本输出
    """
    if not info.get("success"):
        return f"❌ 无法提取视频信息\n{info.get('error', '未知错误')}"
    
    data = info.get('raw_data', {})
    
    output = []
    output.append("🎬 抖音视频信息")
    output.append("=" * 60)
    output.append(f"📺 标题: {data.get('title', '未知')}")
    output.append(f"👤 UP 主: {data.get('uploader', '未知')}")
    output.append(f"📅 发布时间: {data.get('upload_date', '未知')}")
    output.append(f"👁 观看次数: {data.get('view_count', 0):,}")
    output.append(f"👍 点赞数: {data.get('like_count', 0):,}")
    output.append(f"💬 评论数: {data.get('comment_count', 0):,}\")
    output.append(f"🔗 链接: {info.get('url', '')}")
    
    if data.get('duration'):
        output.append(f"⏱️ 时长: {data.get('duration', '')}")
    
    if data.get('tags'):
        output.append(f("🏷️ 标签: {', '.join(data.get('tags', []))}")
    
    if data.get('description'):
        output.append(f"\n📝 描述:")
        output.append(f"   {data.get('description', '')}")
    
    return "\n".join(output)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 extract_douyin.py <抖音视频链接>")
        print("\n示例:")
        print("  python3 extract_douyin.py https://v.douyin.com/wYZLOj3ywPQ/")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # 提取视频信息
    print("🔄 正在提取抖音视频信息...")
    info = extract_douyin_video_info(url)
    
    # 格式化输出
    print("\n" + format_video_info(info))


if __name__ == '__main__':
    main()
