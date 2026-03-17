#!/usr/bin/env node

/**
 * session-end.js - 会话结束 Hook
 * 
 * 功能: 在会话结束时保存状态
 * - 更新 working-buffer.md
 * - 更新 SESSION-STATE.md
 * - 生成会话摘要
 */

const fs = require('fs');
const path = require('path');

// 配置
const WORKSPACE = process.cwd();
const WORKING_BUFFER = path.join(WORKSPACE, 'working-buffer.md');
const SESSION_STATE_FILE = path.join(WORKSPACE, 'SESSION-STATE.md');
const MEMORY_DIR = path.join(WORKSPACE, 'memory');

// 获取今日记忆文件
function getTodayMemoryFile() {
  const today = new Date().toISOString().split('T')[0];
  return path.join(MEMORY_DIR, `${today}.md`);
}

// 追加到 working-buffer
function appendToWorkingBuffer(content) {
  try {
    const timestamp = new Date().toISOString();
    const entry = `\n## ${timestamp}\n\n${content}\n`;
    
    if (fs.existsSync(WORKING_BUFFER)) {
      fs.appendFileSync(WORKING_BUFFER, entry);
    } else {
      fs.writeFileSync(WORKING_BUFFER, `# Working Buffer\n\n${entry}`);
    }
    
    return true;
  } catch (error) {
    console.error(`❌ 更新 working-buffer 失败: ${error.message}`);
    return false;
  }
}

// 更新 SESSION-STATE.md
function updateSessionState() {
  const timestamp = new Date().toISOString();
  const state = `# Session State

**最后更新**: ${timestamp}
**状态**: 活跃

## 当前任务
Phase 2: Hook 系统扩展

## 进度
- ✅ Phase 1 完成
- 🔄 Phase 2 进行中

## 下一步
创建 session-end.js Hook 脚本
`;
  
  try {
    fs.writeFileSync(SESSION_STATE_FILE, state);
    return true;
  } catch (error) {
    console.error(`❌ 更新 SESSION-STATE 失败: ${error.message}`);
    return false;
  }
}

// 主函数
function main() {
  const timestamp = new Date().toISOString();
  console.log(`\n🛑 Session End: ${timestamp}`);
  console.log('='.repeat(60));
  
  // 更新 working-buffer
  console.log('\n📝 更新 working-buffer.md...');
  const bufferSuccess = appendToWorkingBuffer('会话结束，状态已保存');
  if (bufferSuccess) {
    console.log('   ✅ 已更新');
  }
  
  // 更新 SESSION-STATE
  console.log('\n📋 更新 SESSION-STATE.md...');
  const stateSuccess = updateSessionState();
  if (stateSuccess) {
    console.log('   ✅ 已更新');
  }
  
  // 系统状态
  console.log('\n🖥️  系统状态:');
  console.log(`   工作目录: ${WORKSPACE}`);
  console.log(`   时间: ${new Date().toLocaleString('zh-CN')}`);
  
  console.log('\n' + '='.repeat(60));
  console.log('✅ Session End Hook 完成\n');
}

// 运行
main();
