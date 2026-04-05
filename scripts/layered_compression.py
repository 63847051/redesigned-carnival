#!/usr/bin/env python3
"""
分层压缩策略 - CloudCode 风格
3 层压缩机制，精细上下文管理
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class LayeredCompression:
    """分层压缩管理器"""
    
    def __init__(self, max_tokens: int = 128000):
        """
        初始化分层压缩管理器
        
        Args:
            max_tokens: 最大 token 数量
        """
        self.max_tokens = max_tokens
        self.safety_margin = 0.1  # 10% 安全空间
        self.effective_max = int(max_tokens * (1 - self.safety_margin))
        
        # 压缩阈值
        self.layer1_threshold = int(self.effective_max * 0.8)  # 第 1 层阈值
        self.layer2_threshold = int(self.effective_max * 0.9)  # 第 2 层阈值
        self.layer3_threshold = self.effective_max  # 第 3 层阈值
        
        # 统计信息
        self.stats = {
            "layer1_count": 0,
            "layer2_count": 0,
            "layer3_count": 0,
            "total_compressions": 0
        }
    
    # ========================================
    # Token 估算
    # ========================================
    def estimate_tokens(self, text: str) -> int:
        """
        估算文本的 token 数量
        
        Args:
            text: 文本内容
        
        Returns:
            估算的 token 数量
        """
        # 简单估算：英文约 4 字符/token，中文约 2 字符/token
        # 这里使用混合估算
        char_count = len(text)
        
        # 计算中文字符比例
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        chinese_ratio = chinese_chars / char_count if char_count > 0 else 0
        
        # 混合估算
        if chinese_ratio > 0.5:
            # 中文为主
            return int(char_count / 2)
        else:
            # 英文为主
            return int(char_count / 4)
    
    def estimate_messages_tokens(self, messages: List[Dict]) -> int:
        """
        估算消息列表的 token 数量
        
        Args:
            messages: 消息列表
        
        Returns:
            总 token 数量
        """
        total = 0
        for msg in messages:
            # 角色和内容
            if "role" in msg:
                total += 10  # 角色标记
            if "content" in msg:
                total += self.estimate_tokens(str(msg["content"]))
            # 其他字段
            for key, value in msg.items():
                if key not in ["role", "content"]:
                    total += self.estimate_tokens(str(value)) + 5
        
        return total
    
    # ========================================
    # 第 1 层：旧对话压缩
    # ========================================
    def compress_old_conversations(self, messages: List[Dict], keep_recent: int = 10) -> List[Dict]:
        """
        第 1 层：压缩旧对话为记忆板历史
        
        Args:
            messages: 消息列表
            keep_recent: 保留最近的消息数量
        
        Returns:
            压缩后的消息列表
        """
        print(f"  [第 1 层] 压缩旧对话...")
        
        if len(messages) <= keep_recent:
            print(f"    → 消息数量不足，无需压缩")
            return messages
        
        # 分离旧消息和最近消息
        old_messages = messages[:-keep_recent]
        recent_messages = messages[-keep_recent:]
        
        # 生成摘要
        summary = self._generate_conversation_summary(old_messages)
        
        # 创建记忆板条目
        memory_entry = {
            "role": "system",
            "content": f"📝 历史对话摘要:\n{summary}",
            "metadata": {
                "type": "conversation_summary",
                "timestamp": datetime.now().isoformat(),
                "original_count": len(old_messages)
            }
        }
        
        # 组合结果
        compressed = [memory_entry] + recent_messages
        
        print(f"    → 压缩 {len(old_messages)} 条消息为摘要")
        print(f"    → 保留最近 {keep_recent} 条消息")
        
        self.stats["layer1_count"] += 1
        self.stats["total_compressions"] += 1
        
        return compressed
    
    def _generate_conversation_summary(self, messages: List[Dict]) -> str:
        """
        生成对话摘要
        
        Args:
            messages: 消息列表
        
        Returns:
            摘要文本
        """
        # 简单摘要：提取关键信息
        key_points = []
        
        for msg in messages:
            role = msg.get("role", "unknown")
            content = str(msg.get("content", ""))[:100]  # 限制长度
            
            if role == "user":
                key_points.append(f"• 用户: {content}")
            elif role == "assistant":
                # 只记录助手的回复标记
                key_points.append(f"• 助手: 已回复")
        
        return "\n".join(key_points)
    
    # ========================================
    # 第 2 层：常规压缩
    # ========================================
    def regular_compress(self, messages: List[Dict]) -> List[Dict]:
        """
        第 2 层：常规压缩（内容精简）
        
        Args:
            messages: 消息列表
        
        Returns:
            压缩后的消息列表
        """
        print(f"  [第 2 层] 常规压缩...")
        
        compressed = []
        for msg in messages:
            # 压缩每条消息
            compressed_msg = self._compress_message(msg)
            compressed.append(compressed_msg)
        
        print(f"    → 已压缩所有消息内容")
        
        self.stats["layer2_count"] += 1
        self.stats["total_compressions"] += 1
        
        return compressed
    
    def _compress_message(self, msg: Dict) -> Dict:
        """
        压缩单条消息
        
        Args:
            msg: 消息对象
        
        Returns:
            压缩后的消息
        """
        compressed = msg.copy()
        
        # 压缩内容
        if "content" in msg:
            content = str(msg["content"])
            # 保留重要信息，删除冗余
            compressed["content"] = self._compress_text(content)
        
        # 删除不必要的元数据
        if "metadata" in compressed:
            # 只保留关键元数据
            metadata = compressed["metadata"]
            essential_metadata = {
                k: v for k, v in metadata.items()
                if k in ["type", "timestamp", "tool_calls"]
            }
            compressed["metadata"] = essential_metadata
        
        return compressed
    
    def _compress_text(self, text: str, max_length: int = 500) -> str:
        """
        压缩文本
        
        Args:
            text: 原始文本
            max_length: 最大长度
        
        Returns:
            压缩后的文本
        """
        if len(text) <= max_length:
            return text
        
        # 截断并添加标记
        return text[:max_length] + "\n...[内容已压缩]..."
    
    # ========================================
    # 第 3 层：应急压缩
    # ========================================
    def emergency_compress(self, messages: List[Dict]) -> List[Dict]:
        """
        第 3 层：应急压缩（极限压缩）
        
        Args:
            messages: 消息列表
        
        Returns:
            压缩后的消息列表
        """
        print(f"  [第 3 层] 应急压缩...")
        
        # 只保留最近的消息和关键信息
        compressed = []
        
        # 保留系统消息
        system_messages = [m for m in messages if m.get("role") == "system"]
        
        # 保留最近的用户消息和助手消息（最多各 3 条）
        user_messages = [m for m in messages if m.get("role") == "user"][-3:]
        assistant_messages = [m for m in messages if m.get("role") == "assistant"][-3:]
        
        # 极限压缩内容
        for msg in system_messages + user_messages + assistant_messages:
            compressed_msg = self._emergency_compress_message(msg)
            compressed.append(compressed_msg)
        
        print(f"    → 极限压缩完成")
        print(f"    → 原始 {len(messages)} 条 → 压缩后 {len(compressed)} 条")
        
        self.stats["layer3_count"] += 1
        self.stats["total_compressions"] += 1
        
        return compressed
    
    def _emergency_compress_message(self, msg: Dict) -> Dict:
        """
        极限压缩单条消息
        
        Args:
            msg: 消息对象
        
        Returns:
            压缩后的消息
        """
        compressed = {
            "role": msg.get("role", "unknown")
        }
        
        # 只保留核心内容（最多 200 字符）
        if "content" in msg:
            content = str(msg["content"])[:200]
            compressed["content"] = content + ("..." if len(str(msg["content"])) > 200 else "")
        
        return compressed
    
    # ========================================
    # 分层压缩逻辑
    # ========================================
    def layered_compress(self, messages: List[Dict]) -> List[Dict]:
        """
        分层压缩主逻辑
        
        Args:
            messages: 消息列表
        
        Returns:
            压缩后的消息列表
        """
        # 估算当前 token 数量
        current_tokens = self.estimate_messages_tokens(messages)
        
        print(f"\n📊 当前上下文: {current_tokens:,} tokens")
        print(f"📊 最大限制: {self.max_tokens:,} tokens")
        print(f"📊 有效限制: {self.effective_max:,} tokens (含安全空间)")
        
        # 检查是否需要压缩
        if current_tokens <= self.layer1_threshold:
            print("✅ 上下文在安全范围内，无需压缩")
            return messages
        
        # 第 1 层：旧对话压缩
        if current_tokens > self.layer1_threshold:
            print(f"\n⚠️ 超过第 1 层阈值 ({self.layer1_threshold:,} tokens)")
            messages = self.compress_old_conversations(messages)
            current_tokens = self.estimate_messages_tokens(messages)
            
            if current_tokens <= self.effective_max:
                print(f"✅ 第 1 层压缩后: {current_tokens:,} tokens")
                return messages
        
        # 第 2 层：常规压缩
        if current_tokens > self.layer2_threshold:
            print(f"\n⚠️ 超过第 2 层阈值 ({self.layer2_threshold:,} tokens)")
            messages = self.regular_compress(messages)
            current_tokens = self.estimate_messages_tokens(messages)
            
            if current_tokens <= self.effective_max:
                print(f"✅ 第 2 层压缩后: {current_tokens:,} tokens")
                return messages
        
        # 第 3 层：应急压缩
        if current_tokens > self.layer3_threshold:
            print(f"\n🚨 超过第 3 层阈值 ({self.layer3_threshold:,} tokens)")
            messages = self.emergency_compress(messages)
            current_tokens = self.estimate_messages_tokens(messages)
            print(f"✅ 第 3 层压缩后: {current_tokens:,} tokens")
            return messages
        
        print(f"✅ 压缩完成: {current_tokens:,} tokens")
        return messages
    
    # ========================================
    # 统计信息
    # ========================================
    def get_stats(self) -> Dict[str, Any]:
        """获取压缩统计信息"""
        return {
            "layer1_compressions": self.stats["layer1_count"],
            "layer2_compressions": self.stats["layer2_count"],
            "layer3_compressions": self.stats["layer3_count"],
            "total_compressions": self.stats["total_compressions"],
            "compression_ratio": self._calculate_compression_ratio()
        }
    
    def _calculate_compression_ratio(self) -> float:
        """计算压缩比"""
        if self.stats["total_compressions"] == 0:
            return 0.0
        
        # 简单计算：平均压缩层级
        weighted_sum = (
            self.stats["layer1_count"] * 1 +
            self.stats["layer2_count"] * 2 +
            self.stats["layer3_count"] * 3
        )
        
        return weighted_sum / self.stats["total_compressions"]


# ========================================
# 测试代码
# ========================================
def main():
    """测试分层压缩"""
    # 创建测试消息
    test_messages = []
    
    # 添加 50 条测试消息
    for i in range(50):
        test_messages.append({
            "role": "user" if i % 2 == 0 else "assistant",
            "content": f"这是第 {i+1} 条测试消息。" * 20,  # 较长内容
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "index": i
            }
        })
    
    # 创建压缩器
    compressor = LayeredCompression(max_tokens=10000)
    
    # 执行分层压缩
    print("="*60)
    print("分层压缩测试")
    print("="*60)
    
    original_tokens = compressor.estimate_messages_tokens(test_messages)
    print(f"\n原始消息: {len(test_messages)} 条")
    print(f"原始 tokens: {original_tokens:,}")
    
    compressed_messages = compressor.layered_compress(test_messages)
    
    compressed_tokens = compressor.estimate_messages_tokens(compressed_messages)
    print(f"\n压缩后消息: {len(compressed_messages)} 条")
    print(f"压缩后 tokens: {compressed_tokens:,}")
    print(f"压缩比: {(1 - compressed_tokens/original_tokens)*100:.1f}%")
    
    # 统计信息
    print(f"\n📊 压缩统计:")
    stats = compressor.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == '__main__':
    main()
