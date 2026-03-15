#!/usr/bin/env python3
"""
OpenClaw 前端修复补丁

修复 OpenClaw 2026.3.13 前端无法读取 model 字符串的问题
在前端代码中添加适配层，自动将字符串转换为对象
"""

import json
import re
from pathlib import Path

def patch_frontend_code():
    """
    修补前端代码，让它能读取字符串格式的 model
    """
    # 前端代码路径（需要根据实际情况调整）
    frontend_paths = [
        Path("/root/.openclaw/ui/dist/assets/*.js"),
        Path("/root/.openclaw/web/dist/*.js"),
        Path("/root/.openclaw/node_modules/openclaw-ui/dist/*.js"),
    ]
    
    print("🔍 搜索前端代码...")
    
    # 这是一个示例，实际需要找到正确的文件
    # 并进行字符串替换
    print("⚠️  需要手动修补前端代码")
    print()
    print("📝 修补方法:")
    print("1. 找到前端代码中读取 model 的地方")
    print("2. 添加适配层:")
    print("   if (typeof model === 'string') {")
    print("     model = { primary: model, fallback: [] };")
    print("   }")
    
    return False

def create_wrapper_script():
    """
    创建一个包装脚本，在前端启动前自动转换配置
    """
    wrapper_script = """#!/bin/bash
# OpenClaw 前端启动包装脚本

CONFIG_FILE="/root/.openclaw/openclaw.json"
BACKUP_FILE="/root/.openclaw/openclaw.json.pre-frontend"

# 备份配置
cp "$CONFIG_FILE" "$BACKUP_FILE"

# 读取配置
python3 << 'PYTHON_EOF'
import json

with open("$CONFIG_FILE") as f:
    config = json.load(f)

# 获取当前模型
current_model = config.get('agents', {}).get('defaults', {}).get('model')

# 如果是字符串，转换为对象（前端兼容）
if isinstance(current_model, str):
    frontend_model = {
        "primary": current_model,
        "fallback": []
    }
    config['agents']['defaults']['model'] = frontend_model
    print(f"📱 前端模式: 模型转换为对象格式")
else:
    print(f"📱 前端模式: 已是对象格式")

# 保存为前端专用配置
with open("$CONFIG_FILE", 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print("✅ 前端配置已准备")
PYTHON_EOF

# 启动前端
echo "🚀 启动 OpenClaw 前端..."
# 这里添加实际的前端启动命令
"""
    
    wrapper_path = Path("/root/.openclaw/workspace/scripts/start-frontend.sh")
    with open(wrapper_path, 'w') as f:
        f.write(wrapper_script)
    
    wrapper_path.chmod(0o755)
    
    print(f"✅ 包装脚本已创建: {wrapper_path}")
    print(f"\n📝 使用方法:")
    print(f"   启动前端前运行: {wrapper_path}")
    
    return True

def main():
    print("🔧 OpenClaw 前端修复工具")
    print()
    
    print("⚠️  自动修补可能不可用，建议手动修复")
    print()
    print("💡 推荐方案:")
    print("1. 暂时不要使用前端界面切换模型")
    print("2. 使用命令行工具切换模型")
    print("3. 等待 OpenClaw 官方修复前后端兼容问题")
    print()
    
    create_wrapper_script()
    
    print("\n📚 或者使用简化版前端:")
    print("   只查看配置，不编辑配置")

if __name__ == "__main__":
    main()
