# TOOLS.md - 工具和环境配置

## 服务器信息

### 主服务器

- **地址:** 43.134.63.176
- **内网地址:** 10.3.0.8
- **网关端口:** 18789
- **系统:** OpenCloudOS (Linux 6.6.117-45.1.oc9.x86_64)
- **Node.js:** v22.22.0

## OpenClaw 配置

- **配置文件位置:** （待确认）
- **当前模型:** GLM-4.7
- **Shell:** bash
- **运行时:** agent=main

## API 和服务

### 智谱 AI (GLM)

- **Base URL:** https://open.bigmodel.cn/api/anthropic
- **当前模型:** glm-4.7
- **可用模型:** glm-5, glm-4.7, glm-4.6, glm-4.5-air, glm-4.5

### 飞书开放平台

- **App ID:** cli_a90df9a07db8dcb1
- **Domain:** feishu

## 工作目录

- **主工作区:** /root/.openclaw/workspace
- **数据目录:** （待添加）
- **项目目录:** （待添加）

## 开发工具

_（待添加常用工具和命令）_

---

## 🧠 HeyCube Server（黑方体 AI 记忆管家）⭐ 2026-03-21 新增

### 配置信息

- **Base URL:** https://heifangti.com/api/api/v1/heifangti
- **API Key:** （需要配置）
- **数据库路径:** /root/.openclaw/workspace/personal-db.sqlite

### 功能说明

HeyCube 是一个**结构化个人档案管理方案**，为 OpenClaw 打造的 AI 记忆管理系统。

**核心特性**:
- 🧠 **结构化记忆** - 8 大域分类（身份认知、心理结构、审美偏好、职业画像、计划目标、日程节奏、杂项偏好、关系网络）
- ⚡ **按需加载** - 一次只花 ~2000 tokens
- 🎯 **智能召回** - 不是检索，是推理
- 🔒 **隐私分离** - 本地存储，数据不出站

### CLI 工具

**位置**: `/root/.openclaw/workspace/scripts/personal-db.py`

**使用方法**:
```bash
# 列出所有维度
python3 /root/.openclaw/workspace/scripts/personal-db.py list

# 获取单个维度
python3 /root/.openclaw/workspace/scripts/personal-db.py get profile.career

# 批量获取维度
python3 /root/.openclaw/workspace/scripts/personal-db.py get-batch "profile.career,behavior.work_habits"

# 设置单个维度
python3 /root/.openclaw/workspace/scripts/personal-db.py set profile.career.career_stage "职业阶段" "资深"

# 批量设置维度
python3 /root/.openclaw/workspace/scripts/personal-db.py set-batch '{"profile.career": "软件工程师", "behavior.work_habits.time_management": "番茄工作法"}'

# 导出为 JSON
python3 /root/.openclaw/workspace/scripts/personal-db.py export
```

### OpenClaw 集成

**前置 Hook**: `~/.agents/skills/heycube-get-config-0.1.0/SKILL.md`
- 对话前自动加载用户画像

**后置 Hook**: `~/.agents/skills/heycube-update-data-0.1.0/SKILL.md`
- 对话后自动更新用户档案

### 项目信息

- **GitHub**: https://github.com/MMMMMMTL/heycube-heifangti
- **文档位置**: `/root/.openclaw/workspace/skills/heycube-heifangti/docs/`
- **License**: MIT

---

## 📱 网页内容提取工具 ⭐ v5.15 更新

### 方法 1: web-content-fetcher Skill（推荐）⭐ v5.15 新增

**快捷脚本**: `~/.openclaw/workspace/scripts/fetch-web-content.sh`

**使用方法**:
```bash
# 使用快捷脚本
~/.openclaw/workspace/scripts/fetch-web-content.sh <URL>

# 或直接使用 Python
python3 ~/.openclaw/workspace/skills/web-content-fetcher/scripts/fetch.py <URL>
```

**支持平台**:
- ✅ 微信公众号（专门优化）
- ✅ GitHub
- ✅ 知乎
- ✅ CSDN
- ✅ Substack
- ✅ Medium

**优势**:
- ✅ 永久免费
- ✅ 安装简单（30 秒）
- ✅ 输出标准 Markdown
- ✅ 支持多平台

**位置**: `~/.openclaw/workspace/skills/web-content-fetcher/`

**依赖**:
- scrapling 0.4.1
- html2text 2025.4.15

**测试报告**: `.learnings/improvements/web-content-fetcher-test-report-20260316.md`

---

### 方法 2: read-wechat.py（备用）

**快速读取工具**: `/root/.openclaw/workspace/scripts/read-wechat.py`

**使用方法**:
```bash
python3 /root/.openclaw/workspace/scripts/read-wechat.py <微信文章URL>
```

**原理**:
- 使用 iPhone User-Agent 绕过反爬虫
- 通过 BeautifulSoup 解析 HTML
- 提取 `#js_content` 区域的正文

**成功案例**:
- 2026-03-13: 成功读取 3 篇微信文章
- 2026-03-14: 成功提取「四地住建厅90个AI案例」（4599字符）

**关键规则**:
> 当用户发送微信公众号链接时，永远不要说"读不了"。
> 直接使用 iPhone UA + BeautifulSoup 方法提取内容！

**示例**:
```python
import requests
from bs4 import BeautifulSoup

url = "https://mp.weixin.qq.com/s/XXXXX"
headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) ...'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
content_div = soup.find('div', id='js_content')
text = content_div.get_text('\n', strip=True)
```
