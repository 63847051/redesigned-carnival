#!/bin/bash
# 集成测试脚本 v1.0
# 测试所有优化组件的协同工作

set -e

echo "🧪 集成测试开始"
echo "⏰ 时间: $(date)"
echo ""

# =============================================================================
# 📊 测试结果统计
# =============================================================================

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

test_result() {
    local test_name=$1
    local result=$2

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    if [ "$result" = "pass" ]; then
        echo "  ✅ $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo "  ❌ $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# =============================================================================
# 🔍 测试 1: API 不变量保护
# =============================================================================

echo "🔍 测试 1: API 不变量保护"
echo ""

bash /root/.openclaw/workspace/scripts/api-invariant-guard.sh test >/dev/null 2>&1
if [ $? -eq 0 ]; then
    test_result "API 调用成功" "pass"
else
    test_result "API 调用失败" "fail"
fi

bash /root/.openclaw/workspace/scripts/api-invariant-guard.sh status >/dev/null 2>&1
if [ $? -eq 0 ]; then
    test_result "状态查询正常" "pass"
else
    test_result "状态查询失败" "fail"
fi

echo ""

# =============================================================================
# 💾 测试 2: 缓存一致性管理
# =============================================================================

echo "💾 测试 2: 缓存一致性管理"
echo ""

bash /root/.openclaw/workspace/scripts/cache-consistency-manager.sh test >/dev/null 2>&1
if [ $? -eq 0 ]; then
    test_result "缓存操作正常" "pass"
else
    test_result "缓存操作失败" "fail"
fi

bash /root/.openclaw/workspace/scripts/cache-consistency-manager.sh stats >/dev/null 2>&1
if [ $? -eq 0 ]; then
    test_result "统计查询正常" "pass"
else
    test_result "统计查询失败" "fail"
fi

echo ""

# =============================================================================
# 🚩 测试 3: Feature Flag 控制
# =============================================================================

echo "🚩 测试 3: Feature Flag 控制"
echo ""

# 创建测试 Flag
bash /root/.openclaw/workspace/scripts/feature-flag-controller.sh create "test-integration" "集成测试" true >/dev/null 2>&1
if [ $? -eq 0 ]; then
    test_result "Flag 创建成功" "pass"
else
    test_result "Flag 创建失败" "fail"
fi

# 禁用 Flag
bash /root/.openclaw/workspace/scripts/feature-flag-controller.sh disable "test-integration" >/dev/null 2>&1
if [ $? -eq 0 ]; then
    test_result "Flag 禁用成功" "pass"
else
    test_result "Flag 禁用失败" "fail"
fi

# 删除 Flag
bash /root/.openclaw/workspace/scripts/feature-flag-controller.sh delete "test-integration" >/dev/null 2>&1
if [ $? -eq 0 ]; then
    test_result "Flag 删除成功" "pass"
else
    test_result "Flag 删除失败" "fail"
fi

echo ""

# =============================================================================
# 🧠 测试 4: 记忆系统组件
# =============================================================================

echo "🧠 测试 4: 记忆系统组件"
echo ""

# 测试记忆新鲜度
bash /root/.openclaw/workspace/scripts/memory-freshness-system-v1.sh >/dev/null 2>&1
if [ $? -eq 0 ]; then
    test_result "新鲜度系统正常" "pass"
else
    test_result "新鲜度系统失败" "fail"
fi

# 测试记忆召回
bash /root/.openclaw/workspace/scripts/memory-recall-fallback-v1.sh "测试" >/dev/null 2>&1
if [ $? -eq 0 ]; then
    test_result "召回降级正常" "pass"
else
    test_result "召回降级失败" "fail"
fi

echo ""

# =============================================================================
# 🔐 测试 5: AutoDream 熔断器
# =============================================================================

echo "🔐 测试 5: AutoDream 熔断器"
echo ""

bash /root/.openclaw/workspace/scripts/auto-dream-v4-circuit-breaker.sh >/dev/null 2>&1
if [ $? -eq 0 ]; then
    test_result "熔断器检查正常" "pass"
else
    test_result "熔断器检查失败" "fail"
fi

echo ""

# =============================================================================
# 📊 测试 6: 系统健康状态
# =============================================================================

echo "📊 测试 6: 系统健康状态"
echo ""

# 检查 Gateway
GATEWAY_STATUS=$(systemctl --user is-active openclaw-gateway 2>/dev/null || echo "unknown")
if [ "$GATEWAY_STATUS" = "active" ]; then
    test_result "Gateway 运行正常" "pass"
else
    test_result "Gateway 未运行" "fail"
fi

# 检查内存
MEMORY_USAGE=$(free | awk '/Mem/{printf("%.0f"), $3/$2*100}')
if [ $MEMORY_USAGE -lt 90 ]; then
    test_result "内存使用正常 ($MEMORY_USAGE%)" "pass"
else
    test_result "内存使用过高 ($MEMORY_USAGE%)" "fail"
fi

# 检查配置文件
python3 -c "import json; json.load(open('/root/.openclaw/openclaw.json'))" 2>/dev/null
if [ $? -eq 0 ]; then
    test_result "配置文件有效" "pass"
else
    test_result "配置文件损坏" "fail"
fi

echo ""

# =============================================================================
# 🎯 测试 7: 组件协同工作
# =============================================================================

echo "🎯 测试 7: 组件协同工作"
echo ""

# 测试 API 调用 + 缓存
echo "  🔄 测试 API 调用..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
    https://open.bigmodel.cn/api/anthropic/v1/messages \
    -H "Content-Type: application/json" \
    -H "x-api-key: c26c6bd6acfc44cda167b15dc338dabc.Hmfe3HhV5TjJiXqp" \
    -H "anthropic-version: 2023-06-01" \
    -d '{"model":"glm-4.7","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}')

if [ "$HTTP_CODE" = "200" ]; then
    test_result "API 调用成功" "pass"
else
    test_result "API 调用失败 (HTTP $HTTP_CODE)" "fail"
fi

# 测试记忆搜索
echo "  🔍 测试记忆搜索..."
SEARCH_RESULT=$(bash /root/.openclaw/workspace/scripts/memory-recall-fallback-v1.sh "优化" 2>/dev/null | grep -c "✅ 第一层找到")
if [ $SEARCH_RESULT -gt 0 ]; then
    test_result "记忆搜索正常" "pass"
else
    test_result "记忆搜索失败" "fail"
fi

echo ""

# =============================================================================
# 📈 测试总结
# =============================================================================

echo "📈 测试总结"
echo ""
echo "  总测试数: $TOTAL_TESTS"
echo "  通过: $PASSED_TESTS"
echo "  失败: $FAILED_TESTS"
echo ""

PASS_RATE=$(awk "BEGIN {printf \"%.1f\", ($PASSED_TESTS/$TOTAL_TESTS)*100}")
echo "  通过率: $PASS_RATE%"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo "🎉 所有测试通过！系统运行正常！"
    exit 0
else
    echo "⚠️ 有 $FAILED_TESTS 个测试失败，请检查"
    exit 1
fi
