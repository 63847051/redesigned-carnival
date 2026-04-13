# Hermes Agent API 参考文档

**版本**: v1.1
**更新时间**: 2026-04-12

---

## 📚 目录

1. [核心模块](#核心模块)
2. [集成层](#集成层)
3. [优化系统](#优化系统)
4. [监控系统](#监控系统)
5. [使用示例](#使用示例)

---

## 🔧 核心模块

### 1. 知识持久化系统

#### OptimizedKnowledgePersistenceSystem

优化的知识持久化系统，支持缓存、批量操作和全文搜索。

**初始化**:
```python
from system.hermes_core.optimized_knowledge import OptimizedKnowledgePersistenceSystem

system = OptimizedKnowledgePersistenceSystem(
    db_path="/path/to/knowledge.db",  # 数据库路径
    cache_size=100,                     # 缓存容量
    cache_ttl=3600                      # 缓存生存时间（秒）
)
```

**方法**:

##### `learn(key, value, category="general", source="system")`
学习新知识。

**参数**:
- `key` (str): 知识键
- `value` (Any): 知识值
- `category` (str): 分类
- `source` (str): 来源

**返回**: `bool` - 是否成功

**示例**:
```python
system.learn("user_preference", {"theme": "dark"}, "user")
```

##### `learn_batch(items)`
批量学习知识。

**参数**:
- `items` (List[Dict]): 知识条目列表

**返回**: `int` - 成功存储的数量

**示例**:
```python
items = [
    {"key": "k1", "value": {...}, "category": "test"},
    {"key": "k2", "value": {...}, "category": "test"},
]
count = system.learn_batch(items)
```

##### `recall(key)`
回忆知识。

**参数**:
- `key` (str): 知识键

**返回**: `Any` - 知识值，如果不存在返回 `None`

**示例**:
```python
value = system.recall("user_preference")
```

##### `recall_batch(keys)`
批量回忆知识。

**参数**:
- `keys` (List[str]): 知识键列表

**返回**: `Dict[str, Any]` - 键值对字典

**示例**:
```python
results = system.recall_batch(["k1", "k2", "k3"])
```

##### `search_knowledge(query, category=None)`
搜索知识。

**参数**:
- `query` (str): 搜索查询
- `category` (str, optional): 分类过滤

**返回**: `List[Dict]` - 匹配的知识条目列表

**示例**:
```python
# 全文搜索
results = system.search_knowledge("user preference")

# 分类搜索
results = system.search_knowledge("config", category="system")
```

##### `get_stats()`
获取统计信息。

**返回**: `Dict` - 统计信息

**示例**:
```python
stats = system.get_stats()
print(f"总条目数: {stats['total_items']}")
print(f"缓存大小: {stats['cache']['size']}")
```

---

### 2. 压缩快照系统

#### CompressedSnapshotAtomicSystem

支持压缩和增量快照的状态管理系统。

**初始化**:
```python
from system.hermes_core.compressed_snapshot import CompressedSnapshotAtomicSystem

system = CompressedSnapshotAtomicSystem(
    snapshot_dir="/path/to/snapshots",  # 快照目录
    compression_level=6                 # 压缩级别（0-9）
)
```

**方法**:

##### `save_state(file_path, content, create_snapshot=True, description="", incremental=True)`
保存状态。

**参数**:
- `file_path` (str): 文件路径
- `content` (str): 文件内容
- `create_snapshot` (bool): 是否创建快照
- `description` (str): 快照描述
- `incremental` (bool): 是否增量快照

**返回**: `bool` - 是否成功

**示例**:
```python
# 保存配置（自动创建压缩快照）
system.save_state(
    "config.json",
    json_content,
    create_snapshot=True,
    description="Before upgrade",
    incremental=True
)
```

##### `restore_state(file_path, snapshot_id)`
恢复状态。

**参数**:
- `file_path` (str): 文件路径
- `snapshot_id` (str): 快照 ID

**返回**: `bool` - 是否成功

**示例**:
```python
snapshots = system.list_states()
success = system.restore_state("config.json", snapshots[0]["snapshot_id"])
```

##### `get_compression_stats()`
获取压缩统计。

**返回**: `Dict` - 压缩统计信息

**示例**:
```python
stats = system.get_compression_stats()
print(f"压缩比: {stats['average_compression_ratio']:.2%}")
print(f"节省空间: {stats['space_saved_percentage']:.1f}%")
```

##### `optimize_storage(keep_count=10)`
优化存储（删除旧快照）。

**参数**:
- `keep_count` (int): 保留快照数量

**返回**: `int` - 删除的快照数量

**示例**:
```python
deleted = system.optimize_storage(keep_count=10)
print(f"删除了 {deleted} 个旧快照")
```

---

### 3. 用户建模系统

#### HonchoLite

4 层用户建模系统。

**初始化**:
```python
from system.hermes_core.modeling.honcho_lite import HonchoLite

model = HonchoLite(db_path="/path/to/honcho.db")
```

**方法**:

##### `profile(user_id, name=None)`
获取用户画像。

**参数**:
- `user_id` (str): 用户 ID
- `name` (str, optional): 用户名称

**返回**: `UserProfile` - 用户画像对象

**示例**:
```python
profile = model.profile("user_123", "张三")
print(f"用户: {profile.name}")
print(f"偏好: {profile.preferences}")
```

##### `record_interaction(user_id, content, metadata=None)`
记录用户交互。

**参数**:
- `user_id` (str): 用户 ID
- `content` (str): 交互内容
- `metadata` (Dict, optional): 元数据

**返回**: `None`

**示例**:
```python
model.record_interaction(
    "user_123",
    "用户完成了任务",
    metadata={"task_id": "task_456", "duration": 120}
)
```

##### `search(user_id, query, limit=10)`
搜索用户历史。

**参数**:
- `user_id` (str): 用户 ID
- `query` (str): 搜索查询
- `limit` (int): 结果数量限制

**返回**: `List[Dict]` - 匹配的交互列表

**示例**:
```python
results = model.search("user_123", "任务", limit=5)
```

---

## 🔄 集成层

### HermesIntegration

Hermes 核心功能集成到 OpenClaw 的主接口。

**初始化**:
```python
from system.hermes_integration.integration_layer import get_hermes

hermes = get_hermes()

if hermes.enabled:
    print("Hermes 已启用")
```

**触发器**:

##### `on_task_completion(task_result)`
任务完成触发器。

**参数**:
- `task_result` (Dict): 任务结果

**示例**:
```python
hermes.on_task_completion({
    "task_id": "task_123",
    "status": "completed",
    "result": {...}
})
```

##### `on_session_start(session_id)`
会话开始触发器。

**参数**:
- `session_id` (str): 会话 ID

**示例**:
```python
hermes.on_session_start("session_456")
```

##### `on_session_end(session_id, session_data)`
会话结束触发器。

**参数**:
- `session_id` (str): 会话 ID
- `session_data` (Dict): 会话数据

**示例**:
```python
hermes.on_session_end("session_456", {"duration": 120, "messages": 50})
```

##### `on_error(error, context)`
错误触发器。

**参数**:
- `error` (Exception): 错误对象
- `context` (Dict): 上下文信息

**示例**:
```python
try:
    # 一些操作
    pass
except Exception as e:
    hermes.on_error(e, {"operation": "save_config"})
```

**工具方法**:

##### `search_knowledge(query, category=None)`
搜索知识。

##### `get_user_profile()`
获取用户画像。

##### `create_snapshot(file_path, description)`
创建快照。

##### `apply_fuzzy_patch(file_path, old_code, new_code)`
应用模糊补丁。

---

## 📊 监控系统

### HermesMonitor

性能指标收集和错误追踪。

**初始化**:
```python
from system.hermes_core.monitoring import HermesMonitor

monitor = HermesMonitor()
```

**方法**:

##### `record_metric(name, value, unit="", tags=None)`
记录指标。

**示例**:
```python
monitor.record_metric("knowledge_ops", 1, "", {"operation": "store"})
monitor.record_metric("response_time", 0.123, "seconds")
```

##### `track_error(error, context=None)`
追踪错误。

**示例**:
```python
try:
    # 一些操作
    pass
except Exception as e:
    monitor.track_error(e, {"operation": "save_data"})
```

##### `get_health_status()`
获取健康状态。

**返回**: `Dict` - 健康状态信息

**示例**:
```python
health = monitor.get_health_status()
if health["overall_healthy"]:
    print("系统健康")
else:
    print("系统异常")
    for check_name, result in health["checks"].items():
        if not result["healthy"]:
            print(f"  {check_name}: {result}")
```

##### `get_dashboard_data()`
获取监控仪表板数据。

**返回**: `Dict` - 完整的监控数据

**示例**:
```python
dashboard = monitor.get_dashboard_data()
print(f"健康状态: {dashboard['health']}")
print(f"错误统计: {dashboard['errors']}")
print(f"最近错误: {len(dashboard['recent_errors'])} 个")
```

##### `save_report(path=None)`
保存监控报告。

**示例**:
```python
report_path = monitor.save_report()
print(f"报告已保存: {report_path}")
```

---

## 💡 使用示例

### 完整工作流

```python
from system.hermes_integration.integration_layer import get_hermes
from system.hermes_core.monitoring import HermesMonitor

# 初始化
hermes = get_hermes()
monitor = HermesMonitor()

# 会话开始
hermes.on_session_start("session_123")

# 记录指标
monitor.record_metric("session_start", 1)

try:
    # 执行任务
    result = do_some_work()
    
    # 任务完成
    hermes.on_task_completion({
        "task_id": "task_456",
        "status": "completed",
        "result": result
    })
    
    monitor.record_metric("task_completed", 1)
    
except Exception as e:
    # 错误处理
    hermes.on_error(e, {"task_id": "task_456"})
    monitor.track_error(e)
    
# 会话结束
hermes.on_session_end("session_123", {"duration": 120})

# 保存监控报告
monitor.save_report()
```

### 知识管理工作流

```python
from system.hermes_core.optimized_knowledge import OptimizedKnowledgePersistenceSystem

# 初始化
knowledge = OptimizedKnowledgePersistenceSystem()

# 批量学习
items = [
    {"key": "config_theme", "value": "dark", "category": "config"},
    {"key": "config_lang", "value": "zh-CN", "category": "config"},
]
knowledge.learn_batch(items)

# 搜索
results = knowledge.search_knowledge("config", category="config")
for item in results:
    print(f"{item['key']}: {item['value']}")

# 查看统计
stats = knowledge.get_stats()
print(f"总条目: {stats['total_items']}")
```

### 快照管理工作流

```python
from system.hermes_core.compressed_snapshot import CompressedSnapshotAtomicSystem

# 初始化
snapshot = CompressedSnapshotAtomicSystem()

# 保存状态（自动压缩）
with open("config.json", "r") as f:
    content = f.read()

snapshot.save_state("config.json", content, create_snapshot=True, description="Before upgrade")

# 查看压缩统计
stats = snapshot.get_compression_stats()
print(f"压缩比: {stats['average_compression_ratio']:.2%}")
print(f"节省空间: {stats['space_saved_percentage']:.1f}%")

# 如果需要回滚
snapshots = snapshot.list_states()
if snapshots:
    snapshot.restore_state("config.json", snapshots[0]["snapshot_id"])

# 定期优化
deleted = snapshot.optimize_storage(keep_count=10)
print(f"删除了 {deleted} 个旧快照")
```

---

## 🔍 故障排除

### 常见问题

#### 1. 数据库锁定

**问题**: `sqlite3.OperationalError: database is locked`

**解决**:
```python
# 增加超时时间
import sqlite3
conn = sqlite3.connect("db.sqlite", timeout=30.0)
```

#### 2. 缓存未命中

**问题**: 缓存命中率低

**解决**:
```python
# 增加缓存容量
system = OptimizedKnowledgePersistenceSystem(cache_size=200)

# 增加 TTL
system = OptimizedKnowledgePersistenceSystem(cache_ttl=7200)
```

#### 3. 快照文件过大

**问题**: 快照文件占用空间过大

**解决**:
```python
# 提高压缩级别
system = CompressedSnapshotAtomicSystem(compression_level=9)

# 启用增量快照
system.save_state(file, content, incremental=True)

# 定期清理
system.optimize_storage(keep_count=5)
```

---

## 📞 支持

如有问题，请查看：
- 测试报告: `/root/.openclaw/workspace/system/hermes-core/stability_tests.py`
- 监控日志: `/root/.openclaw/workspace/data/monitoring/hermes_monitor.log`
- 监控报告: `/root/.openclaw/workspace/data/monitoring/monitor_report_*.json`

---

**文档版本**: v1.1
**最后更新**: 2026-04-12
**状态**: ✅ 生产就绪
