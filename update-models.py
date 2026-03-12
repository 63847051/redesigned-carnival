#!/usr/bin/env python3
import json
import shutil

# 读取当前配置
with open('/root/.openclaw/openclaw.json', 'r') as f:
    config = json.load(f)

# 添加新的提供商
config['models']['providers']['groq'] = {
    "baseUrl": "https://api.groq.com/openai/v1",
    "apiKey": "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",
    "models": [
        {"id": "llama-3.3-70b-versatile", "name": "Llama-3.3-70B"},
        {"id": "mixtral-8x7b-32768", "name": "Mixtral-8x7B"}
    ]
}

config['models']['providers']['google'] = {
    "baseUrl": "https://generativelanguage.googleapis.com/v1beta",
    "apiKey": "AIzaSyAcMMIXeaM7Or0Z2HA20z00VgWG8RxXHyg",
    "api": "vertex",
    "models": [
        {"id": "gemini-2.5-flash", "name": "Gemini-2.5-Flash"}
    ]
}

# 备份原文件
shutil.copy('/root/.openclaw/openclaw.json', '/root/.openclaw/openclaw.json.backup')

# 写入新配置
with open('/root/.openclaw/openclaw.json', 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print("✅ 配置已更新!")
print("\n新增提供商:")
print("  🚀 Groq - Llama-3.3-70B (超快速)")
print("  🌏 Google - Gemini-2.5-Flash (中文优化)")
print("\n备份: /root/.openclaw/openclaw.json.backup")
