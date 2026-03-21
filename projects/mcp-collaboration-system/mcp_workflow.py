#!/usr/bin/env python3
"""
MCP-S 工作流引擎 - Phase 5
整合所有组件，实现完整的多 Agent 协作工作流
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging

from dag_scheduler import DAGScheduler, Task, TaskStatus
from role_pool import RolePool, RoleConfig
from quality_gate import QualityGate, QualityReport, QualityLevel
from prompt_template import TemplateManager, PromptTemplate, TemplateType


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """工作流状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowConfig:
    """工作流配置"""
    workflow_id: str
    name: str
    description: str
    max_parallel_tasks: int = 3
    enable_quality_gate: bool = True
    min_quality_score: float = 70.0
    timeout_seconds: int = 600


@dataclass
class WorkflowResult:
    """工作流结果"""
    workflow_id: str
    status: WorkflowStatus
    tasks_completed: int
    tasks_failed: int
    total_execution_time: float
    quality_reports: List[QualityReport]
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MCPWorkflow:
    """MCP-S 工作流引擎 - 整合所有组件"""

    def __init__(self, config: WorkflowConfig):
        self.config = config
        self.status = WorkflowStatus.PENDING

        # 核心组件
        self.scheduler = DAGScheduler()
        self.role_pool = RolePool(max_pool_size=10)
        self.quality_gate = QualityGate(min_score=config.min_quality_score)
        self.template_manager = TemplateManager()

        # 执行状态
        self.execution_start_time = None
        self.execution_end_time = None
        self.quality_reports: List[QualityReport] = []

    def add_task(self, task: Task):
        """添加任务到工作流"""
        self.scheduler.add_task(task)

    def add_role_config(self, config: RoleConfig):
        """添加角色配置"""
        asyncio.create_task(self.role_pool.create_role(config))

    def register_template(self, template: PromptTemplate):
        """注册 Prompt 模板"""
        self.template_manager.register_template(template)

    async def execute(self) -> WorkflowResult:
        """
        执行工作流

        返回:
            工作流结果
        """
        import time
        self.execution_start_time = time.time()
        self.status = WorkflowStatus.RUNNING

        logger.info(f"工作流 {self.config.workflow_id} 开始执行")

        try:
            # 1. 检测循环依赖
            cycle = self.scheduler.detect_cycle()
            if cycle:
                raise ValueError(f"检测到循环依赖: {' -> '.join(cycle)}")

            # 2. 拓扑排序
            execution_order = self.scheduler.topological_sort()
            logger.info(f"执行顺序: {' -> '.join(execution_order)}")

            # 3. 按批次执行任务（考虑依赖关系）
            completed_count = 0
            failed_count = 0

            for task_id in execution_order:
                task = self.scheduler.get_task(task_id)

                # 检查依赖是否完成
                if not self._check_dependencies_completed(task):
                    logger.warning(f"任务 {task_id} 的依赖未完成，跳过")
                    failed_count += 1
                    continue

                # 执行任务
                logger.info(f"执行任务: {task_id} ({task.name})")

                try:
                    await self._execute_task(task)
                    completed_count += 1

                except Exception as e:
                    logger.error(f"任务 {task_id} 执行失败: {str(e)}")
                    failed_count += 1

                    # 根据配置决定是否继续
                    if task.metadata.get("blocking", True):
                        raise

            # 4. 计算执行时间
            self.execution_end_time = time.time()
            execution_time = self.execution_end_time - self.execution_start_time

            # 5. 确定最终状态
            self.status = WorkflowStatus.COMPLETED if failed_count == 0 else WorkflowStatus.FAILED

            # 6. 生成结果
            result = WorkflowResult(
                workflow_id=self.config.workflow_id,
                status=self.status,
                tasks_completed=completed_count,
                tasks_failed=failed_count,
                total_execution_time=execution_time,
                quality_reports=self.quality_reports.copy()
            )

            logger.info(f"工作流执行完成: {completed_count} 成功, {failed_count} 失败")
            return result

        except Exception as e:
            logger.error(f"工作流执行失败: {str(e)}")
            self.status = WorkflowStatus.FAILED
            self.execution_end_time = time.time()

            return WorkflowResult(
                workflow_id=self.config.workflow_id,
                status=WorkflowStatus.FAILED,
                tasks_completed=0,
                tasks_failed=1,
                total_execution_time=time.time() - self.execution_start_time,
                quality_reports=self.quality_reports.copy()
            )

    async def _execute_task(self, task: Task):
        """
        执行单个任务

        参数:
            task: 任务对象
        """
        # 1. 获取角色
        role_id = await self.role_pool.acquire_role(task.id, task.metadata.get("role_type", "default"))

        if not role_id:
            # 如果没有可用角色，使用默认方式执行
            logger.warning(f"没有可用角色，使用默认方式执行任务 {task.id}")
            role_id = "default"

        # 2. 渲染 Prompt（如果有模板）
        prompt = task.metadata.get("prompt", "")

        if "template_id" in task.metadata:
            template_id = task.metadata["template_id"]
            template_vars = task.metadata.get("template_vars", {})
            prompt = self.template_manager.render_template(template_id, **template_vars)

        # 3. 模拟执行（实际应该调用 Agent）
        logger.info(f"角色 {role_id} 执行任务 {task.id}")
        await asyncio.sleep(0.5)  # 模拟执行时间

        # 4. 质量检查（如果启用）
        if self.config.enable_quality_gate:
            report = await self.quality_gate.check_quality(
                task_id=task.id,
                content=prompt,
                metadata={"task": task.name, "role": role_id}
            )

            self.quality_reports.append(report)

            # 如果质量不达标且任务标记为阻塞
            if not report.passed and task.metadata.get("quality_blocking", True):
                raise ValueError(f"质量检查未通过: 分数 {report.overall_score:.1f} < {self.config.min_quality_score}")

        # 5. 更新任务状态
        self.scheduler.update_task_status(task.id, TaskStatus.COMPLETED)

        # 6. 释放角色
        if role_id != "default":
            await self.role_pool.release_role(task.id)

    def _check_dependencies_completed(self, task: Task) -> bool:
        """检查任务依赖是否完成"""
        for dep_id in task.dependencies:
            dep_task = self.scheduler.get_task(dep_id)
            if dep_task and dep_task.status != TaskStatus.COMPLETED:
                return False
        return True

    def get_execution_summary(self) -> Dict:
        """获取执行摘要"""
        summary = self.scheduler.get_execution_summary()
        pool_stats = self.role_pool.get_pool_stats()
        quality_stats = self.quality_gate.get_statistics()

        return {
            "workflow_id": self.config.workflow_id,
            "status": self.status.value,
            "tasks": summary,
            "role_pool": pool_stats,
            "quality": quality_stats,
        }

    def visualize_workflow(self) -> str:
        """可视化工作流"""
        lines = [
            f"工作流: {self.config.name}",
            f"状态: {self.status.value}",
            "=" * 60
        ]

        # DAG 结构
        lines.append("\n任务结构:")
        lines.append(self.scheduler.visualize_dag())

        # 角色池状态
        lines.append("\n角色池:")
        lines.append(self.role_pool.visualize_pool())

        # 质量报告摘要
        if self.quality_reports:
            lines.append("\n质量检查:")
            for report in self.quality_reports[-3:]:  # 只显示最近 3 个
                lines.append(f"  任务 {report.task_id}: {report.overall_score:.1f} ({report.quality_level.value})")

        return "\n".join(lines)


# 工厂函数
def create_simple_workflow(
    workflow_id: str,
    name: str,
    tasks: List[Task],
    role_configs: List[RoleConfig] = None
) -> MCPWorkflow:
    """
    创建简单工作流

    参数:
        workflow_id: 工作流 ID
        name: 工作流名称
        tasks: 任务列表
        role_configs: 角色配置列表（可选）

    返回:
        工作流对象
    """
    config = WorkflowConfig(
        workflow_id=workflow_id,
        name=name,
        description=f"工作流: {name}"
    )

    workflow = MCPWorkflow(config)

    # 添加任务
    for task in tasks:
        workflow.add_task(task)

    # 添加角色配置
    if role_configs:
        for role_config in role_configs:
            workflow.add_role_config(role_config)

    return workflow


if __name__ == "__main__":
    # 测试完整工作流
    async def test():
        # 创建任务
        tasks = [
            Task("t1", "数据采集", "agent_a"),
            Task("t2", "数据清洗", "agent_b", dependencies=["t1"]),
            Task("t3", "数据分析", "agent_c", dependencies=["t2"]),
            Task("t4", "生成报告", "agent_d", dependencies=["t3"]),
        ]

        # 创建工作流
        workflow = create_simple_workflow(
            workflow_id="wf001",
            name="数据处理工作流",
            tasks=tasks
        )

        # 注册内置模板
        from prompt_template import BuiltInTemplates
        for template in [
            BuiltInTemplates.coding_task_template(),
            BuiltInTemplates.code_review_template(),
        ]:
            workflow.register_template(template)

        # 执行工作流
        result = await workflow.execute()

        # 显示结果
        print("\n执行结果:")
        print(f"  状态: {result.status.value}")
        print(f"  完成任务: {result.tasks_completed}")
        print(f"  失败任务: {result.tasks_failed}")
        print(f"  执行时间: {result.total_execution_time:.2f}秒")

        # 显示可视化
        print("\n" + workflow.visualize_workflow())

    asyncio.run(test())
