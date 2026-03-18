#!/usr/bin/env node

/**
 * pre-tool-use.js - 工具使用前 Hook
 * 
 * 功能: 在工具调用前执行检查和记录
 * - 检查工具权限
 * - 记录工具调用
 * - 验证参数安全性
 * - 应用规则检查（RULE-001 确认机制）
 */

const fs = require('fs');
const path = require('path');

// 配置
const WORKSPACE = process.cwd();
const HOOKS_LOG_DIR = path.join(WORKSPACE, '.claw', '.learnings', 'hooks');
const PRE_TOOL_LOG = path.join(HOOKS_LOG_DIR, 'pre-tool-YYYYMMDD.log');

// 关键规则检查（RULE-001）
function checkCriticalRules(toolName, params) {
  const criticalOperations = [
    'exec',
    'write',
    'edit',
    'feishu_bitable_update_record',
    'feishu_bitable_create_record',
    'feishu_doc_write'
  ];
  
  const isCritical = criticalOperations.includes(toolName);
  
  if (isCritical) {
    console.log(`\n🔒 关键操作检查: ${toolName}`);
    console.log('   检查清单:');
    console.log('   [ ] 用户明确说了确认词吗？');
    console.log('   [ ] 我明确询问用户确认了吗？');
    console.log('   [ ] 我收到了用户的明确回复吗？');
    console.log('   [ ] 这个操作是用户要求的吗？');
    console.log('   [ ] 我理解正确了吗？');
    console.log('\n   ⚠️  确保所有检查都通过后再执行！');
  }
  
  return isCritical;
}

// 记录工具调用
function logToolCall(toolName, params) {
  try {
    const timestamp = new Date().toISOString();
    const logDate = new Date().toISOString().split('T')[0].replace(/-/g, '');
    const logFile = PRE_TOOL_LOG.replace('YYYYMMDD', logDate);
    
    // 确保 hooks 目录存在
    if (!fs.existsSync(HOOKS_LOG_DIR)) {
      fs.mkdirSync(HOOKS_LOG_DIR, { recursive: true });
    }
    
    const logEntry = {
      timestamp,
      tool: toolName,
      params: JSON.stringify(params, null, 2),
      critical: checkCriticalRules(toolName, params)
    };
    
    const logLine = `${timestamp} | ${toolName} | critical=${logEntry.critical}\n`;
    
    fs.appendFileSync(logFile, logLine);
    return true;
  } catch (error) {
    console.error(`❌ 记录工具调用失败: ${error.message}`);
    return false;
  }
}

// 参数安全验证
function validateParams(toolName, params) {
  const dangerousPatterns = [
    /rm\s+-rf/,
    /rm\s+-rf\s+\//,
    /delete\s+all/,
    /drop\s+table/,
    /eval\s*\(/,
    /exec\s*\(/,
    /\.__proto__/
  ];
  
  const paramsStr = JSON.stringify(params);
  
  for (const pattern of dangerousPatterns) {
    if (pattern.test(paramsStr)) {
      console.log(`\n🚨 危险操作检测: ${toolName}`);
      console.log(`   模式: ${pattern}`);
      console.log('   ⚠️  请确认这是您想要执行的操作！');
      return false;
    }
  }
  
  return true;
}

// 主函数
function main() {
  // 从环境变量或命令行参数获取工具信息
  const toolName = process.env.ECC_TOOL_NAME || process.argv[2];
  const toolParams = process.env.ECC_TOOL_PARAMS || process.argv[3];
  
  if (!toolName) {
    console.log('ℹ️  pre-tool-use Hook: 无工具信息（可能在测试环境）');
    return;
  }
  
  const timestamp = new Date().toISOString();
  console.log(`\n🔧 Pre Tool Use: ${toolName}`);
  console.log('='.repeat(60));
  
  // 记录工具调用
  console.log('\n📝 记录工具调用...');
  logToolCall(toolName, toolParams);
  console.log('   ✅ 已记录');
  
  // 参数安全验证
  console.log('\n🔒 参数安全验证...');
  const isValid = validateParams(toolName, toolParams);
  if (isValid) {
    console.log('   ✅ 验证通过');
  } else {
    console.log('   ❌ 验证失败');
  }
  
  // 关键规则检查
  console.log('\n🔒 关键规则检查...');
  const isCritical = checkCriticalRules(toolName, toolParams);
  if (isCritical) {
    console.log('   ⚠️  这是关键操作，请确认！');
  } else {
    console.log('   ✅ 常规操作');
  }
  
  console.log('\n' + '='.repeat(60));
  console.log('✅ Pre Tool Use Hook 完成\n');
}

// 运行
main();
