# 敏感信息配置指南

**⚠️ 重要提醒**: 本文档中的所有占位符都需要替换为你自己的真实密钥！

**版本**: v5.12.0
**更新时间**: 2026-03-15

---

## 🔐 安全须知

### 为什么需要单独配置？

1. **安全性**: API Keys 和密钥是敏感信息，不能上传到公开仓库
2. **个人化**: 每个用户需要使用自己的 API Keys 和飞书应用
3. **合规性**: API Keys 通常有使用限制，需要个人账户

### 已脱敏的内容

在本仓库中，以下内容已经替换为占位符：
- ✅ 所有 API Keys
- ✅ 飞书 App Secrets
- ✅ Gateway 认证 Token
- ✅ 第三方服务密钥

---

## 📋 配置清单

### 必须配置（核心功能）

1. **智谱 AI API Key** - GLM 模型提供商
2. **飞书应用凭证** - App ID + App Secret

### 可选配置（扩展功能）

3. **Groq API Key** - 代码和快速响应
4. **Google API Key** - Gemini 模型
5. **NVIDIA API Key** - GPT-OSS-120B

---

## 🔧 配置步骤

### 1. 配置文件位置

主配置文件: `~/.openclaw/openclaw.json`

### 2. 获取 API Keys

#### 智谱 AI (GLM) - 必需 ⭐

1. 访问 [智谱 AI 开放平台](https://open.bigmodel.cn/)
2. 注册/登录账户
3. 进入 API Keys 页面
4. 创建新的 API Key
5. 复制 Key

**格式示例**:
```
c26c6bd6acfc44cda167b15dc338dabc.Hmfe3HhV5TjJiXqp
```

#### 飞书开放平台 - 必需 ⭐

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 获取凭证:
   - **App ID**: `cli_a90df9a07db8dcb1`（你的应用）
   - **App Secret**: 从开放平台获取

**格式示例**:
```
App ID: cli_a90df9a07db8dcb1
App Secret: 7CERQM7oIW4YTEbSaieAfZMplHBxJTPJ
```

#### Groq - 可选

1. 访问 [Groq Console](https://console.groq.com/)
2. 注册/登录
3. 创建 API Key

**格式示例**:
```
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
```

#### Google AI - 可选

1. 访问 [Google AI Studio](https://makersuite.google.com/)
2. 创建项目
3. 生成 API Key

**格式示例**:
```
AIzaSyAcMMIXeaM7Or0Z2HA20z00VgWG8RxXHyg
```

#### NVIDIA - 可选

1. 访问 [NVIDIA API Catalog](https://build.nvidia.com/)
2. 注册/登录
3. 创建 API Key

**格式示例**:
```
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
```

---

## 📝 配置文件模板

### 完整配置示例

将 `~/.openclaw/openclaw.json` 修改为以下内容，**替换所有占位符**：

```json
{
  "models": {
    "mode": "merge",
    "providers": {
      "glmcode": {
        "baseUrl": "https://open.bigmodel.cn/api/anthropic",
        "apiKey": "YOUR_GLMCODE_API_KEY_HERE",
        "api": "anthropic-messages",
        "models": [
          {
            "id": "glm-5",
            "name": "GLM-5"
          },
          {
            "id": "glm-4.7",
            "name": "GLM-4.7"
          },
          {
            "id": "glm-4.6",
            "name": "GLM-4.6"
          },
          {
            "id": "glm-4.5-air",
            "name": "GLM-4.5-Air"
          }
        ]
      },
      "groq": {
        "baseUrl": "https://api.groq.com/openai/v1",
        "apiKey": "YOUR_GROQ_API_KEY_HERE",
        "models": [
          {
            "id": "llama-3.3-70b-versatile",
            "name": "Llama-3.3-70B"
          }
        ]
      },
      "google": {
        "baseUrl": "https://generativelanguage.googleapis.com/v1beta",
        "apiKey": "YOUR_GOOGLE_API_KEY_HERE",
        "api": "google-generative-ai",
        "models": [
          {
            "id": "gemini-2.5-flash",
            "name": "Gemini-2.5-Flash"
          }
        ]
      },
      "nvidia-gpt-oss": {
        "baseUrl": "https://integrate.api.nvidia.com/v1",
        "apiKey": "YOUR_NVIDIA_API_KEY_HERE",
        "api": "openai-completions",
        "models": [
          {
            "id": "openai/gpt-oss-120b",
            "name": "GPT-OSS-120B"
          }
        ]
      }
    }
  },
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "YOUR_FEISHU_APP_ID_HERE",
      "appSecret": "YOUR_FEISHU_APP_SECRET_HERE",
      "domain": "feishu",
      "groupPolicy": "open",
      "streaming": false,
      "threadSession": true,
      "requireMention": true
    }
  },
  "gateway": {
    "port": 18789,
    "mode": "local",
    "bind": "loopback",
    "auth": {
      "mode": "token",
      "token": "GENERATE_RANDOM_TOKEN_HERE"
    }
  }
}
```

---

## 🔑 快速配置脚本

为了方便配置，我提供了一个自动化脚本：

### 方法 1: 交互式配置

```bash
# 运行配置向导
bash ~/.openclaw/workspace/scripts/setup-secrets.sh
```

脚本会提示你输入所有必要的 API Keys。

### 方法 2: 手动编辑

```bash
# 编辑配置文件
nano ~/.openclaw/openclaw.json

# 替换以下占位符：
# - YOUR_GLMCODE_API_KEY_HERE
# - YOUR_GROQ_API_KEY_HERE
# - YOUR_GOOGLE_API_KEY_HERE
# - YOUR_NVIDIA_API_KEY_HERE
# - YOUR_FEISHU_APP_ID_HERE
# - YOUR_FEISHU_APP_SECRET_HERE
# - GENERATE_RANDOM_TOKEN_HERE
```

---

## 🛡️ 安全最佳实践

### 1. API Keys 管理

**❌ 不要**:
- 将 API Keys 提交到 Git
- 在公开场合分享 API Keys
- 使用相同密钥用于多个环境

**✅ 应该**:
- 使用环境变量存储密钥
- 定期轮换 API Keys
- 为不同环境使用不同密钥

### 2. 文件权限

```bash
# 设置配置文件权限（仅所有者可读写）
chmod 600 ~/.openclaw/openclaw.json

# 设置凭证目录权限
chmod 700 ~/.openclaw/credentials/
```

### 3. 密钥轮换

建议每 90 天轮换一次 API Keys：

```bash
# 生成随机 Token
openssl rand -hex 32
```

---

## 🧪 验证配置

### 1. 检查配置文件格式

```bash
# 使用 jq 验证 JSON 格式
cat ~/.openclaw/openclaw.json | jq .
```

如果输出错误，说明 JSON 格式有问题。

### 2. 测试 API 连接

```bash
# 运行诊断
openclaw doctor

# 或者使用飞书插件诊断
openclaw plugin doctor @larksuite/openclaw-lark
```

### 3. 启动 Gateway

```bash
# 启动服务
openclaw gateway start

# 查看状态
openclaw gateway status

# 查看日志
tail -f ~/.openclaw/logs/gateway.log
```

---

## 🔍 故障排查

### 问题 1: API Key 无效

**症状**: 提示认证失败

**解决**:
1. 检查 API Key 是否正确复制
2. 确认 API Key 未过期
3. 检查账户余额

### 问题 2: 飞书无法连接

**症状**: 飞书机器人无响应

**解决**:
1. 检查 App ID 和 App Secret
2. 确认应用已发布
3. 检查网络连接

### 问题 3: JSON 格式错误

**症状**: Gateway 无法启动

**解决**:
```bash
# 验证 JSON 格式
cat ~/.openclaw/openclaw.json | jq .

# 修复语法错误
nano ~/.openclaw/openclaw.json
```

---

## 📚 相关资源

### API 文档
- [智谱 AI 文档](https://open.bigmodel.cn/dev/api)
- [飞书开放平台文档](https://open.feishu.cn/document/)
- [Groq 文档](https://console.groq.com/docs)
- [Google AI 文档](https://ai.google.dev/docs)

### 账户注册
- [智谱 AI 注册](https://open.bigmodel.cn/)
- [飞书开放平台](https://open.feishu.cn/)
- [Groq Console](https://console.groq.com/)
- [Google AI Studio](https://makersuite.google.com/)

---

## ✅ 配置检查清单

配置完成后，使用以下清单验证：

- [ ] 智谱 AI API Key 已配置
- [ ] 飞书 App ID 和 App Secret 已配置
- [ ] 配置文件 JSON 格式正确
- [ ] 文件权限已设置（600）
- [ ] Gateway 成功启动
- [ ] 飞书机器人能够响应
- [ ] 至少一个模型能够正常工作

---

**配置指南版本**: v5.12.0
**最后更新**: 2026-03-15
**维护者**: 幸运小行星
