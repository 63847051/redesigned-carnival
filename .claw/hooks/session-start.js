#!/usr/bin/env node

/**
 * session-start.js - 会话开始 Hook
 * 
 * 功能: 在会话开始时加载上下文
 * - 加载 MEMORY.md
 * - 加载 SESSION-STATE.md
 * - 加载今日记忆文件
 * - 显示系统状态
 */

const fs = require('fs');
const path = require('path');

// 配置
const WORKSPACE = process.cwd();
const MEMORY_FILE = path.join(WORKSPACE, 'MEMORY.md');
const SESSION_STATE_FILE = path.join(WORKSPACE, 'SESSION-STATE.md');
const MEMORY_DIR = path.join(WORKSPACE, 'memory');

// 获取今日记忆文件
function getTodayMemoryFile() {
  const today = new Date().toISOString().split('T')[0];
  return path.join(MEMORY_DIR, `${today}.md`);
}

// 加载文件内容
function loadFile(filePath) {
  try {
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf-8');
      return {
        exists: true,
        size: content.length,
        lines: content.split('\n').length
      };
    }
    return { exists: false, size: 0, lines: 0 };
  } catch (error) {
    return { exists: false, error: error.message };
  }
}

// 主函数
function main() {
  const timestamp = new Date().toISOString();
  console.log(`\n🚀 Session Start: ${timestamp}`);
  console.log('='.repeat(60));
  
  // 加载 MEMORY.md
  const memory = loadFile(MEMORY_FILE);
  console.log('\n📚 MEMORY.md:');
  if (memory.exists) {
    console.log(`   ✅ 已加载 (${memory.lines} 行, ${(memory.size / 1024).toFixed(1)} KB)`);
  } else {
    console.log('   ⚠️  文件不存在');
  }
  
  // 加载 SESSION-STATE.md
  const sessionState = loadFile(SESSION_STATE_FILE);
  console.log('\n📋 SESSION-STATE.md:');
  if (sessionState.exists) {
    console.log(`   ✅ 已加载 (${sessionState.lines} 行, ${(sessionState.size / 1024).toFixed(1)} KB)`);
  } else {
    console.log('   ⚠️  文件不存在');
  }
  
  // 加载今日记忆
  const todayMemory = getTodayMemoryFile();
  const today = loadFile(todayMemory);
  console.log('\n📝 今日记忆:');
  if (today.exists) {
    console.log(`   ✅ 已加载 (${today.lines} 行, ${(today.size / 1024).toFixed(1)} KB)`);
  } else {
    console.log('   ℹ️  将创建新文件');
  }
  
  // 系统状态
  console.log('\n🖥️  系统状态:');
  console.log(`   工作目录: ${WORKSPACE}`);
  console.log(`   时间: ${new Date().toLocaleString('zh-CN')}`);
  
  console.log('\n' + '='.repeat(60));
  console.log('✅ Session Start Hook 完成\n');
}

// 运行
main();
