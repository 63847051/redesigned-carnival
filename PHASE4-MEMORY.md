# 🧠 Phase 4: 记忆整固系统

**开始时间**: 2026-03-31 23:30
**目标**: 实现 DREAM_TASK - 后台记忆整固

---

## 🎯 目标

**实现3级记忆管理**

| 级别 | 名称 | 功能 | 状态 |
|------|------|------|------|
| 1级 | 短期记忆 | 最近50条消息 | ⏳ |
| 2级 | 记忆快照 | 保存/恢复状态 | ⏳ |
| 3级 | 长期记忆 | MEMORY.md 整固 | ⏳ |

---

## 📝 实现步骤

### 步骤 1: 创建记忆服务

```python
# services/memory/__init__.py
"""
记忆管理服务
"""

class MemoryService:
    def __init__(self):
        self.short_term = []
        self.snapshots = []
        self.long_term_file = "/root/.openclaw/workspace/MEMORY.md"
    
    def add_message(self, message):
        """
        添加到短期记忆
        """
        self.short_term.append({
            "role": message.get("role"),
            "content": message.get("content"),
            "timestamp": now()
        })
        
        # 超过100条时触发整固
        if len(self.short_term) > 100:
            self.consolidate()
    
    def create_snapshot(self):
        """
        创建记忆快照
        """
        snapshot = {
            "messages": self.short_term.copy(),
            "timestamp": now()
        }
        self.snapshots.append(snapshot)
        return snapshot
    
    def restore_snapshot(self, snapshot):
        """
        从快照恢复
        """
        self.short_term = snapshot["messages"].copy()
    
    def consolidate(self):
        """
        整固记忆到长期记忆
        """
        # 1. 提取关键信息
        key_points = []
        
        for msg in self.short_term[:-50]:
            if msg.get("role") == "user":
                key_points.append({
                    "time": msg["timestamp"],
                    "content": msg["content"][:100]
                })
        
        # 2. 追加到长期记忆
        with open(self.long_term_file, "a") as f:
            f.write(f"\n## {now()}\n")
            for point in key_points:
                f.write(f"- {point['content']}\n")
        
        # 3. 清理短期记忆
        self.short_term = self.short_term[-50:]
```

### 步骤 2: 实现 DREAM_TASK

```python
# services/memory/dream_task.py
import asyncio

class DreamTask:
    """
    后台记忆整固任务
    """
    
    def __init__(self, memory_service):
        self.memory_service = memory_service
        self.running = False
    
    async def start(self):
        """
        启动后台整固
        """
        self.running = True
        
        while self.running:
            # 每小时整固一次
            await asyncio.sleep(3600)
            
            # 检查是否空闲
            if await self.is_idle():
                await self.consolidate()
    
    async def is_idle(self):
        """
        检查系统是否空闲
        """
        # 简化实现：总是返回 True
        return True
    
    async def consolidate(self):
        """
        执行记忆整固
        """
        # 调用记忆服务的整固方法
        self.memory_service.consolidate()
```

### 步骤 3: 实现记忆快照

```python
# services/memory/snapshot.py
class MemorySnapshot:
    """
    记忆快照管理
    """
    
    def __init__(self):
        self.snapshots = []
    
    def create(self, messages):
        """
        创建快照
        """
        snapshot = {
            "messages": messages.copy(),
            "timestamp": now(),
            "hash": self.hash_messages(messages)
        }
        self.snapshots.append(snapshot)
        return snapshot
    
    def restore(self, snapshot):
        """
        从快照恢复
        """
        return snapshot["messages"].copy()
    
    def hash_messages(self, messages):
        """
        生成消息哈希
        """
        import hashlib
        content = str(messages)
        return hashlib.md5(content.encode()).hexdigest()
```

---

## 📊 进度跟踪

- [ ] 创建记忆服务框架
- [ ] 实现短期记忆
- [ ] 实现记忆快照
- [ ] 实现长期记忆整固
- [ ] 实现DREAM_TASK
- [ ] 测试记忆管理
- [ ] 更新文档

---

## 🎯 成功指标

### 记忆管理
- ✅ 3级记忆全部实现
- ✅ 短期记忆 < 100条
- ✅ 关键信息不丢失
- ✅ 自动整固

---

**开始执行 Phase 4！**

😊
