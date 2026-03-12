# 🤖 Claude Code 配置 GLM-4.7 指南

**创建时间**: 2026-03-04 23:54
**目标**: 配置 GLM-4.7 到 Claude Code

---

## 🎯 配置方式

Claude Code 支持自定义模型提供商，可以通过 OpenAI-compatible API 配置 GLM-4.7。

### GLM-4.7 API 信息

根据你的 OpenClaw 配置：
- **Base URL**: https://open.bigmodel.cn/api/anthropic
- **API Key**: c26c6bd6acfc44cda167b15dc338dabc.Hmfe3HhV5TjJiXqp
- **模型**: glm-4.7

---

## 📋 配置步骤

### 方式 1: 环境变量配置（推荐）

```bash
# 设置 OpenAI Base URL 到 GLM API
export OPENAI_BASE_URL="https://open.bigmodel.cn/api/v1"

# 设置 API Key
export OPENAI_API_KEY="c26c6bd6acfc44cda167b15dc338dabc.Hmfe3HhV5TjJiXqp"

# 使用 GLM-4.7
claude --model glm-4.7 "测试连接"
```

### 方式 2: 配置文件

#### 创建配置文件
```bash
# Claude Code 配置目录
mkdir -p ~/.config/claude

# 创建配置文件
cat > ~/.config/claude/config.json << 'EOF'
{
  "apiKey": "c26c6bd6acfc44cda167b15dc338dabc.Hmfe3HhV5TjJiXqp",
  "baseUrl": "https://open.bigmodel.cn/api/v1",
  "model": "glm-4.7",
  "provider": "openai-compatible"
}
EOF
```

### 方式 3: 命令行参数

```bash
# 直接指定
OPENAI_API_KEY="c26c6bd6acfc44cda167b15dc338dabc.Hmfe3HhV5TjJiXqp" \
OPENAI_BASE_URL="https://open.bigmodel.cn/api/v1" \
claude --model glm-4.7 "你好"
```

---

## 🧪 测试配置

### 快速测试
```bash
# 设置环境变量
export OPENAI_API_KEY="c26c6bd6acfc44cda167b15dc338dabc.Hmfe3HhV5TjJiXqp"
export OPENAI_BASE_URL="https://open.bigmodel.cn/api/v1"

# 测试连接
claude --model glm-4.7 "你好，请用一句话介绍你自己"
```

### 如果成功
你应该看到 GLM-4.7 的回复。

---

## 🎯 在 PAI 项目中使用

### 创建专门的 Agent

```bash
# 创建技术专家 Agent（使用 GLM-4.7）
cat > ~/.config/claude/agents.json << 'EOF'
{
  "tech-expert": {
    "description": "技术专家，负责 PAI 技术研究和实施",
    "prompt": "你是技术专家，擅长深入研究和实施复杂系统。",
    "model": "glm-4.7",
    "apiKey": "c26c6bd6acfc44cda167b15dc338dabc.Hmfe3HhV5TjJiXqp",
    "baseUrl": "https://open.bigmodel.cn/api/v1"
  }
}
EOF
```

### 使用 Agent

```bash
# 启动技术专家会话
claude --agent tech-expert "开始研究 PAI 架构"
```

---

## 💡 优化建议

### 1. 创建别名

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
alias claude-glm='OPENAI_API_KEY="c26c6bd6acfc44cda167b15dc338dabc.Hmfe3HhV5TjJiXqp" OPENAI_BASE_URL="https://open.bigmodel.cn/api/v1" claude --model glm-4.7'

# 使用
claude-glm "你好"
```

### 2. 配置到 shell 启动文件

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export OPENAI_API_KEY="c26c6bd6acfc44cda167b15dc338dabc.Hmfe3HhV5TjJiXqp"
export OPENAI_BASE_URL="https://open.bigmodel.cn/api/v1"
export DEFAULT_MODEL="glm-4.7"
```

---

## ⚠️ 注意事项

### API 兼容性

GLM-4.7 的 OpenAI-compatible API：
- **端点**: https://open.bigmodel.cn/api/v1
- **格式**: OpenAI Chat Completions format
- **支持**: 大部分功能兼容

### 可能的限制

- 某些 Claude Code 特定功能可能不兼容
- 需要测试验证核心功能
- 如有问题可以切换回默认模型

---

## 🎉 总结

### 配置确认
- ✅ **可以配置**: GLM-4.7 到 Claude Code
- ✅ **使用方式**: OpenAI-compatible API
- ✅ **推荐方式**: 环境变量配置

### 下一步
1. 测试配置
2. 验证功能
3. 在 PAI 项目中使用

---

## 🚀 立即测试

```bash
# 快速测试命令
export OPENAI_API_KEY="c26c6bd6acfc44cda167b15dc338dabc.Hmfe3HhV5TjJiXqp"
export OPENAI_BASE_URL="https://open.bigmodel.cn/api/v1"

claude --model glm-4.7 "你好，请用一句话介绍你自己"
```

---

*创建时间: 2026-03-04 23:54*
*配置指南: v1.0*
*状态: ✅ 可以配置*
