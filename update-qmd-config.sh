#!/bin/bash
# 更新 QMD 配置使用智谱 AI embeddings

echo "🔄 更新 QMD 配置..."
echo ""

# 备份原配置
cp ~/.qmd/config.json ~/.qmd/config.json.backup

# 创建新配置
cat > ~/.qmd/config.json << 'EOF'
{
  "collections": [
    {
      "name": "memory-root",
      "path": "/root/.openclaw/workspace",
      "pattern": "MEMORY.md"
    },
    {
      "name": "memory-dir",
      "path": "/root/.openclaw/workspace/memory",
      "pattern": "**/*.md"
    }
  ],
  "search": {
    "mode": "query",
    "embedding": {
      "provider": "openai",
      "model": "embedding-2",
      "baseUrl": "https://open.bigmodel.cn/api/paas/v4",
      "apiKey": "c26c6bd6acfc44cda167b15dc338dabc.Hmfe3HhV5TjJiXqp"
    }
  }
}
EOF

echo "✅ QMD 配置已更新！"
echo ""
echo "📋 新配置:"
echo "  - Provider: 智谱 AI (GLM)"
echo "  - Model: embedding-2"
echo "  - Dimensions: 1024"
echo "  - Cost: 免费（已包含在 GLM API 中）"
echo ""
echo "🔄 下一步: 运行 'qmd embed' 生成 embeddings"
