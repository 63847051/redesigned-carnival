"""
Extractor Agent Registration Module
====================================

This module integrates the Extractor Agent with the MCP-S RolePool system.

Usage:
------
    from extractor_registration import register_extractor_agent

    # Register to existing role pool
    await register_extractor_agent(role_pool)

    # Or create standalone
    extractor = create_extractor_agent()
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

# Import MCP-S components
from role_pool import RolePool, RoleConfig, RoleStatus


class ExtractionFormat(Enum):
    EPUB = "epub"
    PDF = "pdf"
    TEXT = "text"
    STRUCTURED = "structured"


@dataclass
class ExtractorAgentConfig:
    """Configuration for Extractor Agent"""

    role_id: str = "extractor"
    role_name: str = "内容提取 Agent"
    agent_type: str = "opencode"
    model: str = "opencode/minimax-m2.5-free"
    max_concurrent_tasks: int = 3
    warm_up: bool = False
    timeout_seconds: int = 300
    metadata: Dict[str, Any] = field(
        default_factory=lambda: {
            "skills": [
                "epub-parser",
                "pdf-parser",
                "text-extractor",
                "structure-parser",
            ],
            "supported_formats": ["epub", "pdf"],
            "description": "Extracts content from EPUB and PDF files",
        }
    )


def create_extractor_role_config(
    config: Optional[ExtractorAgentConfig] = None,
) -> RoleConfig:
    """Create RoleConfig for Extractor Agent"""
    cfg = config or ExtractorAgentConfig()

    return RoleConfig(
        role_id=cfg.role_id,
        role_name=cfg.role_name,
        agent_id=cfg.agent_type,
        model=cfg.model,
        max_concurrent_tasks=cfg.max_concurrent_tasks,
        warm_up=cfg.warm_up,
        timeout_seconds=cfg.timeout_seconds,
        metadata=cfg.metadata,
    )


async def register_extractor_agent(role_pool: RolePool) -> bool:
    """
    Register Extractor Agent to an existing RolePool

    Args:
        role_pool: Instance of RolePool to register to

    Returns:
        True if registration successful
    """
    try:
        config = create_extractor_role_config()
        await role_pool.create_role(config)
        print(f"✓ Extractor Agent registered with role_id: {config.role_id}")
        return True
    except Exception as e:
        print(f"✗ Failed to register Extractor Agent: {e}")
        return False


def create_extractor_agent():
    """Create a standalone Extractor Agent instance"""
    from agents.extractor_agent import ExtractorAgent

    return ExtractorAgent()


async def demo_workflow_integration():
    """Demonstrate how Extractor Agent integrates with MCP-S workflow"""
    from mcp_workflow import MCPWorkflow, WorkflowConfig

    print("=" * 60)
    print("Extractor Agent - MCP-S Workflow Integration Demo")
    print("=" * 60)

    # Create workflow
    config = WorkflowConfig(
        workflow_id="extractor_demo",
        name="Document Extraction Workflow",
        description="Demonstrates Extractor Agent in action",
    )
    workflow = MCPWorkflow(config)

    # Register Extractor Agent
    success = await register_extractor_agent(workflow.role_pool)

    if success:
        print("\n✓ Extractor Agent ready for tasks")
        print("\nSkills available:")
        for skill in [
            "epub-parser",
            "pdf-parser",
            "text-extractor",
            "structure-parser",
        ]:
            print(f"  - {skill}")

        print("\nSupported operations:")
        print("  - Parse EPUB files and extract metadata, TOC, chapters")
        print("  - Parse PDF files and extract text, metadata")
        print("  - Clean and extract text content")
        print("  - Parse document structure")

    return success


async def main():
    """Main entry point for registration demo"""
    success = await demo_workflow_integration()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
