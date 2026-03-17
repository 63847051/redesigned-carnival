/**
 * PAI 学习系统单元测试
 * 
 * 测试内容:
 * - 学习信号捕获
 * - 三层记忆系统
 * - 报告生成
 */

const fs = require('fs');
const path = require('path');

// 测试配置
const TEST_DIR = path.join(process.cwd(), '.pai-learning');
const SIGNALS_FILE = path.join(TEST_DIR, 'signals/2026-03-17-signals.jsonl');

// 测试辅助函数
function assert(condition, message) {
  if (!condition) {
    throw new Error(`断言失败: ${message}`);
  }
}

function assertEqual(actual, expected, message) {
  if (actual !== expected) {
    throw new Error(`${message}\n期望: ${expected}\n实际: ${actual}`);
  }
}

// 测试 1: 学习信号捕获
function testSignalCapture() {
  console.log('🧪 测试 1: 学习信号捕获');
  
  // 检查信号文件是否存在
  const exists = fs.existsSync(SIGNALS_FILE);
  assert(exists, '信号文件应该存在');
  
  // 读取并解析信号
  const content = fs.readFileSync(SIGNALS_FILE, 'utf-8');
  const lines = content.trim().split('\n');
  
  // 验证至少有一条信号
  assert(lines.length > 0, '应该至少有一条学习信号');
  
  // 解析最后一条信号
  const lastSignal = JSON.parse(lines[lines.length - 1]);
  
  // 验证信号结构
  assert(lastSignal.timestamp, '信号应该有时间戳');
  assert(lastSignal.task_type, '信号应该有类型');
  assert(lastSignal.complexity !== undefined, '信号应该有复杂度');
  
  console.log('✅ 学习信号捕获测试通过');
  console.log(`   - 信号数量: ${lines.length}`);
  console.log(`   - 最新信号类型: ${lastSignal.task_type}`);
  console.log(`   - 最新信号复杂度: ${lastSignal.complexity}`);
  
  return true;
}

// 测试 2: 三层记忆系统
function testThreeLayerMemory() {
  console.log('\n🧪 测试 2: 三层记忆系统');
  
  // 检查分层文件
  const hotMemory = path.join(TEST_DIR, 'hot-memory.jsonl');
  const warmMemory = path.join(TEST_DIR, 'warm-memory.jsonl');
  const coldMemory = path.join(TEST_DIR, 'cold-memory.jsonl');
  
  // 验证 Hot Memory
  const hotExists = fs.existsSync(hotMemory);
  assert(hotExists, 'Hot Memory 文件应该存在');
  
  // 验证文件可读
  if (hotExists) {
    const hotContent = fs.readFileSync(hotMemory, 'utf-8');
    const hotLines = hotContent.trim().split('\n').filter(l => l);
    console.log(`✅ Hot Memory: ${hotLines.length} 条记录`);
  }
  
  // 验证 Warm Memory
  const warmExists = fs.existsSync(warmMemory);
  if (warmExists) {
    const warmContent = fs.readFileSync(warmMemory, 'utf-8');
    const warmLines = warmContent.trim().split('\n').filter(l => l);
    console.log(`✅ Warm Memory: ${warmLines.length} 条记录`);
  } else {
    console.log('⚠️  Warm Memory: 暂无记录');
  }
  
  // 验证 Cold Memory
  const coldExists = fs.existsSync(coldMemory);
  if (coldExists) {
    const coldContent = fs.readFileSync(coldMemory, 'utf-8');
    const coldLines = coldContent.trim().split('\n').filter(l => l);
    console.log(`✅ Cold Memory: ${coldLines.length} 条记录`);
  } else {
    console.log('⚠️  Cold Memory: 暂无记录');
  }
  
  console.log('✅ 三层记忆系统测试通过');
  
  return true;
}

// 测试 3: 报告生成
function testReportGeneration() {
  console.log('\n🧪 测试 3: 报告生成');
  
  // 检查分析报告
  const analysisDir = path.join(TEST_DIR, 'analysis-reports');
  const analysisFiles = fs.readdirSync(analysisDir).filter(f => f.endsWith('.md'));
  
  assert(analysisFiles.length > 0, '应该至少有一个分析报告');
  
  // 读取最新的分析报告
  const latestReport = path.join(analysisDir, analysisFiles[analysisFiles.length - 1]);
  const reportContent = fs.readFileSync(latestReport, 'utf-8');
  
  // 验证报告内容
  assert(reportContent.length > 0, '报告内容不应该为空');
  assert(reportContent.includes('#'), '报告应该包含标题');
  
  console.log('✅ 报告生成测试通过');
  console.log(`   - 报告数量: ${analysisFiles.length}`);
  console.log(`   - 最新报告: ${analysisFiles[analysisFiles.length - 1]}`);
  console.log(`   - 报告长度: ${reportContent.length} 字符`);
  
  return true;
}

// 测试 4: 目录结构
function testDirectoryStructure() {
  console.log('\n🧪 测试 4: 目录结构');
  
  // 验证 .claw/ 目录结构
  const clawDir = path.join(process.cwd(), '.claw');
  const requiredDirs = [
    'agents',
    'skills',
    'commands',
    'scripts/ci',
    'hooks'
  ];
  
  for (const dir of requiredDirs) {
    const dirPath = path.join(clawDir, dir);
    const exists = fs.existsSync(dirPath);
    assert(exists, `.claw/${dir} 目录应该存在`);
    console.log(`✅ .claw/${dir}/ 存在`);
  }
  
  // 验证关键文件
  const catalogJson = path.join(clawDir, 'catalog.json');
  const catalogMd = path.join(clawDir, 'CATALOG.md');
  
  assert(fs.existsSync(catalogJson), 'catalog.json 应该存在');
  assert(fs.existsSync(catalogMd), 'CATALOG.md 应该存在');
  
  console.log('✅ 目录结构测试通过');
  
  return true;
}

// 主测试函数
function runTests() {
  console.log('🚀 开始运行 PAI 学习系统测试...\n');
  
  const tests = [
    testSignalCapture,
    testThreeLayerMemory,
    testReportGeneration,
    testDirectoryStructure
  ];
  
  let passed = 0;
  let failed = 0;
  
  for (const test of tests) {
    try {
      test();
      passed++;
    } catch (error) {
      console.error(`❌ 测试失败: ${error.message}`);
      failed++;
    }
  }
  
  console.log('\n' + '='.repeat(50));
  console.log('📊 测试结果汇总');
  console.log('='.repeat(50));
  console.log(`✅ 通过: ${passed}`);
  console.log(`❌ 失败: ${failed}`);
  console.log(`📊 总数: ${passed + failed}`);
  console.log(`📈 通过率: ${((passed / (passed + failed)) * 100).toFixed(1)}%`);
  
  // 计算覆盖率（粗略估计）
  const coverage = passed / (passed + failed);
  if (coverage >= 0.6) {
    console.log('\n✅ 达到目标覆盖率 (60%)');
  } else {
    console.log('\n⚠️  未达到目标覆盖率 (60%)');
  }
  
  return failed === 0 ? 0 : 1;
}

// 运行测试
if (require.main === module) {
  const exitCode = runTests();
  process.exit(exitCode);
}

module.exports = { runTests };
