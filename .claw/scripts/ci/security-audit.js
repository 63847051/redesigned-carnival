#!/usr/bin/env node

/**
 * security-audit.js - 安全审计脚本
 * 
 * 功能: 执行全面的安全审计
 * - 扫描配置文件
 * - 检查凭证文件
 * - 验证 Hook 安全
 * - 生成审计报告
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 配置
const WORKSPACE = process.cwd();
const CONFIG_FILE = path.join(WORKSPACE, '.claw', 'rules', 'security', 'config.json');
const REPORTS_DIR = path.join(WORKSPACE, '.claw', 'reports');

// 加载配置
let config;
try {
  config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
} catch (error) {
  console.error(`❌ 无法加载配置文件: ${error.message}`);
  process.exit(1);
}

// 审计结果
const auditResults = {
  timestamp: new Date().toISOString(),
  workspace: WORKSPACE,
  findings: [],
  summary: {
    high: 0,
    medium: 0,
    low: 0,
    total: 0
  }
};

// 扫描敏感信息
function scanSensitiveInfo() {
  console.log('\n🔍 扫描敏感信息...');
  
  const sensitiveInfo = config.sensitiveInfo;
  if (!sensitiveInfo.enabled) {
    console.log('   ⏭️  已跳过');
    return;
  }
  
  let findings = 0;
  
  // 扫描目录
  function scanDirectory(dir, depth = 0) {
    if (depth > 10) return; // 限制深度
    
    try {
      const files = fs.readdirSync(dir);
      
      for (const file of files) {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);
        
        // 跳过排除的目录
        if (stat.isDirectory()) {
          if (config.excludeDirectories.some(excluded => filePath.includes(excluded))) {
            continue;
          }
          scanDirectory(filePath, depth + 1);
          continue;
        }
        
        // 检查文件扩展名
        const ext = path.extname(file);
        if (!sensitiveInfo.fileExtensions.includes(ext)) {
          continue;
        }
        
        // 跳过排除的文件
        if (config.excludeFiles.some(excluded => file.match(excluded.replace('*', '.*')))) {
          continue;
        }
        
        // 读取文件内容
        try {
          const content = fs.readFileSync(filePath, 'utf-8');
          const lines = content.split('\n');
          
          // 检查每个模式
          for (const [name, patternInfo] of Object.entries(sensitiveInfo.patterns)) {
            const pattern = new RegExp(patternInfo.pattern, 'gi');
            let match;
            let lineNum = 0;
            
            while ((match = pattern.exec(content)) !== null) {
              lineNum = content.substring(0, match.index).split('\n').length;
              
              findings++;
              
              auditResults.findings.push({
                type: 'sensitive-info',
                severity: patternInfo.severity,
                file: filePath.replace(WORKSPACE + '/', ''),
                line: lineNum,
                pattern: name,
                description: patternInfo.description,
                match: match[0].substring(0, 50) + '...'
              });
            }
          }
        } catch (readError) {
          // 跳过无法读取的文件
        }
      }
    } catch (error) {
      // 跳过无法访问的目录
    }
  }
  
  scanDirectory(WORKSPACE);
  
  console.log(`   ✅ 发现 ${findings} 个问题`);
}

// 检查文件权限
function checkFilePermissions() {
  console.log('\n🔒 检查文件权限...');
  
  const filePermissions = config.filePermissions;
  if (!filePermissions.enabled) {
    console.log('   ⏭️  已跳过');
    return;
  }
  
  let findings = 0;
  
  for (const rule of filePermissions.rules) {
    try {
      // 解析模式
      const pattern = rule.pattern.replace(/\*\*/g, '.*').replace(/\*/g, '[^/]*');
      const regex = new RegExp('^' + pattern + '$');
      
      // 查找匹配的文件
      function findFiles(dir, pattern, depth = 0) {
        if (depth > 10) return [];
        
        let results = [];
        try {
          const files = fs.readdirSync(dir);
          
          for (const file of files) {
            const filePath = path.join(dir, file);
            const stat = fs.statSync(filePath);
            
            if (stat.isDirectory()) {
              if (config.excludeDirectories.some(excluded => filePath.includes(excluded))) {
                continue;
              }
              results = results.concat(findFiles(filePath, pattern, depth + 1));
            } else {
              const relativePath = filePath.replace(WORKSPACE + '/', '');
              if (regex.test(relativePath)) {
                results.push(filePath);
              }
            }
          }
        } catch (error) {
          // 跳过无法访问的目录
        }
        
        return results;
      }
      
      const files = findFiles(WORKSPACE, pattern);
      
      for (const file of files) {
        try {
          const stats = fs.statSync(file);
          const mode = stats.mode.toString(8).slice(-3);
          const expected = rule.expectedPermissions.slice(-3);
          
          if (mode !== expected) {
            findings++;
            
            auditResults.findings.push({
              type: 'file-permissions',
              severity: rule.severity,
              file: file.replace(WORKSPACE + '/', ''),
              current: mode,
              expected: expected,
              description: rule.description,
              command: `chmod ${rule.expectedPermissions} ${file}`
            });
          }
        } catch (error) {
          // 跳过无法检查的文件
        }
      }
    } catch (error) {
      console.error(`   ❌ 检查权限失败: ${error.message}`);
    }
  }
  
  console.log(`   ✅ 发现 ${findings} 个问题`);
}

// 审计凭证文件
function auditCredentials() {
  console.log('\n🔐 审计凭证文件...');
  
  const credentialsAudit = config.credentialsAudit;
  if (!credentialsAudit.enabled) {
    console.log('   ⏭️  已跳过');
    return;
  }
  
  let findings = 0;
  
  for (const auditFile of credentialsAudit.auditFiles) {
    const filePath = path.join(WORKSPACE, auditFile);
    
    try {
      if (!fs.existsSync(filePath)) {
        continue;
      }
      
      const stats = fs.statSync(filePath);
      const mode = stats.mode.toString(8).slice(-3);
      
      // 检查权限
      if (mode !== '600' && mode !== '400') {
        findings++;
        
        auditResults.findings.push({
          type: 'credentials-audit',
          severity: 'high',
          file: auditFile,
          issue: 'permissions',
          current: mode,
          expected: '600',
          description: '凭证文件权限过宽'
        });
      }
      
      // 检查是否在 .gitignore 中
      try {
        const gitignore = fs.readFileSync(path.join(WORKSPACE, '.gitignore'), 'utf-8');
        const ignored = gitignore.split('\n').some(line => {
          const pattern = line.trim().replace(/\*\*/g, '.*').replace(/\*/g, '[^/]*');
          return auditFile.match(new RegExp(pattern));
        });
        
        if (!ignored) {
          findings++;
          
          auditResults.findings.push({
            type: 'credentials-audit',
            severity: 'medium',
            file: auditFile,
            issue: 'gitignore',
            description: '凭证文件未在 .gitignore 中',
            suggestion: `添加 "${auditFile}" 到 .gitignore`
          });
        }
      } catch (error) {
        // .gitignore 不存在
      }
    } catch (error) {
      // 文件不存在或无法访问
    }
  }
  
  console.log(`   ✅ 发现 ${findings} 个问题`);
}

// 验证 Hook 安全
function verifyHookSecurity() {
  console.log('\n🪝 验证 Hook 安全...');
  
  const hookSecurity = config.hookSecurity;
  if (!hookSecurity.enabled) {
    console.log('   ⏭️  已跳过');
    return;
  }
  
  let findings = 0;
  const hooksDir = path.join(WORKSPACE, '.claw', 'hooks');
  
  for (const hookScript of hookSecurity.hookScripts) {
    const hookPath = path.join(hooksDir, hookScript);
    
    try {
      if (!fs.existsSync(hookPath)) {
        findings++;
        
        auditResults.findings.push({
          type: 'hook-security',
          severity: 'high',
          file: hookScript,
          issue: 'missing',
          description: 'Hook 脚本不存在'
        });
        continue;
      }
      
      // 检查可执行权限
      const stats = fs.statSync(hookPath);
      const mode = stats.mode.toString(8);
      const executable = (mode & parseInt('0111', 8)) !== 0;
      
      if (!executable) {
        findings++;
        
        auditResults.findings.push({
          type: 'hook-security',
          severity: 'medium',
          file: hookScript,
          issue: 'not-executable',
          description: 'Hook 脚本不可执行',
          command: `chmod +x ${hookPath}`
        });
      }
      
      // 检查语法
      try {
        execSync(`node --check "${hookPath}"`, { stdio: 'pipe' });
      } catch (error) {
        findings++;
        
        auditResults.findings.push({
          type: 'hook-security',
          severity: 'high',
          file: hookScript,
          issue: 'syntax-error',
          description: 'Hook 脚本语法错误',
          error: error.message
        });
      }
    } catch (error) {
      // 无法检查 Hook
    }
  }
  
  console.log(`   ✅ 发现 ${findings} 个问题`);
}

// 生成审计报告
function generateReport() {
  console.log('\n📊 生成审计报告...');
  
  // 统计
  for (const finding of auditResults.findings) {
    auditResults.summary.total++;
    if (finding.severity === 'high') auditResults.summary.high++;
    else if (finding.severity === 'medium') auditResults.summary.medium++;
    else if (finding.severity === 'low') auditResults.summary.low++;
  }
  
  // 确保报告目录存在
  if (!fs.existsSync(REPORTS_DIR)) {
    fs.mkdirSync(REPORTS_DIR, { recursive: true });
  }
  
  // 生成报告文件名
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0] + '-' +
                    new Date().toTimeString().split(' ')[0].replace(/:/g, '-');
  const reportFile = path.join(REPORTS_DIR, `security-audit-${timestamp}.md`);
  
  // 生成 Markdown 报告
  let report = `# 安全审计报告

**审计时间**: ${new Date().toLocaleString('zh-CN')}
**审计范围**: ${WORKSPACE}
**配置版本**: ${config.version}

---

## 📊 审计摘要

- **发现问题**: ${auditResults.summary.total}
- **高危**: ${auditResults.summary.high}
- **中危**: ${auditResults.summary.medium}
- **低危**: ${auditResults.summary.low}

---

`;
  
  // 按严重程度分组
  if (config.reporting.groupBySeverity) {
    const high = auditResults.findings.filter(f => f.severity === 'high');
    const medium = auditResults.findings.filter(f => f.severity === 'medium');
    const low = auditResults.findings.filter(f => f.severity === 'low');
    
    if (high.length > 0) {
      report += `## 🚨 高危问题 (${high.length})\n\n`;
      for (const finding of high) {
        report += `### ${finding.type}\n\n`;
        report += `- **文件**: \`${finding.file}\`\n`;
        if (finding.line) report += `- **行号**: ${finding.line}\n`;
        if (finding.current) report += `- **当前**: ${finding.current}\n`;
        if (finding.expected) report += `- **期望**: ${finding.expected}\n`;
        report += `- **问题**: ${finding.description}\n`;
        if (finding.command) report += `- **修复**: \`${finding.command}\`\n`;
        if (finding.suggestion) report += `- **建议**: ${finding.suggestion}\n`;
        report += '\n';
      }
    }
    
    if (medium.length > 0) {
      report += `## ⚠️ 中危问题 (${medium.length})\n\n`;
      for (const finding of medium) {
        report += `### ${finding.type}\n\n`;
        report += `- **文件**: \`${finding.file}\`\n`;
        if (finding.line) report += `- **行号**: ${finding.line}\n`;
        if (finding.current) report += `- **当前**: ${finding.current}\n`;
        if (finding.expected) report += `- **期望**: ${finding.expected}\n`;
        report += `- **问题**: ${finding.description}\n`;
        if (finding.command) report += `- **修复**: \`${finding.command}\`\n`;
        if (finding.suggestion) report += `- **建议**: ${finding.suggestion}\n`;
        report += '\n';
      }
    }
    
    if (low.length > 0) {
      report += `## 💡 低危问题 (${low.length})\n\n`;
      for (const finding of low) {
        report += `### ${finding.type}\n\n`;
        report += `- **文件**: \`${finding.file}\`\n`;
        if (finding.line) report += `- **行号**: ${finding.line}\n`;
        report += `- **问题**: ${finding.description}\n`;
        if (finding.suggestion) report += `- **建议**: ${finding.suggestion}\n`;
        report += '\n';
      }
    }
  }
  
  // 添加建议
  report += `## ✅ 安全建议\n\n`;
  
  if (auditResults.summary.high > 0) {
    report += `1. 🔴 **立即修复** ${auditResults.summary.high} 个高危问题\n`;
  }
  if (auditResults.summary.medium > 0) {
    report += `2. 🟡 **尽快修复** ${auditResults.summary.medium} 个中危问题\n`;
  }
  if (auditResults.summary.low > 0) {
    report += `3. 🟢 **计划修复** ${auditResults.summary.low} 个低危问题\n`;
  }
  
  report += `
4. 🔄 **定期执行** 安全审计
5. 📚 **建立** 安全审计流程
6. 🔐 **启用** Hook 安全检查
7. 🚨 **监控** 异常访问
8. 📖 **学习** 安全最佳实践

---

**审计完成时间**: ${new Date().toLocaleString('zh-CN')}
**审计工具**: security-audit.js v${config.version}
`;
  
  // 写入报告
  fs.writeFileSync(reportFile, report);
  
  console.log(`   ✅ 报告已生成: ${reportFile.replace(WORKSPACE + '/', '')}`);
  
  return reportFile;
}

// 主函数
function main() {
  console.log('\n🔒 安全审计工具');
  console.log('='.repeat(60));
  console.log(`\n工作区: ${WORKSPACE}`);
  console.log(`配置版本: ${config.version}`);
  console.log(`审计时间: ${new Date().toLocaleString('zh-CN')}`);
  
  // 执行审计
  scanSensitiveInfo();
  checkFilePermissions();
  auditCredentials();
  verifyHookSecurity();
  
  // 生成报告
  const reportFile = generateReport();
  
  // 显示摘要
  console.log('\n📋 审计摘要:');
  console.log(`   总问题数: ${auditResults.summary.total}`);
  console.log(`   高危: ${auditResults.summary.high}`);
  console.log(`   中危: ${auditResults.summary.medium}`);
  console.log(`   低危: ${auditResults.summary.low}`);
  
  console.log('\n' + '='.repeat(60));
  
  if (auditResults.summary.high > 0) {
    console.log('⚠️  发现高危问题，请立即查看报告！');
    process.exit(1);
  } else if (auditResults.summary.total > 0) {
    console.log('✅ 审计完成，发现问题已记录');
    process.exit(0);
  } else {
    console.log('✅ 审计完成，未发现安全问题');
    process.exit(0);
  }
}

// 运行
main();
