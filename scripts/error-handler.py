#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误处理系统
- 错误分类
- 友好提示
- 恢复建议
"""

import re
from typing import Dict, Tuple

# 错误分类和友好提示
ERROR_PATTERNS = {
    "api_error": {
        "patterns": [
            r"API.*失败|API.*error|401|403|429",
            r"连接失败|connection.*error|timeout",
            r"API.*Key.*invalid|认证失败"
        ],
        "icon": "🔌",
        "title": "API 连接失败",
        "message": "无法连接到 API 服务",
        "suggestion": "请检查：\n1. 网络连接是否正常\n2. API Key 是否正确\n3. API 服务是否可用\n4. 是否超过速率限制"
    },
    
    "file_error": {
        "patterns": [
            r"文件.*不存在|File.*not.*found|No such file|file.*not.*found",
            r"文件.*损坏|文件.*格式.*错误"
        ],
        "icon": "📁",
        "title": "文件操作失败",
        "message": "无法读取或写入文件",
        "suggestion": "请检查：\n1. 文件路径是否正确\n2. 文件是否存在\n3. 是否有读写权限\n4. 文件格式是否正确"
    },
    
    "command_error": {
        "patterns": [
            r"命令.*不存在|command.*not.*found",
            r"执行.*失败|execution.*error"
        ],
        "icon": "⚙️",
        "title": "命令执行失败",
        "message": "无法执行命令",
        "suggestion": "请检查：\n1. 命令是否正确\n2. 是否安装了必要的工具\n3. 环境变量是否正确\n4. 是否有执行权限"
    },
    
    "network_error": {
        "patterns": [
            r"网络.*错误|network.*error",
            r"DNS.*解析.*失败|无法连接|连接超时"
        ],
        "icon": "🌐",
        "title": "网络连接失败",
        "message": "无法连接到网络",
        "suggestion": "请检查：\n1. 网络连接是否正常\n2. DNS 配置是否正确\n3. 防火墙设置\n4. 代理设置"
    },
    
    "memory_error": {
        "patterns": [
            r"内存.*不足|out.*of.*memory|MemoryError",
            r"无法.*分配.*内存"
        ],
        "icon": "💾",
        "title": "内存不足",
        "message": "系统内存不足",
        "suggestion": "请尝试：\n1. 关闭其他程序\n2. 减少处理的数据量\n3. 重启系统\n4. 增加系统内存"
    },
    
    "permission_error": {
        "patterns": [
            r"权限.*不足|permission.*denied|访问被拒绝|access.*denied",
            r"需要.*root|sudo.*required"
        ],
        "icon": "🔒",
        "title": "权限不足",
        "message": "没有足够的权限执行操作",
        "suggestion": "请尝试：\n1. 使用 sudo 执行命令\n2. 检查文件/目录权限\n3. 使用正确的用户账户\n4. 联系管理员"
    }
}


def classify_error(error: Exception) -> Tuple[str, Dict]:
    """
    分类错误
    
    Returns:
        (错误类型, 错误信息字典)
    """
    error_str = str(error)
    error_str_lower = error_str.lower()
    
    # 遍历所有错误类型
    for error_type, info in ERROR_PATTERNS.items():
        for pattern in info["patterns"]:
            if re.search(pattern, error_str_lower):
                return error_type, info
    
    # 未分类错误
    return "unknown", {
        "icon": "❓",
        "title": "未知错误",
        "message": error_str,
        "suggestion": "请尝试：\n1. 查看详细日志\n2. 重试操作\n3. 重启系统\n4. 联系技术支持"
    }


def get_friendly_error_message(error: Exception) -> str:
    """
    生成用户友好的错误提示
    
    Returns:
        格式化的错误提示字符串
    """
    error_type, info = classify_error(error)
    
    # 生成友好提示
    lines = [
        f"\n{'='*60}",
        f"{info['icon']} {info['title']}",
        f"{'='*60}",
        f"\n📝 {info['message']}",
        f"\n💡 建议解决方案：",
        info['suggestion'],
        f"\n🔍 错误类型: {error_type}",
        f"📋 详细信息: {str(error)}",
        f"\n{'='*60}\n"
    ]
    
    return "\n".join(lines)


def handle_error_with_retry(
    func: callable,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    friendly_message: bool = True
):
    """
    带重试的错误处理装饰器
    
    Args:
        func: 要执行的函数
        max_retries: 最大重试次数
        retry_delay: 重试延迟（秒）
        friendly_message: 是否显示友好提示
    """
    def wrapper(*args, **kwargs):
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                
                if attempt < max_retries - 1:
                    # 还有重试机会
                    import time
                    time.sleep(retry_delay)
                    continue
                else:
                    # 最后一次也失败了
                    if friendly_message:
                        print(get_friendly_error_message(e))
                    else:
                        raise
        
        raise last_error
    
    return wrapper


# ============================================================================
# 测试
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("错误处理系统测试")
    print("="*60)
    
    # 测试不同类型的错误
    test_errors = [
        Exception("API connection failed: 401 Unauthorized"),
        Exception("File not found: /path/to/file"),
        Exception("Permission denied: cannot write to directory"),
        Exception("Network timeout: connection refused"),
        Exception("Unknown error occurred"),
    ]
    
    for i, error in enumerate(test_errors, 1):
        print(f"\n测试 {i}:")
        print(get_friendly_error_message(error))
    
    print("\n✅ 测试完成！")
