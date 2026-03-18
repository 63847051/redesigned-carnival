#!/usr/bin/env node

/**
 * post-tool-use.js - 工具使用后 Hook
 * 
 * 功能: 在工具调用后执行分析和记录
 * - 记录工具执行结果
 * - 分析性能
 * - 检测错误模式
 * - 更新学习数据（PAI 学习系统）
 */

const fs = require('fs');
const path = require('path');

// 配置
const WORKSPACE = process.cwd();
const HOOKS_LOG_DIR = path.join(WORKSPACE, '.claw', '.learnings', 'hooks');
const POST_TOOL_LOG = path.join(HOOKS_LOG_DIR, 'post-tool-YYYYMMDD.log');
const PAI_LEARNING_DIR = path.join(WORKSPACE, '.pai-learning', 'data');

// 记录工具执行结果
function logToolResult(toolName, result, error) {
  try {
    const timestamp = new Date().toISOString();
    const logDate = new Date().toISOString().split('T')[0].replace(/-/g, '');
    const logFile = POST_TOOL_LOG.replace('YYYYMMDD', logDate);
    
    // 确保 hooks 目录存在
    if (!fs.existsSync(HOOKS_LOG_DIR)) {
      fs.mkdirSync(HOOKS_LOG_DIR, { recursive: true });
    }
    
    const success = !error;
    const logLine = `${timestamp} | ${toolName} | success=${success} | error=${error || 'none'}\n`;
    
    fs.appendFileSync(logFile, logLine);
    return { success, logged: true };
  } catch (logError) {
    console.error(`❌ 记录工具结果失败: ${logError.message}`);
    return { success: false, logged: false };
  }
}

// 分析工具性能
function analyzePerformance(toolName, duration) {
  const performanceThresholds = {
    exec: 5000,      // 5 秒
    web_search: 3000, // 3 秒
    feishu_bitable_list_records: 2000, // 2 秒
    read: 1000       // 1 秒
  };
  
  const threshold = performanceThresholds[toolName] || 3000;
  
  if (duration > threshold) {
    console.log(`\n⚠️  性能警告: ${toolName}`);
    console.log(`   执行时间: ${duration}ms`);
    console.log(`   阈值: ${threshold}ms`);
    console.log('   建议: 考虑优化或使用缓存');
    return { slow: true, duration };
  }
  
  return { slow: false, duration };
}

// 检测错误模式
function detectErrorPatterns(toolName, error) {
  const commonErrors = {
    'ENOENT': '文件不存在',
    'EACCES': '权限不足',
    'ETIMEDOUT': '连接超时',
    '429': 'API 限流',
    '500': '服务器错误',
    '401': '认证失败',
    '403': '权限被拒绝'
  };
  
  if (!error) {
    return { detected: false };
  }
  
  for (const [code, description] of Object.entries(commonErrors)) {
    if (error.includes(code)) {
      console.log(`\n🔍 错误模式检测: ${toolName}`);
      console.log(`   错误代码: ${code}`);
      console.log(`   描述: ${description}`);
      
      // 提供解决建议
      const suggestions = {
        'ENOENT': '检查文件路径是否正确',
        'EACCES': '检查文件权限',
        'ETIMEDOUT': '检查网络连接或增加超时时间',
        '429': '等待后重试或降低请求频率',
        '500': '联系服务提供商或稍后重试',
        '401': '检查 API 密钥是否有效',
        '403': '检查权限配置'
      };
      
      if (suggestions[code]) {
        console.log(`   建议: ${suggestions[code]}`);
      }
      
      return { detected: true, code, description };
    }
  }
  
  return { detected: false };
}

// 更新 PAI 学习数据
function updatePAILearning(toolName, success, duration) {
  try {
    // 确保 PAI 目录存在
    if (!fs.existsSync(PAI_LEARNING_DIR)) {
      fs.mkdirSync(PAI_LEARNING_DIR, { recursive: true });
    }
    
    const today = new Date().toISOString().split('T')[0];
    const learningFile = path.join(PAI_LEARNING_DIR, `learning-signals-${today}.json`);
    
    let signals = [];
    if (fs.existsSync(learningFile)) {
      signals = JSON.parse(fs.readFileSync(learningFile, 'utf-8'));
    }
    
    // 添加学习信号
    signals.push({
      timestamp: new Date().toISOString(),
      type: 'tool_use',
      tool: toolName,
      success,
      duration,
      context: 'post-tool-use-hook'
    });
    
    fs.writeFileSync(learningFile, JSON.stringify(signals, null, 2));
    return { updated: true };
  } catch (error) {
    console.error(`❌ 更新 PAI 学习失败: ${error.message}`);
    return { updated: false };
  }
}

// 主函数
function main() {
  // 从环境变量或命令行参数获取工具信息
  const toolName = process.env.ECC_TOOL_NAME || process.argv[2];
  const toolSuccess = process.env.ECC_TOOL_SUCCESS === 'true' || process.argv[3] === 'true';
  const toolError = process.env.ECC_TOOL_ERROR || process.argv[4];
  const toolDuration = parseInt(process.env.ECC_TOOL_DURATION) || parseInt(process.argv[5]) || 0;
  
  if (!toolName) {
    console.log('ℹ️  post-tool-use Hook: 无工具信息（可能在测试环境）');
    return;
  }
  
  const timestamp = new Date().toISOString();
  console.log(`\n✅ Post Tool Use: ${toolName}`);
  console.log('='.repeat(60));
  
  // 记录工具执行结果
  console.log('\n📝 记录执行结果...');
  const result = logToolResult(toolName, toolSuccess, toolError);
  if (result.logged) {
    console.log(`   ✅ 已记录 (success=${toolSuccess})`);
  }
  
  // 分析性能
  if (toolDuration > 0) {
    console.log('\n⏱️  性能分析...');
    const perf = analyzePerformance(toolName, toolDuration);
    if (perf.slow) {
      console.log(`   ⚠️  执行较慢: ${perf.duration}ms`);
    } else {
      console.log(`   ✅ 性能正常: ${perf.duration}ms`);
    }
  }
  
  // 检测错误模式
  if (!toolSuccess && toolError) {
    console.log('\n🔍 错误模式检测...');
    const errorPattern = detectErrorPatterns(toolName, toolError);
    if (errorPattern.detected) {
      console.log(`   ✅ 已检测: ${errorPattern.code}`);
    }
  }
  
  // 更新 PAI 学习
  console.log('\n🧠 更新 PAI 学习...');
  const pai = updatePAILearning(toolName, toolSuccess, toolDuration);
  if (pai.updated) {
    console.log('   ✅ 已更新学习数据');
  }
  
  console.log('\n' + '='.repeat(60));
  console.log('✅ Post Tool Use Hook 完成\n');
}

// 运行
main();
