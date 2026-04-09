#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const CLAW_DIR = path.join(__dirname, '../../../.claw');
const OUTPUT_DIR = path.join(__dirname, '../../../data');

function ensureDir(dir) {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
}

function scanDirectory(dir, type) {
    const files = [];
    if (!fs.existsSync(dir)) {
        return files;
    }

    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
        if (entry.isDirectory()) {
            const subDir = path.join(dir, entry.name);
            const subFiles = scanDirectory(subDir, type);
            files.push(...subFiles);
        } else if (entry.isFile() && (entry.name.endsWith('.js') || entry.name.endsWith('.cjs'))) {
            const filePath = path.join(dir, entry.name);
            const stats = fs.statSync(filePath);
            files.push({
                name: entry.name.replace('.js', ''),
                type,
                path: path.relative(CLAW_DIR, filePath),
                size: stats.size,
                modified: stats.mtime.toISOString()
            });
        }
    }
    return files;
}

function generateCatalog() {
    ensureDir(OUTPUT_DIR);

    const agents = scanDirectory(path.join(CLAW_DIR, 'agents'), 'agent');
    const skills = scanDirectory(path.join(CLAW_DIR, 'skills'), 'skill');
    const commands = scanDirectory(path.join(CLAW_DIR, 'commands'), 'command');
    const hooks = scanDirectory(path.join(CLAW_DIR, 'hooks'), 'hook');
    const rules = scanDirectory(path.join(CLAW_DIR, 'rules'), 'rule');

    const catalog = {
        generated: new Date().toISOString(),
        agents,
        skills,
        commands,
        hooks,
        rules,
        summary: {
            agents: agents.length,
            skills: skills.length,
            commands: commands.length,
            hooks: hooks.length,
            rules: rules.length,
            total: agents.length + skills.length + commands.length + hooks.length + rules.length
        }
    };

    const jsonPath = path.join(OUTPUT_DIR, 'claw-catalog.json');
    fs.writeFileSync(jsonPath, JSON.stringify(catalog, null, 2));

    const mdPath = path.join(OUTPUT_DIR, 'claw-catalog.md');
    let md = '# Claw Catalog\n\n';
    md += `Generated: ${catalog.generated}\n\n`;
    md += '## Summary\n\n';
    md += `- Agents: ${catalog.summary.agents}\n`;
    md += `- Skills: ${catalog.summary.skills}\n`;
    md += `- Commands: ${catalog.summary.commands}\n`;
    md += `- Hooks: ${catalog.summary.hooks}\n`;
    md += `- Rules: ${catalog.summary.rules}\n`;
    md += `- **Total**: ${catalog.summary.total}\n\n`;

    if (catalog.agents.length) {
        md += '## Agents\n\n';
        catalog.agents.forEach(a => md += `- ${a.name}: ${a.path}\n`);
        md += '\n';
    }
    if (catalog.skills.length) {
        md += '## Skills\n\n';
        catalog.skills.forEach(s => md += `- ${s.name}: ${s.path}\n`);
        md += '\n';
    }
    if (catalog.commands.length) {
        md += '## Commands\n\n';
        catalog.commands.forEach(c => md += `- ${c.name}: ${c.path}\n`);
        md += '\n';
    }
    fs.writeFileSync(mdPath, md);

    console.log('✅ 目录已生成');
    console.log(`   JSON: ${jsonPath}`);
    console.log(`   Markdown: ${mdPath}`);
    console.log(`   Total entries: ${catalog.summary.total}`);
}

generateCatalog();