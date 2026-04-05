#!/usr/bin/env python3
"""
入口分流机制 - CloudCode 风格
简单命令直接处理，复杂任务加载完整系统
"""

import sys
import time
import subprocess
from typing import Dict, Any, Optional


# 简单命令列表
SIMPLE_COMMANDS = {
    'version': {
        'handler': 'get_version',
        'description': '获取系统版本'
    },
    'status': {
        'handler': 'get_status',
        'description': '获取系统状态'
    },
    'ping': {
        'handler': 'ping',
        'description': '测试系统响应'
    },
    'echo': {
        'handler': 'echo',
        'description': '回显输入'
    },
    'uptime': {
        'handler': 'get_uptime',
        'description': '获取系统运行时间'
    }
}


def is_simple_command(cmd: str) -> bool:
    """
    判断是否为简单命令
    
    Args:
        cmd: 用户输入的命令
    
    Returns:
        是否为简单命令
    """
    cmd_parts = cmd.strip().split()
    if not cmd_parts:
        return False
    
    return cmd_parts[0].lower() in SIMPLE_COMMANDS


def get_version(args: list = None) -> Dict[str, Any]:
    """获取系统版本"""
    try:
        result = subprocess.run(
            ['openclaw', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return {
            "success": True,
            "version": result.stdout.strip(),
            "time": time.time()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_status(args: list = None) -> Dict[str, Any]:
    """获取系统状态"""
    try:
        # Gateway 状态
        gateway_status = subprocess.run(
            ['systemctl', '--user', 'is-active', 'openclaw-gateway'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # 内存使用
        memory_info = subprocess.run(
            ['free', '-m'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        return {
            "success": True,
            "gateway": gateway_status.stdout.strip(),
            "memory": memory_info.stdout.strip(),
            "time": time.time()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def ping(args: list = None) -> Dict[str, Any]:
    """测试系统响应"""
    return {
        "success": True,
        "message": "pong",
        "time": time.time()
    }


def echo(args: list) -> Dict[str, Any]:
    """回显输入"""
    if args is None:
        args = []
    return {
        "success": True,
        "message": " ".join(args),
        "time": time.time()
    }


def get_uptime(args: list = None) -> Dict[str, Any]:
    """获取系统运行时间"""
    try:
        uptime_info = subprocess.run(
            ['uptime', '-p'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return {
            "success": True,
            "uptime": uptime_info.stdout.strip(),
            "time": time.time()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def quick_execute(cmd: str) -> Dict[str, Any]:
    """
    快速执行简单命令
    
    Args:
        cmd: 用户输入的命令
    
    Returns:
        执行结果
    """
    start_time = time.time()
    
    cmd_parts = cmd.strip().split()
    command = cmd_parts[0].lower()
    args = cmd_parts[1:] if len(cmd_parts) > 1 else []
    
    if command not in SIMPLE_COMMANDS:
        return {
            "success": False,
            "error": f"未知命令: {command}"
        }
    
    handler_name = SIMPLE_COMMANDS[command]['handler']
    handler = globals().get(handler_name)
    
    if not handler:
        return {
            "success": False,
            "error": f"处理器未找到: {handler_name}"
        }
    
    try:
        result = handler(args)
        result['execution_time'] = time.time() - start_time
        result['command'] = command
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "command": command,
            "execution_time": time.time() - start_time
        }


def full_system_execute(cmd: str) -> Dict[str, Any]:
    """
    完整系统执行
    
    Args:
        cmd: 用户输入的命令
    
    Returns:
        执行结果
    """
    # 这里应该调用完整的系统
    # 暂时返回提示
    return {
        "success": True,
        "message": f"完整系统执行: {cmd}",
        "note": "此功能需要加载完整系统"
    }


def main(cmd: str) -> Dict[str, Any]:
    """
    主入口 - 实现分流逻辑
    
    Args:
        cmd: 用户输入的命令
    
    Returns:
        执行结果
    """
    if is_simple_command(cmd):
        # 简单命令直接处理
        return quick_execute(cmd)
    else:
        # 复杂任务加载完整系统
        return full_system_execute(cmd)


def format_result(result: Dict[str, Any]) -> str:
    """
    格式化输出结果
    
    Args:
        result: 执行结果
    
    Returns:
        格式化的文本
    """
    if not result.get("success"):
        return f"❌ 错误: {result.get('error', '未知错误')}"
    
    output = []
    output.append("✅ 执行成功")
    output.append(f"📊 执行时间: {result.get('execution_time', 0):.3f} 秒")
    
    if 'version' in result:
        output.append(f"📌 版本: {result['version']}")
    
    if 'gateway' in result:
        output.append(f"🚪 Gateway: {result['gateway']}")
    
    if 'uptime' in result:
        output.append(f"⏱️ 运行时间: {result['uptime']}")
    
    if 'memory' in result:
        output.append(f"💾 内存: {result['memory']}")
    
    if 'message' in result:
        output.append(f"💬 {result['message']}")
    
    if 'note' in result:
        output.append(f"📝 {result['note']}")
    
    return "\n".join(output)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 entry_dispatcher.py <命令>")
        print("\n简单命令:")
        for cmd, info in SIMPLE_COMMANDS.items():
            print(f"  - {cmd}: {info['description']}")
        sys.exit(1)
    
    cmd = " ".join(sys.argv[1:])
    
    print(f"🔄 执行命令: {cmd}")
    
    result = main(cmd)
    print("\n" + format_result(result))
