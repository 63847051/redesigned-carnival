#!/usr/bin/env node

/**
 * pre-compact.js - 压缩前 Hook
 * 
 * 功能: 在 working-buffer 压缩前执行分析
 * - 分析 working-buffer 大小
 * - 提取关键信息
 * - 生成压缩建议
 * - 创建压缩备份
 */

const fs = require('fs');
const path = require('path');

// 配置
const WORKSPACE = process.cwd();
const WORKING_BUFFER = path.join(WORKSPACE, 'working-buffer.md');
const BACKUP_DIR = path.join(WORKSPACE, '.claw', '.backups');
const MEMORY_DIR = path.join(WORKSPACE, 'memory');

// 分析 working-buffer
function analyzeWorkingBuffer() {
  try {
    if (!fs.existsSync(WORKING_BUFFER)) {
      return { exists: false };
    }
    
    const content = fs.readFileSync(WORKING_BUFFER, 'utf-8');
    const stats = fs.statSync(WORKING_BUFFER);
    
    const lines = content.split('\n');
    const sections = content.split(/^##\s+/m).filter(s => s.trim());
    
    // 提取时间戳
    const timestamps = content.match(/\d{4}-\d{2}-\d{2}T[\d:\.]+Z/g) || [];
    
    // 提取任务类型
    const taskTypes = {
      用户提问: (content.match(/用户提问:/g) || []).length,
      工具调用: (content.match(/工具调用:/g) || []).length,
      系统更新: (content.match(/系统更新:/g) || []).length,
      错误记录: (content.match(/错误:/g) || []).length
    };
    
    return {
      exists: true,
      size: stats.size,
      lines: lines.length,
      sections: sections.length,
      entries: timestamps.length,
      taskTypes,
      oldestTimestamp: timestamps[0] || null,
      newestTimestamp: timestamps[timestamps.length - 1] || null
    };
  } catch (error) {
    return { exists: false, error: error.message };
  }
}

// 提取关键信息
function extractKeyInfo() {
  try {
    if (!fs.existsSync(WORKING_BUFFER)) {
      return { extracted: 0 };
    }
    
    const content = fs.readFileSync(WORKING_BUFFER, 'utf-8');
    
    // 提取关键模式
    const patterns = {
      重要决策: /(?:重要决策|决策|决定):?\s*([^\n]+)/gi,
      学习成果: /(?:学习|学到|掌握):?\s*([^\n]+)/gi,
      错误教训: /(?:错误|教训|失败):?\s*([^\n]+)/gi,
      待办事项: /(?:待办|TODO|任务):?\s*([^\n]+)/gi,
      用户反馈: /(?:用户说|用户反馈):?\s*([^\n]+)/gi
    };
    
    const extracted = {};
    
    for (const [name, pattern] of Object.entries(patterns)) {
      const matches = content.match(pattern) || [];
      extracted[name] = matches.length;
    }
    
    return extracted;
  } catch (error) {
    return { extracted: 0, error: error.message };
  }
}

// 生成压缩建议
function generateCompactSuggestions(analysis) {
  const suggestions = [];
  
  if (!analysis.exists) {
    return ['working-buffer 不存在，无需压缩'];
  }
  
  // 大小检查
  const sizeKB = analysis.size / 1024;
  if (sizeKB > 100) {
    suggestions.push(`🔴 文件较大 (${sizeKB.toFixed(1)} KB)，强烈建议压缩`);
  } else if (sizeKB > 50) {
    suggestions.push(`🟡 文件中等 (${sizeKB.toFixed(1)} KB)，建议压缩`);
  } else {
    suggestions.push(`🟢 文件较小 (${sizeKB.toFixed(1)} KB)，可以暂缓压缩`);
  }
  
  // 条目数量检查
  if (analysis.entries > 50) {
    suggestions.push(`📝 条目较多 (${analysis.entries})，建议压缩到今日记忆`);
  }
  
  // 任务类型分析
  const highPriorityTasks = analysis.taskTypes['用户提问'] + analysis.taskTypes['错误记录'];
  if (highPriorityTasks > 10) {
    suggestions.push(`⚠️  高优先级任务较多 (${highPriorityTasks})，优先处理这些`);
  }
  
  // 时间跨度
  if (analysis.oldestTimestamp && analysis.newestTimestamp) {
    const oldest = new Date(analysis.oldestTimestamp);
    const newest = new Date(analysis.newestTimestamp);
    const daysDiff = (newest - oldest) / (1000 * 60 * 60 * 24);
    
    if (daysDiff > 7) {
      suggestions.push(`⏰ 时间跨度 ${daysDiff.toFixed(1)} 天，建议按周分割`);
    }
  }
  
  return suggestions;
}

// 创建压缩备份
function createCompactBackup() {
  try {
    if (!fs.existsSync(WORKING_BUFFER)) {
      return { backed: false, reason: 'file_not_exists' };
    }
    
    // 确保备份目录存在
    if (!fs.existsSync(BACKUP_DIR)) {
      fs.mkdirSync(BACKUP_DIR, { recursive: true });
    }
    
    // 创建备份文件名
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupName = `working-buffer.${timestamp}.bak`;
    const backupPath = path.join(BACKUP_DIR, backupName);
    
    // 复制文件
    fs.copyFileSync(WORKING_BUFFER, backupPath);
    
    console.log(`\n💾 压缩备份: working-buffer.md`);
    console.log(`   备份位置: ${backupPath}`);
    console.log(`   大小: ${fs.statSync(backupPath).size} 字节`);
    
    return { backed: true, backupPath };
  } catch (error) {
    console.error(`❌ 创建备份失败: ${error.message}`);
    return { backed: false, error: error.message };
  }
}

// 主函数
function main() {
  const timestamp = new Date().toISOString();
  console.log(`\n🗜️  Pre Compact: ${timestamp}`);
  console.log('='.repeat(60));
  
  // 分析 working-buffer
  console.log('\n📊 分析 working-buffer.md...');
  const analysis = analyzeWorkingBuffer();
  
  if (analysis.exists) {
    console.log(`   ✅ 文件存在`);
    console.log(`   大小: ${(analysis.size / 1024).toFixed(1)} KB`);
    console.log(`   行数: ${analysis.lines}`);
    console.log(`   条目数: ${analysis.entries}`);
    
    if (analysis.oldestTimestamp && analysis.newestTimestamp) {
      const oldest = new Date(analysis.oldestTimestamp);
      const newest = new Date(analysis.newestTimestamp);
      const daysDiff = (newest - oldest) / (1000 * 60 * 60 * 24);
      console.log(`   时间跨度: ${daysDiff.toFixed(1)} 天`);
    }
    
    console.log('\n   任务类型统计:');
    for (const [type, count] of Object.entries(analysis.taskTypes)) {
      if (count > 0) {
        console.log(`   - ${type}: ${count}`);
      }
    }
  } else {
    console.log('   ⚠️  文件不存在');
    return;
  }
  
  // 提取关键信息
  console.log('\n🔍 提取关键信息...');
  const keyInfo = extractKeyInfo();
  let totalExtracted = 0;
  for (const [name, count] of Object.entries(keyInfo)) {
    if (count > 0) {
      console.log(`   - ${name}: ${count} 条`);
      totalExtracted += count;
    }
  }
  
  if (totalExtracted === 0) {
    console.log('   ℹ️  未检测到明显的关键信息模式');
  } else {
    console.log(`   ✅ 共提取 ${totalExtracted} 条关键信息`);
  }
  
  // 生成压缩建议
  console.log('\n💡 压缩建议:');
  const suggestions = generateCompactSuggestions(analysis);
  for (const suggestion of suggestions) {
    console.log(`   ${suggestion}`);
  }
  
  // 创建备份
  console.log('\n💾 创建压缩备份...');
  const backup = createCompactBackup();
  if (backup.backed) {
    console.log('   ✅ 备份成功');
  } else if (backup.reason === 'file_not_exists') {
    console.log('   ℹ️  文件不存在，无需备份');
  } else {
    console.log(`   ❌ 备份失败: ${backup.error || 'unknown'}`);
  }
  
  console.log('\n' + '='.repeat(60));
  console.log('✅ Pre Compact Hook 完成\n');
}

// 运行
main();
