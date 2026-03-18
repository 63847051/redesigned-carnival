# 代码审查自动化 - 使用指南

## 概述

代码审查自动化监控 GitHub 仓库的 PR 状态、Issue 进度、Workflow 执行情况，及时发现延迟和问题。

## 功能特性

- **PR 监控**: 跟踪开放 PR 的状态、年龄、审查进度
- **Issue 监控**: 跟踪开放 Issue 的处理进度
- **Workflow 监控**: 监控 CI/CD 执行状态，失败告警
- **逾期告警**: 自动识别长期未处理的 PR

## 配置说明

编辑 `config/code-review.json`:

```json
{
  "github": {
    "token": "YOUR_GITHUB_TOKEN_HERE",
    "owner": "your-org",
    "repo": "your-repo"
  },
  "targets": [
    {
      "name": "主仓库",
      "owner": "your-org",
      "repo": "your-repo",
      "monitor_prs": true,
      "monitor_issues": true,
      "monitor_workflows": true
    }
  ],
  "check_rules": {
    "pr_age_threshold_days": 3,
    "required_reviewers": 2,
    "workflow_failure_alert": true
  }
}
```

## 获取 GitHub Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选 `repo` 权限
4. 生成并复制 Token

## 运行方式

```bash
# 使用 Python 直接运行
cd /root/.openclaw/workspace/competitors-monitor
python3 plugins/code_review.py

# 或指定配置文件
python3 plugins/code_review.py config/code-review.json
```

## 环境变量

也可以通过环境变量配置 GitHub Token:

```bash
export GITHUB_TOKEN=your_token_here
python3 plugins/code_review.py
```

## 输出示例

```
获取到 15 条数据
发现 3 个告警
  [WARNING] PR #123 已开放 5 天未合并
  [ERROR] Workflow 'CI' 在 main 分支执行失败
  [WARNING] PR #456 已开放 4 天未合并
```

## 告警类型

| 类型 | 严重程度 | 说明 |
|------|----------|------|
| pr_overdue | warning | PR 开放时间超过阈值 |
| workflow_failed | error | Workflow 执行失败 |
| new_comments | info | PR 有新评论 |

## 集成通知

在配置中设置飞书 webhook 即可接收告警:

```json
"notification": {
  "feishu_webhook": "YOUR_WEBHOOK_URL_HERE"
}
```
