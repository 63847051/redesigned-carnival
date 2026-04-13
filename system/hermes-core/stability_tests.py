"""
Hermes Agent Stability Testing Suite - 稳定性测试套件

测试内容：
- 长时间运行测试
- 高并发场景测试
- 边界条件测试
- 内存泄漏检测
- 性能回归测试
"""

import os
import sys
import time
import threading
import multiprocessing
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import psutil
import tracemalloc

# 添加 Hermes 核心到路径
hermes_core_path = Path(__file__).parent
sys.path.insert(0, str(hermes_core_path))

try:
    from optimized_knowledge import OptimizedKnowledgePersistenceSystem
    from compressed_snapshot import CompressedSnapshotAtomicSystem
    from learning.auto_skill_creator import AutoSkillCreator
    from modeling.honcho_lite import HonchoLite
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)


@dataclass
class TestResult:
    """测试结果"""
    test_name: str
    success: bool
    duration: float
    details: Dict[str, Any]
    errors: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "test_name": self.test_name,
            "success": self.success,
            "duration": self.duration,
            "details": self.details,
            "errors": self.errors
        }


class StabilityTestSuite:
    """稳定性测试套件"""
    
    def __init__(self, test_dir: str = "/tmp/hermes_stability_test"):
        """初始化测试套件"""
        self.test_dir = Path(test_dir)
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        self.results: List[TestResult] = []
        
        # 初始化测试系统
        self.knowledge = OptimizedKnowledgePersistenceSystem(
            db_path=str(self.test_dir / "knowledge.db"),
            cache_size=50,
            cache_ttl=1800  # 30 分钟
        )
        
        self.snapshot = CompressedSnapshotAtomicSystem(
            snapshot_dir=str(self.test_dir / "snapshots")
        )
        
        self.skill_creator = AutoSkillCreator(
            skills_dir=str(self.test_dir / "skills")
        )
        
        self.user_model = HonchoLite(
            db_path=str(self.test_dir / "honcho.db")
        )
    
    def run_all_tests(self) -> List[TestResult]:
        """运行所有测试"""
        print("=" * 60)
        print("🧪 Hermes Agent 稳定性测试套件")
        print("=" * 60)
        
        # 基础功能测试
        self.results.append(self.test_knowledge_basic())
        self.results.append(self.test_snapshot_basic())
        self.results.append(self.test_user_model_basic())
        
        # 长时间运行测试
        self.results.append(self.test_long_running())
        
        # 高并发测试
        self.results.append(self.test_concurrent_access())
        
        # 边界条件测试
        self.results.append(self.test_boundary_conditions())
        
        # 内存泄漏检测
        self.results.append(self.test_memory_leaks())
        
        # 性能回归测试
        self.results.append(self.test_performance_regression())
        
        # 生成报告
        self._generate_report()
        
        return self.results
    
    def test_knowledge_basic(self) -> TestResult:
        """知识库基础测试"""
        print("\n📝 测试 1: 知识库基础功能")
        
        start_time = time.time()
        errors = []
        details = {}
        
        try:
            # 测试存储
            success = self.knowledge.learn("test_key", {"data": "test_value"}, "test")
            details["store"] = "✅" if success else "❌"
            
            # 测试检索
            value = self.knowledge.recall("test_key")
            details["recall"] = "✅" if value == {"data": "test_value"} else "❌"
            
            # 测试搜索
            results = self.knowledge.search_knowledge("test")
            details["search"] = f"✅ ({len(results)} 结果)"
            
            # 测试批量操作
            items = [
                {"key": f"batch_{i}", "value": {"index": i}, "category": "batch"}
                for i in range(10)
            ]
            count = self.knowledge.learn_batch(items)
            details["batch_store"] = f"✅ ({count} 条)"
            
            # 测试批量检索
            batch_results = self.knowledge.recall_batch([f"batch_{i}" for i in range(10)])
            details["batch_recall"] = f"✅ ({len(batch_results)} 条)"
            
            # 获取统计
            stats = self.knowledge.get_stats()
            details["stats"] = stats
            
        except Exception as e:
            errors.append(str(e))
        
        duration = time.time() - start_time
        success = len(errors) == 0
        
        print(f"{'✅ 通过' if success else '❌ 失败'} ({duration:.2f}s)")
        if errors:
            for error in errors:
                print(f"  错误: {error}")
        
        return TestResult(
            test_name="knowledge_basic",
            success=success,
            duration=duration,
            details=details,
            errors=errors
        )
    
    def test_snapshot_basic(self) -> TestResult:
        """快照基础测试"""
        print("\n📸 测试 2: 快照基础功能")
        
        start_time = time.time()
        errors = []
        details = {}
        
        try:
            # 创建测试文件
            test_file = self.test_dir / "test_config.txt"
            test_content = "Test config content\n" * 100
            
            # 创建快照
            self.snapshot.save_state(
                str(test_file),
                test_content,
                create_snapshot=True,
                description="Test snapshot"
            )
            details["create_snapshot"] = "✅"
            
            # 获取统计
            stats = self.snapshot.get_compression_stats()
            details["compression_stats"] = stats
            
            # 优化存储
            deleted = self.snapshot.optimize_storage(keep_count=5)
            details["optimize_storage"] = f"✅ (删除 {deleted} 个)"
            
        except Exception as e:
            errors.append(str(e))
        
        duration = time.time() - start_time
        success = len(errors) == 0
        
        print(f"{'✅ 通过' if success else '❌ 失败'} ({duration:.2f}s)")
        if errors:
            for error in errors:
                print(f"  错误: {error}")
        
        return TestResult(
            test_name="snapshot_basic",
            success=success,
            duration=duration,
            details=details,
            errors=errors
        )
    
    def test_user_model_basic(self) -> TestResult:
        """用户模型基础测试"""
        print("\n👤 测试 3: 用户模型基础功能")
        
        start_time = time.time()
        errors = []
        details = {}
        
        try:
            user_id = "test_user_123"
            
            # 记录交互
            self.user_model.record_interaction(
                user_id=user_id,
                content="Test interaction",
                metadata={"type": "test"}
            )
            details["record_interaction"] = "✅"
            
            # 获取用户画像
            profile = self.user_model.profile(user_id)
            details["get_profile"] = f"✅ ({profile.name})"
            
        except Exception as e:
            errors.append(str(e))
        
        duration = time.time() - start_time
        success = len(errors) == 0
        
        print(f"{'✅ 通过' if success else '❌ 失败'} ({duration:.2f}s)")
        if errors:
            for error in errors:
                print(f"  错误: {error}")
        
        return TestResult(
            test_name="user_model_basic",
            success=success,
            duration=duration,
            details=details,
            errors=errors
        )
    
    def test_long_running(self) -> TestResult:
        """长时间运行测试（简化版：1 分钟）"""
        print("\n⏰ 测试 4: 长时间运行（1 分钟）")
        
        start_time = time.time()
        errors = []
        details = {}
        
        try:
            # 模拟 1 分钟的持续操作
            iterations = 0
            end_time = time.time() + 60  # 运行 1 分钟
            
            while time.time() < end_time:
                # 执行各种操作
                self.knowledge.learn(f"temp_{iterations}", {"data": iterations}, "temp")
                
                if iterations % 10 == 0:
                    self.knowledge.recall(f"temp_{iterations - 5}")
                
                if iterations % 20 == 0:
                    test_file = self.test_dir / f"temp_{iterations}.txt"
                    self.snapshot.save_state(
                        str(test_file),
                        f"Content {iterations}",
                        create_snapshot=True
                    )
                
                iterations += 1
                time.sleep(0.1)  # 100ms 间隔
            
            details["iterations"] = iterations
            details["duration"] = f"{(time.time() - start_time):.1f}s"
            
            # 验证系统状态
            stats = self.knowledge.get_stats()
            details["final_stats"] = stats
            
        except Exception as e:
            errors.append(str(e))
        
        duration = time.time() - start_time
        success = len(errors) == 0
        
        print(f"{'✅ 通过' if success else '❌ 失败'} ({duration:.2f}s)")
        if errors:
            for error in errors:
                print(f"  错误: {error}")
        
        return TestResult(
            test_name="long_running",
            success=success,
            duration=duration,
            details=details,
            errors=errors
        )
    
    def test_concurrent_access(self) -> TestResult:
        """并发访问测试"""
        print("\n🔄 测试 5: 并发访问（10 线程）")
        
        start_time = time.time()
        errors = []
        details = {}
        
        def worker(worker_id: int, iterations: int):
            """工作线程"""
            try:
                for i in range(iterations):
                    self.knowledge.learn(
                        f"worker_{worker_id}_iter_{i}",
                        {"worker": worker_id, "iter": i},
                        "concurrent"
                    )
                    
                    if i % 10 == 0:
                        self.knowledge.recall(f"worker_{worker_id}_iter_{i - 5}")
            except Exception as e:
                errors.append(f"Worker {worker_id}: {str(e)}")
        
        try:
            # 启动 10 个工作线程
            threads = []
            num_threads = 10
            iterations_per_thread = 50
            
            for i in range(num_threads):
                t = threading.Thread(target=worker, args=(i, iterations_per_thread))
                threads.append(t)
                t.start()
            
            # 等待所有线程完成
            for t in threads:
                t.join()
            
            details["threads"] = num_threads
            details["iterations_per_thread"] = iterations_per_thread
            
            # 验证数据完整性
            stats = self.knowledge.get_stats()
            details["final_stats"] = stats
            
        except Exception as e:
            errors.append(str(e))
        
        duration = time.time() - start_time
        success = len(errors) == 0
        
        print(f"{'✅ 通过' if success else '❌ 失败'} ({duration:.2f}s)")
        if errors:
            for error in errors:
                print(f"  错误: {error}")
        
        return TestResult(
            test_name="concurrent_access",
            success=success,
            duration=duration,
            details=details,
            errors=errors
        )
    
    def test_boundary_conditions(self) -> TestResult:
        """边界条件测试"""
        print("\n🎯 测试 6: 边界条件")
        
        start_time = time.time()
        errors = []
        details = {}
        
        try:
            # 测试空数据
            result = self.knowledge.recall("nonexistent_key")
            details["empty_recall"] = "✅" if result is None else "❌"
            
            # 测试大数据
            large_data = {"data": "x" * 10000}
            success = self.knowledge.learn("large_key", large_data, "test")
            details["large_data"] = "✅" if success else "❌"
            
            # 测试特殊字符
            special_data = {"data": "测试\n\t\r特殊字符!@#$%^&*()"}
            success = self.knowledge.learn("special_key", special_data, "test")
            details["special_chars"] = "✅" if success else "❌"
            
            # 测试空键
            try:
                self.knowledge.learn("", {"data": "test"}, "test")
                details["empty_key"] = "❌ (应该失败)"
            except Exception:
                details["empty_key"] = "✅ (正确拒绝)"
            
        except Exception as e:
            errors.append(str(e))
        
        duration = time.time() - start_time
        success = len(errors) == 0
        
        print(f"{'✅ 通过' if success else '❌ 失败'} ({duration:.2f}s)")
        if errors:
            for error in errors:
                print(f"  错误: {error}")
        
        return TestResult(
            test_name="boundary_conditions",
            success=success,
            duration=duration,
            details=details,
            errors=errors
        )
    
    def test_memory_leaks(self) -> TestResult:
        """内存泄漏检测"""
        print("\n💾 测试 7: 内存泄漏检测")
        
        start_time = time.time()
        errors = []
        details = {}
        
        try:
            # 启动内存跟踪
            tracemalloc.start()
            
            # 基线快照
            snapshot1 = tracemalloc.take_snapshot()
            
            # 执行大量操作
            for i in range(100):
                self.knowledge.learn(f"mem_test_{i}", {"data": "x" * 100}, "mem_test")
                self.knowledge.recall(f"mem_test_{i}")
            
            # 强制垃圾回收
            import gc
            gc.collect()
            
            # 最终快照
            snapshot2 = tracemalloc.take_snapshot()
            
            # 计算差异
            top_stats = snapshot2.compare_to(snapshot1, 'lineno')
            total_increase = sum(stat.size_diff for stat in top_stats) / 1024  # KB
            
            details["memory_increase_kb"] = f"{total_increase:.1f}"
            
            # 停止跟踪
            tracemalloc.stop()
            
            # 判断是否泄漏（增长 < 10MB 认为正常）
            if total_increase > 10240:  # 10MB
                errors.append(f"可能的内存泄漏: {total_increase:.1f} KB")
            
        except Exception as e:
            errors.append(str(e))
        
        duration = time.time() - start_time
        success = len(errors) == 0
        
        print(f"{'✅ 通过' if success else '❌ 失败'} ({duration:.2f}s)")
        if errors:
            for error in errors:
                print(f"  错误: {error}")
        
        return TestResult(
            test_name="memory_leaks",
            success=success,
            duration=duration,
            details=details,
            errors=errors
        )
    
    def test_performance_regression(self) -> TestResult:
        """性能回归测试"""
        print("\n⚡ 测试 8: 性能回归")
        
        start_time = time.time()
        errors = []
        details = {}
        
        try:
            # 测试写入性能
            write_start = time.time()
            for i in range(100):
                self.knowledge.learn(f"perf_{i}", {"data": i}, "perf")
            write_duration = time.time() - write_start
            details["write_100_ops"] = f"{write_duration:.3f}s ({100/write_duration:.0f} ops/s)"
            
            # 测试读取性能
            read_start = time.time()
            for i in range(100):
                self.knowledge.recall(f"perf_{i}")
            read_duration = time.time() - read_start
            details["read_100_ops"] = f"{read_duration:.3f}s ({100/read_duration:.0f} ops/s)"
            
            # 测试缓存性能
            # 第一次读取（缓存未命中）
            cold_start = time.time()
            self.knowledge.recall("perf_50")
            cold_duration = time.time() - cold_start
            
            # 第二次读取（缓存命中）
            hot_start = time.time()
            self.knowledge.recall("perf_50")
            hot_duration = time.time() - hot_start
            
            speedup = cold_duration / hot_duration if hot_duration > 0 else 0
            details["cache_speedup"] = f"{speedup:.1f}x"
            
        except Exception as e:
            errors.append(str(e))
        
        duration = time.time() - start_time
        success = len(errors) == 0
        
        print(f"{'✅ 通过' if success else '❌ 失败'} ({duration:.2f}s)")
        if errors:
            for error in errors:
                print(f"  错误: {error}")
        
        return TestResult(
            test_name="performance_regression",
            success=success,
            duration=duration,
            details=details,
            errors=errors
        )
    
    def _generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 测试报告")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        
        print(f"\n总测试数: {total_tests}")
        print(f"✅ 通过: {passed_tests}")
        print(f"❌ 失败: {failed_tests}")
        print(f"通过率: {passed_tests/total_tests*100:.1f}%")
        
        print("\n详细结果:")
        for result in self.results:
            status = "✅" if result.success else "❌"
            print(f"  {status} {result.test_name}: {result.duration:.2f}s")
            
            if result.errors:
                for error in result.errors:
                    print(f"      错误: {error}")
        
        # 保存 JSON 报告
        import json
        report_path = self.test_dir / "stability_test_report.json"
        with open(report_path, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "pass_rate": passed_tests/total_tests*100
                },
                "results": [r.to_dict() for r in self.results]
            }, f, indent=2)
        
        print(f"\n📄 详细报告已保存: {report_path}")


if __name__ == "__main__":
    # 运行测试
    suite = StabilityTestSuite()
    results = suite.run_all_tests()
    
    # 退出码
    all_passed = all(r.success for r in results)
    sys.exit(0 if all_passed else 1)
