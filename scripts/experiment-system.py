#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动实验系统 - A/B 测试，数据驱动改进
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
EXPERIMENTS_FILE = WORKSPACE / ".learnings" / "experiments.json"


class ExperimentSystem:
    """自动实验系统"""
    
    def __init__(self):
        self.experiments = self._load_experiments()
    
    def _load_experiments(self) -> List[Dict]:
        """加载实验记录"""
        if EXPERIMENTS_FILE.exists():
            try:
                with open(EXPERIMENTS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        
        return []
    
    def design_experiment(self, hypothesis: str, metrics: List[str]) -> Dict:
        """设计实验"""
        print(f"\n🎯 设计实验: {hypothesis}")
        
        experiment = {
            "id": f"exp-{int(time.time())}",
            "hypothesis": hypothesis,
            "metrics": metrics,
            "created_at": datetime.now().isoformat(),
            "status": "designed",
            "results": None
        }
        
        self.experiments.append(experiment)
        self._save()
        
        print(f"✅ 实验已设计: {experiment['id']}")
        print(f"   假设: {hypothesis}")
        print(f"   指标: {', '.join(metrics)}")
        
        return experiment
    
    def run_experiment(self, experiment_id: str, test_func: callable) -> Dict:
        """运行实验"""
        print(f"\n🔬 运行实验: {experiment_id}")
        
        # 查找实验
        experiment = next((e for e in self.experiments if e["id"] == experiment_id), None)
        if not experiment:
            print(f"❌ 未找到实验: {experiment_id}")
            return None
        
        try:
            # 运行测试函数
            print("   运行测试...")
            start_time = time.time()
            results = test_func()
            elapsed = time.time() - start_time
            
            # 更新实验结果
            experiment["results"] = results
            experiment["elapsed_time"] = elapsed
            experiment["status"] = "completed"
            experiment["completed_at"] = datetime.now().isoformat()
            
            self._save()
            
            print(f"✅ 实验完成")
            print(f"   耗时: {elapsed:.2f}秒")
            
            # 分析结果
            self._analyze_results(experiment)
            
            return experiment
            
        except Exception as e:
            experiment["status"] = "failed"
            experiment["error"] = str(e)
            experiment["failed_at"] = datetime.now().isoformat()
            self._save()
            
            print(f"❌ 实验失败: {e}")
            return None
    
    def _analyze_results(self, experiment: Dict):
        """分析实验结果"""
        print(f"\n📊 分析结果...")
        
        results = experiment.get("results", {})
        metrics = experiment.get("metrics", [])
        
        improvements = []
        regressions = []
        
        for metric in metrics:
            if metric in results:
                before = results[metric].get("before")
                after = results[metric].get("after")
                
                if before is not None and after is not None:
                    if after > before:
                        improvement = ((after - before) / before) * 100
                        improvements.append(f"{metric}: +{improvement:.1f}%")
                    elif after < before:
                        regression = ((before - after) / before) * 100
                        regressions.append(f"{metric}: {regression:.1f}%")
        
        if improvements:
            print(f"   ✅ 提升: {', '.join(improvements)}")
        
        if regressions:
            print(f"   ⚠️ 退步: {', '.join(regressions)}")
        
        # 结论
        if improvements and not regressions:
            conclusion = "建议采用"
            experiment["conclusion"] = "accept"
        elif regressions and not improvements:
            conclusion = "不建议采用"
            experiment["conclusion"] = "reject"
        else:
            conclusion = "需要进一步分析"
            experiment["conclusion"] = "inconclusive"
        
        print(f"   结论: {conclusion}")
        
        experiment["conclusion"] = conclusion
        self._save()
    
    def _save(self):
        """保存实验记录"""
        EXPERIMENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(EXPERIMENTS_FILE, "w", encoding="utf-8 -->") as f:
            json.dump(self.experiments, f, indent=2, ensure_ascii=False)
    
    def generate_report(self) -> str:
        """生成实验报告"""
        report = []
        report.append("="*60)
        report.append("🔬 自动实验系统报告")
        report.append("="*60)
        
        if not self.experiments:
            report.append("\n⏳ 暂无实验记录")
        else:
            for i, exp in enumerate(self.experiments, 1):
                status_icon = "✅" if exp["status"] == "completed" else "⏳" if exp["status"] == "designed" else "❌"
                
                report.append(f"\n{i}. {status_icon} {exp['id']}")
                report.append(f"   假设: {exp['hypothesis']}")
                report.append(f"   状态: {exp['status']}")
                
                if exp.get("conclusion"):
                    report.append(f"   结论: {exp['conclusion']}")
                
                if exp.get("results"):
                    report.append(f"   结果: {json.dumps(exp['results'], ensure_ascii=False)}")
        
        report.append(f"\n{'='*60}")
        
        return "\n".join(report)


# ============================================================================
# 主流程
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse(description="自动实验系统")
    parser.add_argument("--design", help="设计实验")
    parser.add_argument("--run", help="运行实验")
    parser.add_argument("--report", action="store_true", help="显示实验报告")
    
    args = parser.parse_args()
    
    system = ExperimentSystem()
    
    if args.design:
        # 设计实验
        hypothesis = args.design
        
        # 示例：设计一个实验
        if hypothesis == "example":
            system.design_experiment(
                hypothesis="智能确认能减少对话轮次",
                metrics=["对话轮次", "用户满意度"]
            )
        else:
            system.design_experiment(
                hypothesis=hypothesis,
                metrics=["性能", "准确率", "用户满意度"]
            )
    
    elif args.run:
        # 运行实验
        experiment_id = args.run
        
        # 示例：运行一个测试实验
        if experiment_id == "example":
            def test_func():
                return {
                    "对话轮次": {"before": 10, "after": 7},
                    "用户满意度": {"before": 70, "after": 80}
                }
            
            system.run_experiment(experiment_id, test_func)
        else:
            print("请提供实验 ID")
    
    elif args.report:
        # 显示报告
        print(system.generate_report())
    
    else:
        print("用法:")
        print("  python3 experiment-system.py --design \"假设描述\"")
        print("  python3 experiment-system.py --run <实验ID>")
        print("  python3 experiment-system.py --report")
        print("\n示例:")
        print("  python3 experiment-system.py --design example")
        print("  python3 experiment-system.py --run example")
        print("  python3 experiment-system.py --report")
