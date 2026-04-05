# 🔬 Claude Code 核心机制深度学习

**学习时间**: 2026-03-31 22:40
**重点**: 上下文压缩、长期记忆、MCP协议、Multi-Agent协同

---

## 📚 1. 上下文压缩如何实现？⭐⭐⭐⭐⭐

### 文件结构（14个文件）

```
src/services/compact/
├── autoCompact.ts           # 自动压缩 ⭐
├── compact.ts              # 压缩核心逻辑
├── microCompact.ts         # 微型压缩
├── apiMicrocompact.ts      # API 微型压缩
├── sessionMemoryCompact.ts # 会话记忆压缩
├── grouping.ts            # 分组策略
├── prompt.ts              # 压缩 Prompt
├── postCompactCleanup.ts  # 压缩后清理
├── compactWarningHook.ts  # 压缩警告钩子
├── compactWarningState.ts # 压缩警告状态
└── timeBasedMCConfig.ts   # 基于时间的微型压缩配置
```

### 核心压缩策略 ⭐⭐⭐⭐⭐

**1. 分组压缩（grouping.ts）**

```python
# grouping.ts
def group_messages(messages):
    """
    将消息分组，便于压缩
    """
    groups = []
    current_group = []
    
    for message in messages:
        # 按类型分组
        if message["type"] == "user":
            if current_group:
                groups.append(current_group)
            current_group = [message]
        elif message["type"] == "assistant":
            current_group.append(message)
        elif message["type"] == "tool":
            current_group.append(message)
    
    if current_group:
        groups.append(current_group)
    
    return groups

def compress_group(group):
    """
    压缩一个消息组
    """
    if len(group) == 1:
        return group[0]
    
    # 多个消息合并
    user_msg = group[0]
    assistant_msgs = [m for m in group if m["role"] == "assistant"]
    tool_msgs = [m for m in group if m["role"] == "tool"]
    
    # 生成摘要
    summary = {
        "role": "assistant",
        "content": f"用户: {user_msg['content']}\n"
                   f"执行了 {len(tool_msgs)} 个工具\n"
                   f"最终结果: {assistant_msgs[-1]['content'][:100]}..."
    }
    
    return summary
```

**2. 自动压缩（autoCompact.ts）**

```python
# autoCompact.ts
class AutoCompact:
    def __init__(self):
        self.threshold = 0.8  # 上下文使用率超过 80% 触发压缩
    
    async def should_compact(self, context):
        """
        检查是否需要压缩
        """
        usage = context.token_usage / context.max_tokens
        
        if usage > self.threshold:
            return True
        
        return False
    
    async def compact(self, messages):
        """
        执行压缩
        """
        # 1. 分组
        groups = self.group_messages(messages)
        
        # 2. 保留最近的消息
        recent = groups[-10:]  # 保留最近 10 组
        
        # 3. 压缩旧的消息
        old_groups = groups[:-10]
        compressed = []
        
        for group in old_groups:
            compressed.append(self.compress_group(group))
        
        # 4. 返回压缩后的消息
        return compressed + recent
```

**3. 微型压缩（microCompact.ts）**

```python
# microCompact.ts
class MicroCompact:
    """
    微型压缩 - 只压缩工具调用结果
    """
    
    def compact_tool_result(self, tool_result):
        """
        压缩工具结果
        """
        # 如果结果太长，只保留关键部分
        if len(tool_result) > 1000:
            return {
                "summary": tool_result[:500] + "...",
                "key_points": self.extract_key_points(tool_result)
            }
        
        return tool_result
    
    def extract_key_points(self, text):
        """
        提取关键点
        """
        # 使用 LLM 提取关键点
        prompt = f"""
        从以下文本中提取 3-5 个关键点：
        
        {text[:2000]}
        
        关键点：
        """
        
        return call_llm(prompt)
```

**对我有用的**:

```python
# 我的上下文压缩
class ContextCompactor:
    def __init__(self):
        self.threshold = 0.8
    
    def should_compact(self, messages):
        """
        检查是否需要压缩
        """
        total_tokens = sum(len(m["content"]) for m in messages)
        
        if total_tokens > 100000:  # 超过 100k tokens
            return True
        
        return False
    
    def compact(self, messages):
        """
        压缩消息
        """
        # 1. 保留最近 50 条
        recent = messages[-50:]
        
        # 2. 压缩旧的消息
        old_messages = messages[:-50]
        
        # 3. 生成摘要
        summary = self.create_summary(old_messages)
        
        # 4. 返回压缩后的消息
        return [summary] + recent
    
    def create_summary(self, messages):
        """
        创建消息摘要
        """
        key_points = []
        
        for msg in messages:
            if msg["role"] == "user":
                key_points.append(f"用户: {msg['content'][:50]}...")
            elif msg["role"] == "tool":
                key_points.append(f"工具: {msg['name']} -> {msg['content'][:50]}...")
        
        return {
            "role": "system",
            "content": "对话摘要:\n" + "\n".join(key_points)
        }
```

---

## 🧠 2. 智能体长期记忆如何管理？⭐⭐⭐⭐⭐

### 核心设计

**AgentTool 的记忆系统（agentMemory.ts）**

```python
# agentMemory.ts
class AgentMemory:
    def __init__(self):
        self.messages = []
        self.snapshots = []
    
    def add_message(self, message):
        """
        添加消息到记忆
        """
        self.messages.append({
            "role": message["role"],
            "content": message["content"],
            "timestamp": now()
        })
    
    def create_snapshot(self):
        """
        创建记忆快照
        用于传递给子代理或恢复
        """
        snapshot = {
            "messages": self.messages.copy(),
            "timestamp": now()
        }
        self.snapshots.append(snapshot)
        return snapshot
    
    def restore_snapshot(self, snapshot):
        """
        从快照恢复记忆
        """
        self.messages = snapshot["messages"].copy()
    
    def get_relevant_context(self, query, limit=10):
        """
        获取与查询相关的上下文
        """
        # 简单实现：返回最近的消息
        return self.messages[-limit:]
```

**DREAM_TASK - 后台记忆整固**

```python
# DreamTask - 后台自动"做梦"
class DreamTask:
    """
    后台记忆整固
    在空闲时间自主处理和整固记忆
    """
    
    async def consolidate_memory(self):
        """
        整固记忆
        """
        # 1. 读取最近的对话
        recent_conversations = await self.get_recent_conversations()
        
        # 2. 提取关键信息
        key_insights = await self.extract_insights(recent_conversations)
        
        # 3. 更新长期记忆
        await self.update_long_term_memory(key_insights)
        
        # 4. 清理短期记忆
        await self.cleanup_short_term_memory()
    
    async def extract_insights(self, conversations):
        """
        使用 LLM 提取关键洞察
        """
        prompt = f"""
        从以下对话中提取 3-5 个关键洞察：
        
        {conversations}
        
        关键洞察：
        """
        
        return await call_llm(prompt)
    
    async def update_long_term_memory(self, insights):
        """
        更新长期记忆
        """
        # 追加到 MEMORY.md
        with open("MEMORY.md", "a") as f:
            f.write(f"\n## {now()}\n")
            for insight in insights:
                f.write(f"- {insight}\n")
```

**对我有用的**:

```python
# 我的记忆管理系统
class MemoryManager:
    def __init__(self):
        self.short_term = []
        self.long_term_file = "MEMORY.md"
    
    def add_message(self, message):
        """
        添加到短期记忆
        """
        self.short_term.append({
            "role": message["role"],
            "content": message["content"],
            "timestamp": now()
        })
        
        # 超过 100 条时清理
        if len(self.short_term) > 100:
            self.consolidate()
    
    def consolidate(self):
        """
        整固记忆
        """
        # 1. 提取关键信息
        key_points = []
        
        for msg in self.short_term[:-50]:  # 保留最近 50 条
            if msg["role"] == "user":
                key_points.append(f"用户: {msg['content'][:50]}")
        
        # 2. 追加到长期记忆
        with open(self.long_term_file, "a") as f:
            f.write(f"\n## {now()}\n")
            for point in key_points:
                f.write(f"- {point}\n")
        
        # 3. 清理短期记忆
        self.short_term = self.short_term[-50:]
    
    def get_relevant_context(self, query):
        """
        获取相关上下文
        """
        # 读取长期记忆
        with open(self.long_term_file, "r") as f:
            long_term = f.read()
        
        # 简单匹配（实际应该用向量搜索）
        if query.lower() in long_term.lower():
            return long_term[-1000:]  # 返回最近 1000 字符
        
        return ""
```

---

## 🔒 3. MCP 协议如何安全调度？⭐⭐⭐⭐⭐

### 文件结构（28个文件）

```
src/services/mcp/
├── client.ts                 # MCP 客户端 ⭐
├── MCPConnectionManager.tsx  # 连接管理器
├── auth.ts                   # 认证 ⭐
├── channelPermissions.ts     # 频道权限 ⭐
├── channelAllowlist.ts       # 频道白名单 ⭐
├── elicitationHandler.ts     # 诱导处理
├── headersHelper.ts          # 头部辅助（安全）⭐
├── officialRegistry.ts       # 官方注册表
└── types.ts                  # 类型定义
```

### 核心安全机制 ⭐⭐⭐⭐⭐

**1. 认证系统（auth.ts）**

```python
# auth.ts
class MCPAuth:
    def authenticate_server(self, server_config):
        """
        认证 MCP 服务器
        """
        auth_type = server_config.get("auth", "none")
        
        if auth_type == "oauth":
            return self.oauth_authenticate(server_config)
        elif auth_type == "token":
            return self.token_authenticate(server_config)
        else:
            return None
    
    def oauth_authenticate(self, config):
        """
        OAuth 认证
        """
        # 1. 生成认证 URL
        auth_url = self.build_auth_url(config)
        
        # 2. 用户授权
        code = await self.get_user_auth_code(auth_url)
        
        # 3. 换取 token
        token = await self.exchange_token(code)
        
        return token
```

**2. 频道权限（channelPermissions.ts）**

```python
# channelPermissions.ts
class ChannelPermissions:
    def __init__(self):
        self.permissions = {}
    
    def check_permission(self, channel, tool_name):
        """
        检查频道权限
        """
        if channel not in self.permissions:
            return False
        
        channel_perms = self.permissions[channel]
        
        if tool_name in channel_perms.get("allowed_tools", []):
            return True
        
        return False
    
    def grant_permission(self, channel, tool_name):
        """
        授予权限
        """
        if channel not in self.permissions:
            self.permissions[channel] = {
                "allowed_tools": []
            }
        
        self.permissions[channel]["allowed_tools"].append(tool_name)
```

**3. 频道白名单（channelAllowlist.ts）**

```python
# channelAllowlist.ts
class ChannelAllowlist:
    def __init__(self):
        self.whitelist = set()
    
    def is_allowed(self, channel):
        """
        检查频道是否在白名单中
        """
        return channel in self.whitelist
    
    def add_to_whitelist(self, channel):
        """
        添加到白名单
        """
        self.whitelist.add(channel)
```

**4. 头部辅助（headersHelper.ts）- 安全关键 ⭐⭐⭐⭐⭐**

```python
# headersHelper.ts
class HeadersHelper:
    """
    动态头处理中的敏感安全边界
    """
    
    def sanitize_headers(self, headers):
        """
        清理头部，防止注入攻击
        """
        safe_headers = {}
        
        for key, value in headers.items():
            # 移除敏感头
            if key.lower() in ["authorization", "cookie", "x-api-key"]:
                continue
            
            # 验证头值
            if self.is_safe_header_value(value):
                safe_headers[key] = value
        
        return safe_headers
    
    def is_safe_header_value(self, value):
        """
        检查头值是否安全
        """
        # 检查是否包含可疑内容
        dangerous_patterns = [
            "<script",
            "javascript:",
            "data:",
            "vbscript:"
        ]
        
        for pattern in dangerous_patterns:
            if pattern in value.lower():
                return False
        
        return True
```

**对我有用的**:

```python
# 我的 MCP 集成
class MyMCPManager:
    def __init__(self):
        self.servers = {}
        self.permissions = {}
        self.whitelist = set()
    
    async def connect_server(self, name, config):
        """
        连接 MCP 服务器
        """
        # 1. 检查白名单
        if not self.is_allowed(name):
            return f"服务器 {name} 不在白名单中"
        
        # 2. 认证
        auth_token = await self.authenticate(config)
        
        # 3. 连接
        server = MCPServer(config, auth_token)
        await server.connect()
        
        self.servers[name] = server
        return server
    
    async def call_tool(self, server_name, tool_name, params):
        """
        调用 MCP 工具
        """
        # 1. 检查权限
        if not self.check_permission(server_name, tool_name):
            return f"工具 {tool_name} 无权限"
        
        # 2. 清理参数
        safe_params = self.sanitize_params(params)
        
        # 3. 调用工具
        server = self.servers.get(server_name)
        return await server.call_tool(tool_name, safe_params)
    
    def sanitize_params(self, params):
        """
        清理参数
        """
        safe_params = {}
        
        for key, value in params.items():
            # 移除敏感参数
            if key.lower() in ["password", "token", "secret"]:
                continue
            
            safe_params[key] = value
        
        return safe_params
```

---

## 🤝 4. 多智能体系统如何协同？⭐⭐⭐⭐⭐

### Coordinator 模式

```python
# coordinatorMode.ts
class Coordinator:
    """
    多代理协调器
    支持多个代理之间的协调任务执行
    """
    
    def __init__(self):
        self.agents = {}
        self.shared_state = {}
        self.message_queue = []
    
    async def coordinate(self, task):
        """
        协调任务执行
        """
        # 1. 分解任务
        subtasks = await self.decompose_task(task)
        
        # 2. 分配给不同代理
        agent_tasks = []
        for subtask in subtasks:
            agent = self.select_agent(subtask)
            agent_tasks.append((agent, subtask))
        
        # 3. 并行执行
        results = await asyncio.gather(*[
            agent.run(subtask)
            for agent, subtask in agent_tasks
        ])
        
        # 4. 同步共享状态
        await self.sync_shared_state(results)
        
        # 5. 消息传递
        await self.pass_messages(results)
        
        # 6. 汇总结果
        return await self.aggregate_results(results)
    
    async def sync_shared_state(self, results):
        """
        同步共享状态
        """
        for result in results:
            if "state_update" in result:
                self.shared_state.update(result["state_update"])
    
    async def pass_messages(self, results):
        """
        在代理间传递消息
        """
        for result in results:
            if "messages" in result:
                self.message_queue.extend(result["messages"])
```

**对我有用的**:

```python
# 我的 Multi-Agent 系统
class MultiAgentCoordinator:
    def __init__(self):
        self.agents = {
            "小新": TechAgent(),
            "小蓝": LogAgent(),
            "设计专家": DesignAgent()
        }
        self.shared_state = {}
        self.message_bus = []
    
    async def coordinate(self, task):
        """
        协调任务执行
        """
        # 1. 分解任务
        subtasks = self.decompose_task(task)
        
        # 2. 分配代理
        agent_tasks = []
        for subtask in subtasks:
            agent = self.select_agent(subtask)
            agent_tasks.append((agent, subtask))
        
        # 3. 并行执行
        results = await asyncio.gather(*[
            agent.run(subtask, self.shared_state)
            for agent, subtask in agent_tasks
        ])
        
        # 4. 同步状态
        self.sync_state(results)
        
        # 5. 传递消息
        self.pass_messages(results)
        
        # 6. 汇总结果
        return self.aggregate(results)
    
    def decompose_task(self, task):
        """
        分解任务
        """
        if task["type"] == "complex":
            # 复杂任务分解
            return [
                {"type": "tech", "content": task["tech_part"]},
                {"type": "design", "content": task["design_part"]}
            ]
        else:
            return [task]
    
    def select_agent(self, subtask):
        """
        选择合适的代理
        """
        if subtask["type"] == "tech":
            return self.agents["小新"]
        elif subtask["type"] == "design":
            return self.agents["设计专家"]
        elif subtask["type"] == "log":
            return self.agents["小蓝"]
        else:
            return self.agents["小新"]  # 默认
    
    def sync_state(self, results):
        """
        同步状态
        """
        for result in results:
            if "state" in result:
                self.shared_state.update(result["state"])
    
    def pass_messages(self, results):
        """
        传递消息
        """
        for result in results:
            if "message" in result:
                self.message_bus.append(result["message"])
    
    def aggregate(self, results):
        """
        汇总结果
        """
        summary = {
            "status": "completed",
            "results": [r["summary"] for r in results],
            "messages": self.message_bus
        }
        return summary
```

---

## 🎯 立即可用的改进

### 1. 添加上下文压缩

```python
class ContextCompactor:
    def compact(self, messages):
        recent = messages[-50:]
        old_messages = messages[:-50]
        summary = self.create_summary(old_messages)
        return [summary] + recent
```

### 2. 添加记忆整固

```python
class MemoryManager:
    def consolidate(self):
        key_points = [msg["content"][:50] for msg in self.short_term]
        with open("MEMORY.md", "a") as f:
            f.write(f"\n## {now()}\n")
            for point in key_points:
                f.write(f"- {point}\n")
```

### 3. 添加 MCP 安全

```python
class MCPManager:
    async def call_tool(self, server_name, tool_name, params):
        if not self.check_permission(server_name, tool_name):
            return "无权限"
        safe_params = self.sanitize_params(params)
        return await server.call_tool(tool_name, safe_params)
```

### 4. 添加 Multi-Agent 协调

```python
class Coordinator:
    async def coordinate(self, task):
        subtasks = self.decompose_task(task)
        results = await asyncio.gather(*[
            agent.run(subtask)
            for agent, subtask in agent_tasks
        ])
        return self.aggregate(results)
```

---

## 📊 最终总结

**Claude Code 的 4 个核心机制**:

1. **上下文压缩** - 分组、微型压缩、自动清理 ⭐⭐⭐⭐⭐
2. **长期记忆** - 快照、整固、DREAM_TASK ⭐⭐⭐⭐⭐
3. **MCP 协议** - 认证、权限、白名单、安全 ⭐⭐⭐⭐⭐
4. **Multi-Agent** - 分解、并行、状态同步、消息传递 ⭐⭐⭐⭐⭐

---

**这次是真正深入核心机制的学习！**

**重点**: 
- **上下文压缩** ⭐⭐⭐⭐⭐
- **记忆整固** ⭐⭐⭐⭐⭐
- **MCP 安全** ⭐⭐⭐⭐⭐
- **Multi-Agent** ⭐⭐⭐⭐⭐

😊
