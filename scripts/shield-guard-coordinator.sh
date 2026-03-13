#!/bin/bash
# 🛡️ "盾构"协调脚本
# 统一协调任务分配和 API 调用

set -e

# API Keys - 从环境变量或配置文件读取
GOOGLE_KEY="${GOOGLE_API_KEY:-}"
GROQ_KEY="${GROQ_API_KEY:-}"
OPENROUTER_KEY="${OPENROUTER_API_KEY:-}"

# 检查必需的环境变量
if [[ -z "$GOOGLE_KEY" || -z "$GROQ_KEY" || -z "$OPENROUTER_KEY" ]]; then
    echo "❌ 错误: 缺少必需的 API Keys"
    echo "请设置以下环境变量:"
    echo "  export GOOGLE_API_KEY='your-key'"
    echo "  export GROQ_API_KEY='your-key'"
    echo "  export OPENROUTER_API_KEY='your-key'"
    exit 1
fi

# 颜色定义
ECHO_GREEN='\033[0;32m'
ECHO_YELLOW='\033[1;33m'
ECHO_BLUE='\033[0;34m'
ECHO_NC='\033[0m'

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 错误处理
error_exit() {
    log "❌ $1"
    exit 1
}

# 调用 Google Gemini（设计专家）
call_google() {
    local prompt="$1"
    
    log "🏠 调用 Google Gemini 2.5 Flash..."
    
    response=$(curl -s -X POST \
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GOOGLE_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"contents\": [{\"parts\":[{\"text\": \"${prompt}\"}]}]}")
    
    # 提取并返回结果
    echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'error' in data:
        print(f\"错误: {data['error']['message']}\")
        sys.exit(1)
    text = data['candidates'][0]['content']['parts'][0]['text']
    print(text)
except Exception as e:
    print(f\"解析错误: {e}\")
    sys.exit(1)
"
}

# 调用 Groq（技术专家）
call_groq() {
    local prompt="$1"
    
    log "💻 调用 Groq Llama-3.3-70B..."
    
    response=$(curl -s -X POST \
        "https://api.groq.com/openai/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${GROQ_KEY}" \
        -d "{
            \"model\": \"llama-3.3-70b-versatile\",
            \"messages\": [{\"role\": \"user\", \"content\": \"${prompt}\"}],
            \"max_tokens\": 2000
        }")
    
    # 提取并返回结果
    echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'error' in data:
        print(f\"错误: {data['error']['message']}\")
        sys.exit(1)
    text = data['choices'][0]['message']['content']
    print(text)
except Exception as e:
    print(f\"解析错误: {e}\")
    sys.exit(1)
"
}

# 调用 OpenRouter（日志专家）
call_openrouter() {
    local prompt="$1"
    
    log "📋 调用 OpenRouter Gemma-3-4B..."
    
    response=$(curl -s -X POST \
        "https://openrouter.ai/api/v1/chat/completions" \
        -H "Content-Type: application协调" \
        -H "Authorization: Bearer ${OPENROUTER_KEY}" \
        -H "HTTP-Referer: http://43.134.63.176:18789" \
        -H "X-Title: OpenClaw" \
        -d "{
            \"model\": \"google/gemma-3-4b-it:free\",
            \"messages\": [{\"role\": \"user\", \"content\": \"${prompt}\"}],
            \"max_tokens\": 1000
        }")
    
    # 提取并返回结果
    echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'error' in data:
        print(f\"错误: {data['error']['message']}\")
        sys.exit(1)
    text = data['choices'][0]['message']['content']
    print(text)
except Exception as e:
    print(f\"解析错误: {e}\")
    sys.exit(1)
"
}

# 主函数
main() {
    # 参数检查
    if [ $# -lt 2 ]; then
        echo "🛡️ \"盾构\"协调脚本"
        echo ""
        echo "用法:"
        echo "  $0 <task_type> <prompt>"
        echo ""
        echo "任务类型:"
        echo "  design   - 设计任务（Google Gemini）"
        echo "  tech     - 技术任务（Groq Llama-3.3-70B）"
        echo "  log      - 日志任务（OpenRouter Gemma）"
        "  critical - 关键任务（使用大领导 GLM-4.7）"
        echo ""
        echo "示例:"
        echo "  $0 design \"设计一个客厅\""
        echo "  $0 tech \"写一个Python爬虫\""
        echo "  $0 log \"整理今日工作\""
        echo "  $0 critical \"分析项目风险\""
        echo ""
        exit 1
    fi
    
    TASK_TYPE=$1
    PROMPT=$2
    
    log "🎯 任务类型: $TASK_TYPE"
    log "📝 任务内容: $PROMPT"
    
    # 根据任务类型调用对应的 API
    case $TASK_TYPE in
        design)
            log "🏠 使用：室内设计专家（Google Gemini）"
            result=$(call_google "$PROMPT")
            echo ""
            log "✅ 任务完成"
            ;;
            
        tech)
            log "💻 使用：技术支持专家（Groq Llama-3.3-70B）"
            result=$(call_groq "$PROMPT")
            echo ""
            log "✅ 任务完成"
            ;;
            
        log)
            log "📋 使用：工作日志专家（OpenRouter Gemma）"
            result=$(call_openrouter "$PROMPT")
            echo ""
            log "✅ 任务完成"
            ;;
            
        critical)
            log "🎯 使用：大领导（GLM-4.7）"
            log "这是关键任务，由大领导亲自处理"
            log "⚠️ 注意：这会消耗 GLM Token"
            ;;
            
        *)
            log "❓ 未知任务类型: $TASK_TYPE"
            log "🎯 使用：大领导（GLM-4.7）"
            log "这是关键任务，由大领导处理"
            ;;
    esac
}

# 执行主函数
main "$@"
