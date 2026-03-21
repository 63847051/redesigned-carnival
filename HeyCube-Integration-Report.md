# HeyCube（黑方体）集成报告

**集成时间**: 2026-03-21
**版本**: 1.0.0
**状态**: ✅ 集成完成

---

## 🎉 **集成成功！**

HeyCube（黑方体）AI 记忆管家已成功集成到你的 OpenClaw 系统中！

---

## 📦 **已完成的工作**

### 1. 创建 Skill 文件 ✅
- ✅ `~/.agents/skills/heycube-get-config-0.1.0/SKILL.md` - 前置 Hook
- ✅ `~/.agents/skills/heycube-update-data-0.1.0/SKILL.md` - 后置 Hook

### 2. 创建 CLI 工具 ✅
- ✅ `/root/.openclaw/workspace/scripts/personal-db.py` - Python 版本
- ✅ `/root/.openclaw/workspace/scripts/personal-db.js` - Node.js 版本
- ✅ `/root/.openclaw/workspace/scripts/package.json` - 依赖配置

### 3. 更新配置文件 ✅
- ✅ `/root/.openclaw/workspace/TOOLS.md` - 添加 HeyCube 配置段
- ✅ `/root/.openclaw/workspace/AGENTS.md` - 添加 Hook 执行规则

### 4. 初始化数据库 ✅
- ✅ 数据库文件: `/root/.openclaw/workspace/personal-db.sqlite`
- ✅ 表结构已创建

---

## 🚀 **下一步：配置 HeyCube API Key**

### 获取 API Key

1. 访问 HeyCube 官网
2. 注册账号
3. 生成 API Key

### 配置 API Key

在 `/root/.openclaw/workspace/TOOLS.md` 中添加：

```markdown
## 🧠 HeyCube Server（黑方体 AI 记忆管家）

### 配置信息

- **Base URL:** https://heifangti.com/api/api/v1/heifangti
- **API Key:** hey_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  <-- 替换为你的 API Key
- **数据库路径:** /root/.openclaw/workspace/personal-db.sqlite
```

---

## 🎯 **HeyCube 功能说明**

### 核心特性
- 🧠 **结构化记忆** - 8 大域分类
- ⚡ **按需加载** - 一次只花 ~2000 tokens
- 🎯 **智能召回** - 不是检索，是推理
- 🔒 **隐私分离** - 本地存储，数据不出站

### 工作原理

#### 对话前（GET_CONFIG Hook）
1. 分析对话内容
2. 调用 HeyCube API 获取相关维度
3. 从本地 SQLite 查询用户档案
4. 注入到对话上下文

#### 对话后（UPDATE_DATA Hook）
1. 脱敏总结对话内容
2. 调用 HeyCube API 获取更新维度
3. 提取数据写入本地 SQLite

---

## 🛠️ **CLI 工具使用**

### 基本命令

```bash
# 列出所有维度
python3 /root/.openclaw/workspace/scripts/personal-db.py list

# 获取单个维度
python3 /root/.openclaw/workspace/scripts/personal-db.py get profile.career

# 批量获取维度
python3 /root/.openclaw/workspace/scripts/personal-db.py get-batch "profile.career,behavior.work_habits"

# 设置单个维度
python3 /root/.openclaw/workspace/scripts/personal-db.py set profile.career.career_stage "职业阶段" "资深"

# 批量设置维度
python3 /root/.openclaw/workspace/scripts/personal-db.py set-batch '{"profile.career": "软件工程师", "behavior.work_habits.time_management": "番茄工作法"}'

# 导出为 JSON
python3 /root/.openclaw/workspace/scripts/personal-db.py export
```

---

## 📊 **8 大域分类**

1. **身份认知** - 你怎么定义自己
2. **心理结构** - 你的思维模式和决策倾向
3. **审美偏好** - 你的视觉、听觉、品味
4. **职业画像** - 你的技能树和职业轨迹
5. **计划目标** - 你想成为什么样的人
6. **日程节奏** - 你的时间习惯和能量曲线
7. **杂项偏好** - 饮食、运动、生活习惯
8. **关系网络** - 你在意的人和社交模式

---

## 🔧 **开关控制**

### 临时关闭 HeyCube

```bash
touch ~/.openclaw/workspace/.heycube-off
```

### 重新启用 HeyCube

```bash
rm ~/.openclaw/workspace/.heycube-off
```

---

## 📚 **相关文档**

- **GitHub**: https://github.com/MMMMMMTL/heycube-heifangti
- **文档位置**: `/root/.openclaw/workspace/skills/heycube-heifangti/docs/`
- **License**: MIT

---

## ✅ **集成清单**

- [x] 创建 GET_CONFIG Skill
- [x] 创建 UPDATE_DATA Skill
- [x] 创建 Python CLI 工具
- [x] 创建 Node.js CLI 工具
- [x] 更新 TOOLS.md
- [x] 更新 AGENTS.md
- [x] 初始化 SQLite 数据库
- [x] 测试 CLI 工具

---

## 🎊 **总结**

**HeyCube 已成功集成到你的 OpenClaw 系统！**

现在你的 OpenClaw 将：
- ✅ 每次对话前自动加载用户画像
- ✅ 每次对话后自动更新用户档案
- ✅ 越用越懂你
- ✅ 隐私数据完全本地存储

**下一步**: 配置 HeyCube API Key，然后开始享受更智能的 AI 体验！

---

**集成完成时间**: 2026-03-21
**集成耗时**: 约 15 分钟
**状态**: ✅ 成功
