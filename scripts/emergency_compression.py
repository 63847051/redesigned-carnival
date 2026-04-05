#!/usr/bin/env python3
"""
应急压缩机制 - CloudCode 风格
错误自动恢复，应急压缩触发
"""

import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from layered_compression import LayeredCompression


class EmergencyCompression:
    """应急压缩管理器"""
    
    def __init__(self, max_retries: int = 3):
        """
        初始化应急压缩管理器
        
        Args:
            max_retries: 最大重试次数
        """
        self.max_retries = max_retries
        self.layered_compression = LayeredCompression()
        
        # 错误模式识别
        self.error_patterns = {
            "too_long": [
                r"too long",
                r"maximum context length",
                r"exceed.*limit",
                r"token.*exceed"
            ],
            "rate_limit": [
                r"rate limit",
                r"too many requests",
                r"quota exceeded"
            ],
            "server_error": [
                r"500",
                r"502",
                r"503",
                r"504"
            ]
        }
        
        # 恢复策略
        self.recovery_strategies = {
            "too_long": self._handle_too_long,
            "rate_limit": self._handle_rate_limit,
            "server_error": self._handle_server_error
        }
        
        # 统计信息
        self.stats = {
            "total_errors": 0,
            "auto_recovered": 0,
            "emergency_compressed": 0,
            "retry_success": 0
        }
    
    # ========================================
    # 错误识别
    # ========================================
    def identify_error(self, error: str) -> Optional[str]:
        """
        识别错误类型
        
        Args:
            error: 错误信息
        
        Returns:
            错误类型
        """
        error_lower = error.lower()
        
        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_lower):
                    return error_type
        
        return None
    
    # ========================================
    # 错误处理
    # ========================================
    def handle_error(self, error: str, messages: List[Dict], retry_count: int = 0) -> Dict[str, Any]:
        """
        处理错误并尝试恢复
        
        Args:
            error: 错误信息
            messages: 消息列表
            retry_count: 当前重试次数
        
        Returns:
            处理结果
        """
        print(f"\n🚨 错误发生: {error}")
        print(f"📊 重试次数: {retry_count}/{self.max_retries}")
        
        self.stats["total_errors"] += 1
        
        # 识别错误类型
        error_type = self.identify_error(error)
        
        if not error_type:
            print("⚠️ 未知错误类型，无法自动恢复")
            return {
                "success": False,
                "error": error,
                "reason": "unknown_error_type"
            }
        
        print(f"🔍 错误类型: {error_type}")
        
        # 检查重试次数
        if retry_count >= self.max_retries:
            print("❌ 达到最大重试次数")
            return {
                "success": False,
                "error": error,
                "reason": "max_retries_exceeded"
            }
        
        # 执行恢复策略
        recovery_func = self.recovery_strategies.get(error_type)
        
        if not recovery_func:
            print("⚠️ 没有对应的恢复策略")
            return {
                "success": False,
                "error": error,
                "reason": "no_recovery_strategy"
            }
        
        # 执行恢复
        return recovery_func(error, messages, retry_count)
    
    # ========================================
    # 恢复策略
    # ========================================
    def _handle_too_long(self, error: str, messages: List[Dict], retry_count: int) -> Dict[str, Any]:
        """
        处理上下文过长错误
        
        Args:
            error: 错误信息
            messages: 消息列表
            retry_count: 重试次数
        
        Returns:
            处理结果
        """
        print("  [策略] 应急压缩...")
        
        # 执行应急压缩
        compressed_messages = self._emergency_compress(messages)
        
        self.stats["emergency_compressed"] += 1
        
        return {
            "success": True,
            "messages": compressed_messages,
            "retry_count": retry_count + 1,
            "action": "emergency_compression",
            "original_tokens": self.layered_compression.estimate_messages_tokens(messages),
            "compressed_tokens": self.layered_compression.estimate_messages_tokens(compressed_messages)
        }
    
    def _handle_rate_limit(self, error: str, messages: List[Dict], retry_count: int) -> Dict[str, Any]:
        """
        处理速率限制错误
        
        Args:
            error: 错误信息
            messages: 消息列表
            retry_count: 重试次数
        
        Returns:
            处理结果
        """
        print("  [策略] 等待重试...")
        
        # 计算等待时间（指数退避）
        wait_time = 2 ** retry_count
        print(f"  [等待] {wait_time} 秒...")
        
        return {
            "success": True,
            "messages": messages,
            "retry_count": retry_count + 1,
            "action": "wait_and_retry",
            "wait_time": wait_time
        }
    
    def _handle_server_error(self, error: str, messages: List[Dict], retry_count: int) -> Dict[str, Any]:
        """
        处理服务器错误
        
        Args:
            error: 错误信息
            messages: 消息列表
            retry_count: 重试次数
        
        Returns:
            处理结果
        """
        print("  [策略] 直接重试...")
        
        return {
            "success": True,
            "messages": messages,
            "retry_count": retry_count + 1,
            "action": "direct_retry"
        }
    
    # ========================================
    # 应急压缩
    # ========================================
    def _emergency_compress(self, messages: List[Dict]) -> List[Dict]:
        """
        应急压缩（第 3 层压缩）
        
        Args:
            messages: 消息列表
        
        Returns:
            压缩后的消息列表
        """
        print("  🚨 执行应急压缩...")
        
        # 直接使用第 3 层压缩
        compressed = self.layered_compression.emergency_compress(messages)
        
        # 统计
        original_tokens = self.layered_compression.estimate_messages_tokens(messages)
        compressed_tokens = self.layered_compression.estimate_messages_tokens(compressed)
        
        print(f"  📊 压缩效果: {original_tokens:,} → {compressed_tokens:,} tokens")
        print(f"  📊 压缩比: {(1 - compressed_tokens/original_tokens)*100:.1f}%")
        
        return compressed
    
    # ========================================
    # 自动恢复
    # ========================================
    def auto_recover(self, error: str, messages: List[Dict]) -> Dict[str, Any]:
        """
        自动恢复错误
        
        Args:
            error: 错误信息
            messages: 消息列表
        
        Returns:
            恢复结果
        """
        retry_count = 0
        
        while retry_count < self.max_retries:
            # 处理错误
            result = self.handle_error(error, messages, retry_count)
            
            if not result.get("success"):
                # 无法恢复
                self.stats["auto_recovered"] += 1
                return result
            
            # 更新消息
            messages = result.get("messages", messages)
            retry_count = result.get("retry_count", retry_count + 1)
            
            # 如果是等待策略，这里应该实际等待
            if result.get("action") == "wait_and_retry":
                import time
                wait_time = result.get("wait_time", 1)
                time.sleep(wait_time)
            
            # 如果是应急压缩，说明已经处理
            if result.get("action") == "emergency_compression":
                self.stats["auto_recovered"] += 1
                self.stats["retry_success"] += 1
                return result
            
            # 其他策略继续重试
            # 这里应该实际调用 API，暂时返回成功
            print(f"  ✅ 准备重试 {retry_count}/{self.max_retries}")
        
        # 达到最大重试次数
        return {
            "success": False,
            "error": error,
            "reason": "max_retries_exceeded"
        }
    
    # ========================================
    # 统计信息
    # ========================================
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_errors": self.stats["total_errors"],
            "auto_recovered": self.stats["auto_recovered"],
            "emergency_compressed": self.stats["emergency_compressed"],
            "retry_success": self.stats["retry_success"],
            "recovery_rate": self._calculate_recovery_rate()
        }
    
    def _calculate_recovery_rate(self) -> float:
        """计算恢复率"""
        if self.stats["total_errors"] == 0:
            return 1.0
        
        return self.stats["auto_recovered"] / self.stats["total_errors"]


# ========================================
# 测试代码
# ========================================
def main():
    """测试应急压缩"""
    # 创建测试消息
    test_messages = []
    
    for i in range(100):
        test_messages.append({
            "role": "user" if i % 2 == 0 else "assistant",
            "content": f"这是第 {i+1} 条测试消息。" * 50,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "index": i
            }
        })
    
    # 创建应急压缩器
    emergency = EmergencyCompression(max_retries=3)
    
    # 测试错误处理
    print("="*60)
    print("应急压缩测试")
    print("="*60)
    
    # 模拟错误
    test_errors = [
        "This text is too long, exceeds maximum context length",
        "Rate limit exceeded, too many requests",
        "Server error: 500 Internal Server Error"
    ]
    
    for i, error in enumerate(test_errors, 1):
        print(f"\n{'='*60}")
        print(f"测试用例 {i}: {error[:50]}...")
        print('='*60)
        
        result = emergency.auto_recover(error, test_messages.copy())
        
        print(f"\n✅ 处理结果:")
        print(f"  成功: {result.get('success')}")
        print(f"  动作: {result.get('action')}")
        print(f"  原因: {result.get('reason', 'N/A')}")
        
        if result.get("original_tokens"):
            print(f"  原始 tokens: {result.get('original_tokens'):,}")
            print(f"  压缩 tokens: {result.get('compressed_tokens'):,}")
    
    # 统计信息
    print(f"\n{'='*60}")
    print("📊 统计信息")
    print('='*60)
    stats = emergency.get_stats()
    for key, value in stats.items():
        if key == "recovery_rate":
            print(f"  {key}: {value*100:.1f}%")
        else:
            print(f"  {key}: {value}")


if __name__ == '__main__':
    main()
