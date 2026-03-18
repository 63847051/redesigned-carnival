#!/usr/bin/env node

/**
 * post-compact.js - 压缩后 Hook
 * 
 * 功能: 在 working-buffer 压缩后执行清理和记录
 * - 记录压缩操作
 * - 验证压缩结果
 * - 更新 SESSION-STATE.md
 * - 生成压缩报告
 */

const fs = require('fs');
const path = require('path');

// 配置
const WORKSPACE = process.cwd();
const WORKING_BUFFER = path.join(WORKSPACE, 'working-buffer.md');
const SESSION_STATE = path.join(WORKSPACE, 'SESSION-STATE.md');
const MEMORY_DIR = path.join(WORKSPACE, 'memory');
const HOOKS_LOG_DIR = path.join(WORKSPACE, '.claw', '.learnings', 'hooks');
const COMPACT_LOG = path.join(HOOKS_LOG_DIR, 'compact-YYYYMMDD.log');

// 记录压缩操作
function logCompactOperation(entriesCompacted, sizeBefore, sizeAfter) {
  try {
    const timestamp = new Date().toISOString();
    const logDate = new Date().toISOString().split('T')[0].replace(/-/g, '');
    const logFile = COMPACT_LOG.replace('YYYYMMDD', logDate);
    
    // 确保 hooks 目录存在
    if (!fs.existsSync(HOOKS_LOG_DIR)) {
      fs.mkdirSync(HOOKS_LOG_DIR, { recursive: true });
    }
    
    const sizeReduced = sizeBefore - sizeAfter;
    const percentReduced = sizeBefore > 0 ? ((sizeReduced / sizeBefore) * 100).toFixed(1) : 0;
    
    const logLine = `${timestamp} | compacted=${entriesCompacted} | before=${sizeBefore} | after=${sizeAfter} | reduced=${sizeReduced} (${percentReduced}%)\n`;
    
    fs.appendFileSync(logFile, logLine);
    return { logged: true, sizeReduced, percentReduced };
  } catch (error) {
    console.error(`❌ 记录压缩操作失败: ${error.message}`);
    return { logged: false };
  }
}

// 验证压缩结果
function verifyCompactResult() {
  try {
    // 检查 working-buffer
    let bufferStats = { exists: false, size: 0 };
    if (fs.existsSync(WORKING_BUFFER)) {
      bufferStats = {
        exists: true,
        size: fs.statSync(WORKING_BUFFER).size,
        lines: fs.readFileSync(WORKING_BUFFER, 'utf-8').split('\n').length
      };
    }
    
    // 检查今日记忆文件
    const today = new Date().toISOString().split('T')[0];
    const todayMemory = path.join(MEMORY_DIR, `${today}.md`);
    
    let memoryStats = { exists: false, size: 0 };
    if (fs.existsSync(todayMemory)) {
      memoryStats = {
        exists: true,
        size: fs.statSync(todayMemory).size,
        lines: fs.readFileSync(todayMemory, 'utf-8').split('\n').length
      };
    }
    
    console.log(`\n📊 压缩结果验证:`);
    console.log(`   working-buffer.md:`);
    if (bufferStats.exists) {
      console.log(`     存在: ✅ (${bufferStats.lines} 行, ${(bufferStats.size / 1024).toFixed(1)} KB)`);
    } else {
      console.log(`     存在: ❌ (已清空)`);
    }
    
    console.log(`   今日记忆 (${today}.md):`);
    if (memoryStats.exists) {
      console.log(`     存在: ✅ (${memoryStats.lines} 行, ${(memoryStats.size / 1024).toFixed(1)} KB)`);
    } else {
      console.log(`     存在: ❌`);
    }
    
    return {
      buffer: bufferStats,
      memory: memoryStats,
      valid: !bufferStats.exists || bufferStats.size < 10240 // < 10KB 视为有效
    };
  } catch (error) {
    console.error(`❌ 验证压缩结果失败: ${error.message}`);
    return { valid: false, error: error.message };
  }
}

// 更新 SESSION-STATE.md
function updateSessionState() {
  try {
    const timestamp = new Date().toISOString();
    const state = `# Session State

**最后更新**: ${timestamp}
**状态**: 活跃

## 当前任务
Phase 2: Hook 系统扩展

## 进度
- ✅ Phase 1 完成
- 🔄 Phase 2 进行中
- ✅ 最近压缩: ${new Date().toLocaleString('zh-CN')}

## 下一步
继续扩展 Hook 系统事件
`;
    
    fs.writeFileSync(SESSION_STATE, state);
    return { updated: true };
  } catch (error) {
    console.error(`❌ 更新 SESSION-STATE 失败: ${error.message}`);
    return { updated: false };
  }
}

// 生成压缩报告
function generateCompactReport(beforeSize, afterSize, entriesCompacted) {
  const sizeReduced = beforeSize - afterSize;
  const percentReduced = beforeSize > 0 ? ((sizeReduced / beforeSize) * 100).toFixed(1) : 0;
  
  const report = {
    timestamp: new Date().toISOString(),
    operation: 'compact',
    entries_compacted: entriesCompacted,
    size_before: beforeSize,
    size_after: afterSize,
    size_reduced: sizeReduced,
    percent_reduced: percentReduced,
    status: sizeReduced > 0 ? 'success' : 'no_change'
  };
  
  return report;
}

// 主函数
function main() {
  const timestamp = new Date().toISOString();
  console.log(`\n✅ Post Compact: ${timestamp}`);
  console.log('='.repeat(60));
  
  // 从环境变量获取压缩信息
  const entriesCompacted = parseInt(process.env.ECC_COMPACTED_ENTRIES) || parseInt(process.argv[2]) || 0;
  const sizeBefore = parseInt(process.env.ECC_SIZE_BEFORE) || parseInt(process.argv[3]) || 0;
  const sizeAfter = parseInt(process.env.ECC_SIZE_AFTER) || parseInt(process.argv[4]) || 0;
  
  // 记录压缩操作
  console.log('\n📝 记录压缩操作...');
  const logged = logCompactOperation(entriesCompacted, sizeBefore, sizeAfter);
  if (logged.logged) {
    console.log(`   ✅ 已记录`);
    console.log(`   条目数: ${entriesCompacted}`);
    console.log(`   大小变化: ${sizeBefore} → ${sizeAfter} (-${logged.sizeReduced} 字节, ${logged.percentReduced}%)`);
  }
  
  // 验证压缩结果
  console.log('\n🔍 验证压缩结果...');
  const verification = verifyCompactResult();
  if (verification.valid) {
    console.log('   ✅ 压缩有效');
  } else {
    console.log('   ⚠️  压缩可能未完全生效');
  }
  
  // 更新 SESSION-STATE
  console.log('\n📋 更新 SESSION-STATE.md...');
  const updated = updateSessionState();
  if (updated.updated) {
    console.log('   ✅ 已更新');
  }
  
  // 生成压缩报告
  console.log('\n📊 压缩报告:');
  const report = generateCompactReport(sizeBefore, sizeAfter, entriesCompacted);
  console.log(`   操作: ${report.operation}`);
  console.log(`   条目数: ${report.entries_compacted}`);
  console.log(`   大小: ${report.size_before} → ${report.size_after} 字节`);
  console.log(`   减少: ${report.size_reduced} 字节 (${report.percent_reduced}%)`);
  console.log(`   状态: ${report.status}`);
  
  // 压缩建议
  if (verification.buffer && verification.buffer.exists && verification.buffer.size > 10240) {
    console.log('\n💡 建议:');
    console.log('   working-buffer 仍然较大，考虑再次压缩');
  }
  
  console.log('\n' + '='.repeat(60));
  console.log('✅ Post Compact Hook 完成\n');
}

// 运行
main();
