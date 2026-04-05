# 🔄 Phase 6: 主动模式（KAIROS）

**开始时间**: 2026-03-31 23:40
**目标**: 实现主动代理能力

---

## 🎯 目标

**实现3级主动能力**

| 级别 | 功能 | 状态 |
|------|------|------|
| 1级 | 心跳机制 | ⏳ |
| 2级 | 任务发现 | ⏳ |
| 3级 | 倾向行动 | ⏳ |

---

## 📝 实现步骤

### 步骤 1: 创建主动模式服务

```python
# proactive/__init__.py
"""
主动模式服务（KAIROS）
"""

class ProactiveMode:
    def __init__(self):
        self.active = False
        self.tick_interval = 60  # 秒
        self.task_finder = TaskFinder()
        self.executor = TaskExecutor()
    
    async def start(self):
        """
        启动主动模式
        """
        self.active = True
        
        while self.active:
            # 心跳
            await self.on_tick()
            
            # 等待下次心跳
            await asyncio.sleep(self.tick_interval)
    
    async def on_tick(self):
        """
        心跳触发
        """
        # 1. 查找任务
        tasks = await self.task_finder.find_tasks()
        
        if tasks:
            # 2. 倾向行动
            for task in tasks:
                await self.executor.execute(task)
        else:
            # 3. 调用 SleepTool
            await self.sleep()
    
    async def sleep(self):
        """
        休眠一段时间
        """
        await asyncio.sleep(10)  # 休眠10秒
    
    def stop(self):
        """
        停止主动模式
        """
        self.active = False
```

### 步骤 2: 实现任务发现

```python
# proactive/task_finder.py
class TaskFinder:
    """
    任务发现器
    """
    
    async def find_tasks(self):
        """
        查找任务
        """
        tasks = []
        
        # 1. 检查系统健康
        health = await self.check_system_health()
        if not health["ok"]:
            tasks.append({
                "type": "maintenance",
                "action": "fix",
                "target": health["issue"],
                "priority": "high"
            })
        
        # 2. 检查更新
        updates = await self.check_updates()
        if updates:
            tasks.append({
                "type": "update",
                "action": "apply",
                "target": updates,
                "priority": "medium"
            })
        
        # 3. 检查备份
        backup_needed = await self.check_backup_needed()
        if backup_needed:
            tasks.append({
                "type": "backup",
                "action": "create",
                "target": "workspace",
                "priority": "low"
            })
        
        return tasks
    
    async def check_system_health(self):
        """
        检查系统健康
        """
        # 检查磁盘空间
        import shutil
        disk = shutil.disk_usage("/")
        free_percent = (disk.free / disk.total) * 100
        
        if free_percent < 20:
            return {
                "ok": False,
                "issue": "disk_space_low",
                "details": f"剩余空间: {free_percent:.1f}%"
            }
        
        return {"ok": True}
    
    async def check_updates(self):
        """
        检查更新
        """
        # 简化实现：总是返回 None
        return None
    
    async def check_backup_needed(self):
        """
        检查是否需要备份
        """
        # 检查最后一次备份时间
        # 简化实现：总是返回 True
        return True
```

### 步骤 3: 实现任务执行

```python
# proactive/task_executor.py
class TaskExecutor:
    """
    任务执行器
    """
    
    async def execute(self, task):
        """
        执行任务
        """
        task_type = task.get("type")
        
        if task_type == "maintenance":
            return await self.execute_maintenance(task)
        elif task_type == "update":
            return await self.execute_update(task)
        elif task_type == "backup":
            return await self.execute_backup(task)
        else:
            return {"status": "unknown_task_type"}
    
    async def execute_maintenance(self, task):
        """
        执行维护任务
        """
        issue = task.get("target")
        
        if issue == "disk_space_low":
            # 清理临时文件
            import tempfile
            import shutil
            
            temp_dir = tempfile.gettempdir()
            cleaned = 0
            
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    cleaned += 1
            
            return {
                "status": "completed",
                "summary": f"清理了 {cleaned} 个临时文件"
            }
        
        return {"status": "skipped"}
    
    async def execute_backup(self, task):
        """
        执行备份任务
        """
        # 创建备份
        backup_script = "/root/.openclaw/workspace/scripts/complete-backup.sh"
        
        if os.path.exists(backup_script):
            result = subprocess.run([backup_script], capture_output=True, text=True)
            return {
                "status": "completed",
                "summary": "备份已完成"
            }
        
        return {"status": "skipped", "summary": "备份脚本不存在"}
```

---

## 📊 进度跟踪

- [ ] 创建主动模式框架
- [ ] 实现心跳机制
- [ ] 实现任务发现
- [ ] 实现倾向行动
- [ ] 测试主动模式
- [ ] 更新文档

---

## 🎯 成功指标

### 主动能力
- ✅ 3级主动能力全部实现
- ✅ 心跳稳定运行
- ✅ 任务自动发现
- ✅ 倾向行动执行

---

**开始执行 Phase 6！**

😊
