# OpenCLI 集成技能

**版本**: 1.0.0
**创建时间**: 2026-04-01
**作者**: 大领导 🎯

---

## 📖 技能描述

OpenCLI 是一个强大的工具，可以将任何网站变成 CLI。本技能提供了 OpenCLI 的包装接口，让 OpenClaw 系统能够方便地调用 OpenCLI 的功能。

**核心特性**:
- ✅ 80+ 内置命令
- ✅ 支持 30+ 站点和应用
- ✅ 零配置，复用浏览器登录态
- ✅ 专为 AI Agent 设计

---

## 🎯 适用场景

### 数据采集
- B 站热门视频、评论、字幕
- 知乎热榜、搜索
- 小红书笔记
- Twitter/X 时间线、书签
- Reddit 热帖
- YouTube 视频信息

### 跨应用编排
- 股票数据 → AI 分析 → 飞书记录
- B 站抓字幕 → AI 总结 → 发到群聊
- 知乎热榜 → 内容分析 → Notion 文档

### 桌面应用控制
- Cursor IDE
- Notion
- Discord
- 飞书
- 微信

---

## 🚀 使用方法

### 方法 1: 直接命令调用

```bash
# B 站热门
opencli bilibili hot

# 知乎热榜
opencli zhihu hot

# Twitter 书签
opencli twitter bookmarks

# 雪球股票数据
opencli xueqiu stock <代码>
```

### 方法 2: Python 包装函数

```python
import subprocess

def opencli_command(platform, action, args=None):
    """
    调用 OpenCLI 命令
    
    Args:
        platform: 平台名称 (bilibili, zhihu, twitter, etc.)
        action: 动作 (hot, search, bookmarks, etc.)
        args: 额外参数
    
    Returns:
        命令输出结果
    """
    cmd = ['opencli', platform, action]
    if args:
        cmd.extend(args)
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        return f"错误: {result.stderr}"
    
    return result.stdout

# 示例：获取 B 站热门
output = opencli_command('bilibili', 'hot')
print(output)
```

### 方法 3: 通过子 Agent 调用

```bash
# 在 OpenClaw 中调用
sessions_spawn -runtime subagent -skill opencli "bilibili hot"
```

---

## 📋 可用平台列表

### 视频平台
- **bilibili** - B 站热门、搜索、评论、字幕、下载
- **youtube** - YouTube 视频信息、搜索

### 社交平台
- **zhihu** - 知乎热榜、搜索
- **twitter** - Twitter 时间线、书签
- **reddit** - Reddit 热帖、搜索
- **bluesky** - Bluesky 用户、帖子、趋势

### 内容社区
- **xiaohongshu** - 小红书笔记下载
- **band** - Band 帖子、提及

### 财经数据
- **xueqiu** - 雪球股票数据
- **barchart** - 期权数据、希腊值

### 新闻资讯
- **36kr** - 36 氪热榜、文章、搜索
- **bbc** - BBC 新闻头条
- **bloomberg** - 彭博社新闻

### 招聘平台
- **boss** - BOSS 直聘职位搜索、候选人管理

### 学习平台
- **chaoxing** - 学习通作业、考试

### 桌面应用
- **antigravity** - Antigravity AI 对话
- **cursor** - Cursor IDE 操作
- **notion** - Notion 文档操作

---

## 🔧 配置要求

### 前置条件
1. **Node.js** - 已安装 v22.22.0
2. **OpenCLI** - 已全局安装 `npm install -g @jackwener/opencli`
3. **Chrome 浏览器** - 需要安装 OpenCLI 浏览器扩展

### 浏览器扩展安装

1. 访问 OpenCLI GitHub: https://github.com/jackwener/opencli
2. 下载 Chrome 扩展
3. 在 Chrome 中安装扩展
4. 确保 Daemon 运行在 localhost:19825

### 验证安装

```bash
# 检查 OpenCLI 版本
opencli --version

# 检查浏览器连接
opencli doctor

# 列出所有可用命令
opencli list
```

---

## 💡 使用示例

### 示例 1: 获取 B 站热门视频

```python
import subprocess

def get_bilibili_hot():
    result = subprocess.run(
        ['opencli', 'bilibili', 'hot'],
        capture_output=True,
        text=True
    )
    return result.stdout

hot_videos = get_bilibili_hot()
print(hot_videos)
```

### 示例 2: 知乎热榜分析

```python
def get_zhihu_hot():
    result = subprocess.run(
        ['opencli', 'zhihu', 'hot'],
        capture_output=True,
        text=True
    )
    return result.stdout

hot_topics = get_zhihu_hot()
# 可以进一步分析或存储
```

### 示例 3: 跨应用编排

```python
def workflow_analyze_trending():
    """获取 B 站热门，用 AI 分析，发送到飞书"""
    
    # 1. 获取 B 站热门
    hot = subprocess.run(
        ['opencli', 'bilibili', 'hot', '-f', 'json'],
        capture_output=True,
        text=True
    )
    
    # 2. AI 分析
    summary = ai_analyze(hot.stdout)
    
    # 3. 发送到飞书
    send_to_feishu(summary)
    
    return summary
```

---

## ⚠️ 注意事项

### 权限管理
- OpenCLI 复用浏览器登录态
- Agent 拥有和你在浏览器中一样的权限
- 建议限制敏感操作（发帖、删除等）

### 稳定性
- 网站改版可能导致命令失效
- 建议定期更新 OpenCLI
- 遇到问题可以使用 `opencli doctor` 诊断

### 性能
- Daemon 空闲 5 分钟自动退出
- 不占用常驻资源
- 首次启动可能需要几秒钟

---

## 📚 参考资源

- **OpenCLI GitHub**: https://github.com/jackwener/opencli
- **OpenCLI 文档**: https://github.com/jackwener/opencli/blob/main/README.md
- **安装指南**: https://github.com/jackwener/opencli?tab=readme-ov-file#installation

---

## 🔄 更新日志

### v1.0.0 (2026-04-01)
- ✅ 初始版本
- ✅ 支持 80+ 内置命令
- ✅ Python 包装函数
- ✅ 完整文档

---

**技能维护**: 大领导 🎯
**最后更新**: 2026-04-01
