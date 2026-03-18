# 竞品信息抓取 Skill

**Skill 名称**: `competitor-scraper`

**版本**: v1.0

---

## description

当用户要求抓取竞品官网、监控竞品动态、获取竞品信息时使用此技能。

不适用于：加密货币数据、社交媒体抓取（需要特殊 API）、非公开信息。

---

## 触发条件

- 用户要求抓取竞品数据
- 每日定时任务（9:00 AM 触发）
- 被其他 Agent 调用时

---

## 工作流程

### 1. 读取配置

- 读取 `competitors-monitor/config.json`
- 获取竞品 URL 列表
- 获取抓取规则（User-Agent、超时时间等）

### 2. 抓取网页

- 遍历所有竞品的所有页面
- 使用 `requests` + `BeautifulSoup` 抓取
- 提取标题、内容、价格
- 处理异常和超时

### 3. 数据清洗

- 去除 HTML 标签
- 提取纯文本
- 截取前 500 字符（避免数据过大）

### 4. 保存数据

- 输出为 JSON 格式
- 文件路径：`workspace/competitors-monitor/data/YYYY-MM-DD.json`
- 格式：
  ```json
  [
    {
      "competitor": "竞品A",
      "page_type": "homepage",
      "url": "https://...",
      "title": "页面标题",
      "content": "页面内容...",
      "price": "价格信息（如果有）",
      "timestamp": "2026-03-18T09:00:00"
    }
  ]
  ```

### 5. 异常处理

- 如果请求失败，等待 30 秒后重试，最多 3 次
- 如果超时，记录错误并继续下一个页面
- 如果失败率超过 50%，通知用户

### 6. 输出摘要

- 在对话中输出：
  ```
  ✅ 竞品信息抓取完成
  📊 共抓取 XX 个页面
  ✅ 成功: XX
  ❌ 失败: XX
  📁 文件保存到: workspace/competitors-monitor/data/YYYY-MM-DD.json
  ```

---

## 需要的环境变量

无（所有配置在 `config.json` 中）

---

## 使用的脚本

- `scripts/scrape.py` - 主抓取脚本

---

## 注意事项

### 频率控制
- ⚠️ 不要频繁抓取（每天 1 次即可）
- ⚠️ 每个请求之间延迟 2 秒
- ⚠️ 遵守 robots.txt

### 法律合规
- ✅ 只抓取公开信息
- ✅ 不抓取用户数据
- ✅ 遵守网站服务条款

### 数据存储
- ✅ 定期清理旧数据（保留 30 天）
- ✅ 只存储必要信息

---

## 输出示例

### 用户输入
```
抓取一下竞品数据
```

### Agent 输出
```
收到，正在执行竞品信息抓取任务...

📊 抓取竞品: 竞品A
  正在抓取: 竞品A - 首页
  正在抓取: 竞品A - 产品页
  正在抓取: 竞品A - 新闻页
  正在抓取: 竞品A - 价格页

📊 抓取竞品: 竞品B
  正在抓取: 竞品B - 首页
  正在抓取: 竞品B - 产品页

✅ 竞品信息抓取完成
📊 共抓取 6 个页面
✅ 成功: 6
❌ 失败: 0
📁 文件保存到: workspace/competitors-monitor/data/2026-03-18.json
```

---

## 与其他 Agent 的协作

### 下游 Agent
- **competitor-diff-detector**（变化检测 Agent）
  - 读取本 Agent 输出的 JSON 文件
  - 对比昨天和今天的数据
  - 识别变化

### 触发方式
- 本 Agent 完成后，自动触发 `competitor-diff-detector`

---

**Skill 版本**: v1.0
**创建时间**: 2026-03-18
**作者**: 大领导 🎯
