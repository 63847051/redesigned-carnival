# 记忆系统使用指南

**创建时间**: 2026-03-09
**版本**: v3.0 (结构化升级)

---

## 📚 新的记忆结构

```
/root/.openclaw/workspace/memory/
├── long-term/             # 长期记忆
│   ├── people/            # 人物信息
│   │   └── lucky-asteroid.md
│   ├── projects/          # 项目信息
│   │   └── blue-focus-shanghai.md
│   ├── knowledge/         # 知识点
│   │   └── openclaw-system.md
│   └── preferences/       # 偏好设置
│       └── communication.md
├── short-term/            # 短期记忆
│   ├── conversations/     # 对话记录
│   └── tasks/             # 任务记录
├── indexes/               # 搜索索引
│   ├── knowledge.idx      # FAISS 索引
│   └── knowledge_metadata.json  # 元数据
└── YYYY-MM-DD.md          # 旧格式日志（待迁移）
```

---

## 🔍 语义搜索

### 安装依赖

```bash
pip3 install sentence-transformers faiss-cpu numpy
```

### 使用方法

#### 1. 建立索引
```bash
python3 /root/.openclaw/workspace/scripts/semantic-search.py build
```

#### 2. 搜索记忆
```bash
# 中文搜索
python3 /root/.openclaw/workspace/scripts/semantic-search.py search --query "幸运小行星"

# 英文搜索
python3 /root/.openclaw/workspace/scripts/semantic-search.py search --query "OpenClaw system"

# 返回更多结果
python3 /root/.openclaw/workspace/scripts/semantic-search.py search --query "蓝色光标" --top-k 10
```

#### 3. 重建索引
```bash
python3 /root/.openclaw/workspace/scripts/semantic-search.py rebuild
```

---

## 📝 添加新记忆

### 方式 1: 手动创建

```bash
# 创建人物档案
vim /root/.openclaw/workspace/memory/long-term/people/new-person.md

# 创建项目记录
vim /root/.openclaw/workspace/memory/long-term/projects/new-project.md

# 创建知识点
vim /root/.openclaw/workspace/memory/long-term/knowledge/new-topic.md
```

### 方式 2: 使用模板

```markdown
# 标题

**创建时间**: YYYY-MM-DD
**最后更新**: YYYY-MM-DD

---

## 基本信息

- **字段1**: 值1
- **字段2**: 值2

---

## 详细内容

...

---

*标签: #标签1 #标签2*
```

---

## 🔄 迁移旧记忆

### 从旧格式迁移

```bash
# 迁移每日日志
mv /root/.openclaw/workspace/memory/2026-03-*.md \
   /root/.openclaw/workspace/memory/short-term/conversations/

# 更新 MEMORY.md
# 将重要信息提取到 long-term/ 对应目录
```

---

## 🧠 记忆管理最佳实践

### 1. 分类原则
- **long-term/** - 永久保存的信息（人物、项目、知识）
- **short-term/** - 临时信息（对话、任务）

### 2. 命名规范
- 使用小写字母和连字符
- 包含日期或 ID
- 示例: `lucky-asteroid.md`, `blue-focus-shanghai.md`

### 3. 标签使用
- 在文件末尾添加标签
- 格式: `*标签: #tag1 #tag2 #tag3*`
- 便于搜索和分类

### 4. 更新频率
- **长期记忆**: 按需更新（重要变化时）
- **短期记忆**: 每日清理（归档或删除）

---

## 🔗 集成到日常工作

### 1. 对话后更新
```bash
# 重要对话后，记录到 short-term/conversations/
vim /root/.openclaw/workspace/memory/short-term/conversations/feishu-2026-03-09.md
```

### 2. 项目进展更新
```bash
# 更新项目状态
vim /root/.openclaw/workspace/memory/long-term/projects/blue-focus-shanghai.md
```

### 3. 知识积累
```bash
# 新学到的知识点
vim /root/.openclaw/workspace/memory/long-term/knowledge/new-skill.md
```

---

## 📊 索引维护

### 自动更新索引

添加到 Crontab:
```bash
# 每小时更新索引
0 * * * * python3 /root/.openclaw/workspace/scripts/semantic-search.py rebuild
```

### 手动更新索引

当添加新记忆后，手动重建索引:
```bash
python3 /root/.openclaw/workspace/scripts/semantic-search.py rebuild
```

---

## 🎯 搜索技巧

### 1. 精确搜索
使用完整短语:
```bash
python3 /root/.openclaw/workspace/scripts/semantic-search.py search --query "蓝色光标上海办公室"
```

### 2. 概念搜索
使用关键词，语义搜索会找到相关内容:
```bash
python3 /root/.openclaw/workspace/scripts/semantic-search.py search --query "室内设计"
```

### 3. 英文搜索
支持中英文混合搜索:
```bash
python3 /root/.openclaw/workspace/scripts/semantic-search.py search --query "OpenClaw configuration"
```

---

## 🔧 故障排除

### 索引损坏
```bash
# 删除旧索引
rm /root/.openclaw/workspace/memory/indexes/knowledge.idx

# 重建索引
python3 /root/.openclaw/workspace/scripts/semantic-search.py rebuild
```

### 依赖缺失
```bash
# 重新安装依赖
pip3 install --upgrade sentence-transformers faiss-cpu numpy
```

### 搜索无结果
- 检查查询是否准确
- 尝试更通用的关键词
- 重建索引

---

## 📈 性能指标

- **索引大小**: 约 10-50 MB (取决于文档数量)
- **搜索速度**: < 1 秒
- **支持文档数**: 100,000+
- **语言**: 中文、英文

---

## 🚀 未来改进

- [ ] 自动从对话中提取关键信息
- [ ] 跨会话记忆共享
- [ ] 智能推荐相关记忆
- [ ] Web UI 界面
- [ ] 导出为 JSON/CSV

---

*创建时间: 2026-03-09*
*版本: v3.0*
*状态: ✅ 运行中*
