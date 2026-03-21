#!/usr/bin/env python3
"""
Prompt 模板系统 - Phase 4
实现 Prompt 模板管理和变量插值
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import re
import json


class TemplateType(Enum):
    """模板类型"""
    SYSTEM = "system"       # 系统提示词
    TASK = "task"          # 任务提示词
    REVIEW = "review"      # 审查提示词
    CUSTOM = "custom"      # 自定义


@dataclass
class PromptTemplate:
    """Prompt 模板"""
    template_id: str
    name: str
    template_type: TemplateType
    content: str
    variables: List[str] = field(default_factory=list)
    description: str = ""
    parent_id: Optional[str] = None  # 父模板 ID（用于继承）
    metadata: Dict = field(default_factory=dict)

    def render(self, **kwargs) -> str:
        """
        渲染模板

        参数:
            **kwargs: 变量值

        返回:
            渲染后的 Prompt
        """
        # 检查必需变量
        missing_vars = set(self.variables) - set(kwargs.keys())
        if missing_vars:
            raise ValueError(f"缺少必需的变量: {', '.join(missing_vars)}")

        # 替换变量
        rendered = self.content
        for var, value in kwargs.items():
            placeholder = f"{{{{{var}}}}}"
            rendered = rendered.replace(placeholder, str(value))

        return rendered

    def extract_variables(self) -> List[str]:
        """从模板内容中提取变量"""
        pattern = r"\{\{(\w+)\}\}"
        self.variables = list(set(re.findall(pattern, self.content)))
        return self.variables


class TemplateManager:
    """模板管理器 - 管理所有 Prompt 模板"""

    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self.variable_defaults: Dict[str, Any] = {}

    def register_template(self, template: PromptTemplate):
        """
        注册模板

        参数:
            template: 模板对象
        """
        # 自动提取变量
        if not template.variables:
            template.extract_variables()

        self.templates[template.template_id] = template

    def unregister_template(self, template_id: str):
        """取消注册模板"""
        if template_id in self.templates:
            del self.templates[template_id]

    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """获取模板"""
        return self.templates.get(template_id)

    def render_template(self, template_id: str, **kwargs) -> str:
        """
        渲染模板

        参数:
            template_id: 模板 ID
            **kwargs: 变量值

        返回:
            渲染后的 Prompt
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"模板不存在: {template_id}")

        return template.render(**kwargs)

    def set_variable_default(self, variable: str, default_value: Any):
        """设置变量默认值"""
        self.variable_defaults[variable] = default_value

    def get_templates_by_type(self, template_type: TemplateType) -> List[PromptTemplate]:
        """按类型获取模板"""
        return [
            t for t in self.templates.values()
            if t.template_type == template_type
        ]

    def search_templates(self, keyword: str) -> List[PromptTemplate]:
        """
        搜索模板

        参数:
            keyword: 关键词

        返回:
            匹配的模板列表
        """
        keyword_lower = keyword.lower()
        return [
            t for t in self.templates.values()
            if keyword_lower in t.name.lower() or
               keyword_lower in t.description.lower() or
               keyword_lower in t.content.lower()
        ]

    def export_templates(self, filepath: str):
        """
        导出模板到文件

        参数:
            filepath: 文件路径
        """
        data = []
        for template in self.templates.values():
            data.append({
                "template_id": template.template_id,
                "name": template.name,
                "template_type": template.template_type.value,
                "content": template.content,
                "variables": template.variables,
                "description": template.description,
                "parent_id": template.parent_id,
                "metadata": template.metadata,
            })

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def import_templates(self, filepath: str):
        """
        从文件导入模板

        参数:
            filepath: 文件路径
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            template = PromptTemplate(
                template_id=item["template_id"],
                name=item["name"],
                template_type=TemplateType(item["template_type"]),
                content=item["content"],
                variables=item.get("variables", []),
                description=item.get("description", ""),
                parent_id=item.get("parent_id"),
                metadata=item.get("metadata", {})
            )
            self.register_template(template)


# 内置模板
class BuiltInTemplates:
    """内置 Prompt 模板"""

    @staticmethod
    def coding_task_template() -> PromptTemplate:
        """编码任务模板"""
        return PromptTemplate(
            template_id="coding_task",
            name="编码任务",
            template_type=TemplateType.TASK,
            content="""你是一个专业的程序员。

任务描述:
{{task_description}}

要求:
1. 代码要清晰、可维护
2. 添加必要的注释
3. 处理错误情况
4. 编写简单的测试

技术栈:
{{tech_stack}}

输出格式:
请直接输出代码，不要有多余的解释。""",
            description="用于编码任务的通用模板"
        )

    @staticmethod
    def code_review_template() -> PromptTemplate:
        """代码审查模板"""
        return PromptTemplate(
            template_id="code_review",
            name="代码审查",
            template_type=TemplateType.REVIEW,
            content="""请审查以下代码:

```{{language}}
{{code}}
```

检查要点:
1. 代码质量和可读性
2. 潜在的 bug
3. 安全问题
4. 性能优化建议
5. 最佳实践建议

请以结构化的方式给出审查意见。""",
            description="用于代码审查的模板"
        )

    @staticmethod
    def data_analysis_template() -> PromptTemplate:
        """数据分析模板"""
        return PromptTemplate(
            template_id="data_analysis",
            name="数据分析",
            template_type=TemplateType.TASK,
            content="""你是一个数据分析师。

数据源:
{{data_source}}

分析目标:
{{analysis_goal}}

分析要求:
1. 数据清洗和预处理
2. 探索性数据分析
3. 可视化关键发现
4. 得出结论和建议

请提供详细的分析报告。""",
            description="用于数据分析任务的模板"
        )

    @staticmethod
    def documentation_template() -> PromptTemplate:
        """文档编写模板"""
        return PromptTemplate(
            template_id="documentation",
            name="文档编写",
            template_type=TemplateType.TASK,
            content="""请编写{{doc_type}}文档。

主题:
{{topic}}

目标读者:
{{audience}}

文档要求:
1. 结构清晰，层次分明
2. 语言简洁易懂
3. 包含必要的示例
4. 使用 Markdown 格式

请提供完整的文档内容。""",
            description="用于编写各类文档的模板"
        )


if __name__ == "__main__":
    # 测试模板系统
    manager = TemplateManager()

    # 注册内置模板
    for template in [
        BuiltInTemplates.coding_task_template(),
        BuiltInTemplates.code_review_template(),
        BuiltInTemplates.data_analysis_template(),
        BuiltInTemplates.documentation_template(),
    ]:
        manager.register_template(template)

    # 渲染编码任务模板
    prompt = manager.render_template(
        "coding_task",
        task_description="实现一个快速排序算法",
        tech_stack="Python 3.9"
    )

    print("渲染结果:")
    print("=" * 60)
    print(prompt)
    print("=" * 60)

    # 搜索模板
    print("\n搜索 '代码':")
    results = manager.search_templates("代码")
    for t in results:
        print(f"  - {t.name}: {t.description}")
