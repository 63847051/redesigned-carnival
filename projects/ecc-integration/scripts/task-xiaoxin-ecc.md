# 小新的任务 - ECC 安全增强（Phase 1）

**任务类型**: 技术实施
**分配时间**: 2026-04-08 06:58
**预期完成**: 2026-04-08 12:00

---

## 🎯 任务目标

建立 ECC 风格的系统化基础架构

---

## 📋 具体步骤

### Step 1: 创建单一数据源脚本（30 分钟）

**文件**: `/root/.openclaw/workspace/projects/ecc-integration/.claw/scripts/ci/catalog.js`

**功能**:
1. 扫描 agents/, skills/, commands/ 目录
2. 生成目录（JSON/Markdown 格式）
3. CI 验证（检查重复、缺失）

**代码框架**:
```javascript
#!/usr/bin/env node
/**
 * 单一数据源生成器
 * 扫描 .claw/ 目录，生成统一的目录
 */

const fs = require('fs');
const path = require('path');

const CLAW_DIR = path.join(__dirname, '../../.claw');
const OUTPUT_DIR = path.join(__dirname, '../../../data');

function scanDirectory(dir, type) {
    // 扫描目录，返回文件列表
    const files = [];
    // TODO: 实现扫描逻辑
    return files;
}

function generateCatalog() {
    const agents = scanDirectory(path.join(CLAW_DIR, 'agents'), 'agent');
    const skills = scanDirectory(path.join(CLAW_DIR, 'skills'), 'skill');
    const commands = scanDirectory(path.join(CLAW_DIR, 'commands'), 'command');

    const catalog = { agents, skills, commands };

    // 保存 JSON
    fs.writeFileSync(
        path.join(OUTPUT_DIR, 'claw-catalog.json'),
        JSON.stringify(catalog, null, 2)
    );

    console.log('✅ 目录已生成');
}

generateCatalog();
```

### Step 2: 创建基础测试（30 分钟）

**文件**: `/root/.openclaw/workspace/projects/ecc-integration/tests/unit/test_catalog.js`

**功能**:
1. 测试目录生成
2. 验证数据完整性
3. CI 集成

### Step 3: 创建 Hook 示例（30 分钟）

**文件**: `/root/.openclaw/workspace/projects/ecc-integration/.claw/hooks/session-start.js`

**功能**:
1. Session 开始时的 Hook
2. 记录日志
3. 初始化数据

### Step 4: 更新文档（15 分钟）

更新 `IMPLEMENTATION.md`，记录完成情况。

---

## ✅ 验收标准

1. ✅ `.claw/` 目录结构创建完成
2. ✅ 单一数据源脚本可以运行
3. ✅ 基础测试通过
4. ✅ Hook 示例可以工作

---

## 📞 汇报要求

完成后向大领导汇报：
- 目录结构
- 目录生成结果
- 测试结果
- 下一步建议

---

**任务分配者**: 大领导 🎯
**任务接收者**: 小新 💻
**状态**: 🔄 待执行
