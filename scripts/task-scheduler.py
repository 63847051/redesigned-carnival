#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后台任务调度器
- 自动记忆压缩
- 自动记忆分层
- 自动缓存清理
- 自动性能优化
"""

import os
import sys
import time
import json
import shutil
import schedule
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
MEMORY_KEY_POINTS = MEMORY_DIR / "key-points"
MEMORY_STRUCTURED = MEMORY_DIR / "structured"
LOG_FILE = MEMORY_DIR / ".scheduler.log"
TASKS_FILE = MEMORY_DIR / ".tasks.json"

# 颜色输出
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    RED = '\033[0;31m'
    NC = '\033[0m'

def log(message: str, level: str = "INFO"):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}"
    print(log_line)

    # 写入日志文件
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except Exception as e:
        print(f"写入日志失败: {e}")

# ============================================================================
# 任务 1: 自动记忆压缩
# ============================================================================

def task_compress_memory():
    """自动记忆压缩"""
    log("开始执行：记忆压缩", "INFO")

    try:
        # 压缩昨天的记忆
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        compressor_script = WORKSPACE / "scripts" / "memory-compressor.sh"

        if not compressor_script.exists():
            log(f"压缩脚本不存在: {compressor_script}", "ERROR")
            return False

        # 执行压缩脚本
        result = subprocess.run(
            ["bash", str(compressor_script), yesterday],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            log(f"✓ 记忆压缩成功: {yesterday}", "INFO")
            return True
        else:
            log(f"✗ 记忆压缩失败: {result.stderr}", "ERROR")
            return False

    except Exception as e:
        log(f"✗ 记忆压缩异常: {e}", "ERROR")
        return False

# ============================================================================
# 任务 2: 自动记忆分层
# ============================================================================

def task_layer_memory():
    """自动记忆分层"""
    log("开始执行：记忆分层", "INFO")

    try:
        # 检查最近 3 天的记忆是否需要分层
        for i in range(1, 4):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            daily_file = MEMORY_DIR / f"{date}.md"

            if not daily_file.exists():
                continue

            # 检查是否已经分层
            month = date[:7]
            key_points_file = MEMORY_KEY_POINTS / f"{month}.md"

            if not key_points_file.exists():
                log(f"需要分层: {date}", "INFO")

                # 执行迁移脚本（只分层，不覆盖）
                migrate_script = WORKSPACE / "scripts" / "memory-migrate.sh"

                result = subprocess.run(
                    ["bash", str(migrate_script)],
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                if result.returncode == 0:
                    log(f"✓ 记忆分层成功: {date}", "INFO")
                else:
                    log(f"✗ 记忆分层失败: {result.stderr}", "ERROR")
                    return False

        log("✓ 记忆分层检查完成", "INFO")
        return True

    except Exception as e:
        log(f"✗ 记忆分层异常: {e}", "ERROR")
        return False

# ============================================================================
# 任务 3: 自动缓存清理
# ============================================================================

def task_cleanup_cache():
    """自动缓存清理"""
    log("开始执行：缓存清理", "INFO")

    try:
        # 清理 30 天前的临时文件
        temp_files = [
            MEMORY_DIR / ".write_buffer.json",
            MEMORY_DIR / ".write_queue.json",
        ]

        cleaned = 0
        for temp_file in temp_files:
            if temp_file.exists():
                # 检查文件修改时间
                mtime = temp_file.stat().st_mtime
                age = time.time() - mtime

                # 超过 30 天，删除
                if age > 30 * 24 * 3600:
                    temp_file.unlink()
                    cleaned += 1
                    log(f"删除过期文件: {temp_file.name}", "INFO")

        # 清理空的分类文件
        for category_dir in MEMORY_STRUCTURED.glob("*"):
            if category_dir.is_dir():
                for empty_file in category_dir.glob("*.md"):
                    if empty_file.stat().st_size == 0:
                        empty_file.unlink()
                        cleaned += 1
                        log(f"删除空文件: {empty_file.name}", "INFO")

        log(f"✓ 缓存清理完成: 清理 {cleaned} 个文件", "INFO")
        return True

    except Exception as e:
        log(f"✗ 缓存清理异常: {e}", "ERROR")
        return False

# ============================================================================
# 任务 4: 自动摘要生成
# ============================================================================

def task_auto_summary():
    """自动摘要生成"""
    log("开始执行：自动摘要生成", "INFO")

    try:
        auto_summary_script = WORKSPACE / "scripts" / "auto-summary.sh"

        if not auto_summary_script.exists():
            log(f"自动摘要脚本不存在: {auto_summary_script}", "ERROR")
            return False

        # 执行自动摘要生成
        result = subprocess.run(
            ["bash", str(auto_summary_script)],
            capture_output=True,
            text=True,
            timeout=300  # 5 分钟超时
        )

        if result.returncode == 0:
            log(f"✓ 自动摘要生成成功", "INFO")
            return True
        else:
            log(f"✗ 自动摘要生成失败: {result.stderr}", "ERROR")
            return False

    except Exception as e:
        log(f"✗ 自动摘要生成异常: {e}", "ERROR")
        return False

# ============================================================================
# 任务 5: 自动性能优化
# ============================================================================

def task_optimize_performance():
    """自动性能优化"""
    log("开始执行：性能优化", "INFO")

    try:
        # 1. 更新 QMD 索引
        log("更新 QMD 索引...", "INFO")
        result = subprocess.run(
            ["qmd", "update"],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            log("✓ QMD 索引更新成功", "INFO")
        else:
            log(f"✗ QMD 索引更新失败: {result.stderr}", "ERROR")

        # 2. 生成 embeddings
        log("生成 embeddings...", "INFO")
        result = subprocess.run(
            ["qmd", "embed"],
            capture_output=True,
            text=True,
            timeout=300  # 增加到 5 分钟
        )

        if result.returncode == 0:
            log("✓ Embeddings 生成成功", "INFO")
        else:
            log(f"✗ Embeddings 生成失败: {result.stderr}", "ERROR")

        # 3. 清理日志文件（保留最近 7 天）
        log_file = MEMORY_DIR / ".scheduler.log"
        if log_file.exists():
            # 读取日志文件
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # 只保留最近 7 天的日志
            cutoff_time = datetime.now() - timedelta(days=7)
            filtered_lines = []

            for line in lines:
                try:
                    # 提取时间戳
                    timestamp_str = line.split("]")[0].split("[")[1]
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

                    if timestamp > cutoff_time:
                        filtered_lines.append(line)
                except:
                    # 无法解析时间，保留
                    filtered_lines.append(line)

            # 写回文件
            with open(log_file, "w", encoding="utf-8") as f:
                f.writelines(filtered_lines)

            log("✓ 日志清理完成", "INFO")

        log("✓ 性能优化完成", "INFO")
        return True

    except Exception as e:
        log(f"✗ 性能优化异常: {e}", "ERROR")
        return False

# ============================================================================
# 任务调度
# ============================================================================

def setup_schedule():
    """设置任务调度"""
    log("设置任务调度...", "INFO")

    # 每天凌晨 1 点：自动摘要生成
    schedule.every().day.at("01:00").do(task_auto_summary)

    # 每天凌晨 2 点：记忆压缩
    schedule.every().day.at("02:00").do(task_compress_memory)

    # 每天凌晨 3 点：记忆分层
    schedule.every().day.at("03:00").do(task_layer_memory)

    # 每周日凌晨 4 点：缓存清理
    schedule.every().sunday.at("04:00").do(task_cleanup_cache)

    # 每周日凌晨 5 点：性能优化
    schedule.every().sunday.at("05:00").do(task_optimize_performance)

    log("✓ 任务调度设置完成", "INFO")
    log("  - 自动摘要生成: 每天 01:00", "INFO")
    log("  - 记忆压缩: 每天 02:00", "INFO")
    log("  - 记忆分层: 每天 03:00", "INFO")
    log("  - 缓存清理: 每周日 04:00", "INFO")
    log("  - 性能优化: 每周日 05:00", "INFO")

def run_scheduler():
    """运行调度器"""
    log("启动任务调度器...", "INFO")
    log(f"{Colors.GREEN}调度器已启动，按 Ctrl+C 停止{Colors.NC}", "INFO")

    # 设置调度
    setup_schedule()

    # 主循环
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        log(f"\n{Colors.YELLOW}收到停止信号，正在退出...{Colors.NC}", "INFO")
        log("任务调度器已停止", "INFO")

# ============================================================================
# CLI 接口
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="后台任务调度器")
    parser.add_argument("action", choices=["start", "run", "test"],
                       help="操作: start(启动), run(立即运行), test(测试任务)")

    parser.add_argument("--task", choices=["summary", "compress", "layer", "cleanup", "optimize"],
                       help="测试任务: summary(摘要), compress(压缩), layer(分层), cleanup(清理), optimize(优化)")

    args = parser.parse_args()

    if args.action == "start":
        # 启动调度器
        run_scheduler()

    elif args.action == "run":
        # 立即运行所有任务
        log("立即运行所有任务...", "INFO")

        tasks = [
            ("自动摘要生成", task_auto_summary),
            ("记忆压缩", task_compress_memory),
            ("记忆分层", task_layer_memory),
            ("缓存清理", task_cleanup_cache),
            ("性能优化", task_optimize_performance),
        ]

        results = {}
        for name, task in tasks:
            log(f"执行任务: {name}", "INFO")
            results[name] = task()
            time.sleep(1)

        # 输出结果
        log("\n" + "="*50, "INFO")
        log("任务执行结果:", "INFO")
        for name, result in results.items():
            status = f"{Colors.GREEN}✓{Colors.NC}" if result else f"{Colors.RED}✗{Colors.NC}"
            log(f"  {status} {name}", "INFO")

    elif args.action == "test":
        # 测试单个任务
        if not args.task:
            print("请指定 --task 参数")
            sys.exit(1)

        log(f"测试任务: {args.task}", "INFO")

        if args.task == "summary":
            task_auto_summary()
        elif args.task == "compress":
            task_compress_memory()
        elif args.task == "layer":
            task_layer_memory()
        elif args.task == "cleanup":
            task_cleanup_cache()
        elif args.task == "optimize":
            task_optimize_performance()
