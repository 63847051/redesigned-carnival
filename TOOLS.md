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

## 🎯 DeerFlow 技能库 ⭐ 2026-03-23 新增

### 已移植技能（5个）

| 技能名称 | 描述 | 文件数 |
|---------|------|--------|
| `deerflow-skill-creator` | 创建和优化 agent 技能，测量技能性能 | 20 |
| `deerflow-deep-research` | 深度网络研究，多角度系统性调研 | 1 |
| `deerflow-data-analysis` | Excel/CSV 数据分析，DuckDB 支持 | 2 |
| `deerflow-find-skills` | 发现和安装 agent 技能 | 2 |
| `deerflow-github-deep-research` | GitHub 仓库深度研究 | 3 |

### 原始可用技能（16个公开技能）

位于 `/root/.openclaw/workspace/projects/deerflow-study/deer-flow-source/skills/public/`：

- `bootstrap` - 快速启动
- `chart-visualization` - **26种图表可视化**（28文件）⭐
- `claude-to-deerflow` - Claude 迁移
- `consulting-analysis` - 咨询分析
- `data-analysis` - 数据分析（DuckDB）
- `deep-research` - 深度研究
- `find-skills` - 查找技能
- `frontend-design` - 前端设计
- `github-deep-research` - GitHub 研究
- `image-generation` - 图片生成
- `podcast-generation` - 播客生成
- `ppt-generation` - PPT 生成
- `skill-creator` - 技能创建（核心）
- `surprise-me` - 惊喜技能
- `vercel-deploy-claimable` - Vercel 部署
- `video-generation` - 视频生成
- `web-design-guidelines` - 网页设计指南

### 技能位置

**已移植**: `/root/.openclaw/workspace/skills/deerflow-*`
**原始**: `/root/.openclaw/workspace/projects/deerflow-study/deer-flow-source/skills/public/`

### 使用方法

```bash
# 查看已安装的 DeerFlow 技能
ls /root/.openclaw/workspace/skills/deerflow-*

# 查看技能详情
cat /root/.openclaw/workspace/skills/deerflow-<skill-name>/SKILL.md
```

---

## ⚡ 上下文优化模块 ⭐ 2026-03-23 新增

### 位置

`/root/.openclaw/workspace/context-optimization/`

### 核心组件

| 模块 | 功能 | 状态 |
|------|------|------|
| `auto_summarizer.py` | 自动总结已完成任务，节省 Token | ✅ 测试通过 |
| `result_offloader.py` | 大结果存储到磁盘，按需加载 | ✅ 测试通过 |
| `compressor.py` | 上下文压缩，提取关键信息 | ✅ 测试通过 |

### 测试结果

- **AutoSummarizer**: Token 节省 40%
- **ResultOffloader**: 文件存储和加载正常
- **ContextCompressor**: 消息压缩比 35%
- **集成测试**: 全部通过 ✅

### 使用方法

```python
from context_optimization import AutoSummarizer, ResultOffloader, ContextCompressor

# 总结任务
summarizer = AutoSummarizer()
summary = summarizer.create_summary("test_session")

# 存储大结果
offloader = ResultOffloader()
result_id = offloader.save_result(large_data)

# 压缩上下文
compressor = ContextCompressor()
compressed = compressor.compress(messages, token_budget=4000)
```

### 测试脚本

```bash
python3 /root/.openclaw/workspace/context-optimization/test_context_optimization.py
```

---

## 🔌 MCP 增强模块 ⭐ 2026-03-23 新增

### 位置

`/root/.openclaw/workspace/mcp-enhancement/`

### 核心组件

| 模块 | 功能 | 状态 |
|------|------|------|
| `oauth.py` | OAuth 认证提供商（Google/GitHub） | ✅ 测试通过 |
| `tool_extension.py` | 工具扩展和注册系统 | ✅ 测试通过 |

### OAuth 支持

```python
from mcp_enhancement.oauth import OAuthProvider

provider = OAuthProvider("google")
auth_url = provider.get_authorization_url()
```

### 工具扩展

```python
from mcp_enhancement.tool_extension import ToolExtension, standard_tool

extension = ToolExtension()

@standard_tool(name="greet", description="Greet a user")
def greet(name: str):
    return f"Hello, {name}!"

extension.register_tool(greet)
result = extension.call_tool("greet", {"name": "World"})
```

### 测试脚本

```bash
python3 /root/.openclaw/workspace/mcp-enhancement/test_mcp_enhancement.py
```

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
