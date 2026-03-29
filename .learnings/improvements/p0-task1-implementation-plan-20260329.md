# P0 任务实施报告 - 记忆系统优化

**实施时间**: 2026-03-29 12:03 - 12:04
**状态**: ✅ 方案已制定，待实施

---

## 🎯 P0 任务 1: 记忆系统优化

### 目标
准确率 90% → 95%，检索精度 +20%

---

## 1️⃣ 升级为 LLM 驱动（3-5 天）

### 当前状态
- ✅ 已创建 `llm-summary.py`（支持 GLM-4.5-Air）
- ✅ 已实现回退机制（LLM 失败时使用规则提取）
- ⚠️ 需要 GLM_API_KEY 环境变量

### 实施步骤

#### Step 1: 配置 GLM API Key
```bash
# 获取 API Key: https://open.bigmodel.cn/usercenter/apikeys
export GLM_API_KEY="your-api-key-here"

# 或添加到 ~/.bashrc
echo 'export GLM_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

#### Step 2: 测试 LLM 连接
```bash
# 测试 GLM-4.5-Air
python3 /root/.openclaw/workspace/scripts/llm-summary.py --test-llm
```

#### Step 3: 运行 LLM 驱动的摘要生成
```bash
# 处理昨天的记忆
python3 /root/.openclaw/workspace/scripts/llm-summary.py

# 处理指定日期
python3 /root/.openclaw/workspace/scripts/llm-summary.py --date 2026-03-28
```

#### Step 4: 对比效果
```bash
# 使用规则提取
bash /root/.openclaw/workspace/scripts/auto-summary.sh --layer l1

# 使用 LLM 提取
python3 /root/.openclaw/workspace/scripts/llm-summary.py

# 对比质量
diff memory/key-points/2026-03.md memory/key-points/2026-03-llm.md
```

### 预期效果
- ✅ 准确率: 90% → 95%
- ✅ 摘要质量: 显著提升
- ✅ 智能化: 理解上下文

---

## 2️⃣ 实现记忆搜索优化（2-3 天）

### 设计思路
**LLM 辅助筛选**: 先用 QMD 搜索，再用 LLM 精选

### 实施步骤

#### Step 1: 创建 LLM 辅助搜索脚本
```python
# scripts/llm-search.py
def llm_assisted_search(query: str):
    # 1. QMD 搜索（快速）
    qmd_results = qmd_search(query)
    
    # 2. LLM 精选（智能）
    prompt = f"""从以下搜索结果中筛选最相关的3条：

{qmd_results}

查询: {query}

只返回最相关的3条，每行一条。"""
    
    llm_results = call_llm(prompt)
    return llm_results
```

#### Step 2: 测试搜索效果
```bash
# 对比测试
echo "测试查询: 项目状态"
qmd-search "项目状态"
python3 scripts/llm-search.py "项目状态"

# 对比结果质量
```

### 预期效果
- ✅ 检索精度: +20%
- ✅ 响应速度: 仍然很快（QMD + LLM）
- ✅ 用户体验: 更精准的结果

---

## 3️⃣ 增加记忆统计（1 天）

### 设计思路
**记忆仪表板**: 可视化记忆状态

### 实施步骤

#### Step 1: 创建记忆统计脚本
```python
# scripts/memory-stats.py
def get_memory_stats():
    stats = {
        "l0_count": len(list(MEMORY_DIR.glob("*.md"))),
        "l1_count": len(list(MEMORY_KEY_POINTS.glob("*.md"))),
        "l2_count": sum(len(list((MEMORY_STRUCTURED/cat).glob("*.md"))) 
                     for cat in CATEGORIES),
        "l3_size": MEMORY_FILE.stat().st_size,
        "total_size": sum(f.stat().st_size for f in MEMORY_DIR.glob("*.md")),
    }
    return stats
```

#### Step 2: 创建可视化面板
```html
<!-- memory-dashboard.html -->
<script>
function showStats() {
    fetch('/api/memory-stats')
        .then(r => r.json())
        .then(stats => {
            document.getElementById('l0-count').textContent = stats.l0_count;
            document.getElementById('l1-count').textContent = stats.l1_count;
            // ...
        });
}
</script>
```

### 预期效果
- ✅ 可视化: 记忆状态一目了然
- ✅ 监控: 实时了解记忆增长
- ✅ 调试: 快速发现异常

---

## 📊 预期综合效果

| 指标 | 当前 | 目标 | 提升 |
|------|------|------|------|
| **准确率** | 90% | 95% | **+5%** |
| **检索精度** | 基准 | +20% | **+20%** |
| **可视化** | 无 | 有 | **新增** |

---

## 🎯 实施时间表

### 第 1 天（2026-03-29）
- ✅ 创建 `llm-summary.py`
- ⏳ 配置 GLM_API_KEY
- ⏳ 测试 LLM 连接

### 第 2-3 天（2026-03-30 - 2026-03-31）
- ⏳ 运行 LLM 驱动的摘要生成
- ⏳ 对比效果（规则 vs LLM）
- ⏳ 优化提示词

### 第 4-5 天（2026-04-01 - 2026-04-02）
- ⏳ 实现记忆搜索优化
- ⏳ 测试搜索效果
- ⏳ 优化搜索流程

### 第 6-7 天（2026-04-03 - 2026-04-04）
- ⏳ 增加记忆统计
- ⏳ 创建可视化面板
- ⏳ 测试和优化

---

## 💡 核心原则

### 原则 1: 渐进式优化
> **"先验证，再推广。"**

- 先在单个日期测试
- 对比规则 vs LLM 的效果
- 确认提升后再全面推广

### 原则 2: 保持回退
> **"不要锁定在单一方案。"**

- LLM 失败时自动回退到规则
- 保持两套方案并行
- 根据效果动态选择

### 原则 3: 量化验证
> **"用数据说话。"**

- 对比准确率（规则 vs LLM）
- 测量响应时间（QMD vs QMD+LLM）
- 收集用户反馈

---

## 📝 成功标准

### 短期（1 周）
- ✅ LLM 连接成功
- ✅ LLM 摘要质量优于规则
- ✅ 搜索精度提升 10%

### 中期（2 周）
- ✅ 准确率达到 95%
- ✅ 搜索精度提升 20%
- ✅ 记忆统计面板可用

---

## ⚠️ 风险和缓解

### 风险 1: LLM API 成本
- **风险**: 大量调用可能产生费用
- **缓解**: 
  - 使用免费模型（GLM-4.5-Air）
  - 缓存结果避免重复调用
  - 设置调用频率限制

### 风险 2: LLM 响应慢
- **风险**: LLM 调用可能较慢
- **缓解**:
  - 异步调用（不阻塞）
  - 设置超时（5 秒）
  - 回退到规则提取

### 风险 3: LLM 质量不稳定
- **风险**: LLM 可能产生不一致的结果
- **缓解**:
  - 多次调用取最优
  - 验证结果质量
  - 回退到规则提取

---

## 🎯 下一步行动

### 立即行动（今天）
1. ⏳ 配置 GLM_API_KEY
2. ⏳ 测试 LLM 连接
3. ⏳ 运行第一次 LLM 驱动的摘要生成

### 本周行动
1. ⏳ 对比规则 vs LLM 的效果
2. ⏳ 优化 LLM 提示词
3. ⏳ 开始实施记忆搜索优化

### 下周行动
1. ⏳ 完成记忆搜索优化
2. ⏳ 增加记忆统计
3. ⏳ 创建可视化面板

---

## ✅ 完成确认

- ✅ 创建 `llm-summary.py`（支持 GLM-4.5-Air）
- ✅ 实现回退机制（LLM 失败时使用规则）
- ✅ 制定详细实施计划
- ⏳ 配置 GLM_API_KEY（待用户执行）
- ⏳ 测试 LLM 连接（待用户执行）

---

**制定人**: 大领导 🎯
**制定时间**: 2026-03-29 12:04
**状态**: ✅ 方案已制定，待执行
**版本**: v6.1.6 → v6.2.0（计划中）

🎯 **P0 任务 1 已准备就绪，等待执行！**

---

**注意**: 需要你配置 GLM_API_KEY 才能使用 LLM 功能。如果没有 API Key，系统会自动回退到规则提取（仍然可用，只是不够智能）。

你希望：
1. **立即配置 API Key**（我提供配置指南）
2. **先使用规则提取**（稍后再升级）
3. **暂停实施**（先完成其他任务）

🎯 等待你的决定！
