#!/bin/bash
# 免费模型API配置脚本
# 基于https://github.com/cheahjs/free-llm-api-resources

# 配置目录
CONFIG_DIR="$HOME/.openclaw/providers"
mkdir -p "$CONFIG_DIR"

echo "🚀 配置免费模型API"
echo "================================"
echo ""

# ==================== OpenRouter 配置 ====================
echo "📡 配置 OpenRouter..."
cat > "$CONFIG_DIR/openrouter-free.json" << 'EOF'
{
  "name": "OpenRouter Free Models",
  "base_url": "https://openrouter.ai/api/v1",
  "api_key_env": "OPENROUTER_API_KEY",
  "models": {
    "ultra_fast": {
      "model": "google/gemma-3-4b-it:free",
      "description": "超快速响应",
      "use_case": "问候、简单确认"
    },
    "fast": {
      "model": "z-ai/glm-4.5-air:free",
      "description": "快速响应",
      "use_case": "日常对话"
    },
    "code_expert": {
      "model": "openai/gpt-oss-120b:free",
      "description": "代码专家",
      "use_case": "代码编写、调试"
    },
    "general": {
      "model": "meta-llama/llama-3.3-70b-instruct:free",
      "description": "通用模型",
      "use_case": "复杂任务"
    },
    "chinese": {
      "model": "qwen/qwen3-4b:free",
      "description": "中文优化",
      "use_case": "中文任务"
    }
  },
  "limits": {
    "requests_per_minute": 20,
    "requests_per_day": 50,
    "max_requests_per_day": 1000
  },
  "priority": 1
}
EOF
echo "✅ OpenRouter配置完成"
echo ""

# ==================== Groq 配置 ====================
echo "📡 配置 Groq..."
cat > "$CONFIG_DIR/groq-free.json" << 'EOF'
{
  "name": "Groq Free Models",
  "base_url": "https://api.groq.com/openai/v1",
  "api_key_env": "GROQ_API_KEY",
  "models": {
    "ultra_fast": {
      "model": "gemma-3-2b-it",
      "description": "超快速（70K tokens/min）",
      "use_case": "极速响应"
    },
    "fast": {
      "model": "llama-3.1-8b-instruct",
      "description": "快速",
      "use_case": "快速对话"
    },
    "code_expert": {
      "model": "openai/gpt-oss-120b",
      "description": "代码专家",
      "use_case": "代码任务"
    },
    "general": {
      "model": "llama-3.3-70b-versatile",
      "description": "通用高质量",
      "use_case": "复杂任务"
    }
  },
  "limits": {
    "requests_per_day": 250,
    "tokens_per_minute": 70000
  },
  "priority": 2
}
EOF
echo "✅ Groq配置完成"
echo ""

# ==================== Google AI Studio 配置 ====================
echo "📡 配置 Google AI Studio..."
cat > "$CONFIG_DIR/googleai-free.json" << 'EOF'
{
  "name": "Google AI Studio Free",
  "base_url": "https://generativelanguage.googleapis.com/v1beta",
  "api_key_env": "GOOGLE_API_KEY",
  "models": {
    "chinese_optimized": {
      "model": "gemini-2.5-flash",
      "description": "中文优化",
      "use_case": "中文任务"
    },
    "general": {
      "model": "gemini-3-flash",
      "description": "通用",
      "use_case": "通用任务"
    },
    "light": {
      "model": "gemini-3.1-flash-lite",
      "description": "轻量",
      "use_case": "快速任务"
    }
  },
  "limits": {
    "tokens_per_minute": 250000,
    "requests_per_day": 20,
    "requests_per_minute": 5
  },
  "priority": 3,
  "requires_phone_verification": true
}
EOF
echo "✅ Google AI Studio配置完成"
echo ""

# ==================== GitHub Models 配置 ====================
echo "📡 配置 GitHub Models..."
cat > "$CONFIG_DIR/github-models-free.json" << 'EOF'
{
  "name": "GitHub Models (Copilot)",
  "base_url": "https://models.inference.github.azure.com",
  "api_key_env": "GITHUB_TOKEN",
  "models": {
    "flagship": {
      "model": "openai/gpt-5",
      "description": "最新旗舰",
      "use_case": "最重要任务"
    },
    "reasoning": {
      "model": "openai/o1",
      "description": "推理",
      "use_case": "复杂推理"
    },
    "code_expert": {
      "model": "openai/gpt-oss-120b",
      "description": "代码专家",
      "use_case": "代码任务"
    },
    "general": {
      "model": "meta-llama/llama-3.3-70b-instruct",
      "description": "通用",
      "use_case": "通用任务"
    }
  },
  "limits": {
    "dependent_on": "Copilot subscription"
  },
  "priority": 10,
  "requires_github_copilot": true
}
EOF
echo "✅ GitHub Models配置完成"
echo ""

# ==================== 模型选择脚本 ====================
cat > "$CONFIG_DIR/select-model.sh" << 'SCRIPT'
#!/bin/bash
# 智能模型选择脚本

TASK_TYPE="$1"
CONFIG_DIR="$HOME/.openclaw/providers"

# 检查API Key
check_api_key() {
    local provider="$1"
    local key_var="$2"
    
    if [ -z "${!key_var}" ]; then
        echo "⚠️  警告: $provider API Key未设置"
        return 1
    fi
    
    return 0
}

# 选择模型
select_model() {
    case "$TASK_TYPE" in
        "ultra_fast")
            # 优先级: Groq > OpenRouter > Google
            if check_api_key "Groq" "GROQ_API_KEY"; then
                echo "groq:gemma-3-2b-it"
            elif check_api_key "OpenRouter" "OPENROUTER_API_KEY"; then
                echo "openrouter:google/gemma-3-4b-it:free"
            else
                echo "googleai:gemini-3.1-flash-lite"
            fi
            ;;
        "chinese")
            # 优先级: Google > OpenRouter > Vercel
            if check_api_key "Google AI Studio" "GOOGLE_API_KEY"; then
                echo "googleai:gemini-2.5-flash"
            elif check_api_key "OpenRouter" "OPENROUTER_API_KEY"; then
                echo "openrouter:qwen/qwen3-4b:free"
            else
                echo "googleai:gemini-3-flash"
            fi
            ;;
        "code")
            # 优先级: OpenRouter > Groq > GitHub
            if check_api_key "OpenRouter" "OPENROUTER_API_KEY"; then
                echo "openrouter:openai/gpt-oss-120b:free"
            elif check_api_key "Groq" "GROQ_API_KEY"; then
                echo "groq:openai/gpt-oss-120b"
            elif check_api_key "GitHub Models" "GITHUB_TOKEN"; then
                echo "github:openai/gpt-oss-120b"
            else
                echo "openrouter:qwen/qwen3-coder:free"
            fi
            ;;
        "general")
            # 优先级: Groq > OpenRouter > Google
            if check_api_key "Groq" "GROQ_API_KEY"; then
                echo "groq:llama-3.3-70b-versatile"
            elif check_api_key "OpenRouter" "OPENROUTER_API_KEY"; then
                echo "openrouter:meta-llama/llama-3.3-70b-instruct:free"
            else
                echo "googleai:gemini-3-flash"
            fi
            ;;
        "flagship")
            # 只使用GitHub Models
            if check_api_key "GitHub Models" "GITHUB_TOKEN"; then
                echo "github:openai/gpt-5"
            else
                echo "openrouter:meta-llama/llama-3.3-70b-instruct:free"
            fi
            ;;
        *)
            echo "openrouter:meta-llama/llama-3.3-70b-instruct:free"
            ;;
    esac
}

# 如果没有指定任务类型，默认使用general
if [ -z "$TASK_TYPE" ]; then
    TASK_TYPE="general"
fi

select_model
SCRIPT

chmod +x "$CONFIG_DIR/select-model.sh"
echo "✅ 模型选择脚本已创建"
echo ""

# ==================== 完成提示 ====================
echo "================================"
echo "🎉 免费模型配置完成！"
echo ""
echo "📁 配置位置: $CONFIG_DIR"
echo ""
echo "📋 配置文件:"
echo "  - openrouter-free.json"
echo "  - groq-free.json"
echo "  - googleai-free.json"
echo "  - github-models-free.json"
echo ""
echo "🔧 模型选择脚本:"
echo "  bash $CONFIG_DIR/select-model.sh <task_type>"
echo ""
echo "📖 任务类型:"
echo "  ultra_fast  - 超快速响应"
echo "  chinese    - 中文优化"
echo "  code       - 代码专家"
echo "  general    - 通用任务"
echo "  flagship   - 旗舰模型"
echo ""
echo "⚠️  下一步:"
echo "  1. 设置API Key环境变量"
echo "  2. 测试模型选择"
echo "  3. 集成到日常工作流"
echo ""
echo "📚 完整文档:"
echo "  ~/.openclaw/workspace/.learnings/design-patterns/free-llm-api-complete-list.md"
echo ""
echo "🚀 开始使用免费模型吧！"
