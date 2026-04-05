# 📦 Phase 3: 上下文压缩系统

**开始时间**: 2026-03-31 23:25
**目标**: 实现智能上下文管理

---

## 🎯 目标

**实现3级压缩策略**

| 级别 | 名称 | 触发条件 | 状态 |
|------|------|----------|------|
| 1级 | 分组压缩 | 消息 > 100条 | ⏳ |
| 2级 | 微型压缩 | 工具结果 > 1000字符 | ⏳ |
| 3级 | 自动压缩 | Token > 100k | ⏳ |

---

## 📝 实现步骤

### 步骤 1: 创建压缩服务

```python
# services/compact/__init__.py
"""
上下文压缩服务
"""

class CompactService:
    def __init__(self):
        self.grouping_compactor = GroupingCompactor()
        self.micro_compactor = MicroCompactor()
        self.auto_compactor = AutoCompactor()
    
    def should_compact(self, messages):
        """
        检查是否需要压缩
        """
        # 检查消息数量
        if len(messages) > 100:
            return True
        
        # 检查 Token 数量
        total_tokens = sum(len(m.get("content", "")) for m in messages)
        if total_tokens > 100000:
            return True
        
        return False
    
    def compact(self, messages, level="auto"):
        """
        压缩消息
        """
        if level == "grouping":
            return self.grouping_compactor.compact(messages)
        elif level == "micro":
            return self.micro_compactor.compact(messages)
        else:
            return self.auto_compactor.compact(messages)
```

### 步骤 2: 实现分组压缩

```python
# services/compact/grouping_compactor.py
class GroupingCompactor:
    """
    分组压缩 - 按用户消息分组
    """
    
    def compact(self, messages):
        # 1. 分组
        groups = self.group_messages(messages)
        
        # 2. 保留最近
        recent = groups[-10:]
        
        # 3. 压缩旧的
        old_groups = groups[:-10]
        compressed = []
        
        for group in old_groups:
            compressed.append(self.compact_group(group))
        
        return compressed + recent
    
    def group_messages(self, messages):
        """
        分组消息
        """
        groups = []
        current_group = []
        
        for message in messages:
            if message.get("role") == "user":
                if current_group:
                    groups.append(current_group)
                current_group = [message]
            else:
                current_group.append(message)
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def compact_group(self, group):
        """
        压缩一个消息组
        """
        if len(group) == 1:
            return group[0]
        
        # 提取关键信息
        user_msg = group[0]
        tool_msgs = [m for m in group if m.get("role") == "tool"]
        assistant_msgs = [m for m in group if m.get("role") == "assistant"]
        
        # 生成摘要
        summary = f"用户: {user_msg.get('content', '')[:50]}...\n"
        summary += f"执行了 {len(tool_msgs)} 个工具\n"
        if assistant_msgs:
            summary += f"结果: {assistant_msgs[-1].get('content', '')[:100]}..."
        
        return {
            "role": "system",
            "content": summary
        }
```

### 步骤 3: 实现微型压缩

```python
# services/compact/micro_compactor.py
class MicroCompactor:
    """
    微型压缩 - 压缩工具结果
    """
    
    def compact(self, messages):
        """
        压缩消息中的工具结果
        """
        compressed = []
        
        for message in messages:
            if message.get("role") == "tool":
                # 压缩工具结果
                compressed.append(self.compact_tool_result(message))
            else:
                compressed.append(message)
        
        return compressed
    
    def compact_tool_result(self, tool_result):
        """
        压缩工具结果
        """
        content = tool_result.get("content", "")
        
        if len(content) > 1000:
            # 生成摘要
            return {
                "role": "tool",
                "content": content[:500] + "...",
                "summary": self.extract_key_points(content)
            }
        
        return tool_result
    
    def extract_key_points(self, text):
        """
        提取关键点（简化版）
        """
        # 简化实现：返回前500字符
        return text[:500] + "..."
```

### 步骤 4: 实现自动压缩

```python
# services/compact/auto_compactor.py
class AutoCompactor:
    """
    自动压缩 - 根据情况选择压缩策略
    """
    
    def __init__(self):
        self.grouping_compactor = GroupingCompactor()
        self.micro_compactor = MicroCompactor()
    
    def compact(self, messages):
        """
        自动压缩
        """
        # 1. 先微型压缩
        messages = self.micro_compactor.compact(messages)
        
        # 2. 再分组压缩
        messages = self.grouping_compactor.compact(messages)
        
        return messages
```

---

## 📊 进度跟踪

- [ ] 创建压缩服务框架
- [ ] 实现分组压缩
- [ ] 实现微型压缩
- [ ] 实现自动压缩
- [ ] 测试压缩效果
- [ ] 更新文档

---

## 🎯 成功指标

### 上下文管理
- ✅ 3级压缩全部实现
- ✅ Token 使用率 < 80%
- ✅ 关键信息不丢失
- ✅ 自动触发压缩

---

**开始执行 Phase 3！**

😊
