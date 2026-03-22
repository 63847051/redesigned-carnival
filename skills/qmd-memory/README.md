# QMD Memory Search Skill

**版本**: 1.0.0
**创建时间**: 2026-03-22

---

## 🚀 快速开始

### 安装

```bash
# 脚本已安装到 /root/.openclaw/workspace/skills/qmd-memory/scripts/

# 创建软链接（可选）
ln -s /root/.openclaw/workspace/skills/qmd-memory/scripts/qmd-search.sh /usr/local/bin/qmd-search
ln -s /root/.openclaw/workspace/skills/qmd-memory/scripts/qmd-get.sh /usr/local/bin/qmd-get
ln -s /root/.openclaw/workspace/skills/qmd-memory/scripts/qmd-multi.sh /usr/local/bin/qmd-multi
```

### 使用

```bash
# 搜索记忆
qmd-search "蓝色光标"

# 查看文件
qmd-get memory/long-term/projects/blue-focus-shanghai.md

# 批量查看
qmd-multi "memory/**/*.md"
```

---

## 📖 文档

详细文档请查看: [SKILL.md](./SKILL.md)

---

## 🎯 功能

- ✅ 快速全文搜索（BM25）
- ✅ 智能语义搜索（Groq API）
- ✅ 文件查看
- ✅ 批量查看

---

**作者**: 大领导 🎯
**状态**: ✅ 活跃
