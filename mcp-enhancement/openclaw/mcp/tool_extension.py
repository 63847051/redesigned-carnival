import json
import inspect
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ToolDefinition:
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable = field(repr=False)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
            "metadata": self.metadata,
        }


class MCPToolExtension:
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools: Dict[str, ToolDefinition] = {}
        self._call_history: List[Dict[str, Any]] = []

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ToolDefinition:
        if name in self.tools:
            raise ValueError(f"Tool '{name}' already registered")

        if not callable(handler):
            raise ValueError(f"Handler for '{name}' must be callable")

        tool = ToolDefinition(
            name=name,
            description=description,
            input_schema=input_schema,
            handler=handler,
            metadata=metadata or {},
        )

        self.tools[name] = tool
        return tool

    def unregister_tool(self, name: str) -> bool:
        if name in self.tools:
            del self.tools[name]
            return True
        return False

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self.tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        return [tool.to_dict() for tool in self.tools.values()]

    def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Any:
        tool = self.tools.get(name)

        if not tool:
            raise ValueError(f"Tool '{name}' not found")

        args = arguments or {}

        self._call_history.append(
            {"tool": name, "arguments": args, "timestamp": datetime.now().isoformat()}
        )

        try:
            sig = inspect.signature(tool.handler)
            param_names = list(sig.parameters.keys())

            if len(param_names) == 0:
                result = tool.handler()
            elif len(param_names) == 1:
                result = tool.handler(args)
            else:
                filtered_args = {k: v for k, v in args.items() if k in param_names}
                result = tool.handler(**filtered_args)

            return {"success": True, "result": result, "tool": name}
        except Exception as e:
            return {"success": False, "error": str(e), "tool": name}

    def call_tools_batch(self, calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for call in calls:
            tool_name = call.get("tool")
            arguments = call.get("arguments", {})
            result = self.call_tool(tool_name, arguments)
            results.append(result)
        return results

    def get_call_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        if limit:
            return self._call_history[-limit:]
        return self._call_history.copy()

    def clear_history(self):
        self._call_history.clear()

    def get_schema(self) -> Dict[str, Any]:
        return {"name": self.name, "version": self.version, "tools": self.list_tools()}

    def export_schema(self, path: str):
        with open(path, "w") as f:
            json.dump(self.get_schema(), f, indent=2)

    def load_tools_from_module(self, module: Any):
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, BaseTool):
                tool_instance = attr()
                if hasattr(tool_instance, "name") and hasattr(tool_instance, "execute"):
                    self.register_tool(
                        name=getattr(tool_instance, "name"),
                        description=getattr(tool_instance, "description", ""),
                        input_schema=getattr(tool_instance, "input_schema", {}),
                        handler=tool_instance.execute,
                        metadata=getattr(tool_instance, "metadata", {}),
                    )


class BaseTool:
    name: str = ""
    description: str = ""
    input_schema: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}

    def execute(self, arguments: Dict[str, Any]) -> Any:
        raise NotImplementedError("Subclasses must implement execute()")


def create_tool_handler(func: Callable) -> Callable:
    def handler(arguments: Dict[str, Any] = None) -> Any:
        args = arguments or {}
        if inspect.iscoroutinefunction(func):
            import asyncio

            return asyncio.run(func(**args))
        return func(**args)

    return handler


def standard_tool(name: str, description: str, input_schema: Dict[str, Any]):
    def decorator(func: Callable) -> Callable:
        func._tool_name = name
        func._tool_description = description
        func._tool_input_schema = input_schema
        return func

    return decorator
