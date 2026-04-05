#!/usr/bin/env python3
"""
OpenCLI 包装脚本
为 OpenClaw 系统提供 OpenCLI 功能的 Python 接口
"""

import subprocess
import json
import sys
from typing import Optional, List, Dict, Any


class OpenCLIWrapper:
    """OpenCLI 包装类"""
    
    def __init__(self, timeout: int = 30):
        """
        初始化 OpenCLI 包装器
        
        Args:
            timeout: 命令超时时间（秒）
        """
        self.timeout = timeout
    
    def run_command(
        self,
        platform: str,
        action: str,
        args: Optional[List[str]] = None,
        format: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        执行 OpenCLI 命令
        
        Args:
            platform: 平台名称 (bilibili, zhihu, twitter, etc.)
            action: 动作 (hot, search, bookmarks, etc.)
            args: 额外参数列表
            format: 输出格式 (json, yaml, markdown, csv)
        
        Returns:
            包含 status, data, error 的字典
        """
        cmd = ['opencli', platform, action]
        
        # 添加格式参数
        if format:
            cmd.extend(['-f', format])
        
        # 添加额外参数
        if args:
            cmd.extend(args)
        
        try:
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            # 检查返回码
            if result.returncode != 0:
                return {
                    'status': 'error',
                    'data': None,
                    'error': result.stderr.strip() or '命令执行失败'
                }
            
            # 尝试解析 JSON
            if format == 'json':
                try:
                    data = json.loads(result.stdout)
                    return {
                        'status': 'success',
                        'data': data,
                        'error': None
                    }
                except json.JSONDecodeError:
                    return {
                        'status': 'success',
                        'data': result.stdout,
                        'error': None
                    }
            
            # 文本输出
            return {
                'status': 'success',
                'data': result.stdout,
                'error': None
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'error',
                'data': None,
                'error': f'命令超时（超过 {self.timeout} 秒）'
            }
        except Exception as e:
            return {
                'status': 'error',
                'data': None,
                'error': str(e)
            }
    
    def bilibili_hot(self, format: str = 'json') -> Dict[str, Any]:
        """获取 B 站热门视频"""
        return self.run_command('bilibili', 'hot', format=format)
    
    def zhihu_hot(self, format: str = 'json') -> Dict[str, Any]:
        """获取知乎热榜"""
        return self.run_command('zhihu', 'hot', format=format)
    
    def twitter_timeline(self, format: str = 'json') -> Dict[str, Any]:
        """获取 Twitter 时间线"""
        return self.run_command('twitter', 'timeline', format=format)
    
    def twitter_bookmarks(self, format: str = 'json') -> Dict[str, Any]:
        """获取 Twitter 书签"""
        return self.run_command('twitter', 'bookmarks', format=format)
    
    def reddit_hot(self, subreddit: str = '', format: str = 'json') -> Dict[str, Any]:
        """获取 Reddit 热帖"""
        args = [subreddit] if subreddit else None
        return self.run_command('reddit', 'hot', args=args, format=format)
    
    def xiaohongshu_note(self, note_id: str, format: str = 'json') -> Dict[str, Any]:
        """获取小红书笔记"""
        return self.run_command('xiaohongshu', 'note', args=[note_id], format=format)
    
    def xueqiu_stock(self, symbol: str, format: str = 'json') -> Dict[str, Any]:
        """获取雪球股票数据"""
        return self.run_command('xueqiu', 'stock', args=[symbol], format=format)
    
    def kr36_hot(self, category: str = 'renqi', format: str = 'json') -> Dict[str, Any]:
        """获取 36 氦热榜"""
        return self.run_command('36kr', 'hot', args=[category], format=format)
    
    def boss_search(self, keyword: str, format: str = 'json') -> Dict[str, Any]:
        """BOSS 直聘搜索职位"""
        return self.run_command('boss', 'search', args=[keyword], format=format)
    
    def youtube_video(self, video_id: str, format: str = 'json') -> Dict[str, Any]:
        """获取 YouTube 视频信息"""
        return self.run_command('youtube', 'video', args=[video_id], format=format)
    
    def arxiv_search(self, query: str, format: str = 'json') -> Dict[str, Any]:
        """搜索 arXiv 论文"""
        return self.run_command('arxiv', 'search', args=[query], format=format)
    
    def list_all_commands(self) -> Dict[str, Any]:
        """列出所有可用命令"""
        return self.run_command('list', '', format='text')
    
    def doctor(self) -> Dict[str, Any]:
        """诊断 OpenCLI 浏览器连接"""
        return self.run_command('doctor', '', format='text')


def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenCLI 包装脚本')
    parser.add_argument('platform', help='平台名称')
    parser.add_argument('action', help='动作名称')
    parser.add_argument('--format', '-f', default='json', help='输出格式')
    parser.add_argument('--args', nargs='*', help='额外参数')
    
    args = parser.parse_args()
    
    # 创建包装器
    wrapper = OpenCLIWrapper()
    
    # 执行命令
    result = wrapper.run_command(
        args.platform,
        args.action,
        args=args.args,
        format=args.format
    )
    
    # 输出结果
    if result['status'] == 'success':
        print(result['data'])
        sys.exit(0)
    else:
        print(f"错误: {result['error']}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
