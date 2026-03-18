#!/usr/bin/env node

/**
 * ERROR-HANDLING.js - 错误处理 Hook
 * 
 * 功能: 捕获和处理系统错误
 * - 记录错误详情
 * - 分析错误原因
 * - 提供解决建议
 * - 更新错误学习库
 */

const fs = require('fs');
const path = require('path');

// 配置
const WORKSPACE = process.cwd();
const HOOKS_LOG_DIR = path.join(WORKSPACE, '.claw', '.learnings', 'hooks');
const ERROR_LOG = path.join(HOOKS_LOG_DIR, 'errors-YYYYMMDD.log');
const LEARNINGS_DIR = path.join(WORKSPACE, '.learnings', 'errors');

// 错误分类
const ERROR_CATEGORIES = {
  'ENOENT': { category: '文件操作', description: '文件或目录不存在' },
  'EACCES': { category: '权限', description: '权限不足' },
  'ETIMEDOUT': { category: '网络', description: '连接超时' },
  'ECONNREFUSED': { category: '网络', description: '连接被拒绝' },
  '429': { category: 'API', description: '请求过于频繁（限流）' },
  '500': { category: 'API', description: '服务器内部错误' },
  '401': { category: '认证', description: '认证失败' },
  '403': { category: '权限', description: '权限被拒绝' },
  '404': { category: 'HTTP', description: '资源未找到' },
  'TypeError': { category: '代码', description: '类型错误' },
  'ReferenceError': { category: '代码', description: '引用错误' },
  'SyntaxError': { category: '代码', description: '语法错误' }
};

// 解决建议库
const SOLUTIONS = {
  'ENOENT': [
    '检查文件路径是否正确',
    '确认文件是否存在',
    '检查文件名拼写'
  ],
  'EACCES': [
    '检查文件权限',
    '使用 chmod 修改权限',
    '确认是否有写权限'
  ],
  'ETIMEDOUT': [
    '检查网络连接',
    '增加超时时间',
    '检查防火墙设置'
  ],
  '429': [
    '等待后重试',
    '降低请求频率',
    '检查 API 限制'
  ],
  '500': [
    '联系服务提供商',
    '稍后重试',
    '检查服务状态页面'
  ],
  '401': [
    '检查 API 密钥',
    '确认认证信息',
    '重新生成密钥'
  ]
};

// 记录错误
function logError(errorType, errorMessage, stack, context) {
  try {
    const timestamp = new Date().toISOString();
    const logDate = new Date().toISOString().split('T')[0].replace(/-/g, '');
    const logFile = ERROR_LOG.replace('YYYYMMDD', logDate);
    
    // 确保 hooks 目录存在
    if (!fs.existsSync(HOOKS_LOG_DIR)) {
      fs.mkdirSync(HOOKS_LOG_DIR, { recursive: true });
    }
    
    const logEntry = {
      timestamp,
      type: errorType,
      message: errorMessage,
      stack: stack ? stack.split('\n').slice(0, 5).join('\n') : 'none',
      context
    };
    
    const logLine = `${timestamp} | ${errorType} | ${errorMessage.substring(0, 100)}\n`;
    
    fs.appendFileSync(logFile, logLine);
    return { logged: true };
  } catch (logError) {
    console.error(`❌ 记录错误失败: ${logError.message}`);
    return { logged: false };
  }
}

// 分析错误原因
function analyzeError(errorType, errorMessage) {
  // 从错误类型中提取关键信息
  const category = ERROR_CATEGORIES[errorType];
  
  if (category) {
    return {
      category: category.category,
      description: category.description,
      known: true
    };
  }
  
  // 尝试从错误消息中提取信息
  for (const [code, info] of Object.entries(ERROR_CATEGORIES)) {
    if (errorMessage.includes(code)) {
      return {
        category: info.category,
        description: info.description,
        known: true
      };
    }
  }
  
  // 未知错误类型
  return {
    category: '未知',
    description: '未能识别的错误类型',
    known: false
  };
}

// 提供解决建议
function provideSolutions(errorType, errorMessage) {
  const solutions = SOLUTIONS[errorType];
  
  if (solutions) {
    return {
      available: true,
      solutions
    };
  }
  
  // 尝试从错误消息中匹配
  for (const [code, sols] of Object.entries(SOLUTIONS)) {
    if (errorMessage.includes(code)) {
      return {
        available: true,
        solutions: sols
      };
    }
  }
  
  // 通用建议
  return {
    available: false,
    solutions: [
      '检查错误消息详情',
      '搜索相关文档',
      '联系技术支持'
    ]
  };
}

// 创建错误学习记录
function createErrorLearning(errorType, errorMessage, analysis) {
  try {
    // 确保 learnings/errors 目录存在
    if (!fs.existsSync(LEARNINGS_DIR)) {
      fs.mkdirSync(LEARNINGS_DIR, { recursive: true });
    }
    
    // 创建错误记录文件
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const errorFile = path.join(LEARNINGS_DIR, `error-${timestamp}.md`);
    
    const content = `# 错误记录

**时间**: ${new Date().toLocaleString('zh-CN')}
**类型**: ${errorType}
**分类**: ${analysis.category}

## 错误信息

\`\`\`
${errorMessage}
\`\`\`

## 分析

**分类**: ${analysis.category}
**描述**: ${analysis.description}
**是否已知**: ${analysis.known ? '是' : '否'}

## 解决方案

${provideSolutions(errorType, errorMessage).solutions.map(s => `- ${s}`).join('\n')}

## 预防措施

- [ ] 添加错误处理
- [ ] 增加输入验证
- [ ] 实施重试机制
- [ ] 改进错误提示

---

*此文件由 ERROR-HANDLING Hook 自动生成*
`;
    
    fs.writeFileSync(errorFile, content);
    return { created: true, file: errorFile };
  } catch (error) {
    console.error(`❌ 创建错误学习记录失败: ${error.message}`);
    return { created: false };
  }
}

// 主函数
function main() {
  // 从环境变量或命令行参数获取错误信息
  const errorType = process.env.ECC_ERROR_TYPE || process.argv[2] || 'Unknown';
  const errorMessage = process.env.ECC_ERROR_MESSAGE || process.argv[3] || 'No message';
  const errorStack = process.env.ECC_ERROR_STACK || process.argv[4] || '';
  const errorContext = process.env.ECC_ERROR_CONTEXT || process.argv[5] || 'general';
  
  const timestamp = new Date().toISOString();
  console.log(`\n🚨 Error Handling: ${errorType}`);
  console.log('='.repeat(60));
  
  // 记录错误
  console.log('\n📝 记录错误...');
  const logged = logError(errorType, errorMessage, errorStack, errorContext);
  if (logged.logged) {
    console.log('   ✅ 已记录');
  }
  
  // 分析错误
  console.log('\n🔍 分析错误...');
  const analysis = analyzeError(errorType, errorMessage);
  console.log(`   分类: ${analysis.category}`);
  console.log(`   描述: ${analysis.description}`);
  console.log(`   已知: ${analysis.known ? '是' : '否'}`);
  
  // 提供解决方案
  console.log('\n💡 解决建议:');
  const solutions = provideSolutions(errorType, errorMessage);
  if (solutions.available) {
    console.log('   ✅ 有已知解决方案:');
    for (const solution of solutions.solutions) {
      console.log(`   - ${solution}`);
    }
  } else {
    console.log('   ⚠️  无已知解决方案，使用通用建议:');
    for (const solution of solutions.solutions) {
      console.log(`   - ${solution}`);
    }
  }
  
  // 创建错误学习记录
  console.log('\n📚 创建错误学习记录...');
  const learning = createErrorLearning(errorType, errorMessage, analysis);
  if (learning.created) {
    console.log(`   ✅ 已创建: ${learning.file}`);
  }
  
  console.log('\n📊 错误摘要:');
  console.log(`   类型: ${errorType}`);
  console.log(`   消息: ${errorMessage.substring(0, 100)}${errorMessage.length > 100 ? '...' : ''}`);
  console.log(`   上下文: ${errorContext}`);
  console.log(`   时间: ${new Date().toLocaleString('zh-CN')}`);
  
  console.log('\n' + '='.repeat(60));
  console.log('✅ Error Handling Hook 完成\n');
}

// 运行
main();
