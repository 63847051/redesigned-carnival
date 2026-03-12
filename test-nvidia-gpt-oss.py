#!/usr/bin/env python3
"""
NVIDIA免费gpt-oss-120b配置测试
使用NVIDIA NIM API访问gpt-oss-120b
"""

import os

# NVIDIA配置
NVIDIA_API_KEY = "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"
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

def test_nvidia_gpt_oss():
    """测试NVIDIA的gpt-oss-120b"""
    try:
        from openai import OpenAI
        
        print("🧪 测试 NVIDIA gpt-oss-120b")
        print("=" * 50)
        print()
        
        # 创建客户端
        client = OpenAI(
            base_url=NVIDIA_BASE_URL,
            api_key=NVIDIA_API_KEY
        )
        
        print("📡 发送测试请求...")
        print()
        
        # 发送测试消息
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": "你好！请回复：NVIDIA测试成功！"}],
            temperature=1,
            top_p=1,
            max_tokens=100,
            stream=False
        )
        
        # 获取响应
        response = completion.choices[0].message.content
        
        print("✅ 成功！")
        print()
        print("📝 响应:")
        print(response)
        print()
        print("=" * 50)
        print("🎉 NVIDIA gpt-oss-120b 可用！")
        
        return True
        
    except ImportError:
        print("❌ 错误: 需要安装 openai 库")
        print("安装命令: pip install openai")
        return False
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False

def test_streaming():
    """测试流式响应"""
    try:
        from openai import OpenAI
        
        print()
        print("=" * 50)
        print("🌊 测试流式响应")
        print("=" * 50)
        print()
        
        client = OpenAI(
            base_url=NVIDIA_BASE_URL,
            api_key=NVIDIA_API_KEY
        )
        
        print("📡 发送流式请求...")
        print()
        print("📝 响应:")
        print()
        
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": "用一句话介绍你自己"}],
            temperature=1,
            top_p=1,
            max_tokens=200,
            stream=True
        )
        
        for chunk in completion:
            if not hasattr(chunk, 'choices') or not chunk.choices:
                continue
            
            # 检查推理内容
            delta = chunk.choices[0].delta
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                print(delta.reasoning_content, end="", flush=True)
            
            # 检查内容
            if hasattr(delta, 'content') and delta.content:
                print(delta.content, end="", flush=True)
        
        print()
        print()
        print("✅ 流式响应完成！")
        
        return True
        
    except Exception as e:
        print(f"❌ 流式测试失败: {e}")
        return False

if __name__ == "__main__":
    # 测试普通请求
    if test_nvidia_gpt_oss():
        print()
        print("💡 说明:")
        print("  - ✅ NVIDIA gpt-oss-120b 可用")
        print("  - ✅ 120B参数的GPT模型")
        print("  - ✅ 代码专家级性能")
        print("  - ✅ 完全免费")
        print()
        
        # 测试流式响应
        test_streaming()
        
        print()
        print("🚀 可以使用！配置如下:")
        print()
        print("import os")
        print("from openai import OpenAI")
        print()
        print("client = OpenAI(")
        print(f'    base_url=\"{NVIDIA_BASE_URL}\",')
        print(f'    api_key=\"{NVIDIA_API_KEY}\"')
        print(")")
        print("completion = client.chat.completions.create(")
        print("    model=\"openai/gpt-oss-120b\",")
        print("    messages=[{\"role\": \"user\", \"content\": \"Hello!\"}]]")
        print(")")
