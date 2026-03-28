# Tavily Search Skill

**作者**: OpenClaw
**版本**: v1.0
**创建时间**: 2026-03-28 22:50
**状态**: ✅ 已创建，待配置 API Key

---

## 🎯 功能说明

为 OpenClaw 添加 AI 搜索能力，使用 Tavily API 进行实时搜索和内容提取。

---

## 📋 核心功能

### 1️⃣ AI 驱动搜索
- 实时搜索网络内容
- AI 自动总结
- 多语言支持

### 2️⃣ 智能过滤
- 指定域名搜索
- 搜索深度控制
- 时间范围过滤

### 3️⃣ 结果格式化
- Markdown 格式输出
- 结构化数据
- 原始内容可选

---

## 🔧 配置步骤

### Step 1: 注册 Tavily 账号

1. 访问：https://tavily.com
2. 点击 "Sign Up"
3. 使用 Google 账号注册
4. 设置密码

### Step 3: 获取 API Key

1. 登录 Dashboard
2. 点击 "API Keys"
3. 复制 API Key（tvly-xxxxx...）

### Step 4: 配置 OpenClaw

方法 1: 环境变量
```bash
export TAVILLYLY_API_KEY="tvly-你的Key"
```

方法 2: Skill 配置
```bash
# 添加到环境变量
echo 'export TAVILLYLY_API_KEY="tvly-你的Key"' >> ~/.bashrc
source ~/.bashrc
```

---

## 📊 使用示例

### 示例 1: 每日选题灵感
```bash
python3 skills/tavily-search/skill.py "搜索 AI 领域最新进展"
```

### 示例 2: 热点话题追踪
```bash
python3 skills/tavily-search/skill.py "搜索 AI 绘画版权最新进展"
```

### 示例 3: 背景调研
```bash
python3 skills/tavily-search/skill.py "搜索 SaaS 客户成功案例"
```

---

## 💰 费用

| 套餐 | 价格 | 说明 |
|------|------|------|
| Free | $0 | 1000 credits/月 |
| Researcher | $19/月起 | 5000 credits/月 |
| Teams | 按量计费 | 大规模商业 |

**个人使用建议**：
- 每天 5 次搜索 ≈ 150 credits/月
- 1000 次/月 ≈ 200 天免费

---

## 🎯 适用场景

- 每日选题灵感
- 热点话题追踪
- 背景调研
- 竞争对手分析
- 行业追踪

---

**详细配置指南**: 见 `TAVILY-SETUP-GUIDE.md`
**技术文档**: 见 `skill.md`
