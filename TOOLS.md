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
