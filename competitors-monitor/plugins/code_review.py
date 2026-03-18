#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码审查自动化插件
使用 GitHub API 获取 PR、Issue、Workflow 状态
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any


class GitHubPlugin:
    """GitHub 数据源插件"""

    def __init__(self):
        try:
            import requests

            self.requests = requests
        except ImportError:
            raise ImportError("请安装依赖: pip3 install requests")

    def fetch(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """抓取 GitHub 数据"""
        results = []

        github_config = config.get("github", {})
        token = github_config.get("token", os.environ.get("GITHUB_TOKEN"))

        if not token or token == "YOUR_GITHUB_TOKEN_HERE":
            results.append(
                {
                    "source": "github",
                    "error": "未配置 GitHub Token",
                    "timestamp": datetime.now().isoformat(),
                }
            )
            return results

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Code-Review-Monitor/1.0",
        }

        for target in config.get("targets", []):
            owner = target.get("owner")
            repo = target.get("repo")

            if not owner or not repo:
                continue

            base_url = f"https://api.github.com/repos/{owner}/{repo}"

            if target.get("monitor_prs", True):
                prs = self._fetch_pull_requests(base_url, headers, config)
                results.extend(prs)

            if target.get("monitor_issues", True):
                issues = self._fetch_issues(base_url, headers, config)
                results.extend(issues)

            if target.get("monitor_workflows", True):
                workflows = self._fetch_workflows(base_url, headers)
                results.extend(workflows)

        return results

    def _fetch_pull_requests(
        self, base_url: str, headers: Dict, config: Dict
    ) -> List[Dict]:
        """获取 PR 列表"""
        results = []

        try:
            url = f"{base_url}/pulls"
            params = {"state": "open", "sort": "updated", "per_page": 20}
            response = self.requests.get(
                url, headers=headers, params=params, timeout=30
            )
            response.raise_for_status()

            prs = response.json()
            check_rules = config.get("check_rules", {})
            pr_age_threshold = check_rules.get("pr_age_threshold_days", 3)

            for pr in prs:
                created_at = datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                age_days = (datetime.now() - created_at).days

                pr_result = {
                    "source": "github_pr",
                    "type": "pull_request",
                    "number": pr["number"],
                    "title": pr["title"],
                    "state": pr["state"],
                    "user": pr["user"]["login"],
                    "created_at": pr["created_at"],
                    "age_days": age_days,
                    "url": pr["html_url"],
                    "review_status": self._get_review_status(pr),
                    "labels": [l["name"] for l in pr.get("labels", [])],
                    "is_overdue": age_days > pr_age_threshold,
                    "timestamp": datetime.now().isoformat(),
                }

                if pr_result["is_overdue"]:
                    pr_result["alert"] = (
                        f"PR 已开放 {age_days} 天，超过阈值 {pr_age_threshold} 天"
                    )

                results.append(pr_result)

        except Exception as e:
            results.append(
                {
                    "source": "github_pr",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return results

    def _fetch_issues(self, base_url: str, headers: Dict, config: Dict) -> List[Dict]:
        """获取 Issue 列表"""
        results = []

        try:
            url = f"{base_url}/issues"
            params = {"state": "open", "sort": "updated", "per_page": 20}
            response = self.requests.get(
                url, headers=headers, params=params, timeout=30
            )
            response.raise_for_status()

            issues = response.json()

            for issue in issues:
                if "pull_request" in issue:
                    continue

                created_at = datetime.strptime(
                    issue["created_at"], "%Y-%m-%dT%H:%M:%SZ"
                )
                age_days = (datetime.now() - created_at).days

                results.append(
                    {
                        "source": "github_issue",
                        "type": "issue",
                        "number": issue["number"],
                        "title": issue["title"],
                        "state": issue["state"],
                        "user": issue["user"]["login"],
                        "created_at": issue["created_at"],
                        "age_days": age_days,
                        "url": issue["html_url"],
                        "labels": [l["name"] for l in issue.get("labels", [])],
                        "comments_count": issue.get("comments", 0),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        except Exception as e:
            results.append(
                {
                    "source": "github_issue",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return results

    def _fetch_workflows(self, base_url: str, headers: Dict) -> List[Dict]:
        """获取 Workflow 运行状态"""
        results = []

        try:
            url = f"{base_url}/actions/runs"
            params = {"per_page": 10}
            response = self.requests.get(
                url, headers=headers, params=params, timeout=30
            )
            response.raise_for_status()

            runs = response.json().get("workflow_runs", [])

            for run in runs:
                results.append(
                    {
                        "source": "github_workflow",
                        "type": "workflow",
                        "name": run.get("name", "Unknown"),
                        "status": run.get("status"),
                        "conclusion": run.get("conclusion"),
                        "branch": run.get("head_branch"),
                        "url": run.get("html_url"),
                        "created_at": run.get("created_at"),
                        "updated_at": run.get("updated_at"),
                        "actor": run.get("actor", {}).get("login"),
                        "is_failed": run.get("conclusion") == "failure",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        except Exception as e:
            results.append(
                {
                    "source": "github_workflow",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return results

    def _get_review_status(self, pr: Dict) -> str:
        """获取 PR 审查状态"""
        review_state = pr.get("draft", True) and "draft" or "ready"

        if pr.get("mergeable_state") == "blocked":
            review_state = "blocked"
        elif pr.get("mergeable_state") == "clean":
            review_state = "approved"

        return review_state

    def validate(self, data: List[Dict[str, Any]]) -> bool:
        """验证数据"""
        return len(data) > 0


class CodeReviewMonitor:
    """代码审查监控器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.plugin = GitHubPlugin()

    def fetch(self) -> List[Dict[str, Any]]:
        """抓取数据"""
        return self.plugin.fetch(self.config)

    def analyze(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """分析代码审查状态"""
        alerts = []

        for item in data:
            if item.get("type") == "pull_request":
                if item.get("is_overdue"):
                    alerts.append(
                        {
                            "type": "pr_overdue",
                            "severity": "warning",
                            "number": item.get("number"),
                            "title": item.get("title"),
                            "user": item.get("user"),
                            "age_days": item.get("age_days"),
                            "url": item.get("url"),
                            "message": f"PR #{item.get('number')} 已开放 {item.get('age_days')} 天未合并",
                        }
                    )

            elif item.get("type") == "workflow":
                if item.get("is_failed"):
                    alerts.append(
                        {
                            "type": "workflow_failed",
                            "severity": "error",
                            "name": item.get("name"),
                            "branch": item.get("branch"),
                            "url": item.get("url"),
                            "message": f"Workflow '{item.get('name')}' 在 {item.get('branch')} 分支执行失败",
                        }
                    )

        return alerts


def run_monitor():
    """运行代码审查监控"""
    import sys

    config_path = "config/code-review.json"

    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    monitor = CodeReviewMonitor(config)
    data = monitor.fetch()
    alerts = monitor.analyze(data)

    print(f"获取到 {len(data)} 条数据")
    print(f"发现 {len(alerts)} 个告警")

    for alert in alerts:
        print(f"  [{alert['severity'].upper()}] {alert['message']}")

    return data, alerts


if __name__ == "__main__":
    run_monitor()
