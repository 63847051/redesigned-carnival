#!/bin/bash
# 🧬 超级进化系统（SES）v3.0 - 增强版任务后评估
# 集成ivangdavila/self-improving的四步自我改进循环

set -e

WORKSPACE="/root/.openclaw/workspace"
SELF_CRITIQUE="$WORKSPACE/scripts/self-critique-module.sh"
AUTO_MEMORY="$WORKSPACE/scripts/auto-organize-memory.sh"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}📊 任务后强制评估 v3.0${NC}"
echo -e "${GREEN}========================${NC}"
echo ""

# ============================================================================
# 阶段1: 自我反思 (Reflect)
# =============================================================================

echo -e "${BLUE}🔍 阶段1: 自我反思${NC}"
echo "======================"
echo ""

reflect_phase() {
    echo "📋 任务分配评估："
    echo "  ❓ 我分配这个任务了吗？"
    read -p "  [y/n]: " allocated
    echo ""

    echo "🎯 API 选择评估："
    echo "  ❓ 我用了最合适的 API 吗？"
    read -p "  [y/n]: " optimal
    echo ""

    echo "💡 透明化评估："
    echo "  ❓ 我透明化汇报了吗？"
    echo "  ❓ 我说了用了谁、什么模型、为什么吗？"
    read -p "  [y/n]: " transparent
    echo ""

    echo "🎯 直接答案评估："
    echo "  ❓ 我给用户直接答案了吗？"
    echo "  ❓ 我让用户自己去查了吗？"
    read -p "  [y/n]: " direct_answer
    echo ""

    echo "✅ 验证评估："
    echo "  ❓ 我验证信息了吗？"
    echo "  ❓ 我给出准确答案了吗？"
    read -p "  [y/n]: " verified
    echo ""

    # 计算反思得分
    score=0
    [ "$allocated" = "y" ] && score=$((score+1))
    [ "$optimal" = "y" ] && score=$((score+1))
    [ "$transparent" = "y" ] && score=$((score+1))
    [ "$direct_answer" = "y" ] && score=$((score+1))
    [ "$verified" = "y" ] && score=$((score+1))

    echo -e "${GREEN}✓ 反思得分: $score/5${NC}"
    echo ""

    # 保存反思结果
    mkdir -p "$WORKSPACE/.learnings/reflections"
    {
        echo "# 任务反思"
        echo ""
        echo "**时间**: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "**得分**: $score/5"
        echo ""
        echo "## 评估结果"
        echo ""
        echo "- 任务分配: $allocated"
        echo "- API选择: $optimal"
        echo "- 透明化: $transparent"
        echo "- 直接答案: $direct_answer"
        echo "- 验证: $verified"
        echo ""
    } > "$WORKSPACE/.learnings/reflections/reflection_$(date +%Y%m%d_%H%M%S).md"
}

reflect_phase

# ============================================================================
# 阶段2: 自我批评 (Criticize)
# =============================================================================

echo -e "${BLUE}🔍 阶段2: 自我批评${NC}"
echo "======================"
echo ""

critique_phase() {
    echo "📝 自我批评："
    echo ""

    # 根据反思结果进行批评
    if [ "$score" -lt 5 ]; then
        echo "⚠️  发现问题："
        echo ""

        [ "$allocated" != "y" ] && echo "  - ❌ 未正确分配任务"
        [ "$optimal" != "y" ] && echo "  - ❌ 未选择最优API"
        [ "$transparent" != "y" ] && echo "  - ❌ 未透明化汇报"
        [ "$direct_answer" != "y" ] && echo "  - ❌ 未给出直接答案"
        [ "$verified" != "y" ] && echo "  - ❌ 未验证信息"
        echo ""

        echo "💡 改进建议："
        echo ""

        [ "$allocated" != "y" ] && echo "  - 需要改进任务分配逻辑"
        [ "$optimal" != "y" ] && echo "  - 需要优化API选择策略"
        [ "$transparent" != "y" ] && echo "  - 需要透明化汇报过程"
        [ "$direct_answer" != "y" ] && echo "  - 需要直接给出答案"
        [ "$verified" != "y" ] && echo "  - 需要验证所有信息"
        echo ""
    else
        echo "✅ 任务执行良好！"
        echo ""
        echo "💡 继续保持："
        echo "  - 正确分配任务"
        echo "  - 选择最优API"
        echo "  - 透明化汇报"
        echo "  - 给出直接答案"
        echo "  - 验证所有信息"
        echo ""
    fi

    # 保存批评结果
    mkdir -p "$WORKSPACE/.learnings/self-critiques"
    {
        echo "# 自我批评"
        echo ""
        echo "**时间**: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "**反思得分**: $score/5"
        echo ""
        echo "## 问题识别"
        echo ""
        if [ "$score" -lt 5 ]; then
            [ "$allocated" != "y" ] && echo "- 任务分配问题"
            [ "$optimal" != "y" ] && echo "- API选择问题"
            [ "$transparent" != "y" ] && echo "- 透明化问题"
            [ "$direct_answer" != "y" ] && echo "- 直接答案问题"
            [ "$verified" != "y" ] && echo "- 验证问题"
        else
            echo "无问题发现"
        fi
        echo ""
        echo "## 改进建议"
        echo ""
        echo "（见上述改进建议）"
        echo ""
    } > "$WORKSPACE/.learnings/self-critiques/critique_$(date +%Y%m%d_%H%M%S).md"
}

critique_phase

# ============================================================================
# 阶段3: 提取模式 (Learn)
# =============================================================================

echo -e "${BLUE}🔍 阶段3: 提取模式${NC}"
echo "======================"
echo ""

learn_phase() {
    echo "🧠 提取可复用模式："
    echo ""

    # 生成模式库
    mkdir -p "$WORKSPACE/.learnings/patterns"

    # 从当前反思和批评中提取模式
    if [ "$score" -eq 5 ]; then
        pattern_name="优秀任务执行模式"
        pattern_desc="正确分配、最优API、透明化、直接答案、验证信息"
    elif [ "$score" -ge 3 ]; then
        pattern_name="一般任务执行模式"
        pattern_desc="部分环节需要改进"
    else
        pattern_name="问题任务执行模式"
        pattern_desc="多个环节存在问题，需要全面改进"
    fi

    echo "模式: $pattern_name"
    echo "描述: $pattern_desc"
    echo ""

    # 保存模式
    {
        echo "# 模式: $pattern_name"
        echo ""
        echo "**时间**: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "**得分**: $score/5"
        echo ""
        echo "## 模式描述"
        echo ""
        echo "$pattern_desc"
        echo ""
        echo "## 最佳实践"
        echo ""
        if [ "$score" -eq 5 ]; then
            echo "- ✅ 正确分配任务"
            echo "- ✅ 选择最优API"
            echo "- ✅ 透明化汇报"
            echo "- ✅ 给出直接答案"
            echo "- ✅ 验证所有信息"
        fi
        echo ""
    } > "$WORKSPACE/.learnings/patterns/pattern_$(date +%Y%m%d_%H%M%S).md"

    echo "✅ 模式已保存"
    echo ""
}

learn_phase

# ============================================================================
# 阶段4: 组织记忆 (Organize)
# =============================================================================

echo -e "${BLUE}🔍 阶段4: 组织记忆${NC}"
echo "======================"
echo ""

organize_phase() {
    echo "🗂️  组织知识库："
    echo ""

    # 运行自组织记忆系统
    if [ -f "$AUTO_MEMORY" ]; then
        bash "$AUTO_MEMORY"
        echo "✅ 记忆组织完成"
        echo ""
    else
        echo "⚠️  自组织记忆脚本不存在，跳过"
        echo ""
    fi
}

organize_phase

# ============================================================================
# 完成总结
# =============================================================================

echo -e "${GREEN}========================${NC}"
echo -e "${GREEN}✅ 四步循环完成！${NC}"
echo -e "${GREEN}========================${NC}"
echo ""

echo "📊 本次评估结果:"
echo "  - 反思得分: $score/5"
echo "  - 自我批评: 已记录"
echo "  - 模式提取: 已完成"
echo "  - 记忆组织: 已完成"
echo ""

echo "📁 生成文件:"
echo "  - 反思: $WORKSPACE/.learnings/reflections/"
echo "  - 批评: $WORKSPACE/.learnings/self-critiques/"
echo "  - 模式: $WORKSPACE/.learnings/patterns/"
echo "  - 记忆: $WORKSPACE/.learnings/auto-organized/"
echo ""

if [ "$score" -eq 5 ]; then
    echo -e "${GREEN}🎉 优秀！继续保持！${NC}"
elif [ "$score" -ge 3 ]; then
    echo -e "${YELLOW}⚠️  还可以做得更好！${NC}"
else
    echo -e "${YELLOW}❌ 需要全面改进！${NC}"
fi

echo ""

exit 0
