#!/usr/bin/env node

/**
 * 单元测试 - 测试核心组件功能
 */

const ParallelExecutionManager = require('./ParallelExecutionManager');
const PriorityTaskQueue = require('./PriorityTaskQueue');
const ResultCollector = require('./ResultCollector');
const ParallelExecutionOrchestrator = require('./ParallelExecutionOrchestrator');

class UnitTest {
  constructor() {
    this.testResults = [];
    this.currentTestId = 0;
  }
  
  async runAllTests() {
    console.log('🚀 开始单元测试...\n');
    
    const tests = [
      { name: 'PriorityTaskQueue 测试', test: this.testPriorityTaskQueue.bind(this) },
      { name: 'ResultCollector 测试', test: this.testResultCollector.bind(this) },
      { name: 'ParallelExecutionOrchestrator 测试', test: this.testOrchestrator.bind(this) },
      { name: 'ParallelExecutionManager 基础测试', test: this.testManagerBasics.bind(this) }
    ];
    
    for (const test of tests) {
      console.log(`\n📋 运行测试: ${test.name}`);
      console.log('='.repeat(test.name.length + 10));
      
      try {
        const startTime = Date.now();
        await test.test();
        const duration = Date.now() - startTime;
        
        console.log(`✅ ${test.name} 通过 (${duration}ms)`);
        this.testResults.push({
          id: ++this.currentTestId,
          name: test.name,
          status: 'passed',
          duration,
          timestamp: new Date()
        });
      } catch (error) {
        console.log(`❌ ${test.name} 失败: ${error.message}`);
        this.testResults.push({
          id: ++this.currentTestId,
          name: test.name,
          status: 'failed',
          error: error.message,
          timestamp: new Date()
        });
      }
    }
    
    this.generateTestReport();
  }
  
  async testPriorityTaskQueue() {
    const queue = new PriorityTaskQueue({ enableLogging: false });
    
    // 添加任务
    queue.enqueue('task1', { type: 'echo', data: 'High Priority' }, 'high');
    queue.enqueue('task2', { type: 'echo', data: 'Low Priority' }, 'low');
    queue.enqueue('task3', { type: 'echo', data: 'Medium Priority' }, 'medium');
    
    // 验证队列状态
    const status = queue.getStatus();
    if (status.queueSizes.high !== 1 || status.queueSizes.medium !== 1 || status.queueSizes.low !== 1) {
      throw new Error('队列状态不正确');
    }
    
    // 测试优先级排序
    let task1 = queue.dequeue();
    let task2 = queue.dequeue();
    let task3 = queue.dequeue();
    
    if (task1.priority !== 'high' || task2.priority !== 'medium' || task3.priority !== 'low') {
      throw new Error('优先级排序不正确');
    }
    
    // 测试优先级更新
    queue.enqueue('task4', { type: 'echo', data: 'Original Medium' }, 'medium');
    queue.updateTaskPriority('task4', 'high');
    
    const updatedTask = queue.dequeue();
    if (updatedTask.priority !== 'high') {
      throw new Error('优先级更新不正确');
    }
  }
  
  async testResultCollector() {
    const collector = new ResultCollector({ enableLogging: false });
    
    // 添加结果
    const result1 = {
      content: 'Test Result 1',
      type: 'code',
      score: 0.9
    };
    
    const result2 = {
      content: 'Test Result 2',
      type: 'design',
      score: 0.8
    };
    
    const result3 = {
      content: 'Test Result 1', // 相同内容用于测试去重
      type: 'code',
      score: 0.7
    };
    
    collector.addResult('task1', result1, 'agent1', { priority: 'high' });
    collector.addResult('task2', result2, 'agent2', { priority: 'medium' });
    collector.addResult('task3', result3, 'agent3', { priority: 'low' });
    
    // 验证结果收集
    const allResults = collector.getAllResults();
    if (allResults.length !== 3) {
      throw new Error('结果收集不正确');
    }
    
    // 测试结果去重
    const deduplicatedResults = collector.getAllResults();
    // 应该有一个结果被去重
    const highQualityResults = collector.getHighQualityResults(0.8);
    if (highQualityResults.length < 1) {
      throw new Error('高质量结果筛选不正确');
    }
    
    // 测试报告生成
    const report = collector.generateReport();
    if (!report.summary || !report.qualityMetrics) {
      throw new Error('报告生成不正确');
    }
  }
  
  async testOrchestrator() {
    const orchestrator = new ParallelExecutionOrchestrator({ 
      maxConcurrentAgents: 2,
      enableLogging: false 
    });
    
    // 测试状态获取
    const status = orchestrator.getStatus();
    if (typeof status.activeAgents !== 'number') {
      throw new Error('编排器状态获取不正确');
    }
    
    // 测试任务添加（虽然不会实际执行，但可以验证逻辑）
    orchestrator.addTask('test_task', { type: 'echo', data: 'Test' }, 'medium');
    
    // 验证任务被添加到队列
    const taskCount = orchestrator.taskQueue.getStatus().queueSizes.total;
    if (taskCount !== 1) {
      throw new Error('任务添加不正确');
    }
    
    // 等待处理完成
    await orchestrator.waitForAll();
    
    // 验证结果收集
    const resultStatus = orchestrator.resultCollector.getStatus();
    if (resultStatus.totalResults !== 1) {
      throw new Error('结果收集不正确');
    }
  }
  
  async testManagerBasics() {
    const manager = new ParallelExecutionManager({ 
      enableLogging: false,
      maxConcurrentAgents: 2
    });
    
    // 测试任务添加
    manager.addTask('manager_task1', { type: 'echo', data: 'Test 1' }, 'high');
    manager.addTask('manager_task2', { type: 'echo', data: 'Test 2' }, 'medium');
    
    // 测试状态获取
    const status = manager.getStatus();
    if (status.tasks.total !== 2) {
      throw new Error('管理器状态获取不正确');
    }
    
    // 测试任务状态查询
    const taskStatus = manager.getTaskStatus('manager_task1');
    if (taskStatus.status !== 'queued') {
      throw new Error('任务状态查询不正确');
    }
    
    // 启动管理器
    manager.start();
    
    // 等待任务完成（这里使用超时）
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // 验证完成状态
    const finalStatus = manager.getStatus();
    if (finalStatus.tasks.completed !== 2) {
      throw new Error('任务完成不正确');
    }
    
    // 测试报告生成
    const report = manager.generateReport();
    if (!report.executiveSummary || !report.taskDistribution) {
      throw new Error('报告生成不正确');
    }
    
    manager.cleanup();
  }
  
  generateTestReport() {
    console.log('\n📊 测试报告');
    console.log('='.repeat(20));
    
    const passed = this.testResults.filter(t => t.status === 'passed').length;
    const failed = this.testResults.filter(t => t.status === 'failed').length;
    const total = this.testResults.length;
    
    console.log(`✅ 通过: ${passed}/${total}`);
    console.log(`❌ 失败: ${failed}/${total}`);
    console.log(`📈 成功率: ${((passed / total) * 100).toFixed(1)}%`);
    
    if (failed > 0) {
      console.log('\n❌ 失败的测试:');
      this.testResults
        .filter(t => t.status === 'failed')
        .forEach(test => {
          console.log(`  - ${test.name}: ${test.error}`);
        });
    }
    
    // 保存测试结果
    this.saveTestReport();
  }
  
  saveTestReport() {
    const report = {
      testResults: this.testResults,
      summary: {
        total: this.testResults.length,
        passed: this.testResults.filter(t => t.status === 'passed').length,
        failed: this.testResults.filter(t => t.status === 'failed').length,
        successRate: (this.testResults.filter(t => t.status === 'passed').length / this.testResults.length) * 100
      },
      timestamp: new Date()
    };
    
    const fs = require('fs');
    const path = require('path');
    
    const reportPath = path.join(__dirname, 'unit-test-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    console.log(`\n📄 测试报告已保存到: ${reportPath}`);
  }
}

// 运行测试
async function main() {
  const test = new UnitTest();
  await test.runAllTests();
  
  process.exit(test.testResults.filter(t => t.status === 'failed').length > 0 ? 1 : 0);
}

// 如果直接运行此脚本
if (require.main === module) {
  main().catch(error => {
    console.error('测试运行失败:', error);
    process.exit(1);
  });
}

module.exports = UnitTest;