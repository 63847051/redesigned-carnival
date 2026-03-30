#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三层上下文压缩 - 自动清理旧上下文，保持关键信息
基于 learn-claude-code 的 s06 课程
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class ThreeLayerCompressor:
    """三层上下文压缩器 - 无限会话支持"""
    
    def __init__(self, workspace: str = "/root/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.memory_dir = self.workspace / "memory"
        
        # 压缩配置
        self.l1_max = 10  # L1: 保留最近 10 条
        self.l2_max = 5   # L2: 提取长期记忆
        self.l3_keep = 5  # L3: 保留核心 5 条
    
    def compress(self, messages: List[Dict], token_budget: int = 4000) -> List[Dict]:
        """
        压缩上下文
        
        Args:
            messages: 消息列表
            token_budget: Token 预算
        
        Returns:
            压缩后的消息列表
        """
        print(f"\n🗜️ 压缩上下文（预算: {token_budget} tokens）")
        print("="*60)
        
        # 当前 token 数
        current_tokens = sum(len(m.get("content", "").split()) for m in messages)
        print(f"当前: {current_tokens} tokens")
        
        if current_tokens <= token_budget:
            print("✅ 无需压缩")
            return messages
        
        # L1: 保留最近 N 条
        l1_messages = messages[-self.l1_max:]
        
        # L2: 提取长期记忆（标记为重要的）
        l2_messages = self._extract_important(messages)
        
        # L3: 保留核心 N 条
        l3_messages = messages[:self.l3_keep]
        
        # 合并
        compressed = l3_messages + l2_messages + l1_messages
        
        # 去重
        seen = set()
        unique_compressed = []
        for msg in compressed:
            msg_str = json.dumps(msg, sort_keys=True)
            if msg_str not in seen:
                seen.add(msg_str)
                unique_compressed.append(msg)
        
        new_tokens = sum(len(m.get("content", "").split()) for m in unique_compressed)
        
        print(f"压缩后: {new_tokens} tokens")
        print(f"节省: {current_tokens - new_tokens} tokens ({((current_tokens - new_tokens)/current_tokens*100):.1f}%)")
        print("="*60)
        
        return unique_compressed
    
    def _extract_important(self, messages: List[Dict]) -> List[Dict]:
        """
        提取重要消息（长期记忆）
        
        Args:
            messages: 消息列表
        
        Returns:
            重要消息列表
        """
        important = []
        
        for msg in messages:
            content = msg.get("content", "")
            
            # 标记为重要的
            is_important = (
                "总结" in content or
                "决定" in content or
                "规则" in content or
                "最佳实践" in content or
                "架构" in content or
                "设计" in content or
                "系统" in content or
                "核心" in content
            )
            
            if is_important:
                important.append(msg)
        
        return important[-self.l2_max:]  # 保留最近 N 条
    
    def save_checkpoint(self, messages: List[Dict]):
        """
        保存检查点（持久化）
        
        Args:
            messages: 消息列表
        """
        checkpoint_file = self.workspace / ".data" / "context-checkpoint.jsonl"
        checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "message_count": len(messages),
            "messages": messages[-50:]  # 保存最近 50 条
        }
        
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)


# ============================================================================
# 主流程
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="三层上下文压缩")
    parser.add_argument("--test", action="store_true", help="测试压缩")
    parser.add_argument("--compress", type=int, default=4000, metavar="budget", help="压缩上下文")
    
    args = parser.parse_args()
    
    compressor = ThreeLayerCompressor()
    
    if args.test:
        # 测试数据
        test_messages = [
            {"role": "user", "content": f"消息 {i}"}
            for i in range(20)
        ]
        
        # 添加一些重要消息
        test_messages[0]["content"] = "这是系统架构决定：使用 Python 作为主要语言"
        test_messages[5]["content"] = "总结：今天学习了 14 个项目"
        test_messages[10]["content"] = "最佳实践：先列步骤再执行"
        
        print("="*60)
        print("🧪 三层上下文压缩测试")
        print("="*60)
        
        compressed = compressor.compress(test_messages, args.compress)
        
        print(f"\n原始: {len(test_messages)} 条消息")
        print(f"压缩后: {len(compressed)} 条消息")
    
    elif args.compress:
        print("需要传入消息文件")
    
    else:
        print("用法:")
        print("  python3 context-compressor.py --test  # 测试压缩")
        print("  python3 context-compressor.py --compress 4000  # 压缩上下文")
        print("\n核心价值:")
        print("  会话持久化")
        print("  无限会话支持")
        print("  自动清理旧上下文")
