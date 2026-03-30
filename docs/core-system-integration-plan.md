# 核心系统集成方案

**版本**: v3.0
**创建时间**: 2026-03-29 20:12
**原则**: 所有系统服务于核心系统，不创建独立系统

---

## 🎯 **核心原则**

### ✅ **单一系统原则**
- **只有一个核心系统** - OpenClaw 核心系统
- **所有增强都是插件** - 服务于核心系统
- **不是并行系统** - 而是能力增强

### ✅ **集成而非替代**
- **保留 memory/** - 这是核心存储
- **增强能力** - 添加新功能到现有结构
- **不创建新目录** - 使用现有结构

---

## 🏗️ **正确架构：核心系统增强**

```
┌─────────────────────────────────────┐
│   OpenClaw 核心系统                  │
│   - MEMORY.md (长期记忆)            │
│   - memory/YYYY-MM-DD.md (每日记忆) │
│   - skills/ (技能目录)              │
│   - .learnings/ (学习记录)          │
└─────────────────────────────────────┘
              ↑
              | 增强
              |
┌─────────────────────────────────────┐
│   增强能力（插件）                   │
│   1. 分层加载 - 优化 memory/ 加载   │
│   2. 可视化检索 - 记录检索过程      │
│   3. 持久化 Hooks - 自动保存        │
│   4. 向量搜索 - 快速检索 memory/    │
│   5. 协调机制 - 确保一致性         │
└─────────────────────────────────────┘
```

---

## 🔄 **重新设计：使用核心系统**

### ❌ **不要创建 .context/**
- `.context/` 是独立的系统
- 会导致数据分散
- 增加维护成本

### ✅ **增强现有 memory/**
- 使用 `memory/` 作为唯一存储
- 增强检索能力
- 优化加载方式

---

## 🎯 **具体实施方案**

### ✅ **方案 A：增强现有系统（推荐）**

#### 1️⃣ **分层加载 - 针对 memory/**
```python
class EnhancedMemoryLoader:
    """增强的记忆加载器"""
    
    def load_memory(self, token_budget: int = 4000) -> str:
        """
        智能加载 memory/
        
        分层：
        - L0: MEMORY.md (核心)
        - L1: 最近 7 天的记忆
        - L2: 更早的记忆（按需）
        """
        # 加载 MEMORY.md
        memory_md = self.workspace / "MEMORY.md"
        l0_content = memory_md.read_text() if memory_md.exists() else ""
        
        # 加载最近 7 天
        l1_content = self._load_recent_days(days=7)
        
        # 计算剩余预算
        remaining = token_budget - len(l0_content.split()) - len(l1_content.split())
        
        # 按需加载更早的记忆
        l2_content = ""
        if remaining > 0:
            l2_content = self._load_earlier_days(remaining)
        
        return l0_content + "\n\n" + l1_content + "\n\n" + l2_content
```

#### 2️⃣ **可视化检索 - 针对 memory/**
```python
class MemoryRetrievalVisualizer:
    """记忆检索可视化器"""
    
    def record_memory_retrieval(self, query: str, results: List[Dict]):
        """
        记录 memory/ 检索过程
        
        Args:
            query: 查询
            results: 来自 memory/ 的结果
        """
        trajectory = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "source": "memory/",
            "results": results
        }
        
        # 保存到 .learnings/retrieval-trajectories.jsonl
        # 而不是 .context/
```

#### 3️⃣ **向量搜索 - 针对 memory/**
```python
class MemoryVectorSearch:
    """记忆向量搜索"""
    
    def search_memory(self, query: str) -> List[Dict]:
        """
        在 memory/ 中搜索
        
        使用 QMD 或 semantic-search
        """
        # 使用 qmd-search
        results = qmd_search(query, scope="memory/")
        
        return results
```

---

### ✅ **方案 B：移除独立系统**

#### 🗑️ **删除 .context/**
```bash
# 删除独立的 .context/ 系统
rm -rf /root/.openclaw/workspace/.context

# 保留核心系统
# memory/
# MEMORY.md
# skills/
# .learnings/
```

#### ✅ **更新脚本**
- 所有脚本改为使用 `memory/`
- 移除对 `.context/` 的引用

---

## 🎯 **统一接口：核心系统增强**

```python
class CoreMemoryEnhancer:
    """核心记忆系统增强器"""
    
    def __init__(self, workspace: str = "/root/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.memory_dir = self.workspace / "memory"
        
        # 初始化增强功能
        self.loader = EnhancedMemoryLoader(workspace)
        self.visualizer = MemoryRetrievalVisualizer(workspace)
        self.search = MemoryVectorSearch(workspace)
    
    def save_memory(self, content: str):
        """保存到 memory/（使用现有机制）"""
        today = datetime.now().strftime("%Y-%m-%d")
        memory_file = self.memory_dir / f"{today}.md"
        
        # 追加到今日记忆
        with open(memory_file, "a", encoding="utf-8") as f:
            f.write("\n\n" + content)
    
    def load_memory(self, token_budget: int = 4000) -> str:
        """从 memory/ 智能加载"""
        return self.loader.load_memory(token_budget)
    
    def search_memory(self, query: str) -> List[Dict]:
        """在 memory/ 中搜索"""
        results = self.search.search_memory(query)
        
        # 记录检索轨迹
        self.visualizer.record_memory_retrieval(query, results)
        
        return results
```

---

## 📊 **对比：错误 vs 正确**

| 维度 | ❌ 错误方式 | ✅ 正确方式 |
|------|-----------|-----------|
| **存储** | 创建 .context/ | 使用 memory/ |
| **架构** | 并行系统 | 核心系统增强 |
| **数据** | 分散在两处 | 统一在 memory/ |
| **复杂度** | 两套系统 | 一套系统 + 增强 |
| **维护** | 需要同步 | 无需同步 |

---

## 🚀 **实施步骤**

### ✅ **Phase 1: 移除独立系统**
1. 删除 `.context/` 目录
2. 更新所有脚本
3. 移除对 `.context/` 的引用

### ✅ **Phase 2: 增强核心系统**
1. 创建 `CoreMemoryEnhancer`
2. 增强现有 `memory/` 功能
3. 集成向量搜索

### ✅ **Phase 3: 测试验证**
1. 测试保存
2. 测试加载
3. 测试检索

---

## 🎯 **总结**

### ✅ **核心原则**
- **一个系统** - OpenClaw 核心系统
- **增强而非替代** - 插件式增强
- **统一存储** - 所有数据在 memory/

### ❌ **不要做的**
- ❌ 创建 .context/
- ❌ 并行系统
- ❌ 数据分散

### ✅ **要做的**
- ✅ 增强现有 memory/
- ✅ 集成到核心系统
- ✅ 统一存储

---

**设计人**: 大领导 🎯
**创建时间**: 2026-03-29 20:12
**版本**: v3.0
**状态**: ✅ **核心系统集成方案已设计！**

🎉 **所有系统服务于核心系统，不创建独立系统！** 🚀
