#!/usr/bin/env python3
"""
书籍分析 DAG 定义 - Phase 2.1 Step 1
基于 MCP-S 系统架构设计
"""

from typing import List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class BookAnalysisStage(Enum):
    """书籍分析阶段"""

    EXTRACT_CONTENT = "extract-content"  # 提取内容
    PARSE_STRUCTURE = "parse-structure"  # 解析结构
    SUMMARIZE_CHAPTERS = "summarize-chapters"  # 章节总结
    EXTRACT_KNOWLEDGE = "extract-knowledge"  # 提取知识
    GENERATE_MINDMAP = "generate-mindmap"  # 生成思维导图
    SYNC_TO_HEYCUBE = "sync-to-heycube"  # 同步到 HeyCube
    SYNC_TO_IMA = "sync-to-ima"  # 同步到 IMA


@dataclass
class AgentRole:
    """Agent 角色定义"""

    role_id: str
    role_name: str
    agent_type: str
    model: str = "glmcode/glm-4.5-air"
    description: str = ""
    skills: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# 书籍分析 Agent 角色定义
BOOK_ANALYSIS_AGENTS = {
    "extractor": AgentRole(
        role_id="extractor",
        role_name="内容提取 Agent",
        agent_type="opencode",
        description="从 EPUB/PDF 文件中提取内容和目录结构",
        skills=["epub-parser", "pdf-parser", "text-extractor", "structure-parser"],
    ),
    "summarizer": AgentRole(
        role_id="summarizer",
        role_name="内容总结 Agent",
        agent_type="opencode",
        description="总结每章内容，提取关键信息",
        skills=["text-summarizer", "chapter-summarizer", "key-point-extractor"],
    ),
    "knowledge_extractor": AgentRole(
        role_id="knowledge_extractor",
        role_name="知识提取 Agent",
        agent_type="opencode",
        description="从文本中提取概念、定义和关系",
        skills=["concept-extractor", "entity-extractor", "relation-extractor"],
    ),
    "mindmap_generator": AgentRole(
        role_id="mindmap_generator",
        role_name="思维导图生成 Agent",
        agent_type="opencode",
        description="根据知识结构生成思维导图",
        skills=["mindmap-creator", "hierarchy-builder", "visualization"],
    ),
    "heycube_syncer": AgentRole(
        role_id="heycube_syncer",
        role_name="HeyCube 同步 Agent",
        agent_type="opencode",
        description="同步阅读数据到 HeyCube",
        skills=["heysqlite-sync", "dimension-updater", "data-transformer"],
    ),
    "ima_syncer": AgentRole(
        role_id="ima_syncer",
        role_name="IMA 同步 Agent",
        agent_type="opencode",
        description="同步笔记到 IMA",
        skills=["ima-api", "note-formatter", "tag-mapper"],
    ),
}


# DAG 定义 - 每个阶段的任务和依赖
BOOK_ANALYSIS_DAG = {
    "workflow_id": "book-analysis",
    "name": "书籍分析工作流",
    "description": "自动分析书籍并生成报告",
    "stages": [
        {
            "stage_id": "extract-content",
            "name": "提取内容",
            "description": "从书籍文件中提取内容",
            "agent_role": "extractor",
            "dependencies": [],
            "metadata": {
                "input_type": "file",
                "output_type": "structured_content",
                "quality_blocking": True,
                "timeout": 120,
            },
        },
        {
            "stage_id": "parse-structure",
            "name": "解析结构",
            "description": "解析目录结构和章节关系",
            "agent_role": "extractor",
            "dependencies": ["extract-content"],
            "metadata": {
                "input_type": "content",
                "output_type": "structure",
                "quality_blocking": True,
                "timeout": 60,
            },
        },
        {
            "stage_id": "summarize-chapters",
            "name": "章节总结",
            "description": "总结每章内容",
            "agent_role": "summarizer",
            "dependencies": ["parse-structure"],
            "metadata": {
                "input_type": "chapters",
                "output_type": "summaries",
                "quality_blocking": True,
                "timeout": 300,
            },
        },
        {
            "stage_id": "extract-knowledge",
            "name": "提取知识",
            "description": "提取关键概念和知识点",
            "agent_role": "knowledge_extractor",
            "dependencies": ["summarize-chapters"],
            "metadata": {
                "input_type": "summaries",
                "output_type": "knowledge_graph",
                "quality_blocking": True,
                "timeout": 180,
            },
        },
        {
            "stage_id": "generate-mindmap",
            "name": "生成思维导图",
            "description": "生成书籍思维导图",
            "agent_role": "mindmap_generator",
            "dependencies": ["extract-knowledge"],
            "metadata": {
                "input_type": "knowledge_graph",
                "output_type": "mindmap",
                "quality_blocking": False,
                "timeout": 120,
            },
        },
        {
            "stage_id": "sync-to-heycube",
            "name": "同步 HeyCube",
            "description": "同步到 HeyCube 知识库",
            "agent_role": "heycube_syncer",
            "dependencies": ["extract-knowledge"],
            "metadata": {
                "input_type": "knowledge_graph",
                "output_type": "sync_result",
                "quality_blocking": False,
                "timeout": 60,
            },
        },
        {
            "stage_id": "sync-to-ima",
            "name": "同步 IMA",
            "description": "同步笔记到 IMA",
            "agent_role": "ima_syncer",
            "dependencies": ["summarize-chapters"],
            "metadata": {
                "input_type": "summaries",
                "output_type": "sync_result",
                "quality_blocking": False,
                "timeout": 60,
            },
        },
    ],
    "output": {
        "content": "完整的分析报告",
        "summary": "章节摘要列表",
        "knowledge": "知识图谱",
        "mindmap": "思维导图数据",
        "sync_status": "同步状态",
    },
}


def get_dag_stages() -> List[Dict]:
    """获取 DAG 阶段列表"""
    return BOOK_ANALYSIS_DAG["stages"]


def get_stage_dependencies(stage_id: str) -> List[str]:
    """获取阶段的依赖"""
    for stage in BOOK_ANALYSIS_DAG["stages"]:
        if stage["stage_id"] == stage_id:
            return stage["dependencies"]
    return []


def get_stage_by_id(stage_id: str) -> Dict:
    """获取阶段配置"""
    for stage in BOOK_ANALYSIS_DAG["stages"]:
        if stage["stage_id"] == stage_id:
            return stage
    return None


def get_agent_role(role_id: str) -> AgentRole:
    """获取 Agent 角色配置"""
    return BOOK_ANALYSIS_AGENTS.get(role_id)


if __name__ == "__main__":
    print("=" * 60)
    print("书籍分析 DAG 定义")
    print("=" * 60)
    print(f"\n工作流: {BOOK_ANALYSIS_DAG['name']}")
    print(f"描述: {BOOK_ANALYSIS_DAG['description']}")
    print(f"\n阶段数量: {len(BOOK_ANALYSIS_DAG['stages'])}")

    print("\n" + "=" * 60)
    print("阶段详情")
    print("=" * 60)

    for stage in BOOK_ANALYSIS_DAG["stages"]:
        print(f"\n📌 {stage['stage_id']}")
        print(f"   名称: {stage['name']}")
        print(f"   描述: {stage['description']}")
        print(f"   Agent: {stage['agent_role']}")
        print(f"   依赖: {stage['dependencies'] or '无'}")

    print("\n" + "=" * 60)
    print("Agent 角色")
    print("=" * 60)

    for role_id, role in BOOK_ANALYSIS_AGENTS.items():
        print(f"\n🤖 {role_id}")
        print(f"   名称: {role.role_name}")
        print(f"   描述: {role.description}")
        print(f"   技能: {', '.join(role.skills)}")

    print("\n✅ DAG 定义完成")
