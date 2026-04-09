# ✅ DeerFlow Image Generation Skill 安装完成！

**版本**: 1.0
**安装时间**: 2026-04-05 23:16
**位置**: `/root/.openclaw/workspace/skills/deerflow-image-generation/`

---

## 📁 目录结构

```
deerflow-image-generation/
├── SKILL.md          (8.9 KB - 主技能文件)
├── README.md         (7.3 KB - 使用文档)
├── scripts/          (Python 脚本)
│   └── generate.py
└── templates/        (场景模板)
    └── doraemon.md
```

---

## 🎯 技能特性

### **核心能力**：
- ✅ 生成高质量图像
- ✅ 结构化 JSON 提示词
- ✅ 参考图像引导
- ✅ 多种场景支持
- ✅ Negative Prompt

### **支持场景**：
- 角色设计（详细人物描述）
- 场景生成（环境、氛围）
- 产品可视化（细节、材料）

---

## 🚀 立即可用

### **触发条件**：
当你说以下内容时，此技能会自动加载：
- "生成图片"
- "创建图像"
- "想象一下"
- "可视化"
- "设计一个角色"

### **工作流程**：
```
1. 理解需求 → 2. 创建 JSON → 3. 执行脚本 → 4. 输出图像
```

---

## 📋 快速示例

### **东京街头角色**：

**JSON 提示词**：
```json
{
  "characters": [{
    "gender": "female",
    "age": "mid-20s",
    "ethnicity": "Japanese",
    "clothing": "stylish trench coat",
    "era": "1990s"
  }],
  "style": "Leica M11 street photography aesthetic",
  "composition": "medium shot, rule of thirds",
  "lighting": "neon lights, wet pavement reflections"
}
```

**执行命令**：
```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/tokyo-woman.json \
  --output-file /mnt/user-data/outputs/tokyo-woman-01.jpg \
  --aspect-ratio 2:3
```

---

## 💡 高级特性

### **1. 结构化提示词** ⭐⭐⭐
```json
{
  "characters": [...],
  "prompt": "...",
  "negative_prompt": "...",
  "style": "...",
  "composition": "...",
  "lighting": "...",
  "color_palette": "...",
  "technical": {
    "aspect_ratio": "16:9"
  }
}
```

### **2. 参考图像支持** ⭐⭐⭐
- 使用 `image_search` 工具先找参考图
- 支持多张参考图像
- 提供风格/构图引导

### **3. Negative Prompt**
```json
{
  "negative_prompt": "blurry face, deformed, low quality"
}
```

---

## 📊 与其他技能对比

| 特性 | DeerFlow Image Gen | OpenAI Frontend |
|------|-------------------|-----------------|
| **专注** | 图像生成 | 前端设计 |
| **输出** | 图像文件 | 设计代码 |
| **提示词** | 结构化 JSON | 自然语言 |
| **参考图** | ✅ 支持 | ❌ 不涉及 |
| **场景** | 角色、场景、产品 | 落地页、应用 |

---

## 🎨 核心价值

### **为什么使用这个技能？**

1. **结构化提示词** - 精确控制生成结果
2. **参考图像引导** - 提升生成质量
3. **多种场景支持** - 角色、场景、产品
4. **Negative Prompt** - 避免不良结果
5. **Python 脚本** - 自动化执行

---

## ✅ 安装状态

**技能文件**: ✅ 已安装
**Python 脚本**: ✅ 已安装
**场景模板**: ✅ 已安装
**使用文档**: ✅ 已创建

---

**安装完成！已准备使用！** ✅

**需要测试这个技能吗？或者有其他需要安装的技能？** 🚀✨
