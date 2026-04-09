# DeerFlow Image Generation Skill

**版本**: 1.0
**来源**: DeerFlow Project
**安装时间**: 2026-04-05 23:15
**位置**: `/root/.openclaw/workspace/skills/deerflow-image-generation/`

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
- "设计一个角色"

---

## 📋 工作流程

### **Step 1: 理解需求**
识别：
- **主题/内容**：图像中应该有什么
- **风格偏好**：艺术风格、情绪、色彩
- **技术规格**：宽高比、构图、光照
- **参考图像**：引导生成的图像

### **Step 2: 创建结构化提示词**
生成 JSON 文件：`/mnt/user-data/workspace/{name}.json`

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
  "prompt": "Character description...",
  "negative_prompt": "blurry face, deformed, low quality",
  "style": "Leica M11 street photography aesthetic",
  "composition": "medium shot, rule of thirds",
  "lighting": "neon lights, wet pavement reflections",
  "color_palette": "muted naturalistic tones",
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

**参数说明**：
- `--prompt-file`: JSON 提示词文件路径（必需）
- `--reference-images`: 参考图像路径（可选，空格分隔）
- `--output-file`: 输出图像文件路径（必需）
- `--aspect-ratio`: 宽高比（可选，默认 16:9）

---

## 🎨 核心特性

### **1. 结构化 JSON 提示词** ⭐⭐⭐
- **characters**: 详细角色描述
- **prompt**: 统一提示词
- **negative_prompt**: 负面提示词
- **style**: 艺术风格
- **composition**: 构图
- **lighting**: 光照
- **color_palette**: 色彩
- **technical**: 技术规格

### **2. 参考图像支持** ⭐⭐⭐
- 使用 `image_search` 工具先找参考图
- 支持多张参考图像
- 提供风格/构图引导

### **3. Negative Prompt**
```json
{
  "negative_prompt": "blurry face, deformed, low quality, overly sharp digital look"
}
```

---

## 📊 场景模板

### **角色设计**
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
  }]
}
```

**字段说明**：
- **gender**: 性别
- **age**: 年龄
- **ethnicity**: 种族
- **body_type**: 体型
- **facial_features**: 面部特征
- **clothing**: 服装
- **accessories**: 配饰
- **era**: 时代

### **场景生成**
```json
{
  "environment": "Tokyo street at night",
  "time_of_day": "midnight",
  "weather": "rainy",
  "mood": "cyberpunk, neon-lit",
  "focal_points": "character, neon signs, wet pavement"
}
```

### **产品可视化**
```json
{
  "product": "luxury watch",
  "materials": "stainless steel, leather",
  "lighting": "studio lighting",
  "background": "minimalist",
  "presentation_angle": "front view"
}
```

---

## 💡 高级技巧

### **使用参考图像提升质量** ⭐⭐⭐

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
    "facial_features": "delicate features, expressive eyes, subtle makeup with emphasis on lips, long dark hair partially wet from rain",
    "clothing": "stylish trench coat, designer handbag, high heels, contemporary Tokyo street fashion",
    "accessories": "minimal jewelry, statement earrings, leather handbag",
    "era": "1990s"
  }],
  "negative_prompt": "blurry face, deformed, low quality, overly sharp digital look, oversaturated colors, artificial lighting, studio setting, posed, selfie angle",
  "style": "Leica M11 street photography aesthetic, film-like rendering, natural color palette with slight warmth, bokeh background blur, analog photography feel",
  "composition": "medium shot, rule of thirds, subject slightly off-center, environmental context of Tokyo street visible, shallow depth of field isolating subject",
  "lighting": "neon lights from signs and storefronts, wet pavement reflections, soft ambient city glow, natural street lighting, rim lighting from background neons",
  "color_palette": "muted naturalistic tones, warm skin tones, cool blue and magenta neon accents, desaturated compared to digital photography, film grain texture",
  "technical": {
    "aspect_ratio": "2:3",
    "quality": "high",
    "detail_level": "highly detailed with film-like texture"
  }
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

## 🚀 与其他技能对比

| 特性 | DeerFlow Image Gen | OpenAI Frontend |
|------|-------------------|-----------------|
| **专注** | 图像生成 | 前端设计 |
| **输出** | 图像文件 | 设计代码 |
| **提示词** | 结构化 JSON | 自然语言 |
| **参考图** | ✅ 支持 | ❌ 不涉及 |
| **场景** | 角色、场景、产品 | 落地页、应用 |

---

## ✅ 安装完成

**技能目录**: `/root/.openclaw/workspace/skills/deerflow-image-generation/`
**主文件**: `SKILL.md`
**脚本**: `scripts/generate.py`
**模板**: `templates/`

**状态**: ✅ 已安装

**需要测试这个技能吗？** 🎨✨
