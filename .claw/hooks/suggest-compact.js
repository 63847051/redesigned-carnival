#!/usr/bin/env node

/**
 * suggest-compact.js - 战略压缩建议 Hook
 * 
 * 功能: 在逻辑断点建议压缩
 * - 检查当前上下文使用情况
 * - 评估是否需要压缩
 * - 提供压缩建议
 */

const fs = require('fs');
const path = require('path');

// 配置
const WORKSPACE = process.cwd();
const MEMORY_FILE = path.join(WORKSPACE, 'MEMORY.md');
const SESSION_STATE_FILE = path.join(WORKSPACE, 'SESSION-STATE.md');

// 检查上下文大小
function checkContextSize() {
  let totalSize = 0;
  
  // 检查 MEMORY.md
  if (fs.existsSync(MEMORY_FILE)) {
    const stats = fs.statSync(MEMORY_FILE);
    totalSize += stats.size;
  }
  
  // 检查 SESSION-STATE.md
  if (fs.existsSync(SESSION_STATE_FILE)) {
    const stats = fs.statSync(SESSION_STATE_FILE);
    totalSize += stats.size;
  }
  
  return totalSize;
}

// 评估是否需要压缩
function shouldCompact(contextSize) {
  // 上下文大小超过 50KB 时建议压缩
  return contextSize > 50 * 1024;
}

// 提供压缩建议
function suggestCompact(contextSize) {
  const sizeKB = (contextSize / 1024).toFixed(1);
  
  console.log(`\n💡 上下文大小: ${sizeKB} KB`);
  
  if (shouldCompact(contextSize)) {
    console.log('⚠️  建议: 考虑压缩上下文');
    console.log('\n合适的压缩时机:');
    console.log('  - 研究完成后，开始实施前');
    console.log('  - 完成一个里程碑后');
    console.log('  - 调试完成后');
    console.log('  - 失败方法尝试后');
    
    console.log('\n不建议压缩的时候:');
    console.log('  - 实施过程中（会丢失变量名）');
    console.log('  - 调试过程中（会丢失状态）');
    
    return true;
  } else {
    console.log('✅ 上下文大小合适，无需压缩');
    return false;
  }
}

// 主函数
function main() {
  const timestamp = new Date().toISOString();
  console.log(`\n🔍 压缩检查: ${timestamp}`);
  console.log('='.repeat(50));
  
  // 检查上下文大小
  const contextSize = checkContextSize();
  
  // 评估并提供建议
  suggestCompact(contextSize);
  
  console.log('\n' + '='.repeat(50));
  console.log('✅ 压缩建议 Hook 完成\n');
}

// 运行
main();
