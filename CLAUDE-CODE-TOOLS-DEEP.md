# 🔧 Claude Code 工具系统深度学习

**学习时间**: 2026-03-31 22:40
**重点**: BashTool、AgentTool、FileTool 等核心工具的具体实现

---

## 🛠️ BashTool - 终端命令执行工具 ⭐⭐⭐⭐⭐

### 文件结构（21个文件）

```
BashTool/
├── BashTool.tsx              # 主工具实现
├── bashCommandHelpers.ts     # 命令辅助函数
├── bashPermissions.ts        # 权限检查
├── bashSecurity.ts          # 安全检查（2592行！）⭐
├── commandSemantics.ts      # 命令语义分析
├── destructiveCommandWarning.ts  # 破坏性命令警告
├── modeValidation.ts        # 模式验证
├── pathValidation.ts        # 路径验证
├── prompt.ts               # Prompt 生成
├── readOnlyValidation.ts    # 只读验证
├── sedEditParser.ts        # sed 编辑解析
├── sedValidation.ts        # sed 验证
├── shouldUseSandbox.ts     # 沙箱判断
└── utils.ts                # 工具函数
```

### 核心安全机制 ⭐⭐⭐⭐⭐

**bashSecurity.ts** - **2592行**的安全检查代码！

**安全检查层级**:

```python
# 1. 命令语义分析
def analyze_command_semantics(command):
    """
    分析命令的语义和意图
    """
    # 检查命令类型
    if is_destructive(command):
        return "destructive"
    elif is_read_only(command):
        return "read_only"
    elif is_modification(command):
        return "modification"

# 2. 路径验证
def validate_path(path):
    """
    验证路径是否安全
    """
    # 检查是否越界
    if is_outside_workspace(path):
        raise SecurityError("路径超出工作区")
    
    # 检查敏感路径
    if is_sensitive_path(path):
        raise SecurityError("敏感路径访问")

# 3. 破坏性命令检测
DESTRUCTIVE_COMMANDS = [
    "rm", "rmdir", "delete", "format",
    "dd", "mkfs", "fdisk",
    ">:  # 覆盖重定向
    "git push --force"
]

def is_destructive_command(command):
    """
    检查是否是破坏性命令
    """
    for dangerous in DESTRUCTIVE_COMMANDS:
        if dangerous in command:
            return True
    return False

# 4. sed 编辑验证
def validate_sed_edit(sed_command):
    """
    验证 sed 编辑命令的安全性
    """
    # 解析 sed 命令
    parsed = parse_sed_command(sed_command)
    
    # 检查是否危险
    if parsed.has_in_place_flag():
        return "sed -i 危险，可能直接修改文件"
    
    if parsed.has_destructive_pattern():
        return "sed 模式可能破坏数据"
```

**对我有用的**:

```python
# 我的安全命令执行
class SecureBashTool:
    DESTRUCTIVE_COMMANDS = [
        "rm", "delete", "format", "git push"
    ]
    
    SENSITIVE_PATHS = [
        "/etc", "/system", "/boot",
        ".git", "node_modules"
    ]
    
    def execute(self, command):
        # 1. 语义分析
        semantics = self.analyze_command(command)
        
        # 2. 破坏性检查
        if self.is_destructive(command):
            response = input(f"⚠️ 破坏性命令: {command}，确认吗？")
            if response != "确认":
                return "已取消"
        
        # 3. 路径验证
        paths = self.extract_paths(command)
        for path in paths:
            if self.is_sensitive(path):
                return f"敏感路径: {path}"
        
        # 4. 执行命令
        return subprocess.run(command, shell=True)
```

---

## 🤖 AgentTool - 子代理生成工具 ⭐⭐⭐⭐⭐

### 文件结构（16个文件）

```
AgentTool/
├── AgentTool.tsx          # 主工具实现
├── builtInAgents.ts      # 内置代理定义
├── runAgent.ts          # 运行代理
├── forkSubagent.ts      # Fork 子代理
├── resumeAgent.ts       # 恢复代理
├── agentMemory.ts       # 代理记忆
├── agentMemorySnapshot.ts  # 记忆快照
├── agentDisplay.ts      # 代理显示
├── agentColorManager.ts # 代理颜色管理
└── prompt.ts           # Prompt 生成
```

### 核心功能 ⭐⭐⭐⭐⭐

**1. 内置代理系统**

```python
# builtInAgents.ts
BUILT_IN_AGENTS = {
    "general-purpose": "通用代理",
    "Explore": "代码探索",
    "Plan": "制定计划",
    "verification": "验证代理",
    "statusline-setup": "状态栏设置"
}
```

**2. Fork 子代理**

```python
# forkSubagent.ts
async def fork_subagent(parent_context):
    """
    Fork 一个子代理
    继承父代理的上下文，但独立运行
    """
    subagent = SubAgent(
        context=parent_context.copy(),
        memory=parent_context.memory.copy()
    )
    
    # 子代理独立运行
    result = await subagent.run()
    
    # 只返回摘要
    return result.summary
```

**3. 代理记忆系统**

```python
# agentMemory.ts
class AgentMemory:
    def __init__(self):
        self.messages = []
        self.snapshots = []
    
    def add_message(self, message):
        self.messages.append(message)
    
    def create_snapshot(self):
        """
        创建记忆快照
        用于恢复或传递给子代理
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
```

**对我有用的**:

```python
# 我的子代理系统
class SubAgentSystem:
    def __init__(self):
        self.agents = {
            "小新": TechAgent(),
            "小蓝": LogAgent(),
            "设计专家": DesignAgent()
        }
    
    async def run_subagent(self, agent_name, task, parent_context=None):
        """
        运行子代理
        """
        # 获取代理
        agent = self.agents.get(agent_name)
        if not agent:
            return f"代理 {agent_name} 不存在"
        
        # 创建独立上下文
        if parent_context:
            context = parent_context.copy()
        else:
            context = {}
        
        # 运行代理
        result = await agent.run(task, context)
        
        # 只返回摘要
        return self.create_summary(result)
    
    def create_summary(self, result):
        """
        创建结果摘要
        """
        return {
            "status": result["status"],
            "summary": result["summary"],
            "key_points": result.get("key_points", [])
        }
```

---

## 📁 FileReadTool / FileEditTool - 文件操作工具 ⭐⭐⭐⭐⭐

### 核心设计

**1. 分层读取**

```python
class FileReadTool:
    def read(self, path, options=None):
        """
        智能文件读取
        支持多种格式和部分读取
        """
        # 1. 检查文件类型
        file_type = self.detect_file_type(path)
        
        # 2. 根据类型选择读取方式
        if file_type == "pdf":
            return self.read_pdf(path)
        elif file_type == "image":
            return self.read_image(path)
        elif file_type == "code":
            return self.read_code(path, options)
        else:
            return self.read_text(path)
    
    def read_code(self, path, options):
        """
        代码文件读取
        支持部分读取和语法高亮
        """
        if options and "offset" in options:
            # 部分读取
            return self.read_range(path, options["offset"], options["limit"])
        else:
            # 完整读取
            return self.read_full(path)
```

**2. 安全编辑**

```python
class FileEditTool:
    def edit(self, path, edits):
        """
        安全文件编辑
        """
        # 1. 创建备份
        backup = self.create_backup(path)
        
        try:
            # 2. 应用编辑
            content = self.read_file(path)
            
            for edit in edits:
                content = self.apply_edit(content, edit)
            
            # 3. 写入文件
            self.write_file(path, content)
            
            return "✅ 编辑成功"
        
        except Exception as e:
            # 4. 失败时恢复备份
            self.restore_backup(path, backup)
            return f"❌ 编辑失败: {e}"
```

**对我有用的**:

```python
# 我的文件操作工具
class SmartFileTool:
    def read(self, path, offset=None, limit=None):
        """
        智能文件读取
        """
        # 检查文件大小
        size = os.path.getsize(path)
        
        if size > 10000:  # 大于10KB
            # 部分读取
            if offset is not None:
                return self.read_range(path, offset, limit)
            else:
                return self.read_full(path)
        else:
            # 完整读取
            return self.read_full(path)
    
    def edit(self, path, old_text, new_text):
        """
        安全文件编辑
        """
        # 创建备份
        backup = self.create_backup(path)
        
        try:
            # 读取文件
            content = self.read_file(path)
            
            # 替换文本
            if old_text not in content:
                return f"❌ 未找到: {old_text[:50]}..."
            
            new_content = content.replace(old_text, new_text)
            
            # 写入文件
            self.write_file(path, new_content)
            
            return "✅ 编辑成功"
        
        except Exception as e:
            # 恢复备份
            self.restore_backup(path, backup)
            return f"❌ 编辑失败: {e}"
```

---

## 🔌 LSP 集成 ⭐⭐⭐⭐

### 核心功能

**Language Server Protocol 集成**

```python
class LSPIntegration:
    def __init__(self):
        self.servers = {}
    
    def start_server(self, language):
        """
        启动 LSP 服务器
        """
        if language not in self.servers:
            server = self.create_lsp_server(language)
            self.servers[language] = server
        
        return self.servers[language]
    
    def get_definition(self, file, line, column):
        """
        跳转到定义
        """
        language = self.detect_language(file)
        server = self.start_server(language)
        
        return server.goto_definition(file, line, column)
    
    def get_completions(self, file, line, column):
        """
        代码补全
        """
        language = self.detect_language(file)
        server = self.start_server(language)
        
        return server.complete(file, line, column)
```

**对我有用的**:

```python
# 我的 LSP 集成
class CodeIntelligence:
    def __init__(self):
        self.lsp_client = None
    
    def get_definition(self, file, position):
        """
        跳转到定义
        """
        # 使用 pyright 或其他 LSP
        if not self.lsp_client:
            self.lsp_client = self.start_lsp()
        
        return self.lsp_client.definition(file, position)
```

---

## 🔌 MCP 集成 ⭐⭐⭐⭐⭐

### Model Context Protocol

**核心设计**:

```python
class MCPManager:
    def __init__(self):
        self.servers = {}
    
    async def connect_server(self, name, config):
        """
        连接 MCP 服务器
        """
        server = MCPServer(config)
        await server.connect()
        
        self.servers[name] = server
        return server
    
    async def call_tool(self, server_name, tool_name, params):
        """
        调用 MCP 工具
        """
        server = self.servers.get(server_name)
        if not server:
            return f"MCP 服务器 {server_name} 未连接"
        
        return await server.call_tool(tool_name, params)
```

**对我有用的**:

```python
# 我的 MCP 集成
class MCPIntegration:
    def __init__(self):
        self.servers = {}
    
    async def connect(self, name, command):
        """
        连接 MCP 服务器
        """
        import asyncio
        
        # 启动服务器进程
        process = await asyncio.create_subprocess_exec(
            *command.split(),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE
        )
        
        self.servers[name] = process
        return process
    
    async def call_tool(self, server_name, tool_name, params):
        """
        调用工具
        """
        server = self.servers.get(server_name)
        if not server:
            return f"服务器 {server_name} 未连接"
        
        # 发送 JSON-RPC 请求
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            }
        }
        
        # 发送请求
        server.stdin.write(json.dumps(request).encode())
        
        # 读取响应
        response = await server.stdout.read()
        
        return json.loads(response)
```

---

## 🎯 立即可用的改进

### 1. 强化 BashTool 安全

```python
class SecureBashTool:
    DESTRUCTIVE_COMMANDS = ["rm", "delete", "format"]
    SENSITIVE_PATHS = ["/etc", "/system", ".git"]
    
    def execute(self, command):
        # 安全检查
        if self.is_destructive(command):
            if not self.confirm():
                return "已取消"
        
        # 路径验证
        paths = self.extract_paths(command)
        for path in paths:
            if self.is_sensitive(path):
                return f"敏感路径: {path}"
        
        # 执行
        return subprocess.run(command, shell=True)
```

### 2. 添加子代理系统

```python
class SubAgentSystem:
    def __init__(self):
        self.agents = {
            "小新": TechAgent(),
            "小蓝": LogAgent()
        }
    
    async def run(self, agent_name, task):
        agent = self.agents.get(agent_name)
        result = await agent.run(task)
        return result.summary
```

### 3. 添加智能文件操作

```python
class SmartFileTool:
    def edit(self, path, old_text, new_text):
        # 创建备份
        backup = self.create_backup(path)
        
        try:
            # 应用编辑
            content = self.read_file(path)
            new_content = content.replace(old_text, new_text)
            self.write_file(path, new_content)
            
            return "✅ 成功"
        except Exception as e:
            # 恢复备份
            self.restore_backup(path, backup)
            return f"❌ 失败: {e}"
```

---

## 📊 最终总结

**Claude Code 工具系统的核心价值**:

1. **BashTool** - 2592行安全检查 ⭐⭐⭐⭐⭐
2. **AgentTool** - 子代理系统 ⭐⭐⭐⭐⭐
3. **FileTool** - 智能文件操作 ⭐⭐⭐⭐⭐
4. **LSP** - 代码智能 ⭐⭐⭐⭐
5. **MCP** - 扩展协议 ⭐⭐⭐⭐⭐

**我应该学习的**:
- ✅ 安全检查的重要性
- ✅ 子代理系统设计
- ✅ 智能文件操作
- ✅ LSP 集成
- ✅ MCP 协议

---

**这次是真正深入工具实现的学习！**

**重点**: 
- **安全第一** ⭐⭐⭐⭐⭐
- **子代理系统** ⭐⭐⭐⭐⭐
- **智能操作** ⭐⭐⭐⭐⭐

😊
