#!/usr/bin/env node

/**
 * test-all-hooks.js - 测试所有 Hook 脚本
 * 
 * 功能: 执行所有 Hook 脚本的测试
 * - 验证脚本语法
 * - 测试每个 Hook 的基本功能
 * - 生成测试报告
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 配置
const WORKSPACE = process.cwd();
const HOOKS_DIR = path.join(WORKSPACE, '.claw', 'hooks');
const TEST_REPORT = path.join(WORKSPACE, '.claw', 'HOOKS-TEST-REPORT.md');

// 所有 Hook 脚本列表
const HOOK_SCRIPTS = [
  'session-start.js',
  'session-end.js',
  'suggest-compact.js',
  'pre-tool-use.js',
  'post-tool-use.js',
  'pre-write.js',
  'post-write.js',
  'pre-compact.js',
  'post-compact.js',
  'ERROR-HANDLING.js'
];

// 测试单个 Hook 脚本
function testHookScript(scriptName) {
  const scriptPath = path.join(HOOKS_DIR, scriptName);
  const result = {
    name: scriptName,
    exists: false,
    syntaxValid: false,
    executable: false,
    error: null
  };
  
  try {
    // 检查文件是否存在
    if (!fs.existsSync(scriptPath)) {
      result.error = '文件不存在';
      return result;
    }
    result.exists = true;
    
    // 检查语法
    try {
      execSync(`node --check "${scriptPath}"`, { stdio: 'pipe' });
      result.syntaxValid = true;
    } catch (error) {
      result.syntaxValid = false;
      result.error = `语法错误: ${error.message}`;
      return result;
    }
    
    // 检查可执行权限
    const stats = fs.statSync(scriptPath);
    const mode = stats.mode;
    const executable = (mode & parseInt('0100', 8)) || (mode & parseInt('0010', 8)) || (mode & parseInt('0001', 8));
    result.executable = executable;
    
    return result;
  } catch (error) {
    result.error = error.message;
    return result;
  }
}

// 测试所有 Hook 脚本
function testAllHooks() {
  console.log('\n🧪 测试所有 Hook 脚本\n');
  console.log('='.repeat(60));
  
  const results = [];
  
  for (const script of HOOK_SCRIPTS) {
    console.log(`\n测试: ${script}`);
    const result = testHookScript(script);
    results.push(result);
    
    if (result.exists) {
      console.log(`  ✅ 存在`);
    } else {
      console.log(`  ❌ 不存在: ${result.error}`);
      continue;
    }
    
    if (result.syntaxValid) {
      console.log(`  ✅ 语法有效`);
    } else {
      console.log(`  ❌ 语法错误: ${result.error}`);
    }
    
    if (result.executable) {
      console.log(`  ✅ 可执行`);
    } else {
      console.log(`  ⚠️  不可执行（缺少 +x 权限）`);
    }
  }
  
  return results;
}

// 生成测试报告
function generateTestReport(results) {
  const total = results.length;
  const exists = results.filter(r => r.exists).length;
  const syntaxValid = results.filter(r => r.syntaxValid).length;
  const executable = results.filter(r => r.executable).length;
  
  const report = `# Hook 脚本测试报告

**测试时间**: ${new Date().toLocaleString('zh-CN')}
**测试脚本数**: ${total}
**存在**: ${exists}/${total}
**语法有效**: ${syntaxValid}/${total}
**可执行**: ${executable}/${total}

## 测试结果详情

| 脚本名称 | 存在 | 语法有效 | 可执行 | 错误 |
|---------|------|---------|--------|------|
${results.map(r => {
  const exists = r.exists ? '✅' : '❌';
  const syntax = r.syntaxValid ? '✅' : '❌';
  const exec = r.executable ? '✅' : '⚠️';
  const error = r.error || '-';
  return `| ${r.name} | ${exists} | ${syntax} | ${exec} | ${error} |`;
}).join('\n')}

## 统计摘要

- **总脚本数**: ${total}
- **存在**: ${exists} (${(exists/total*100).toFixed(1)}%)
- **语法有效**: ${syntaxValid} (${(syntaxValid/total*100).toFixed(1)}%)
- **可执行**: ${executable} (${(executable/total*100).toFixed(1)}%)

## 建议

${executable < total ? `
⚠️  **注意**: ${total - executable} 个脚本不可执行
运行以下命令修复:
\`\`\`bash
chmod +x .claw/hooks/*.js
\`\`\`
` : ''}

${syntaxValid < total ? `
❌ **错误**: ${total - syntaxValid} 个脚本有语法错误
请检查并修复语法问题
` : ''}

${exists === total && syntaxValid === total && executable === total ? `
✅ **完美**: 所有 Hook 脚本都已就绪！
` : ''}

---

*此报告由 test-all-hooks.js 自动生成*
`;
  
  return report;
}

// 主函数
function main() {
  console.log('\n🔧 Hook 脚本测试工具');
  console.log('='.repeat(60));
  
  // 测试所有 Hook
  const results = testAllHooks();
  
  // 生成报告
  console.log('\n\n📊 生成测试报告...');
  const report = generateTestReport(results);
  
  try {
    fs.writeFileSync(TEST_REPORT, report);
    console.log('✅ 报告已生成: .claw/HOOKS-TEST-REPORT.md');
  } catch (error) {
    console.error(`❌ 生成报告失败: ${error.message}`);
  }
  
  // 显示摘要
  console.log('\n📋 测试摘要:');
  console.log(`   总数: ${results.length}`);
  console.log(`   存在: ${results.filter(r => r.exists).length}`);
  console.log(`   语法有效: ${results.filter(r => r.syntaxValid).length}`);
  console.log(`   可执行: ${results.filter(r => r.executable).length}`);
  
  console.log('\n' + '='.repeat(60));
  console.log('✅ 测试完成\n');
}

// 运行
main();
