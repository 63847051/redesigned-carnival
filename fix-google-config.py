#!/usr/bin/env python3
import json

# 读取配置
with open('/root/.openclaw/openclaw.json', 'r') as f:
    config = json.load(f)

# 修复 Google 配置
config['models']['providers']['google']['api'] = 'google-generative-ai'

# 写回
with open('/root/.openclaw/openclaw.json', 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print("✅ Google 配置已修复!")
print("   api: vertex → google-generative-ai")
