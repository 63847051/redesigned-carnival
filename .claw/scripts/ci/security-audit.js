#!/usr/bin/env node

/**
 * security-audit.js - 安全审计脚本
 * 
 * 功能: 扫描配置文件，检查凭证文件，验证 Hook 安全
 */

const fs = require('fs');
const path = require('path');

// 配置
const WORKSPACE = process.cwd();

// 敏感模式
const SECRET_PATTERNS = [
  { name: 'Stripe API Key', pattern: /sk_[a-zA-Z0-9]{24,}/g },
  { name: 'GitHub Token', pattern: /ghp_[a-zA-Z0-9]{36}/g },
  { name: 'AWS Access Key', pattern: /AKIA[0-9A-Z]{16}/g },
  { name: 'Google API Key', pattern: /AIza[0-9A-Za-z\-_]{35}/g },
  { name: 'OAuth Token', pattern: /ya29\.[a-zA-Z0-9\-_]{100,}/g },
  { name: 'Slack Token', pattern: /xoxb-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{24}/g }
];

// 扫描文件中的敏感信息
function scanSecrets(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const findings = [];
    
    SECRET_PATTERNS.forEach(({ name, pattern }) => {
      const matches = content.match(pattern);
      if (matches) {
        findings.push({
          type: name,
          count: matches.length,
          samples: matches.slice(0, 2) // 只显示前 2 个
        });
      }
    });
    
    return findings;
  } catch (error) {
    return [];
  }
}

// 检查文件权限
function checkFilePermissions(filePath) {
  try {
    const stats = fs.statSync(filePath);
    const mode = stats.mode;
    const octal = (mode & parseInt('777', 8)).toString(8);
    
    // 检查是否可被其他用户读取
    const othersReadable = (mode & parseInt('0004', 8)) !== 0;
    
    return {
      path: filePath,
      permissions: octal,
      issue: othersReadable,
      recommendation: '600'
    };
  } catch (error) {
    return null;
  }
}

// 扫描敏感文件
function scanSensitiveFiles() {
  const sensitiveFiles = [
    '.env',
    '.key',
    '.pem',
    'credentials.json',
    'config.json'
  ];
  
  const results = [];
  
  for (const file of sensitiveFiles) {
    const filePath = path.join(WORKSPACE, file);
    if (fs.existsSync(filePath)) {
      const perms = checkFilePermissions(filePath);
      if (perms) {
        results.push(perms);
      }
    }
  }
  
  return results;
}

// 检查 Hook 脚本安全性
function auditHookScripts() {
  const hooksDir = path.join(WORKSPACE, '.claw/hooks');
  const issues = [];
  
  if (!fs.existsSync(hooksDir)) {
    return [];
  }
  
  const files = fs.readdirSync(hooksDir).filter(f => f.endsWith('.js'));
  
  files.forEach(file => {
    const filePath = path.join(hooksDir, file);
    const content = fs.readFileSync(filePath, 'utf-8');
    
    // 检查是否使用了 eval
    if (content.includes('eval(')) {
      issues.push({
        file,
        issue: '使用 eval()',
        severity: 'high',
        recommendation: '避免使用 eval()，使用更安全的方法'
      });
    }
    
    // 检查是否使用了 exec
    if (content.includes('exec(') || content.includes('execSync(')) {
      issues.push({
        file,
        issue: '使用 exec/execSync',
        severity: 'medium',
        recommendation: '验证输入，避免命令注入'
      });
    }
  });
  
  return issues;
}

// 生成审计报告
function generateReport() {
  console.log('\n🔒 安全审计报告');
  console.log('='.repeat(60));
  console.log(`时间: ${new Date().toLocaleString('zh-CN')}`);
  
  // 1. 扫描敏感文件权限
  console.log('\n📁 敏感文件权限:');
  const fileResults = scanSensitiveFiles();
  
  if (fileResults.length === 0) {
    console.log('   ✅ 未发现敏感文件');
  } else {
    fileResults.forEach(result => {
      if (result.issue) {
        console.log(`   ⚠️  ${result.path}`);
        console.log(`      当前权限: ${result.permissions}`);
        console.log(`      建议权限: ${result.recommendation}`);
      } else {
        console.log(`   ✅ ${result.path} (${result.permissions})`);
      }
    });
  }
  
  // 2. 检查 Hook 脚本安全
  console.log('\n🪝 Hook 脚本安全:');
  const hookIssues = auditHookScripts();
  
  if (hookIssues.length === 0) {
    console.log('   ✅ 未发现安全问题');
  } else {
    hookIssues.forEach(issue => {
      console.log(`   ⚠️  ${issue.file}`);
      console.log(`      问题: ${issue.issue}`);
      console.log(`      严重性: ${issue.severity}`);
      console.log(`      建议: ${issue.recommendation}`);
    });
  }
  
  // 3. 扫描代码中的敏感信息
  console.log('\n🔍 代码中的敏感信息:');
  const codeFiles = [
    'SOUL.md',
    'MEMORY.md',
    'IDENTITY.md'
  ];
  
  let secretCount = 0;
  codeFiles.forEach(file => {
    const filePath = path.join(WORKSPACE, file);
    if (fs.existsSync(filePath)) {
      const findings = scanSecrets(filePath);
      if (findings.length > 0) {
        console.log(`   ⚠️  ${file}:`);
        findings.forEach(finding => {
          console.log(`      ${finding.type}: ${finding.count} 个`);
          secretCount += finding.count;
        });
      }
    }
  });
  
  if (secretCount === 0) {
    console.log('   ✅ 未发现敏感信息');
  }
  
  // 总结
  console.log('\n' + '='.repeat(60));
  const totalIssues = fileResults.filter(r => r.issue).length + hookIssues.length + secretCount;
  
  if (totalIssues === 0) {
    console.log('✅ 安全审计完成 - 未发现问题');
  } else {
    console.log(`⚠️  安全审计完成 - 发现 ${totalIssues} 个问题`);
  }
  
  console.log('');
}

// 主函数
function main() {
  generateReport();
}

// 运行
main();
