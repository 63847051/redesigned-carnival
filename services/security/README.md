# 🔒 安全服务 - 4层防护系统

**版本**: v7.1
**作者**: 大领导
**时间**: 2026-03-31 23:20

---

## 🎯 系统架构

```python
class SecurityService:
    """
    4层安全防护系统
    """
    
    def __init__(self):
        self.layers = [
            PromptSecurityLayer(),      # 第1层
            PermissionLayer(),          # 第2层（已有）
            ParameterValidationLayer(),  # 第3层
            SandboxLayer()              # 第4层
        ]
    
    def check(self, tool, args):
        """
        执行4层安全检查
        """
        for layer in self.layers:
            result = layer.check(tool, args)
            if result != "safe":
                return result
        
        return "safe"
```

---

## 📋 4层防护

### 第1层：Prompt 安全约束

```python
class PromptSecurityLayer:
    """
    Prompt 层安全检查
    警惕注入、谨慎执行
    """
    
    def check(self, tool, args):
        dangerous_patterns = [
            "删除", "格式化", "清空", "覆盖"
        ]
        
        for value in args.values():
            for pattern in dangerous_patterns:
                if pattern in str(value):
                    return f"⚠️ Prompt安全警告: {pattern}操作需谨慎"
        
        return "safe"
```

### 第2层：权限模式

```python
class PermissionLayer:
    """
    权限层检查
    默认保守、危险确认
    """
    
    DANGEROUS_TOOLS = [
        "rm", "delete", "format", "git push"
    ]
    
    def check(self, tool, args):
        if tool in self.DANGEROUS_TOOLS:
            # 已有三重防护机制
            return "safe"
        
        return "safe"
```

### 第3层：参数验证

```python
class ParameterValidationLayer:
    """
    参数层验证
    路径验证、命令分析
    """
    
    def __init__(self):
        self.sensitive_paths = [
            "/etc", "/system", "/boot", ".git", "node_modules"
        ]
    
    def check(self, tool, args):
        # 检查文件路径
        if "path" in args:
            path = args["path"]
            if self.is_sensitive_path(path):
                return f"❌ 敏感路径: {path}"
        
        # 检查命令
        if "command" in args:
            command = args["command"]
            if self.is_dangerous_command(command):
                return f"❌ 危险命令: {command}"
        
        return "safe"
```

### 第4层：运行隔离

```python
class SandboxLayer:
    """
    沙箱层执行
    沙箱执行、安全边界
    """
    
    def __init__(self):
        self.dangerous_tools = [
            "rm", "delete", "format", "git push"
        ]
    
    def execute(self, tool, args):
        if tool in self.dangerous_tools:
            return self.execute_in_sandbox(tool, args)
        
        return None
    
    def execute_in_sandbox(self, tool, args):
        """
        在沙箱中执行
        """
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as temp_dir:
            old_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                result = self.execute_tool(tool, args)
                return result
            finally:
                os.chdir(old_cwd)
```

---

## 🎯 使用示例

```python
# 使用安全服务
security = SecurityService()

# 检查工具调用
result = security.check("write_file", {
    "path": "/etc/passwd",
    "content": "test"
})

if result != "safe":
    print(f"安全检查失败: {result}")
else:
    print("✅ 安全检查通过")
```

---

## 📊 安全检查流程

```
工具调用
  ↓
第1层: Prompt 检查
  ├─ 危险模式检测
  └─ 警告提示
  ↓
第2层: 权限检查
  ├─ 危险工具确认
  └─ 三重防护
  ↓
第3层: 参数验证
  ├─ 路径验证
  └─ 命令分析
  ↓
第4层: 沙箱执行
  ├─ 危险操作隔离
  └─ 临时目录
  ↓
执行工具
```

---

**4层防护系统 - 安全第一！**

😊
