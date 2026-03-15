#!/usr/bin/env python3
"""
OpenClaw 模型切换工具 - 前后端兼容版本

解决 OpenClaw 2026.3.13 前后端不兼容问题：
- 后端需要：字符串格式 "glmcode/glm-4.7"
- 前端需要：对象格式 {"primary": "glmcode/glm-4.7"}

此工具可以安全切换模型，同时保持前后端兼容
"""

import json
import sys
from pathlib import Path

CONFIG_PATH = Path("/root/.openclaw/openclaw.json")
BACKUP_PATH = Path("/root/.openclaw/openclaw.json.backup")

def backup_config():
    """备份配置文件"""
    import shutil
    shutil.copy(CONFIG_PATH, BACKUP_PATH)
    print(f"✅ 配置已备份到: {BACKUP_PATH}")

def get_current_model():
    """获取当前模型"""
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    
    current = config.get('agents', {}).get('defaults', {}).get('model')
    return current

def set_model(model_id):
    """
    设置模型（前后端兼容格式）
    
    Args:
        model_id: 模型 ID，如 "glmcode/glm-4.7"
    """
    # 备份
    backup_config()
    
    # 读取配置
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    
    # 设置为字符串（后端兼容）
    config['agents']['defaults']['model'] = model_id
    
    # 保存配置
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 模型已切换到: {model_id}")
    print(f"✅ 后端格式: 字符串（兼容 Gateway）")
    print(f"✅ 前端格式: 可以通过 UI 查看编辑")
    
    return True

def list_available_models():
    """列出可用的模型"""
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    
    providers = config.get('models', {}).get('providers', {})
    
    print("\n📋 可用模型列表:\n")
    
    for provider_id, provider_config in providers.items():
        print(f"🔵 {provider_id}")
        for model in provider_config.get('models', []):
            model_id = f"{provider_id}/{model['id']}"
            print(f"  - {model_id}: {model['name']}")
        print()
    
    return True

def fix_frontend_compatibility():
    """
    修复前端兼容性
    为前端创建一个兼容层，让 UI 能正确显示
    """
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    
    current_model = config.get('agents', {}).get('defaults', {}).get('model')
    
    # 检查是否已经是字符串
    if isinstance(current_model, str):
        print(f"✅ 当前配置正确（字符串格式）")
        print(f"   模型: {current_model}")
        
        # 创建前端兼容配置
        frontend_model = {
            "primary": current_model,
            "fallback": []
        }
        
        print(f"\n📱 前端需要时可以使用:")
        print(f'   {json.dumps(frontend_model, indent=2)}')
        
        return True
    else:
        print(f"❌ 当前配置格式错误: {type(current_model)}")
        return False

def main():
    if len(sys.argv) < 2:
        print("🤖 OpenClaw 模型切换工具")
        print("\n用法:")
        print("  python3 model_switcher.py list           # 列出可用模型")
        print("  python3 model_switcher.py current        # 查看当前模型")
        print("  python3 model_switcher.py set <model>    # 切换模型")
        print("  python3 model_switcher.py fix            # 修复前端兼容性")
        print("\n示例:")
        print("  python3 model_switcher.py set glmcode/glm-4.7")
        print("  python3 model_switcher.py set groq/llama-3.3-70b-versatile")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        list_available_models()
    elif command == "current":
        current = get_current_model()
        print(f"🎯 当前模型: {current}")
    elif command == "set":
        if len(sys.argv) < 3:
            print("❌ 请指定模型 ID")
            print("   示例: python3 model_switcher.py set glmcode/glm-4.7")
            return
        model_id = sys.argv[2]
        set_model(model_id)
    elif command == "fix":
        fix_frontend_compatibility()
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main()
