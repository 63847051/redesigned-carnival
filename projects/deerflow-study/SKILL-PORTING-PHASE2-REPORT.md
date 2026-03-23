# DeerFlow 技能移植报告 - Phase2 (设计相关)
## 移植信息
- **日期**: 2026-03-23
- **源目录**: /root/.openclaw/workspace/projects/deerflow-study/deer-flow-source/skills/public
- **目标目录**: /root/.openclaw/skills
- **技能数量**: 5

## 技能列表

### ✅ frontend-design
- **描述**: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, artifacts, posters, or applications (examples include websites, landing pages, dashboards, React components, HTML/CSS layouts, or when styling/beautifying any web UI). Generates creative, polished code and UI design that avoids generic AI aesthetics.
- **状态**: 移植成功

### 📁 frontend-design

```
  • LICENSE.txt
  • SKILL.md
```

### ✅ chart-visualization
- **描述**: This skill should be used when the user wants to visualize data. It intelligently selects the most suitable chart type from 26 available options, extracts parameters based on detailed specifications, and generates a chart image using a JavaScript script.
- **状态**: 移植成功

### 📁 chart-visualization

```
  • references/generate_area_chart.md
  • references/generate_bar_chart.md
  • references/generate_boxplot_chart.md
  • references/generate_column_chart.md
  • references/generate_district_map.md
  • references/generate_dual_axes_chart.md
  • references/generate_fishbone_diagram.md
  • references/generate_flow_diagram.md
  • references/generate_funnel_chart.md
  • references/generate_histogram_chart.md
  • references/generate_line_chart.md
  • references/generate_liquid_chart.md
  • references/generate_mind_map.md
  • references/generate_network_graph.md
  • references/generate_organization_chart.md
  • references/generate_path_map.md
  • references/generate_pie_chart.md
  • references/generate_pin_map.md
  • references/generate_radar_chart.md
  • references/generate_sankey_chart.md
  • references/generate_scatter_chart.md
  • references/generate_spreadsheet.md
  • references/generate_treemap_chart.md
  • references/generate_venn_chart.md
  • references/generate_violin_chart.md
  • references/generate_word_cloud_chart.md
  • scripts/generate.js
  • SKILL.md
```

### ✅ image-generation
- **描述**: Use this skill when the user requests to generate, create, imagine, or visualize images including characters, scenes, products, or any visual content. Supports structured prompts and reference images for guided generation.
- **状态**: 移植成功

### 📁 image-generation

```
  • scripts/generate.py
  • SKILL.md
  • templates/doraemon.md
```

### ✅ ppt-generation
- **描述**: Use this skill when the user requests to generate, create, or make presentations (PPT/PPTX). Creates visually rich slides by generating images for each slide and composing them into a PowerPoint file.
- **状态**: 移植成功

### 📁 ppt-generation

```
  • scripts/generate.py
  • SKILL.md
```

### ✅ web-design-guidelines
- **描述**: Review UI code for Web Interface Guidelines compliance. Use when asked to review my UI, check accessibility, audit design, review UX, or check my site against best practices.
- **状态**: 移植成功

### 📁 web-design-guidelines

```
  • SKILL.md
```

## 总结

| 项目 | 数量 |
|------|------|
| 总技能数 | 5 |
| 成功移植 | 5 |
| 移植失败 | 0 |

