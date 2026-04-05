#!/usr/bin/env python3
"""
多层权限验证系统 - CloudCode 风格
6 层验证机制，增强安全性
"""

import json
import os
from typing import Dict, Any, List, Optional
from enum import Enum


class PermissionResult(Enum):
    """权限验证结果"""
    ALLOW = "allow"
    DENY = "deny"
    PROMPT = "prompt"


# 全局权限表
GLOBAL_PERMISSIONS = {
    # 永久允许的工具
    "allow": {
        "file.read": True,
        "file.write": True,
        "web.fetch": True,
        "web.search": True,
        "browser.open": True,
    },
    # 永期拒绝的工具
    "deny": {
        "system.shutdown": False,
        "system.reboot": False,
        "system.delete_all": False,
    }
}


class MultiLayerPermissionChecker:
    """多层权限验证器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化权限验证器
        
        Args:
            config_path: 权限配置文件路径
        """
        self.config_path = config_path or "/root/.openclaw/workspace/permissions.json"
        self.global_permissions = GLOBAL_PERMISSIONS.copy()
        self.user_preferences = {}
        self.permission_cache = {}
        
        # 加载用户偏好
        self._load_user_preferences()
    
    def _load_user_preferences(self):
        """加载用户权限偏好"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.user_preferences = json.load(f)
            except Exception as e:
                print(f"⚠️ 加载权限配置失败: {e}")
    
    def _save_user_preferences(self):
        """保存用户权限偏好"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.user_preferences, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 保存权限配置失败: {e}")
    
    # ========================================
    # 第 1 层：全局权限表
    # ========================================
    def global_permission_check(self, tool: str, action: str) -> Optional[PermissionResult]:
        """
        第 1 层：全局权限表检查
        
        Args:
            tool: 工具名称
            action: 操作名称
        
        Returns:
            权限验证结果
        """
        tool_key = f"{tool}.{action}"
        
        # 检查永久允许
        if tool_key in self.global_permissions["allow"]:
            return PermissionResult.ALLOW
        
        # 检查永久拒绝
        if tool_key in self.global_permissions["deny"]:
            return PermissionResult.DENY
        
        # 未定义，继续下一层
        return None
    
    # ========================================
    # 第 2 层：工具自检
    # ========================================
    def tool_self_check(self, tool: str, action: str, params: Dict = None) -> Optional[PermissionResult]:
        """
        第 2 层：工具自检
        
        Args:
            tool: 工具名称
            action: 操作名称
            params: 参数
        
        Returns:
            权限验证结果
        """
        # 模拟工具内置权限检查
        # 实际实现中，每个工具应该有自己的权限检查函数
        
        # 示例：文件写入工具检查
        if tool == "file.write":
            if params and "path" in params:
                path = params["path"]
                # 危险路径检查
                if "/root/.openclaw" in path and "delete" in path:
                    return PermissionResult.DENY
        
        # 示例：系统命令工具检查
        if tool == "system.exec":
            if params and "command" in params:
                cmd = params["command"]
                # 危险命令检查
                dangerous = ["rm -rf", "shutdown", "reboot"]
                if any(d in cmd for d in dangerous):
                    return PermissionResult.PROMPT
        
        # 未定义，继续下一层
        return None
    
    # ========================================
    # 第 3 层：模式改写
    # ========================================
    def mode_check(self, tool: str, action: str) -> Optional[PermissionResult]:
        """
        第 3 层：模式改写
        
        Args:
            tool: 工具名称
            action: 操作名称
        
        Returns:
            权限验证结果
        """
        # 检查当前权限模式
        mode = self.user_preferences.get("mode", "normal")
        
        # 自动模式：某些操作自动允许
        if mode == "auto":
            # 只读操作自动允许
            if action in ["read", "get", "list", "search"]:
                return PermissionResult.ALLOW
        
        # 严格模式：所有操作都需要确认
        if mode == "strict":
            return PermissionResult.PROMPT
        
        # 正常模式：继续下一层
        return None
    
    # ========================================
    # 第 4 层：分类器判断
    # ========================================
    def classifier_check(self, tool: str, action: str, params: Dict = None) -> Optional[PermissionResult]:
        """
        第 4 层：分类器判断
        
        Args:
            tool: 工具名称
            action: 操作名称
            params: 参数
        
        Returns:
            权限验证结果
        """
        # 使用分类器判断风险等级
        risk_level = self._assess_risk(tool, action, params)
        
        # 低风险：自动允许
        if risk_level == "low":
            return PermissionResult.ALLOW
        
        # 高风险：需要确认
        if risk_level == "high":
            return PermissionResult.PROMPT
        
        # 极高风险：拒绝
        if risk_level == "critical":
            return PermissionResult.DENY
        
        # 中等风险：继续下一层
        return None
    
    def _assess_risk(self, tool: str, action: str, params: Dict = None) -> str:
        """
        评估操作风险等级
        
        Args:
            tool: 工具名称
            action: 操作名称
            params: 参数
        
        Returns:
            风险等级: low, medium, high, critical
        """
        # 只读操作：低风险
        if action in ["read", "get", "list", "search", "view"]:
            return "low"
        
        # 写入操作：中等风险
        if action in ["write", "create", "update", "edit"]:
            return "medium"
        
        # 删除操作：高风险
        if action in ["delete", "remove", "destroy"]:
            return "high"
        
        # 系统操作：极高风险
        if tool in ["system", "exec", "shell"]:
            if action in ["shutdown", "reboot", "delete"]:
                return "critical"
            return "high"
        
        # 默认中等风险
        return "medium"
    
    # ========================================
    # 第 5 层：用户确认
    # ========================================
    def user_confirm(self, tool: str, action: str, params: Dict = None) -> PermissionResult:
        """
        第 5 层：用户确认
        
        Args:
            tool: 工具名称
            action: 操作名称
            params: 参数
        
        Returns:
            权限验证结果
        """
        # 检查缓存
        cache_key = f"{tool}.{action}"
        if cache_key in self.permission_cache:
            cached = self.permission_cache[cache_key]
            if cached == "always_allow":
                return PermissionResult.ALLOW
            if cached == "always_deny":
                return PermissionResult.DENY
        
        # 生成确认信息
        message = self._generate_confirmation_message(tool, action, params)
        
        # 这里应该弹出确认对话框
        # 暂时返回 PROMPT，表示需要用户确认
        print(f"\n🔔 需要确认: {message}")
        print("选项: allow(允许), deny(拒绝), always_allow(总是允许), always_deny(总是拒绝)")
        
        # 模拟用户输入（实际应该从用户获取）
        # 这里暂时返回 ALLOW，方便测试
        return PermissionResult.PROMPT
    
    def _generate_confirmation_message(self, tool: str, action: str, params: Dict = None) -> str:
        """生成确认信息"""
        message = f"执行操作: {tool}.{action}"
        if params:
            message += f"\n参数: {json.dumps(params, ensure_ascii=False)}"
        return message
    
    # ========================================
    # 第 6 层：沙箱隔离
    # ========================================
    def sandbox_execute(self, tool: str, action: str, params: Dict = None) -> PermissionResult:
        """
        第 6 层：沙箱隔离
        
        Args:
            tool: 工具名称
            action: 操作名称
            params: 参数
        
        Returns:
            权限验证结果
        """
        # 高危命令使用沙箱
        if tool in ["system", "exec", "shell"]:
            if action in ["exec", "run", "execute"]:
                # 检查是否可以安全执行
                if self._is_safe_to_execute(params):
                    return PermissionResult.ALLOW
                else:
                    # 需要沙箱隔离
                    print("⚠️ 此操作需要在沙箱中执行")
                    return PermissionResult.PROMPT
        
        # 其他操作正常执行
        return PermissionResult.ALLOW
    
    def _is_safe_to_execute(self, params: Dict = None) -> bool:
        """检查命令是否安全"""
        if not params or "command" not in params:
            return False
        
        cmd = params["command"]
        
        # 危险命令列表
        dangerous = ["rm -rf", "shutdown", "reboot", "format", "mkfs"]
        
        # 检查是否包含危险命令
        for d in dangerous:
            if d in cmd:
                return False
        
        return True
    
    # ========================================
    # 综合验证
    # ========================================
    def check_permission(self, tool: str, action: str, params: Dict = None) -> PermissionResult:
        """
        综合权限验证（6 层）
        
        Args:
            tool: 工具名称
            action: 操作名称
            params: 参数
        
        Returns:
            权限验证结果
        """
        print(f"\n🔍 开始 6 层权限验证...")
        print(f"📌 工具: {tool}.{action}")
        
        # 第 1 层：全局权限表
        print("  [1/6] 全局权限表...")
        result = self.global_permission_check(tool, action)
        if result:
            print(f"    → {result.value}")
            return result
        print("    → 继续")
        
        # 第 2 层：工具自检
        print("  [2/6] 工具自检...")
        result = self.tool_self_check(tool, action, params)
        if result:
            print(f"    → {result.value}")
            return result
        print("    → 继续")
        
        # 第 3 层：模式改写
        print("  [3/6] 模式改写...")
        result = self.mode_check(tool, action)
        if result:
            print(f"    → {result.value}")
            return result
        print("    → 继续")
        
        # 第 4 层：分类器判断
        print("  [4/6] 分类器判断...")
        result = self.classifier_check(tool, action, params)
        if result:
            print(f"    → {result.value}")
            return result
        print("    → 继续")
        
        # 第 5 层：用户确认
        print("  [5/6] 用户确认...")
        result = self.user_confirm(tool, action, params)
        print(f"    → {result.value}")
        
        # 第 6 层：沙箱隔离
        print("  [6/6] 沙箱隔离...")
        result = self.sandbox_execute(tool, action, params)
        print(f"    → {result.value}")
        
        return result
    
    # ========================================
    # 用户管理
    # ========================================
    def set_user_preference(self, key: str, value: Any):
        """设置用户偏好"""
        self.user_preferences[key] = value
        self._save_user_preferences()
    
    def cache_permission(self, tool: str, action: str, decision: str):
        """缓存权限决策"""
        cache_key = f"{tool}.{action}"
        self.permission_cache[cache_key] = decision
    
    def clear_cache(self):
        """清除权限缓存"""
        self.permission_cache.clear()


# ========================================
# 测试代码
# ========================================
def main():
    """测试多层权限验证"""
    checker = MultiLayerPermissionChecker()
    
    # 测试用例
    test_cases = [
        {
            "tool": "file",
            "action": "read",
            "params": {"path": "/root/test.txt"}
        },
        {
            "tool": "file",
            "action": "write",
            "params": {"path": "/root/test.txt"}
        },
        {
            "tool": "system",
            "action": "exec",
            "params": {"command": "ls -la"}
        },
        {
            "tool": "system",
            "action": "shutdown",
            "params": {}
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试用例 {i}: {test['tool']}.{test['action']}")
        print('='*60)
        
        result = checker.check_permission(
            test['tool'],
            test['action'],
            test.get('params')
        )
        
        print(f"\n✅ 最终结果: {result.value}")


if __name__ == '__main__':
    main()
