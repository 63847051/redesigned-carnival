#!/usr/bin/env python3
import json
import sys

print("🔍 验证配置文件...")
print()

# 验证 openclaw.json
try:
    with open('/root/.openclaw/openclaw.json', 'r') as f:
        config = json.load(f)
    print("✅ openclaw.json 格式正确")
    
    # 检查关键配置
    if 'models' in config:
        print("✅ models 配置存在")
        providers = config['models'].get('providers', {})
        print(f"   提供商数量: {len(providers)}")
        for name in providers.keys():
            print(f"   - {name}")
    
    if 'channels' in config and 'feishu' in config['channels']:
        print("✅ 飞书通道配置存在")
        
    if 'gateway' in config:
        print("✅ Gateway 配置存在")
        
except Exception as e:
    print(f"❌ openclaw.json 错误: {e}")
    sys.exit(1)

# 验证飞书配对文件
try:
    with open('/root/.openclaw/credentials/feishu-pairing.json', 'r') as f:
        pairing = json.load(f)
    print("✅ feishu-pairing.json 存在且有效")
except Exception as e:
    print(f"❌ feishu-pairing.json 错误: {e}")
    sys.exit(1)

print()
print("🎉 所有配置文件验证通过!")
print()

# 显示关键配置
print("📋 关键配置信息:")
print(f"  Gateway 端口: {config.get('gateway', {}).get('port', '未知')}")
print(f"  飞书 App ID: {config.get('channels', {}).get('feishu', {}).get('appId', '未知')[:20]}...")
print(f"  模型提供商: {', '.join(config.get('models', {}).get('providers', {}).keys())}")
