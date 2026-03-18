#!/usr/bin/env node

/**
 * pre-write.js - 写入前 Hook
 * 
 * 功能: 在文件写入前执行检查
 * - 验证文件路径安全性
 * - 检查是否覆盖重要文件
 * - 创建自动备份
 * - 应用 RULE-001 确认机制
 */

const fs = require('fs');
const path = require('path');

// 配置
const WORKSPACE = process.cwd();
const BACKUP_DIR = path.join(WORKSPACE, '.claw', '.backups');

// 重要文件保护列表
const PROTECTED_FILES = [
  'MEMORY.md',
  'SESSION-STATE.md',
  'SOUL.md',
  'USER.md',
  'IDENTITY.md',
  'AGENTS.md',
  'HEARTBEAT.md',
  'TOOLS.md',
  'openclaw.json',
  'credentials/'
];

// 检查文件路径安全性
function checkPathSafety(filePath) {
  const dangerousPatterns = [
    /\.\./,           // 父目录遍历
    /^\/(?!home)/,    // 绝对路径（除 /home）
    /^~\//,           // home 目录（未展开）
    /\/etc\//,        // 系统配置
    /\/usr\//,        // 系统目录
    /\/var\//,        // 系统目录
    /\.ssh\//,        // SSH 密钥
    /credentials/     // 凭证目录
  ];
  
  for (const pattern of dangerousPatterns) {
    if (pattern.test(filePath)) {
      console.log(`\n🚨 路径安全警告: ${filePath}`);
      console.log(`   检测到危险模式: ${pattern}`);
      console.log('   ⚠️  这可能影响系统安全！');
      return { safe: false, reason: 'dangerous_pattern' };
    }
  }
  
  return { safe: true };
}

// 检查是否覆盖重要文件
function checkProtectedFile(filePath) {
  const fileName = path.basename(filePath);
  const fullPath = path.resolve(WORKSPACE, filePath);
  
  for (const protected of PROTECTED_FILES) {
    if (fullPath.includes(protected) || fileName === protected) {
      console.log(`\n🔒 重要文件保护: ${filePath}`);
      console.log(`   文件: ${protected}`);
      console.log('   ⚠️  这是受保护的重要文件！');
      console.log('   建议: 确认是否真的需要修改');
      return { protected: true, file: protected };
    }
  }
  
  return { protected: false };
}

// 创建自动备份
function createBackup(filePath) {
  try {
    const fullPath = path.resolve(WORKSPACE, filePath);
    
    // 检查文件是否存在
    if (!fs.existsSync(fullPath)) {
      return { backed: false, reason: 'file_not_exists' };
    }
    
    // 确保备份目录存在
    if (!fs.existsSync(BACKUP_DIR)) {
      fs.mkdirSync(BACKUP_DIR, { recursive: true });
    }
    
    // 创建备份文件名
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const fileName = path.basename(filePath);
    const backupName = `${fileName}.${timestamp}.bak`;
    const backupPath = path.join(BACKUP_DIR, backupName);
    
    // 复制文件
    fs.copyFileSync(fullPath, backupPath);
    
    console.log(`\n💾 自动备份: ${filePath}`);
    console.log(`   备份位置: ${backupPath}`);
    console.log(`   大小: ${fs.statSync(backupPath).size} 字节`);
    
    return { backed: true, backupPath };
  } catch (error) {
    console.error(`❌ 创建备份失败: ${error.message}`);
    return { backed: false, error: error.message };
  }
}

// RULE-001 确认检查
function checkConfirmation(filePath) {
  const importantExtensions = ['.md', '.json', '.js', '.sh', '.py'];
  const ext = path.extname(filePath);
  
  if (importantExtensions.includes(ext)) {
    console.log(`\n🔒 RULE-001 确认检查: ${filePath}`);
    console.log('   检查清单:');
    console.log('   [ ] 用户明确说了确认词吗？');
    console.log('   [ ] 我明确询问用户确认了吗？');
    console.log('   [ ] 我收到了用户的明确回复吗？');
    console.log('   [ ] 这个操作是用户要求的吗？');
    console.log('   [ ] 我理解正确了吗？');
    console.log('\n   ⚠️  确保所有检查都通过后再写入！');
    return { requiresConfirmation: true };
  }
  
  return { requiresConfirmation: false };
}

// 主函数
function main() {
  // 从环境变量或命令行参数获取文件信息
  const filePath = process.env.ECC_FILE_PATH || process.argv[2];
  const fileSize = process.env.ECC_FILE_SIZE || process.argv[3];
  
  if (!filePath) {
    console.log('ℹ️  pre-write Hook: 无文件路径信息（可能在测试环境）');
    return;
  }
  
  const timestamp = new Date().toISOString();
  console.log(`\n✏️  Pre Write: ${filePath}`);
  console.log('='.repeat(60));
  
  // 路径安全检查
  console.log('\n🔒 路径安全检查...');
  const safety = checkPathSafety(filePath);
  if (safety.safe) {
    console.log('   ✅ 路径安全');
  } else {
    console.log(`   ❌ 路径不安全: ${safety.reason}`);
    return;
  }
  
  // 重要文件检查
  console.log('\n🔒 重要文件保护检查...');
  const protected = checkProtectedFile(filePath);
  if (protected.protected) {
    console.log(`   ⚠️  受保护文件: ${protected.file}`);
  } else {
    console.log('   ✅ 非受保护文件');
  }
  
  // 创建备份
  console.log('\n💾 创建备份...');
  const backup = createBackup(filePath);
  if (backup.backed) {
    console.log('   ✅ 备份成功');
  } else if (backup.reason === 'file_not_exists') {
    console.log('   ℹ️  新文件，无需备份');
  } else {
    console.log(`   ❌ 备份失败: ${backup.error || 'unknown'}`);
  }
  
  // RULE-001 确认检查
  console.log('\n🔒 RULE-001 确认检查...');
  const confirmation = checkConfirmation(filePath);
  if (confirmation.requiresConfirmation) {
    console.log('   ⚠️  需要确认');
  } else {
    console.log('   ✅ 无需确认');
  }
  
  console.log('\n📊 文件信息:');
  console.log(`   路径: ${filePath}`);
  console.log(`   大小: ${fileSize || 'unknown'} 字节`);
  console.log(`   时间: ${new Date().toLocaleString('zh-CN')}`);
  
  console.log('\n' + '='.repeat(60));
  console.log('✅ Pre Write Hook 完成\n');
}

// 运行
main();
