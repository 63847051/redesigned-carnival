#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
两阶段审查系统 - Phase 1: 规范合规性, Phase 2: 代码质量
"""

import json
import re
from typing import Dict, List


class TwoPhaseReviewer:
    """两阶段审查器"""
    
    def __init__(self):
        self.critical_issues = []
        self.major_issues = []
        self.minor_issues = []
    
    def review(self, plan: Dict, code: str, files: List[str]) -> Dict:
        """
        两阶段审查
        
        Args:
            plan: 实施计划
            code: 代码内容
            files: 文件列表
        
        Returns:
            审查结果
        """
        print(f"\n🔍 两阶段审查")
        print("="*60)
        
        # Phase 1: 规范合规性审查
        print("\nPhase 1: 规范合规性审查")
        phase1_result = self._phase1_compliance(plan, files)
        
        # Phase 2: 代码质量审查
        print("\nPhase 2: 代码质量审查")
        phase2_result = self._phase2_quality(code, files)
        
        # 判断是否通过
        passed = self._should_pass(phase1_result, phase2_result)
        
        result = {
            "phase1": phase1_result,
            "phase2": phase2_result,
            "passed": passed,
            "critical_issues": self.critical_issues,
            "major_issues": self.major_issues,
            "minor_issues": self.minor_issues
        }
        
        return result
    
    def _phase1_compliance(self, plan: Dict, files: List[str]) -> Dict:
        """Phase 1: 规范合规性审查"""
        print("   检查规范合规性...")
        
        issues = []
        
        # 检查 1: 文件是否按计划创建
        planned_files = set(plan.get("files", []))
        actual_files = set(files)
        
        missing_files = planned_files - actual_files
        extra_files = actual_files - planned_files
        
        if missing_files:
            for f in missing_files:
                issues.append({
                    "severity": "major",
                    "type": "missing_file",
                    "message": f"缺少文件: {f}"
                })
        
        if extra_files:
            for f in extra_files:
                issues.append({
                    "severity": "minor",
                    "type": "extra_file",
                    "message": f"额外文件: {f}"
                })
        
        # 检查 2: 是否遵循 TDD
        test_files = [f for f in files if f.endswith("_test.py") or "test" in f]
        source_files = [f for f in files if not f.endswith("_test.py") and "test" not in f]
        
        if source_files and not test_files:
            issues.append({
                "severity": "major",
                "type": "no_tests",
                "message": "没有测试文件，违反 TDD 原则"
            })
        
        # 检查 3: 是否有验证步骤
        verification = plan.get("verification", [])
        if not verification:
            issues.append({
                "severity": "minor",
                "type": "no_verification",
                "message": "计划中没有验证步骤"
            })
        
        print(f"   发现 {len(issues)} 个问题")
        
        return {
            "issues": issues,
            "passed": len([i for i in issues if i["severity"] == "critical"]) == 0
        }
    
    def _phase2_quality(self, code: str, files: List[str]) -> Dict:
        """Phase 2: 代码质量审查"""
        print("   检查代码质量...")
        
        issues = []
        
        # 检查 1: 代码长度
        if len(code) > 1000:
            issues.append({
                "severity": "minor",
                "type": "long_file",
                "message": f"代码过长 ({len(code)} 字符)，建议拆分"
            })
        
        # 检查 2: TODO 注释
        todo_count = code.count("TODO")
        if todo_count > 3:
            issues.append({
                "severity": "minor",
                "type": "many_todos",
                "message": f"有 {todo_count} 个 TODO，建议清理"
            })
        
        # 检查 3: print 语句
        print_count = code.count("print(")
        if print_count > 5:
            issues.append({
                "severity": "minor",
                "type": "many_prints",
                "message": f"有 {print_count} 个 print 语句，建议使用日志"
            })
        
        # 检查 4: 异常处理
        if "try:" in code and "except" not in code:
            issues.append({
                "severity": "major",
                "type": "no_exception_handling",
                "message": "有 try 但没有 except"
            })
        
        print(f"   发现 {len(issues)} 个问题")
        
        return {
            "issues": issues,
            "passed": len([i for i in issues if i["severity"] == "critical"]) == 0
        }
    
    def _should_pass(self, phase1: Dict, phase2: Dict) -> bool:
        """判断是否通过"""
        phase1_critical = len([i for i in phase1["issues"] if i["severity"] == "critical"])
        phase2_critical = len([i for i in phase2["issues"] if i["severity"] == "critical"])
        
        if phase1_critical > 0 or phase2_critical > 0:
            print("\n❌ 审查不通过：发现 Critical 问题")
            return False
        
        phase1_major = len([i for i in phase1["issues"] if i["severity"] == "major"])
        phase2_major = len([i for i in phase2["issues"] if i["severity"] == "major"])
        
        if phase1_major > 2 or phase2_major > 2:
            print("\n⚠️  审查警告：发现多个 Major 问题")
            return False
        
        print("\n✅ 审查通过！")
        return True
    
    def generate_report(self, result: Dict) -> str:
        """生成审查报告"""
        report = []
        report.append("="*60)
        report.append("🔍 两阶段审查报告")
        report.append("="*60)
        
        # Phase 1 结果
        report.append("\nPhase 1: 规范合规性")
        report.append("-"*40)
        if result["phase1"]["issues"]:
            for issue in result["phase1"]["issues"]:
                icon = "🔴" if issue["severity"] == "critical" else "🟡" if issue["severity"] == "major" else "🟢"
                report.append(f"{icon} {issue['type']}: {issue['message']}")
        else:
            report.append("✅ 无问题")
        
        # Phase 2 结果
        report.append("\nPhase 2: 代码质量")
        report.append("-"*40)
        if result["phase2"]["issues"]:
            for issue in result["phase2"]["issues"]:
                icon = "🔴" if issue["severity"] == "critical" else "🟡" if issue["severity"] == "major" else "🟢"
                report.append(f"{icon} {issue['type']}: {issue['message']}")
        else:
            report.append("✅ 无问题")
        
        # 总结
        report.append("\n" + "="*60)
        if result["passed"]:
            report.append("✅ 审查通过！")
        else:
            report.append("❌ 审查不通过！")
        report.append("="*60)
        
        return "\n".join(report)


# ============================================================================
# 主流程
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="两阶段审查系统")
    parser.add_argument("--test", action="store_true", help="测试示例")
    
    args = parser.parse_args()
    
    reviewer = TwoPhaseReviewer()
    
    if args.test:
        # 测试示例
        print("="*60)
        print("🧪 两阶段审查测试")
        print("="*60)
        
        # 模拟计划
        plan = {
            "files": ["main.py", "utils.py", "test_main.py"],
            "verification": ["运行测试", "检查输出"]
        }
        
        # 模拟代码
        code = """
def main():
    print("Hello, World!")
    # TODO: 添加错误处理
    # TODO: 添加日志
    return True
"""
        
        # 模拟文件
        files = ["main.py", "utils.py", "test_main.py"]
        
        # 审查
        result = reviewer.review(plan, code, files)
        
        # 生成报告
        print(reviewer.generate_report(result))
        
        print("\n" + "="*60)
        print("✅ 测试完成")
    
    else:
        print("用法:")
        print("  python3 two-phase-reviewer.py --test  # 测试示例")
        print("\n说明:")
        print("  Phase 1: 规范合规性审查")
        print("  Phase 2: 代码质量审查")
        print("  Critical 问题阻止进度")
