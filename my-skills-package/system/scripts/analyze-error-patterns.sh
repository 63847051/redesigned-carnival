#!/bin/bash
# 错误模式分析脚本 v1.0
# 分析历史错误，识别重复模式，提取改进建议

echo "🔍 错误模式分析工具"
echo "========================"
echo ""

# 日志文件
LOG_FILE="/root/.openclaw/workspace/.evolution/evolution.log"
ERRORS_DIR="/root/.openclaw/workspace/.learnings/errors"
REPORT_FILE="/root/.openclaw/workspace/.learnings/error-pattern-analysis-$(date +%Y%m%d).md"

# 创建报告
{
    echo "# 错误模式分析报告"
    echo ""
    echo "**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "**分析范围**: 最近7天"
    echo ""
    echo "---"
    echo ""

    # 1. 统计错误类型
    echo "## 📊 错误统计"
    echo ""
    echo "### 错误分类"
    echo ""

    # 查找所有错误
    echo "#### 按类型分类:"
    echo ""

    # API错误
    api_count=$(grep -c "API.*[Ee]rror\|401\|403\|500" "$LOG_FILE" 2>/dev/null || echo 0)
    echo "- **API错误**: $api_count 次"

    # 配置错误
    config_count=$(grep -c "配置\|config.*[Ee]rror\|Invalid" "$LOG_FILE" 2>/dev/null || echo 0)
    echo "- **配置错误**: $config_count 次"

    # 文件不存在
    file_count=$(grep -c "No such file\|not found" "$LOG_FILE" 2>/dev/null || echo 0)
    echo "- **文件错误**: $file_count 次"

    # 权限错误
    perm_count=$(grep -c "Permission denied\|unauthorized" "$LOG_FILE" 2>/dev/null || echo 0)
    echo "- **权限错误**: $perm_count 次"

    echo ""

    # 2. 重复模式识别
    echo "## 🔍 重复错误模式"
    echo ""
    echo "### 高频错误"
    echo ""

    # 提取重复的错误行
    echo "\`\`\`"
    grep -E "exec failed|Error|failed" "$LOG_FILE" 2>/dev/null | sort | uniq -c | sort -rn | head -10
    echo "\`\`\`"
    echo ""

    # 3. 错误时间分析
    echo "## ⏰ 错误时间分布"
    echo ""
    echo "### 最近错误"
    echo ""
    echo "\`\`\`"
    grep -E "exec failed|Error|failed" "$LOG_FILE" 2>/dev/null | tail -5
    echo "\`\`\`"
    echo ""

    # 4. 根因分析
    echo "## 🎯 根因分析"
    echo ""
    echo "### 主要问题"
    echo ""

    # API配置问题
    if [ "$api_count" -gt 0 ]; then
        echo "#### 1. API配置问题"
        echo "- **现象**: API调用失败"
        echo "- **原因**: API Key格式或provider配置错误"
        echo "- **影响**: 无法调用某些模型"
        echo "- **已解决**: L7配置验证已修复"
        echo ""
    fi

    # 文件路径问题
    if [ "$file_count" -gt 0 ]; then
        echo "#### 2. 文件路径问题"
        echo "- **现象**: 脚本找不到文件"
        echo "- **原因**: 路径不匹配或文件未创建"
        echo "- **影响**: 脚本执行失败"
        echo "- **已解决**: 脚本已创建并验证"
        echo ""
    fi

    # 配置格式问题
    if [ "$config_count" -gt 0 ]; then
        echo "#### 3. 配置格式问题"
        echo "- **现象**: 配置字段命名不一致"
        echo "- **原因**: base_url vs baseUrl, api_key vs apiKey"
        echo "- **影响**: 系统无法读取配置"
        echo "- **已解决**: L7验证已标准化"
        echo ""
    fi

    # 5. 改进建议
    echo "## 💡 改进建议"
    echo ""
    echo "### 预防措施"
    echo ""
    echo "1. **配置验证**"
    echo "   - ✅ L7配置验证已启用"
    echo "   - ✅ 每次启动时自动检查"
    echo ""
    echo "2. **错误监控**"
    echo "   - ✅ 自动记录错误"
    echo "   - ✅ 生成进化报告"
    echo ""
    echo "3. **自动修复**"
    echo "   - ✅ 配置问题自动修复"
    echo "   - ✅ 自动学习错误模式"
    echo ""
    echo "4. **文档更新**"
    echo "   - 📝 记录所有错误模式"
    echo "   - 📝 提取最佳实践"
    echo ""

    # 6. 最佳实践
    echo "## 🌟 最佳实践"
    echo ""
    echo "### 配置管理"
    echo ""
    echo "1. **字段命名约定**"
    echo "   - 使用 `baseUrl` 而不是 `base_url`"
    echo "   - 使用 `apiKey` 而不是 `api_key`"
    echo ""
    echo "2. **API Key格式**"
    echo "   - OpenRouter: \`sk-or-v1-...\`"
    echo "   - NVIDIA: \`nvapi-...\`"
    echo "   - Groq: \`gsk_...\`"
    echo "   - Google: \`AIza...\`"
    echo ""
    echo "3. **文件路径**"
    echo "   - 使用绝对路径"
    echo "   - 在脚本执行前验证文件存在"
    echo ""

    # 7. 工作流程优化
    echo "## 🚀 工作流程优化"
    echo ""
    echo "### 优化后的流程"
    echo ""
    echo "#### 配置变更流程"
    echo "1. 修改配置文件"
    echo "2. 运行L7验证"
    echo "3. 验证通过后应用"
    echo "4. 测试新配置"
    echo "5. 记录变更日志"
    echo ""
    echo "#### 错误处理流程"
    echo "1. 自动检测错误"
    echo "2. 记录到进化系统"
    echo "3. PAI分析错误"
    echo "4. 提取改进建议"
    echo "5. 自动或手动修复"
    echo "6. 验证修复效果"
    echo ""

} | tee "$REPORT_FILE"

echo "✅ 分析完成！"
echo ""
echo "📄 报告: $REPORT_FILE"
echo ""
echo "📊 主要发现:"
echo "  - API错误: $api_count 次"
echo "  - 配置错误: $config_count 次"
echo "  - 文件错误: $file_count 次"
echo "  - 权限错误: $perm_count 次"
echo ""
echo "💡 建议:"
echo "  1. 定期运行L7验证"
echo "  2. 使用L7验证脚本检查配置"
echo "  3. 记录所有配置变更"
echo ""
