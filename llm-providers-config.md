# 🧠 大模型配置文件

**说明**: 独立的模型提供商配置
**创建时间**: 2026-03-02
**版本**: v1.0

---

## 📋 配置说明

这个文件包含所有大模型提供商的配置信息，与 openclaw.json 分离，便于独立管理和维护。

---

## 🔑 API Keys

### Groq
```bash
API_KEY=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
BASE_URL=https://api.groq.com/openai/v1
```

**性能**：
- 响应时间：0.3-0.7秒 ⚡⚡⚡
- 稳定性：⭐⭐⭐⭐⭐
- 推荐：复杂任务、代码生成

**推荐模型**：
- `llama-3.3-70b-versatile` - 通用，70B 参数
- `mixtral-8x7b-32768` - 快速，8x7B
- `gemma2-9b-it` - 轻量，9B

---

### Google AI Studio
```bash
API_KEY=AIzaSyAcMMIXeaM7Or0Z2HA20z00VgWG8RxXHyg
BASE_URL=https://generativelanguage.googleapis.com/v1beta
```

**性能**：
- 响应时间：4-5秒
- 中文支持：⭐⭐⭐⭐⭐
- 推荐：中文任务、翻译

**推荐模型**：
- `gemini-2.5-flash` - 超快速
- `gemini-2.5-flash-lite` - 更快
- `gemma-3-27b-instruct` - 27B 参数

---

### OpenRouter
```bash
API_KEY=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
BASE_URL=https://openrouter.ai/api/v1
```

**性能**：
- 响应时间：~1秒
- 稳定性：⭐⭐⭐
- 推荐：补充、备用

**推荐模型**：
- `google/gemma-3-4b-it:free` - 稳定可用
- `meta-llama/llama-3.3-70b-instruct:free` - 可能限流
- `qwen/qwen3-coder:free` - 代码专家（可能限流）

---

### GLM（智谱AI）
```bash
API_KEY=c26c6bd6acfc44cda167b15dc338dabc.Hmfe3HhV5TjJiXqp
BASE_URL=https://open.bigmodel.cn/api/anthropic
```

**性能**：
- 响应时间：~1-2秒
- 中文支持：⭐⭐⭐⭐
- 推荐：默认稳定

**推荐模型**：
- `glm-4.7` - 高级模型
- `glm-4.6` - 标准模型
- `glm-4.5-air` - 轻量快速
- `glm-5` - 旗舰模型

---

## 🎯 智能分配策略

### 任务类型 → 模型选择

```
🚀 超快速响应（<1秒）
   → Groq Llama-3.3-70B
   - 简单问答
   - 代码生成
   - 复杂推理

🌏 中文优化（高质量）
   → Google Gemini 2.5 Flash
   - 中文翻译
   - 文本总结
   - 中文对话

💰 免费备用
   → OpenRouter Gemma-3-4B
   - 补充备用
   - 简单任务

🎯 默认稳定
   → GLM-4.7
   - 当前使用
   - 稳定可靠
```

---

## 🔧 使用方法

### 方法 1: 直接调用 API

```bash
# Groq 示例
curl -X POST "https://api.groq.com/openai/v1/chat/completions" \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "你好"}],
    "max_tokens": 100
  }'

# Google 示例
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GOOGLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts":[{"text":"你好"}]}]
  }'
```

### 方法 2: Python 脚本

```python
import requests

# Groq 示例
def call_groq(prompt):
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": "Bearer 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"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        }
    )
    return response.json()

# 使用
result = call_groq("什么是人工智能？")
print(result['choices'][0]['message']['content'])
```

### 方法 3: 配置到 openclaw.json（可选）

如果想要全局自动使用，可以添加到 openclaw.json：

```json
{
  "models": {
    "providers": {
      "groq": {
        "baseUrl": "https://api.groq.com/openai/v1",
        "apiKey": "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",
        "models": [
          {"id": "llama-3.3-70b-versatile", "name": "Llama-3.3-70B"}
        ]
      },
      "google": {
        "baseUrl": "https://generativelanguage.googleapis.com/v1beta",
        "apiKey": "AIzaSyAcMMIXeaM7Or0Z2HA20z00VgWG8RxXHyg",
        "api": "vertex",
        "models": [
          {"id": "gemini-2.5-flash", "name": "Gemini-2.5-Flash"}
        ]
      }
    },
    "mode": "merge"
  }
}
```

---

## 📊 性能对比

| 提供商 | 模型 | 响应时间 | 稳定性 | 推荐度 |
|--------|------|---------|--------|--------|
| **Groq** | Llama-3.3-70B | 0.3-0.7秒 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Google** | Gemini-2.5-Flash | 4-5秒 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **OpenRouter** | Gemma-3-4B | ~1秒 | ⭐⭐⭐ | ⭐⭐⭐ |
| **GLM** | GLM-4.7 | ~1-2秒 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🔐 安全提示

⚠️ **重要**：
- 此文件包含敏感的 API Keys
- 不要上传到公开仓库
- 不要分享给他人
- 定期轮换 Keys
- 设置使用限额

---

## 📝 更新日志

### 2026-03-02
- ✅ 添加 Groq 配置
- ✅ 添加 Google AI Studio 配置
- ✅ 添加 OpenRouter 配置
- ✅ 添加 GLM 配置
- ✅ 完成性能测试

---

*此文件独立于 openclaw.json，便于单独管理和维护*

*创建时间: 2026-03-02*
*版本: v1.0*
*状态: ✅ 就绪*
