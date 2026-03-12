#!/bin/bash
# 永久使用免费模型的配置脚本
# 修改 openclaw.json，将默认模型改为免费模型

CONFIG_FILE="/root/.openclaw/openclaw.json"
BACKUP_FILE="/root/.openclaw/openclaw-backup-$(date +%Y%m%d_%H%M%S).json"

echo "🔄 切换到免费模型..."
echo ""

# 备份原配置
echo "📦 备份当前配置..."
cp "$CONFIG_FILE" "$BACKUP_FILE"
echo "备份: $BACKUP_FILE"
echo ""

# 检查配置
echo "🔍 当前配置:"
grep '"model":' "$CONFIG_FILE" | head -5
echo ""

# 修改默认模型
echo "🔄 修改默认模型为免费模型..."

# 使用Python修改JSON
python3 << 'PYTHON'
import json

# 读取配置
with open("$CONFIG_FILE", 'r', encoding='utf-8') as f:
    config = json.load(f)

# 修改默认模型（如果有）
if 'model' in config.get('defaults', {}):
    config['defaults']['model'] = 'glmcode/glm-4.5-air'
    print("✅ 默认模型已修改为: glmcode/glm-4.5-air")
elif 'agents' in config:
    if 'defaults' in config.get('agents', {}):
        config['agents']['defaults']['model'] = 'glmcode/glm-4.5-air'
        print("✅ agents.defaults.model已修改为: glmcode/glm-4.5-air")
    else:
        config['agents']['defaults'] = {'model': 'glmcode/glm-4.5-air'}
        print("✅ 添加 agents.defaults.model: glmcode/glm-4.5-air")
else:
    # 添加新配置
    config['defaults'] = {'model': 'glmcode/glm-4.5-air'}
    print("✅ 添加默认模型: glmcode/glm-4.5-air")

# 写回文件
with open("$CONFIG_FILE", 'w', encoding='-utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print("✅ 配置已保存")
print(f"文件: {CONFIG_FILE}")
PYTHON

# 验证修改
echo ""
echo "🔍 验证修改..."
grep '"model".*:' "$CONFIG_FILE" | head -5

echo ""
echo "🎉 切换完成！"
echo ""
echo "💡 现在默认使用: glmcode/glm-4.5-air (免费)"
echo ""
echo "📋 其他可用免费模型:"
echo "  - OpenRouter Gemma 3 4B (超快)"
echo "  - NVIDIA gpt-oss-120b (代码)"
echo "  - Google Gemini 3 Flash (中文)"
echo ""
echo "🔄 恢复配置:"
echo "  cp $BACKUP_FILE $CONFIG_FILE"
