#!/bin/bash
# OpenCode 免费模型快捷方式

# 快速使用 OpenCode 免费模型（minimax-m2.5-free）
alias ocode='/root/.opencode/bin/opencode run'
alias ocode-free='/root/.opencode/bin/opencode run -m opencode/minimax-m2.5-free'

# 备用免费模型（nemotron-3-super-free）
alias ocode-backup='/root/.opencode/bin/opencode run -m opencode/nemotron-3-super-free'

# 快速响应模型（mimo-v2-flash-free）
alias ocode-fast='/root/.opencode/bin/opencode run -m opencode/mimo-v2-flash-free'

echo "✅ OpenCode 免费模型别名已加载"
echo "  ocode    - 默认免费模型（minimax-m2.5-free）"
echo "  ocode-free - 明确指定免费模型"
echo "  ocode-backup - 备用免费模型"
echo "  ocode-fast  - 快速响应模型"
echo ""
echo "使用示例："
echo "  ocode '写一个Python函数来...'"
echo "  ocode-free '审查这个代码'"
echo "  ocode-fast '快速总结一下'"
