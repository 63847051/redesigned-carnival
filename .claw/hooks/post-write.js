#!/usr/bin/env node

/**
 * post-write.js - 写入后 Hook
 * 
 * 功能: 在文件写入后执行分析和记录
 * - 记录文件变更
 * - 分析文件大小变化
 * - 检测敏感信息泄露
 * - 更新 Git 状态（如果适用）
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 配置
const WORKSPACE = process.cwd();
const HOOKS_LOG_DIR = path.join(WORKSPACE, '.claw', '.learnings', 'hooks');
const WRITE_LOG = path.join(HOOKS_LOG_DIR, 'writes-YYYYMMDD.log');

// 敏感信息模式
const SENSITIVE_PATTERNS = [
  { name: 'API Key', pattern: /(?:api[_-]?key|apikey|API[_-]?KEY)\s*[:=]\s*['"]?([a-zA-Z0-9_\-]{20,})['"]?/g },
  { name: 'Secret', pattern: /(?:secret|password|token|SECRET|PASSWORD|TOKEN)\s*[:=]\s*['"]?([a-zA-Z0-9_\-]{20,})['"]?/g },
  { name: 'AWS Key', pattern: /AKIA[0-9A-Z]{16}/g },
  { name: 'Private Key', pattern: /-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----/g },
  { name: 'Database URL', pattern: /(?:mongodb|mysql|postgres|redis)\+?:\/\/[^\s'"`]+/g }
];

// 记录文件写入
function logWrite(filePath, fileSize, duration) {
  try {
    const timestamp = new Date().toISOString();
    const logDate = new Date().toISOString().split('T')[0].replace(/-/g, '');
    const logFile = WRITE_LOG.replace('YYYYMMDD', logDate);
    
    // 确保 hooks 目录存在
    if (!fs.existsSync(HOOKS_LOG_DIR)) {
      fs.mkdirSync(HOOKS_LOG_DIR, { recursive: true });
    }
    
    const logLine = `${timestamp} | ${filePath} | size=${fileSize} | duration=${duration}ms\n`;
    
    fs.appendFileSync(logFile, logLine);
    return { logged: true };
  } catch (error) {
    console.error(`❌ 记录写入失败: ${error.message}`);
    return { logged: false };
  }
}

// 检测敏感信息泄露
function detectSensitiveInfo(filePath) {
  try {
    const fullPath = path.resolve(WORKSPACE, filePath);
    
    // 检查文件是否存在
    if (!fs.existsSync(fullPath)) {
      return { detected: false };
    }
    
    // 只检查文本文件
    const ext = path.extname(filePath);
    const textExtensions = ['.md', '.txt', '.js', '.json', '.py', '.sh', '.yml', '.yaml'];
    
    if (!textExtensions.includes(ext)) {
      return { detected: false, reason: 'not_text_file' };
    }
    
    const content = fs.readFileSync(fullPath, 'utf-8');
    const detections = [];
    
    // 检查每个敏感模式
    for (const { name, pattern } of SENSITIVE_PATTERNS) {
      const matches = content.match(pattern);
      if (matches) {
        detections.push({
          type: name,
          count: matches.length,
          samples: matches.slice(0, 2) // 只显示前两个样本
        });
      }
    }
    
    if (detections.length > 0) {
      console.log(`\n🚨 敏感信息检测: ${filePath}`);
      console.log(`   检测到 ${detections.length} 种敏感信息类型:`);
      
      for (const detection of detections) {
        console.log(`   - ${detection.type}: ${detection.count} 处`);
        console.log(`     样本: ${detection.samples.map(s => s.slice(0, 20) + '...').join(', ')}`);
      }
      
      console.log('\n   ⚠️  建议: 立即移除敏感信息或使用环境变量！');
      
      return { detected: true, detections };
    }
    
    return { detected: false };
  } catch (error) {
    console.error(`❌ 检测敏感信息失败: ${error.message}`);
    return { detected: false, error: error.message };
  }
}

// 分析文件大小变化
function analyzeSizeChange(filePath, newSize) {
  try {
    const fullPath = path.resolve(WORKSPACE, filePath);
    
    if (!fs.existsSync(fullPath)) {
      return { changed: false, reason: 'file_not_exists' };
    }
    
    const stats = fs.statSync(fullPath);
    const actualSize = stats.size;
    
    // 计算大小变化
    const sizeDiff = actualSize - (newSize || 0);
    const percentChange = newSize > 0 ? ((sizeDiff / newSize) * 100).toFixed(1) : 0;
    
    if (Math.abs(sizeDiff) > 1024) { // 超过 1KB
      console.log(`\n📊 文件大小变化: ${filePath}`);
      console.log(`   之前: ${newSize || 0} 字节`);
      console.log(`   现在: ${actualSize} 字节`);
      console.log(`   变化: ${sizeDiff > 0 ? '+' : ''}${sizeDiff} 字节 (${percentChange}%)`);
      
      if (sizeDiff > 10240) { // 超过 10KB
        console.log('   ⚠️  文件显著增大，请检查是否包含不必要的内容');
      }
      
      return { changed: true, sizeDiff, percentChange };
    }
    
    return { changed: false };
  } catch (error) {
    return { changed: false, error: error.message };
  }
}

// 更新 Git 状态（如果在 Git 仓库中）
function updateGitStatus(filePath) {
  try {
    const fullPath = path.resolve(WORKSPACE, filePath);
    
    // 检查是否在 Git 仓库中
    try {
      execSync('git rev-parse --git-dir', { cwd: WORKSPACE, stdio: 'ignore' });
    } catch {
      return { inGit: false };
    }
    
    // 检查文件状态
    const status = execSync(`git status --porcelain "${fullPath}"`, { 
      cwd: WORKSPACE, 
      encoding: 'utf-8',
      stdio: 'pipe'
    }).trim();
    
    if (status) {
      console.log(`\n📝 Git 状态: ${filePath}`);
      console.log(`   状态: ${status}`);
      console.log('   ℹ️  文件已修改，记得提交更改');
      
      return { inGit: true, status };
    }
    
    return { inGit: true, status: 'unmodified' };
  } catch (error) {
    return { inGit: false, error: error.message };
  }
}

// 主函数
function main() {
  // 从环境变量或命令行参数获取文件信息
  const filePath = process.env.ECC_FILE_PATH || process.argv[2];
  const fileSize = parseInt(process.env.ECC_FILE_SIZE) || parseInt(process.argv[3]) || 0;
  const duration = parseInt(process.env.ECC_WRITE_DURATION) || parseInt(process.argv[4]) || 0;
  
  if (!filePath) {
    console.log('ℹ️  post-write Hook: 无文件路径信息（可能在测试环境）');
    return;
  }
  
  const timestamp = new Date().toISOString();
  console.log(`\n✅ Post Write: ${filePath}`);
  console.log('='.repeat(60));
  
  // 记录文件写入
  console.log('\n📝 记录文件写入...');
  const logged = logWrite(filePath, fileSize, duration);
  if (logged.logged) {
    console.log(`   ✅ 已记录 (${fileSize} 字节, ${duration}ms)`);
  }
  
  // 检测敏感信息
  console.log('\n🔒 敏感信息检测...');
  const sensitive = detectSensitiveInfo(filePath);
  if (sensitive.detected) {
    console.log(`   🚨 检测到敏感信息！`);
  } else {
    console.log('   ✅ 未检测到敏感信息');
  }
  
  // 分析文件大小变化
  console.log('\n📊 文件大小分析...');
  const sizeChange = analyzeSizeChange(filePath, fileSize);
  if (sizeChange.changed) {
    console.log(`   ℹ️  大小变化: ${sizeChange.percentChange}%`);
  } else {
    console.log('   ✅ 大小正常');
  }
  
  // 更新 Git 状态
  console.log('\n📝 Git 状态检查...');
  const git = updateGitStatus(filePath);
  if (git.inGit) {
    if (git.status !== 'unmodified') {
      console.log(`   ℹ️  Git 状态: ${git.status}`);
    } else {
      console.log('   ✅ 无变更');
    }
  } else {
    console.log('   ℹ️  不在 Git 仓库中');
  }
  
  console.log('\n' + '='.repeat(60));
  console.log('✅ Post Write Hook 完成\n');
}

// 运行
main();
