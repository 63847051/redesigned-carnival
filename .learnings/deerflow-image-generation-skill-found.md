# 🎨 DeerFlow Image Generation Skill - 发现报告

**位置**: `/root/.openclaw/workspace/projects/deerflow-study/deer-flow-source/skills/public/image-generation/`
**发现时间**: 2026-04-05 23:13
**状态**: ✅ 已找到

---

## 🎯 技能概述

### **核心功能**
- 生成高质量图像（使用结构化提示词）
- 支持参考图像引导
- Python 脚本自动化执行
- 支持多种场景（角色、场景、产品）

### **触发条件**
- "生成图片"
- "创建图像"
- "想象一下"
- "可视化"

---

## 📋 工作流程

### **Step 1: 理解需求**
识别：
- **主题/内容**：图像中应该有什么
- **风格偏好**：艺术风格、情绪、色彩
- **技术规格**：宽高比、构图、光照
- **参考图像**：引导生成的图像

### **Step 2: 创建结构化提示词**
生成 JSON 文件：
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
    "aspect_ratio": "16:9",
    "quality": "high"
  }
}
```

### **Step 3: 执行生成**
```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/prompt-file.json \
  --reference-images /path/to/ref1.jpg \
  --output-file /mnt/user-data/outputs/generated-image.jpg \
  --aspect-ratio 16:9
```

---

## 🎨 核心特性

### **1. 结构化 JSON 提示词**
```json
{
  "characters": [{
    "gender": "female",
    "age": "mid-20s",
    "ethnicity": "Japanese",
    "body_type": "slender, elegant",
    "facial_features": "delicate features, expressive eyes",
    "clothing": "stylish trench coat",
    "accessories": "minimal jewelry",
    "era": "1990s"
  }],
  "style": "Leica M11 street photography aesthetic",
  "composition": "medium shot, rule of thirds",
  "lighting": "neon lights, wet pavement reflections",
  "color_palette": "muted naturalistic tones"
}
```

### **2. 参考图像支持**
- 使用 `image_search` 工具先找参考图
- 支持多张参考图像
- 提供风格/构图引导

### **3. Negative Prompt**
```json
{
  "negative_prompt": "blurry face, deformed, low quality, overly sharp digital look"
}
```

### **4. 详细参数控制**
- **characters**: 角色详细描述
- **style**: 艺术风格
- **composition**: 构图
- **lighting**: 光照
- **color_palette**: 色彩
- **technical**: 技术规格

---

## 📊 场景模板

### **角色设计**
- 身体属性（性别、年龄、种族、体型）
- 面部特征和表情
- 服装和配饰
- 历史时代或设置
- 姿势和语境

### **场景生成**
- 环境描述
- 时间、天气
- 情绪和氛围
- 焦点和构图

### **产品可视化**
- 产品细节和材料
- 光照设置
- 背景和语境
- 展示角度

---

## 💡 高级技巧

### **使用参考图像提升质量**

**推荐场景**：
- ✅ **角色/肖像生成**：搜索相似姿势、表情、风格
- ✅ **特定物体/产品**：查找真实物体参考图
- ✅ **建筑/环境场景**：搜索地点参考
- ✅ **时尚/服装**：查找风格参考

**工作流**：
```bash
# 1. 搜索参考图像
image_search(query="Japanese woman street photography 1990s", size="Large")

# 2. 下载图像到本地

# 3. 使用参考图像生成
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/prompt-file.json \
  --reference-images /mnt/user-data/uploads/character-ref.jpg \
  --output-file /mnt/user-data/outputs/generated-image.jpg
```

---

## 🎯 示例：东京街头风格角色

### **JSON 提示词**：
```json
{
  "characters": [{
    "gender": "female",
    "age": "mid-20s",
    "ethnicity": "Japanese",
    "body_type": "slender, elegant",
    "facial_features": "delicate features, expressive eyes, subtle makeup",
    "clothing": "stylish trench coat, designer handbag, high heels",
    "accessories": "minimal jewelry, statement earrings",
    "era": "1990s"
  }],
  "negative_prompt": "blurry face, deformed, low quality, studio setting",
  "style": "Leica M11 street photography aesthetic, film-like rendering",
  "composition": "medium shot, rule of thirds, shallow depth of field",
  "lighting": "neon lights, wet pavement reflections, natural street lighting",
  "color_palette": "muted naturalistic tones, warm skin tones, cool neon accents"
}
```

### **执行命令**：
```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/tokyo-woman.json \
  --output-file /mnt/user-data/outputs/tokyo-woman-01.jpg \
  --aspect-ratio 2:3
```

---

## 📝 注意事项

### **核心规则**：
- ✅ **始终使用英语提示词**（不管用户语言）
- ✅ **JSON 格式确保结构化**
- ✅ **参考图像显著提升质量**
- ✅ **迭代优化是正常的**
- ✅ **角色生成需要详细 character 对象 + 统一 prompt 字段**

### **输出处理**：
- 图像保存在 `/mnt/user-data/outputs/`
- 使用 `present_files` 工具分享
- 提供生成结果简要描述
- 提供迭代优化选项

---

## 🚀 与 OpenAI Frontend 对比

| 特性 | DeerFlow Image Generation | OpenAI Frontend |
|------|---------------------------|-----------------|
| **专注** | 图像生成 | 前端设计 |
| **输出** | 图像文件 | 设计代码 |
| **提示词** | 结构化 JSON | 自然语言 |
| **参考图** | ✅ 支持 | ❌ 不涉及 |
| **场景** | 角色、场景、产品 | 落地页、应用 |

---

## 💡 建议整合

### **可以安装到主技能目录**：
```bash
cp -r /root/.openclaw/workspace/projects/deerflow-study/deer-flow-source/skills/public/image-generation \
     /root/.openclaw/workspace/skills/deerflow-image-generation
```

### **或者创建软链接**：
```bash
ln -s /root/.openclaw/workspace/projects/deerflow-study/deer-flow-source/skills/public/image-generation \
      /root/.openclaw/workspace/skills/image-generation
```

---

## ✅ 总结

**找到了！** 🎉

这是 **DeerFlow Image Generation Skill**，一个强大的图像生成技能，支持：
- ✅ 结构化 JSON 提示词
- ✅ 参考图像引导
- ✅ 多种场景模板
- ✅ Python 脚本自动化

**需要我将它安装到主技能目录吗？或者创建一个软链接？** 🚀✨
