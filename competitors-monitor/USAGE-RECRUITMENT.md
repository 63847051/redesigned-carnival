# 招聘流程自动化 - 使用指南

## 概述

招聘流程自动化系统帮助HR自动解析简历、筛选候选人、安排面试、发送通知邮件。

## 功能特性

- **简历解析**: 支持 PDF、Word、TXT 格式
- **智能筛选**: 基于关键词和权重计算匹配度
- **流程管理**: 追踪候选人面试进度
- **邮件通知**: 自动发送面试邀请和通知

## 配置说明

编辑 `config/recruitment.json`:

```json
{
  "positions": [
    {
      "id": "python_dev",
      "title": "Python 开发工程师",
      "requirements": {
        "skills": ["Python", "Django", "PostgreSQL"],
        "experience_years_min": 3,
        "education": "本科"
      },
      "weight": {
        "skills": 0.5,
        "experience": 0.3,
        "education": 0.2
      }
    }
  ],
  "check_rules": {
    "match_score_threshold": 0.6
  }
}
```

## 运行方式

```bash
cd /root/.openclaw/workspace/competitors-monitor
python3 plugins/recruitment.py
```

## 输出示例

```
处理了 0 份新简历
候选人数: 2
告警数: 2

## 📋 招聘流程报告

**日期**: 2026-03-18

**候选人总数**: 2

### 各阶段人数

- 一面: 1 人
- 筛选: 1 人

### 候选人详情

**张三** - 一面

- 匹配职位: Python 开发工程师 (匹配度: 85%)

**李四** - 筛选

- 匹配职位: 数据分析师 (匹配度: 72%)

### ⚠️ 告警

- 新候选人: 张三 (匹配: Python 开发工程师)
- 新候选人: 李四 (匹配: 数据分析师)
```

## 简历解析

将简历文件放入 `data/resumes/` 目录，支持格式:
- `.txt` - 文本文件
- `.pdf` - PDF 文件（需安装 PyPDF2）
- `.docx` - Word 文件（需安装 python-docx）

自动提取:
- 姓名
- 邮箱
- 电话
- 学历
- 工作年限
- 技能关键词

## 匹配度计算

系统根据以下权重计算候选人匹配度:

| 因素 | 默认权重 | 说明 |
|------|----------|------|
| 技能匹配 | 50% | 技能关键词匹配比例 |
| 经验 | 30% | 工作年限对比 |
| 学历 | 20% | 学历要求对比 |

## 面试流程

系统支持以下阶段:
1. 新简历
2. 筛选
3. 一面
4. 二面
5. Offer
6. 入职

## 邮件配置

配置 SMTP 服务器发送通知邮件:

```json
"email": {
  "enabled": true,
  "smtp_server": "smtp.example.com",
  "smtp_port": 587,
  "sender_email": "hr@example.com",
  "sender_password": "YOUR_PASSWORD"
}
```

## 告警类型

| 类型 | 说明 |
|------|------|
| new_candidate | 新候选人 |
| interview_reminder | 面试提醒 |
| offer_sent | 发出 Offer |
