# OpenAI Frontend Design Skill - Enhanced Edition

**版本**: 2.0 (Enhanced)
**更新时间**: 2026-04-05 23:43
**基于**: OpenAI Frontend Skill + Claude Frontend Design + 深度解读文章

---

## 🎯 版本更新说明

### **v2.0 新增特性**：

#### **1. Claude 风格的维度化指导** ⭐⭐⭐
- **排版维度**: 对比最大化（100/200 vs 800/900）
- **主题维度**: 氛围化设计系统
- **背景与动效**: 大气背景、功能性层级

#### **2. 强化的文案策略** ⭐⭐⭐
- **30%删除测试**
- **产品语言 vs 设计评论**
- **实用文案优先**（工具类产品）

#### **3. 更严格的硬规则** ⭐⭐⭐
- **字体禁止**: Inter、Roboto、Open Sans、Lato、Arial
- **配色禁止**: Purple-on-white、蓝紫渐变
- **卡片反测试**: 移除装饰后是否影响理解

#### **4. 单一职责原则** ⭐⭐
- 每个区块：一个标题、一句支持文案、一个核心动作
- 对抗 AI 倾向堆砌多个营销点

---

## 📊 与原版对比

| 特性 | v1.0 (原版) | v2.0 (增强版) |
|------|------------|--------------|
| **硬规则** | 10 条 | 15+ 条 |
| **字体指导** | 基础 | ⭐ 对比最大化 |
| **主题系统** | 无 | ⭐ 氛围化设计 |
| **文案策略** | 基础 | ⭐ 30%删除测试 |
| **实用文案** | 无 | ⭐ 工具类产品专用 |
| **背景** | 简单 | ⭐ 大气背景 |
| **验证检查** | 7 项 | 11 项 |

---

## 🔥 核心改进

### **1. 字体选择 - 对比最大化**

#### **明确排除**：
```markdown
❌ Inter, Roboto, Open Sans, Lato, Arial, system defaults
```

#### **分类推荐**：
```markdown
代码美学: JetBrains Mono, Fira Code, Space Grotesk
编辑风格: Playfair Display, Crimson Pro
技术感: IBM Plex family, Source Sans 3
独特性: Bricolage Grotesque, Newsreader
```

#### **技术约束**：
```markdown
极端字重对比: 100/200 vs 800/900
字号跳跃: 3x+ 差异
高对比配对: Display + Monospace OR Serif + Geometric Sans
```

### **2. 主题系统 - 氛围化设计**

#### **RPG 主题示例**：
```markdown
色彩: 丰富戏剧性的奇幻色调
材质: 羊皮纸纹理、皮革装订风格、风化质感
装饰: 华丽边框与装饰框架元素
照明: 戏剧性光影效果
字体: 中世纪风格衬线体
```

#### **使用方法**：
> 允许模型基于对特定美学风格的内部理解，自主推导具体的 CSS 实现，而非依赖硬编码的十六进制值。

### **3. 文案策略 - 三重保障**

#### **产品语言 vs 设计评论**：
```markdown
✅ 产品语言: 具体、功能性、行动导向
❌ 设计评论: 抽象、描述性、空洞承诺
```

#### **30%删除测试**：
> 若删除 30% 文案不影响理解，则继续精简。

#### **实用文案优先**（工具类产品）：
```markdown
✅ 好例子: "Selected KPIs", "Plan status", "Search metrics"
❌ 坏例子: "Unlock your potential", "Transform your workflow"
```

**石蕊检查**：
> 如果操作员只扫描标题、标签和数字，能立即理解页面吗？

### **4. 单一职责原则**

每个区块必须遵循：
```markdown
一个标题
一句支持文案
一个核心动作
```

**目的**：对抗 AI 倾向在同一区块堆砌多个营销点。

---

## 💡 核心价值

### **v2.0 的核心改进**：

1. **更可预测的输出**
   - 15+ 硬规则
   - 11 项石蕊检查
   - 明确的禁止清单

2. **更高的质量**
   - 对比最大化（字体）
   - 氛围化设计（主题）
   - 大气背景（视觉）

3. **避免"AI 味"**
   - 禁止 Inter 字体
   - 禁止紫白配色
   - 禁止蓝紫渐变

4. **快速风格探索**
   - 主题系统（RPG、赛博朋克等）
   - 字体分类（代码、编辑、技术、独特）
   - 氛围背景（纹理、渐变、图像）

---

## 🚀 使用方法

### **触发条件**：
- "设计一个落地页"
- "创建一个网站"
- "设计应用界面"
- "需要高质量 UI"

### **自动应用**：
OpenClaw 会自动检测任务类型并加载此技能

---

## 📚 参考资源

### **官方文档**：
- OpenAI Frontend Skill: https://github.com/openai/skills/tree/main/skills/.curated/frontend-skill
- Claude Frontend Design: https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md

### **深度解读**：
- 深度解读 OpenAI 与 Anthropic 的前端设计 Skills（已学习）

---

## ✅ 安装状态

**技能目录**: `/root/.openclaw/workspace/skills/openai-frontend-design/`
**主文件**: `SKILL.md` (v2.0 Enhanced)
**文档**: `README.md`
**版本**: 2.0 (Enhanced)

---

**更新完成！** ✅

**v2.0 增强版已准备使用！** 🚀✨
