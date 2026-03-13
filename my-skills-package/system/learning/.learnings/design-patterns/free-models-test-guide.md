# 🧪 免费LLM模型测试指南

**目的**: 测试各种免费LLM API，验证可用性并记录性能

---

## 📋 测试清单

### 准备工作

#### 1. 获取API Keys

**OpenRouter** (推荐优先级: ⭐⭐⭐⭐⭐)
- 访问: https://openrouter.ai/keys
- 免费额度: 20 req/min, 50 req/day
- 免费模型: 20+ 个

**Groq** (超快，推荐优先级: ⭐⭐⭐⭐⭐)
- 访问: https://console.groq.com/keys
- 免费额度: 250 req/day
- 特点: 70K tokens/min (超快)

**Google AI Studio** (中文优化，推荐优先级: ⭐⭐⭐⭐⭐)
- 访问: https://aistudio.google.com/app/apikey
- 免费额度: 250K tokens/min
- 需要: 手机号验证

**GitHub Models** (旗舰级，推荐优先级: ⭐⭐⭐⭐)
- 需要: GitHub账号 + Copilot订阅
- 免费模型: GPT-4.1, o1, o3, gpt-5, Grok 3, DeepSeek-R1

#### 2. 设置环境变量

```bash
# 临时设置（当前会话）
export OPENROUTER_API_KEY="sk-or-v1-..."
export GROQ_API_KEY="gsk_..."
export GOOGLE_API_KEY="AIza..."
export GITHUB_TOKEN="ghp_..."

# 永久设置（添加到 ~/.bashrc）
echo 'export OPENROUTER_API_KEY="sk-or-v1-..."' >> ~/.bashrc
echo 'export GROQ_API_KEY="gsk_..."' >> ~/.bashrc
echo 'export GOOGLE_API_KEY="AIza..."' >> ~/.bashrc
source ~/.bashrc
```

---

## 🧪 测试脚本

### 自动测试脚本

```bash
#!/bin/bash
# 测试免费模型API

echo "🧪 测试免费LLM模型"
echo "================================"
echo ""

# OpenRouter测试
echo "1️⃣ OpenRouter"
if [ -n "$OPENROUTER_API_KEY" ]; then
    curl -X POST https://openrouter.ai/api/v1/chat/completions \
        -H "Authorization: Bearer $OPENROUTER_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{
            "model": "google/gemma-3-4b-it:free",
            "messages": [{"role": "user", "content": "Hello!"}],
            "max_tokens": 50
        }'
else
    echo "⚠️ API Key未设置"
fi

# Groq测试
echo ""
echo "2️⃣ Groq"
if [ -n "$GROQ_API_KEY" ]; then
    curl -X POST https://api.groq.com/openai/v1/chat/completions \
        -H "Authorization: Bearer $GROQ_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": "Hello!"}],
            "max_tokens": 50
        }'
else
    echo "⚠️ API Key未设置"
fi

echo ""
echo "================================"
echo "✅ 测试完成"
```

---

## 📊 测试结果记录

### 测试维度

| API | 响应时间 | 成功率 | 推荐用途 |
|-----|---------|--------|---------|
| OpenRouter | 待测试 | - | 代码专家 |
| Groq | 待测试 | - | 超快速 |
| Google AI Studio | 待测试 | - | 中文优化 |
| GitHub Models | 待测试 | - | 旗舰级 |

---

## 🚀 快速开始

### 步骤1: 获取API Keys（5分钟）

1. **OpenRouter**: https://openrouter.ai/keys
2. **Groq**: https://console.groq.com/keys
3. **Google AI Studio**: https://aistudio.google.com/app/apikey
4. **GitHub Models**: 使用现有GitHub账号

### 步骤2: 设置环境变量

```bash
# 临时设置
export OPENROUTER_API_KEY="your_key_here"
export GROQ_API_KEY="your_key_here"
export GOOGLE_API_KEY="your_key_here"
```

### 步骤3: 运行测试

```bash
bash /root/.openclaw/workspace/scripts/test-free-models.sh
```

---

## 💡 建议的配置优先级

### 第一优先级（立即配置）

1. **Groq** - 超快，250 req/day
2. **OpenRouter** - 20+ 免费模型
3. **Google AI Studio** - 中文优化

### 第二优先级（有条件）

4. **GitHub Models** - 需要Copilot订阅

### 试用额度（$1-$30）

5. **Baseten** - $1
6. **Nebius** - $1 (1年)
7. **Novita** - $0.5 (1年)

---

## 📝 记录模板

### 测试结果模板

```
## OpenRouter测试

### API Key: sk-or-v1-...
### 测试时间: 2026-03-08 16:45

### 模型: gemma-3-4b-it:free
- 响应时间: Xms
- 状态: ✅/❌
- 备注: 超快！

### 模型: gpt-oss-120b:free
- 响应时间: Xms
- 状态: ✅/❌
- 备注: 代码能力强

---
```

---

## ⚠️ 注意事项

1. **不要滥用** - 遵守使用限制
2. **监控使用** - 避免超限
3. **备用方案** - 准备多个提供商
4. **定期检查** - 关注政策变化

---

**准备好测试了吗？设置好API Key后运行测试脚本！** 🧪✨
