#!/usr/bin/env python3
"""
OpenCLI 集成测试脚本
测试 OpenCLI 包装器的基本功能
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/opencli')

from opencli_wrapper import OpenCLIWrapper


def test_opencli_version():
    """测试 OpenCLI 是否正确安装"""
    import subprocess
    
    print("🔍 测试 1: 检查 OpenCLI 版本...")
    try:
        result = subprocess.run(
            ['opencli', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✅ OpenCLI 版本: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ OpenCLI 未正确安装")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_wrapper_initialization():
    """测试包装器初始化"""
    print("\n🔍 测试 2: 包装器初始化...")
    
    try:
        wrapper = OpenCLIWrapper()
        print("✅ 包装器初始化成功")
        return True
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False


def test_list_commands():
    """测试列出所有命令"""
    print("\n🔍 测试 3: 列出所有可用命令...")
    
    try:
        wrapper = OpenCLIWrapper()
        result = wrapper.list_all_commands()
        
        if result['status'] == 'success':
            # 统计命令数量
            commands = result['data']
            line_count = len(commands.split('\n'))
            print(f"✅ 成功获取命令列表（约 {line_count} 行）")
            print(f"📄 前 5 行预览:")
            print('\n'.join(commands.split('\n')[:5]))
            return True
        else:
            print(f"❌ 获取命令列表失败: {result['error']}")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_public_api():
    """测试公开 API（不需要登录）"""
    print("\n🔍 测试 4: 测试公开 API（BBC 新闻）...")
    
    try:
        wrapper = OpenCLIWrapper()
        result = wrapper.run_command('bbc', 'news', format='json')
        
        if result['status'] == 'success':
            data = result['data']
            if isinstance(data, list) and len(data) > 0:
                print(f"✅ 成功获取 BBC 新闻（{len(data)} 条）")
                print(f"📰 第一条: {data[0].get('title', 'N/A')}")
                return True
            else:
                print("⚠️ 返回数据格式不符合预期")
                return False
        else:
            print(f"⚠️ API 调用失败: {result['error']}")
            print("💡 这可能是因为浏览器扩展未安装或未连接")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_bilibili_hot():
    """测试 B 站热门（需要登录）"""
    print("\n🔍 测试 5: 测试 B 站热门（需要浏览器登录）...")
    
    try:
        wrapper = OpenCLIWrapper()
        result = wrapper.bilibili_hot(format='json')
        
        if result['status'] == 'success':
            data = result['data']
            if isinstance(data, list) and len(data) > 0:
                print(f"✅ 成功获取 B 站热门（{len(data)} 条）")
                if isinstance(data[0], dict):
                    print(f"🎬 第一条: {data[0].get('title', 'N/A')}")
                return True
            else:
                print("⚠️ 返回数据为空或格式不符合预期")
                print("💡 这可能是因为未在浏览器中登录 B 站")
                return False
        else:
            print(f"⚠️ API 调用失败: {result['error']}")
            print("💡 确保已安装 Chrome 扩展并在浏览器中登录 B 站")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 OpenCLI 集成测试")
    print("=" * 60)
    
    tests = [
        test_opencli_version,
        test_wrapper_initialization,
        test_list_commands,
        test_public_api,
        test_bilibili_hot,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append(False)
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ 通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！")
    elif passed >= 3:
        print("⚠️ 部分测试通过（基础功能可用）")
        print("💡 某些需要登录的功能可能需要配置浏览器扩展")
    else:
        print("❌ 多个测试失败，请检查安装")
    
    print("\n📚 下一步:")
    print("1. 如果浏览器扩展未安装，请访问:")
    print("   https://github.com/jackwener/opencli")
    print("2. 安装 Chrome 扩展后，重新测试")
    print("3. 使用 'opencli doctor' 诊断连接问题")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
