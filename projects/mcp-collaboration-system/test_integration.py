#!/usr/bin/env python3
"""
Phase 2.1 Step 3: 测试集成
测试 Extractor Agent 与 MCP-S 工作流的集成

功能:
1. 创建测试 DAG
2. 测试 Agent 协作
3. 验证输出结果
"""

import asyncio
import json
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field

from dag_scheduler import DAGScheduler, Task, TaskStatus
from role_pool import RolePool, RoleConfig, RoleStatus
from quality_gate import QualityGate, QualityReport, QualityLevel
from mcp_workflow import MCPWorkflow, WorkflowConfig, WorkflowStatus
from agents.extractor_agent import (
    ExtractorAgent,
    ExtractorConfig,
    ExtractionResult,
    EPUBParser,
    PDFParser,
)
from book_analysis_dag import (
    BOOK_ANALYSIS_DAG,
    BOOK_ANALYSIS_AGENTS,
    BookAnalysisStage,
)


@dataclass
class TestCase:
    """测试用例"""

    name: str
    description: str
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    validate_func: Optional[
        Callable[["IntegrationTestRunner", "TestCase"], Awaitable[Dict[str, Any]]]
    ] = None


@dataclass
class TestResult:
    """测试结果"""

    test_name: str
    passed: bool
    execution_time: float
    output: Any = None
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


class IntegrationTestRunner:
    """集成测试运行器"""

    def __init__(self):
        self.test_results: List[TestResult] = []
        self.temp_files: List[Path] = []

    def create_test_epub(self, content: str = None) -> Path:
        """创建测试 EPUB 文件"""
        if content is None:
            content = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Test Book</title></head>
<body>
<h1>Chapter 1: Introduction</h1>
<p>This is a test chapter with some sample content.</p>
<h1>Chapter 2: Main Content</h1>
<p>Here we discuss important topics and concepts.</p>
</body>
</html>"""

        epub_content = self._generate_minimal_epub(content)
        temp_file = tempfile.NamedTemporaryFile(suffix=".epub", delete=False, mode="wb")
        temp_file.write(epub_content)
        temp_file.close()
        path = Path(temp_file.name)
        self.temp_files.append(path)
        return path

    def _generate_minimal_epub(self, content: str) -> bytes:
        """生成最小 EPUB 文件内容"""
        import io

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(
                "META-INF/container.xml",
                """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>""",
            )
            zf.writestr(
                "content.opf",
                """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>Test Book</dc:title>
    <dc:creator>Test Author</dc:creator>
    <dc:language>en</dc:language>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="ch1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
    <item id="ch2" href="chapter2.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="ch1"/>
    <itemref idref="ch2"/>
  </spine>
</package>""",
            )
            zf.writestr(
                "nav.xhtml",
                """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/opf">
<head><title>Table of Contents</title></head>
<body>
  <nav epub:type="toc">
    <h1>Table of Contents</h1>
    <ol>
      <li><a href="chapter1.xhtml">Chapter 1: Introduction</a></li>
      <li><a href="chapter2.xhtml">Chapter 2: Main Content</a></li>
    </ol>
  </nav>
</body>
</html>""",
            )
            zf.writestr(
                "chapter1.xhtml",
                """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter 1</title></head>
<body>
  <h1>Chapter 1: Introduction</h1>
  <p>This is a test chapter with some sample content for testing the Extractor Agent.</p>
  <p>It contains multiple paragraphs to simulate a real book chapter.</p>
</body>
</html>""",
            )
            zf.writestr(
                "chapter2.xhtml",
                """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter 2</title></head>
<body>
  <h1>Chapter 2: Main Content</h1>
  <p>Here we discuss important topics and concepts in this test chapter.</p>
  <p>More content to ensure proper parsing behavior.</p>
</body>
</html>""",
            )

        return buffer.getvalue()

    def cleanup(self):
        """清理临时文件"""
        for f in self.temp_files:
            try:
                f.unlink()
            except Exception:
                pass

    async def run_test(self, test_case: TestCase) -> TestResult:
        """运行单个测试"""
        import time

        start_time = time.time()
        result = TestResult(test_name=test_case.name, passed=False, execution_time=0)

        try:
            output = await test_case.validate_func(self, test_case)
            result.passed = True
            result.output = output
            result.details = {"status": "success"}
        except Exception as e:
            result.error = str(e)
            result.details = {"status": "failed", "exception": str(e)}

        result.execution_time = time.time() - start_time
        return result

    async def validate_extraction_result(self, test_case: TestCase) -> Dict[str, Any]:
        """验证提取结果"""
        agent = ExtractorAgent()
        epub_path = self.create_test_epub()

        result = await agent.process(str(epub_path))
        if not result.success:
            raise ValueError(f"Extraction failed: {result.error}")

        if len(result.chapters) == 0:
            raise ValueError("No chapters extracted")

        if not result.metadata:
            raise ValueError("No metadata extracted")

        return {
            "success": True,
            "chapters_count": len(result.chapters),
            "has_metadata": bool(result.metadata),
            "has_toc": len(result.toc) > 0,
        }

    async def validate_dag_execution(self, test_case: TestCase) -> Dict[str, Any]:
        """验证 DAG 执行"""
        config = WorkflowConfig(
            workflow_id="test-workflow",
            name="测试工作流",
            description="集成测试工作流",
            enable_quality_gate=False,
        )
        workflow = MCPWorkflow(config)

        for stage in BOOK_ANALYSIS_DAG["stages"][:3]:
            task = Task(
                id=stage["stage_id"],
                name=stage["name"],
                agent_id=stage["agent_role"],
                dependencies=stage["dependencies"],
            )
            task.metadata = stage.get("metadata", {})
            workflow.add_task(task)

        result = await workflow.execute()
        return {
            "status": result.status.value,
            "tasks_completed": result.tasks_completed,
            "tasks_failed": result.tasks_failed,
        }

    async def validate_role_pool_integration(
        self, test_case: TestCase
    ) -> Dict[str, Any]:
        """验证角色池集成"""
        pool = RolePool(max_pool_size=5)

        for role_id, role in list(BOOK_ANALYSIS_AGENTS.items())[:3]:
            config = RoleConfig(
                role_id=role.role_id,
                role_name=role.role_name,
                agent_id=role.agent_type,
                model=role.model,
                max_concurrent_tasks=2,
            )
            await pool.create_role(config)

        acquired = []
        for i in range(3):
            role_id = await pool.acquire_role(f"task-{i}", "extractor")
            acquired.append(role_id)

        for role_id in acquired:
            if role_id:
                await pool.release_role(role_id)

        stats = pool.get_pool_stats()
        return {
            "pools_created": stats["total_roles"],
            "idle_count": stats["idle_roles"],
            "acquired_count": len([r for r in acquired if r]),
        }

    async def validate_quality_gate(self, test_case: TestCase) -> Dict[str, Any]:
        """验证质量门禁"""
        gate = QualityGate(min_score=70.0)

        result = await gate.check_quality(
            task_id="test-task",
            content="这是一个测试内容，用于验证质量门禁功能是否正常工作。",
            metadata={"task": "测试任务"},
        )

        return {
            "passed": result.passed,
            "score": result.overall_score,
            "level": result.quality_level.value,
        }

    async def run_all_tests(self) -> List[TestResult]:
        """运行所有测试"""
        test_cases = [
            TestCase(
                name="test_extractor_epub_parsing",
                description="测试 EPUB 解析功能",
                input_data={},
                expected_output={"success": True, "chapters_count": 2},
                validate_func=lambda runner, tc: runner.validate_extraction_result(tc),
            ),
            TestCase(
                name="test_dag_execution",
                description="测试 DAG 执行流程",
                input_data={},
                expected_output={"status": "completed", "tasks_completed": 3},
                validate_func=lambda runner, tc: runner.validate_dag_execution(tc),
            ),
            TestCase(
                name="test_role_pool_integration",
                description="测试角色池集成",
                input_data={},
                expected_output={"pools_created": 3},
                validate_func=lambda runner, tc: runner.validate_role_pool_integration(
                    tc
                ),
            ),
            TestCase(
                name="test_quality_gate",
                description="测试质量门禁",
                input_data={},
                expected_output={"passed": True},
                validate_func=lambda runner, tc: runner.validate_quality_gate(tc),
            ),
        ]

        for test_case in test_cases:
            result = await self.run_test(test_case)
            self.test_results.append(result)

        return self.test_results

    def generate_report(self) -> str:
        """生成测试报告"""
        import time

        lines = [
            "=" * 70,
            "Phase 2.1 Step 3: 测试集成报告",
            "=" * 70,
            "",
            f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"总测试数: {len(self.test_results)}",
            f"通过: {sum(1 for r in self.test_results if r.passed)}",
            f"失败: {sum(1 for r in self.test_results if not r.passed)}",
            "",
            "-" * 70,
            "详细结果:",
            "-" * 70,
        ]

        for result in self.test_results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            lines.append(f"\n{status} - {result.test_name}")
            lines.append(f"   执行时间: {result.execution_time:.3f}s")
            if result.error:
                lines.append(f"   错误: {result.error}")
            if result.output:
                lines.append(
                    f"   输出: {json.dumps(result.output, ensure_ascii=False, indent=4)}"
                )

        lines.append("\n" + "=" * 70)
        return "\n".join(lines)


class CollaborationTestRunner:
    """Agent 协作测试运行器"""

    def __init__(self):
        self.agent = ExtractorAgent()

    async def test_multi_agent_workflow(self) -> Dict[str, Any]:
        """测试多 Agent 工作流"""
        epub_path = tempfile.NamedTemporaryFile(suffix=".epub", delete=False)
        temp_epub_path = Path(epub_path.name)
        epub_path.close()

        try:
            with zipfile.ZipFile(temp_epub_path, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr(
                    "META-INF/container.xml",
                    """<?xml version="1.0"?>
<container version="1.0">
  <rootfiles>
    <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>""",
                )
                zf.writestr(
                    "content.opf",
                    """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>Collaboration Test Book</dc:title>
    <dc:creator>Test</dc:creator>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="ch1" href="ch1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="ch1"/>
  </spine>
</package>""",
                )
                zf.writestr(
                    "nav.xhtml",
                    """<?xml version="1.0"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<body>
  <nav><ol><li><a href="ch1.xhtml">Chapter 1</a></li></ol></nav>
</body>
</html>""",
                )
                zf.writestr(
                    "ch1.xhtml",
                    """<?xml version="1.0"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<body>
  <h1>Chapter 1: Test</h1>
  <p>This is a test chapter for collaboration testing.</p>
</body>
</html>""",
                )

            result = await self.agent.process(str(temp_epub_path))

            return {
                "success": result.success,
                "chapters_extracted": len(result.chapters),
                "metadata": result.metadata,
                "toc_entries": len(result.toc),
                "content_preview": result.content[:100] if result.content else "",
            }

        finally:
            temp_epub_path.unlink(missing_ok=True)

    async def test_agent_capabilities(self) -> Dict[str, Any]:
        """测试 Agent 能力"""
        caps = self.agent.get_capabilities()

        return {
            "role_id": caps["role_id"],
            "role_name": caps["role_name"],
            "skills_count": len(caps["skills"]),
            "supported_formats": caps["supported_formats"],
            "features": caps["features"],
        }

    async def run_collaboration_tests(self) -> Dict[str, Any]:
        """运行协作测试"""
        import time

        results = {}

        start = time.time()
        results["multi_agent_workflow"] = await self.test_multi_agent_workflow()
        results["workflow_time"] = time.time() - start

        start = time.time()
        results["agent_capabilities"] = await self.test_agent_capabilities()
        results["capabilities_time"] = time.time() - start

        return results


async def run_integration_tests():
    """运行所有集成测试"""
    print("=" * 70)
    print("Phase 2.1 Step 3: 测试集成")
    print("=" * 70)
    print()

    runner = IntegrationTestRunner()
    collab_runner = CollaborationTestRunner()

    print("1. 运行集成测试...")
    integration_results = await runner.run_all_tests()

    print("\n2. 运行协作测试...")
    collaboration_results = await collab_runner.run_collaboration_tests()

    print("\n" + runner.generate_report())

    print("\n" + "=" * 70)
    print("Agent 协作测试结果")
    print("=" * 70)
    print(json.dumps(collaboration_results, indent=2, ensure_ascii=False))

    runner.cleanup()

    return integration_results, collaboration_results


if __name__ == "__main__":
    asyncio.run(run_integration_tests())
