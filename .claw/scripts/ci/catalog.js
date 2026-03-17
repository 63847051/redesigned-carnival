#!/usr/bin/env node

/**
 * catalog.js - 大领导系统单一数据源生成器
 * 
 * 功能:
 * - 扫描 .claw/agents/, skills/, commands/ 目录
 * - 生成 JSON 格式的目录清单
 * - 生成 Markdown 格式的文档摘要
 */

const fs = require('fs');
const path = require('path');

// 配置
const CLAW_DIR = path.join(process.cwd(), '.claw');
const OUTPUT_JSON = path.join(CLAW_DIR, 'catalog.json');
const OUTPUT_MD = path.join(CLAW_DIR, 'CATALOG.md');

// 扫描目录
function scanDirectory(dirPath, pattern = /.md$/) {
  try {
    if (!fs.existsSync(dirPath)) {
      return { count: 0, list: [] };
    }

    const files = fs.readdirSync(dirPath);
    const items = [];

    for (const file of files) {
      const filePath = path.join(dirPath, file);
      const stat = fs.statSync(filePath);

      if (stat.isFile() && pattern.test(file)) {
        // 读取文件获取元数据
        const content = fs.readFileSync(filePath, 'utf-8');
        const metadata = extractMetadata(content, file);
        items.push(metadata);
      } else if (stat.isDirectory()) {
        // 递归扫描子目录（如 skills/子技能/）
        const subItems = scanDirectory(filePath, pattern);
        items.push(...subItems.list);
      }
    }

    return {
      count: items.length,
      list: items
    };
  } catch (error) {
    console.error(`扫描目录失败: ${dirPath}`, error.message);
    return { count: 0, list: [] };
  }
}

// 提取文件元数据
function extractMetadata(content, filename) {
  // 提取 YAML frontmatter
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
  let metadata = {
    name: filename.replace(/\.md$/, ''),
    description: '',
    type: 'unknown'
  };

  if (frontmatterMatch) {
    const frontmatter = frontmatterMatch[1];
    const lines = frontmatter.split('\n');
    
    for (const line of lines) {
      const match = line.match(/^(\w+):\s*(.+)$/);
      if (match) {
        const [, key, value] = match;
        if (key === 'name' || key === 'title' || key === 'description') {
          metadata[key === 'title' ? 'name' : key] = value;
        }
      }
    }
  }

  // 如果没有 frontmatter，从内容中提取第一行标题
  if (!metadata.description) {
    const titleMatch = content.match(/^#\s+(.+)$/m);
    if (titleMatch) {
      metadata.name = titleMatch[1];
    }
  }

  return metadata;
}

// 生成 JSON 目录
function generateJSONCatalog(agents, skills, commands) {
  return {
    generated: new Date().toISOString(),
    agents: {
      count: agents.count,
      list: agents.list.map(a => ({
        name: a.name,
        description: a.description
      }))
    },
    skills: {
      count: skills.count,
      list: skills.list.map(s => ({
        name: s.name,
        description: s.description
      }))
    },
    commands: {
      count: commands.count,
      list: commands.list.map(c => ({
        name: c.name,
        description: c.description
      }))
    },
    summary: {
      total: agents.count + skills.count + commands.count,
      byType: {
        agents: agents.count,
        skills: skills.count,
        commands: commands.count
      }
    }
  };
}

// 生成 Markdown 目录
function generateMarkdownCatalog(agents, skills, commands) {
  let md = '# 大领导系统目录\n\n';
  md += `**生成时间**: ${new Date().toLocaleString('zh-CN')}\n\n`;
  md += `**总计**: ${agents.count + skills.count + commands.count} 项\n\n`;
  md += '---\n\n';

  // Agents
  md += '## Agents\n\n';
  md += `**数量**: ${agents.count}\n\n`;
  if (agents.list.length > 0) {
    agents.list.forEach(agent => {
      md += `### ${agent.name}\n`;
      if (agent.description) {
        md += `${agent.description}\n`;
      }
      md += '\n';
    });
  } else {
    md += '*暂无 Agents*\n\n';
  }

  // Skills
  md += '## Skills\n\n';
  md += `**数量**: ${skills.count}\n\n`;
  if (skills.list.length > 0) {
    skills.list.forEach(skill => {
      md += `### ${skill.name}\n`;
      if (skill.description) {
        md += `${skill.description}\n`;
      }
      md += '\n';
    });
  } else {
    md += '*暂无 Skills*\n\n';
  }

  // Commands
  md += '## Commands\n\n';
  md += `**数量**: ${commands.count}\n\n`;
  if (commands.list.length > 0) {
    commands.list.forEach(command => {
      md += `### ${command.name}\n`;
      if (command.description) {
        md += `${command.description}\n`;
      }
      md += '\n';
    });
  } else {
    md += '*暂无 Commands*\n\n';
  }

  return md;
}

// 主函数
function main() {
  console.log('🔍 扫描 .claw/ 目录...\n');

  // 扫描各目录
  const agents = scanDirectory(path.join(CLAW_DIR, 'agents'));
  const skills = scanDirectory(path.join(CLAW_DIR, 'skills'), /SKILL.md/);
  const commands = scanDirectory(path.join(CLAW_DIR, 'commands'));

  // 生成 JSON
  const jsonCatalog = generateJSONCatalog(agents, skills, commands);
  fs.writeFileSync(OUTPUT_JSON, JSON.stringify(jsonCatalog, null, 2));
  console.log(`✅ JSON 目录已生成: ${OUTPUT_JSON}`);

  // 生成 Markdown
  const mdCatalog = generateMarkdownCatalog(agents, skills, commands);
  fs.writeFileSync(OUTPUT_MD, mdCatalog);
  console.log(`✅ Markdown 目录已生成: ${OUTPUT_MD}`);

  // 打印摘要
  console.log('\n📊 目录摘要:');
  console.log(`  - Agents: ${agents.count}`);
  console.log(`  - Skills: ${skills.count}`);
  console.log(`  - Commands: ${commands.count}`);
  console.log(`  - 总计: ${agents.count + skills.count + commands.count}`);
}

// 运行
main();
