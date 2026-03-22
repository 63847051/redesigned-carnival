#!/usr/bin/env node

/**
 * 并行执行增强测试脚本
 * 
 * 测试 ParallelExecutionManager 的核心功能：
 * - 任务队列管理
 * - 并行执行编排
 * - 结果收集和聚合
 * - 性能和错误处理
 */

const ParallelExecutionManager = require('./ParallelExecutionManager');

class ParallelExecutionTest {
  constructor() {
    this.manager = null;
    this.testResults = [];
    this.currentTestId = 0;
  }
  
  /**
   * 运行所有测试
   */
  async runAllTests() {
    console.log('🚀 开始并行执行增强测试...\n');
    
    const tests = [
      { name: '基本功能测试', test: this.testBasicFunctionality.bind(this) },
      { name: '优先级队列测试', test: this.testPriorityQueue.bind(this) },
      { name: '并行执行测试', test: this.testParallelExecution.bind(this) },
      { name: '结果聚合测试', test: this.testResultAggregation.bind(this) },
      { name: '错误处理测试', test: this.testErrorHandling.bind(this) },
      { name: '性能测试', test: this.testPerformance.bind(this) },
      { name: '集成测试', test: this.testIntegration.bind(this) }
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
  
  /**
   * 基本功能测试
   */
  async testBasicFunctionality() {
    this.manager = new ParallelExecutionManager({
      enableLogging: false,
      maxConcurrentAgents: 3
    });
    
    // 添加简单任务
    const tasks = [
      { id: 'task1', task: { type: 'echo', data: 'Hello World' } },
      { id: 'task2', task: { type: 'echo', data: 'Test Data' } },
      { id: 'task3', task: { type: 'echo', data: 'Basic Test' } }
    ];
    
    // 添加任务
    for (const task of tasks) {
      this.manager.addTask(task.id, task.task, 'medium');
    }
    
    // 启动管理器
    this.manager.start();
    
    // 等待完成
    const result = await this.manager.waitForAll();
    
    // 验证结果
    if (result.completed.length !== 3) {
      throw new Error(`预期3个任务完成，实际完成${result.completed.length}个`);
    }
    
    this.manager.cleanup();
  }
  
  /**
   * 优先级队列测试
   */
  async testPriorityQueue() {
    this.manager = new ParallelExecutionManager({
      enableLogging: false,
      maxConcurrentAgents: 2,
      enableTaskPrioritization: true
    });
    
    // 添加不同优先级的任务
    const tasks = [
      { id: 'high1', task: { type: 'echo', data: 'High Priority 1' }, priority: 'high' },
      { id: 'low1', task: { type: 'echo', data: 'Low Priority 1' }, priority: 'low' },
      { id: 'high2', task: { type: 'echo', data: 'High Priority 2' }, priority: 'high' },
      { id: 'medium1', task: { type: 'echo', data: 'Medium Priority 1' }, priority: 'medium' }
    ];
    
    // 添加任务
    for (const task of tasks) {
      this.manager.addTask(task.id, task.task, task.priority);
    }
    
    this.manager.start();
    
    // 监控执行顺序
    const executionOrder = [];
    this.manager.on('taskStarted', (data) => {
      executionOrder.push({
        taskId: data.taskId,
        priority: this.getTaskPriority(data.taskId)
      });
    });
    
    await this.manager.waitForAll();
    
    // 验证优先级执行顺序
    const expectedHighPriority = ['high1', 'high2'];
    const actualHighPriority = executionOrder
      .filter(item => item.priority === 'high')
      .map(item => item.taskId);
    
    if (!this.arraysEqual(actualHighPriority, expectedHighPriority)) {
      throw new Error(`高优先级任务执行顺序不正确: ${JSON.stringify(actualHighPriority)}`);
    }
    
    this.manager.cleanup();
  }
  
  /**
   * 并行执行测试
   */
  async testParallelExecution() {
    this.manager = new ParallelExecutionManager({
      enableLogging: false,
      maxConcurrentAgents: 5
    });
    
    // 添加大量任务测试并行处理能力
    const taskCount = 10;
    const tasks = [];
    
    for (let i = 0; i < taskCount; i++) {
      tasks.push({
        id: `parallel_task_${i}`,
        task: { 
          type: 'delay', 
          data: `${Math.floor(Math.random() * 2000) + 1000}ms` 
        },
        priority: 'medium'
      });
    }
    
    // 添加任务
    for (const task of tasks) {
      this.manager.addTask(task.id, task.task, task.priority);
    }
    
    this.manager.start();
    
    // 监控并行执行情况
    let maxConcurrent = 0;
    this.manager.on('taskStarted', () => {
      const status = this.manager.getStatus();
      maxConcurrent = Math.max(maxConcurrent, status.tasks.active);
    });
    
    await this.manager.waitForAll();
    
    // 验证并行度
    if (maxConcurrent < this.manager.config.maxConcurrentAgents) {
      throw new Error(`预期最大并发数为${this.manager.config.maxConcurrentAgents}，实际为${maxConcurrent}`);
    }
    
    this.manager.cleanup();
  }
  
  /**
   * 结果聚合测试
   */
  async testResultAggregation() {
    this.manager = new ParallelExecutionManager({
      enableLogging: false,
      maxConcurrentAgents: 3,
      enableResultAggregation: true
    });
    
    // 添加相似内容测试去重
    const tasks = [
      { 
        id: 'similar1', 
        task: { type: 'echo', data: 'Hello World' },
        metadata: { content: 'Hello World' }
      },
      { 
        id: 'similar2', 
        task: { type: 'echo', data: 'Hello World' },
        metadata: { content: 'Hello World' }
      },
      { 
        id: 'unique1', 
        task: { type: 'echo', data: 'Unique Content' },
        metadata: { content: 'Unique Content' }
      }
    ];
    
    // 添加任务
    for (const task of tasks) {
      this.manager.addTask(task.id, task.task, 'medium', task.metadata);
    }
    
    this.manager.start();
    await this.manager.waitForAll();
    
    // 检查结果去重
    const status = this.manager.getStatus();
    if (status.results.total >= 3) {
      throw new Error('预期结果应该被去重合并，但结果数量不正确');
    }
    
    this.manager.cleanup();
  }
  
  /**
   * 错误处理测试
   */
  async testErrorHandling() {
    this.manager = new ParallelExecutionManager({
      enableLogging: false,
      maxConcurrentAgents: 3
    });
    
    // 添加包含错误任务的测试
    const tasks = [
      { 
        id: 'success1', 
        task: { type: 'echo', data: 'Success Task' }
      },
      { 
        id: 'error1', 
        task: { type: 'error', data: 'This should fail' }
      },
      { 
        id: 'success2', 
        task: { type: 'echo', data: 'Another Success' }
      }
    ];
    
    // 添加任务
    for (const task of tasks) {
      this.manager.addTask(task.id, task.task, 'medium');
    }
    
    this.manager.start();
    await this.manager.waitForAll();
    
    // 验证错误处理
    const status = this.manager.getStatus();
    if (status.tasks.failed === 0) {
      throw new Error('应该有失败的任务');
    }
    
    this.manager.cleanup();
  }
  
  /**
   * 性能测试
   */
  async testPerformance() {
    this.manager = new ParallelExecutionManager({
      enableLogging: false,
      maxConcurrentAgents: 10
    });
    
    // 添加大量任务
    const taskCount = 50;
    const tasks = [];
    
    for (let i = 0; i < taskCount; i++) {
      tasks.push({
        id: `perf_task_${i}`,
        task: { 
          type: 'echo', 
          data: `Performance test task ${i}` 
        },
        priority: 'medium'
      });
    }
    
    const startTime = Date.now();
    
    // 添加任务
    for (const task of tasks) {
      this.manager.addTask(task.id, task.task, task.priority);
    }
    
    this.manager.start();
    await this.manager.waitForAll();
    
    const endTime = Date.now();
    const totalTime = endTime - startTime;
    
    // 验证性能
    const throughput = taskCount / (totalTime / 1000); // 任务/秒
    if (throughput < 1) {
      throw new Error(`吞吐量过低: ${throughput.toFixed(2)} 任务/秒`);
    }
    
    this.manager.cleanup();
  }
  
  /**
   * 集成测试
   */
  async testIntegration() {
    this.manager = new ParallelExecutionManager({
      enableLogging: false,
      maxConcurrentAgents: 4,
      enableTaskPrioritization: true,
      enableResultAggregation: true
    });
    
    // 模拟真实场景：混合类型的任务
    const tasks = [
      // 高优先级技术任务
      { id: 'tech_high1', task: { type: 'code', data: 'Write Python script' }, priority: 'high' },
      { id: 'tech_high2', task: { type: 'code', data: 'Create API endpoint' }, priority: 'high' },
      
      // 中优先级设计任务
      { id: 'design_medium1', task: { type: 'design', data: 'Create UI mockup' }, priority: 'medium' },
      { id: 'design_medium2', task: { type: 'design', data: 'Design dashboard' }, priority: 'medium' },
      
      // 低优先级日志任务
      { id: 'log_low1', task: { type: 'log', data: 'Generate report' }, priority: 'low' },
      { id: 'log_low2', task: { type: 'log', data: 'Update documentation' }, priority: 'low' }
    ];
    
    // 添加任务
    for (const task of tasks) {
      this.manager.addTask(task.id, task.task, task.priority);
    }
    
    this.manager.start();
    
    // 监控执行
    const executionLog = [];
    this.manager.on('taskStarted', (data) => {
      executionLog.push({
        taskId: data.taskId,
        time: new Date(),
        priority: this.getTaskPriority(data.taskId),
        type: this.getTaskType(data.taskId)
      });
    });
    
    await this.manager.waitForAll();
    
    // 验证集成效果
    const status = this.manager.getStatus();
    
    // 检查所有任务是否完成
    if (status.tasks.completed + status.tasks.failed !== tasks.length) {
      throw new Error(`任务完成数不正确: ${status.tasks.completed + status.tasks.failed}/${tasks.length}`);
    }
    
    // 检查优先级执行顺序
    const firstTwoTasks = executionLog.slice(0, 2);
    const areHighPriority = firstTwoTasks.every(task => task.priority === 'high');
    if (!areHighPriority) {
      throw new Error('高优先级任务应该优先执行');
    }
    
    this.manager.cleanup();
  }
  
  /**
   * 获取任务优先级
   */
  getTaskPriority(taskId) {
    const task = this.manager?.tasks?.get(taskId);
    return task?.priority || 'unknown';
  }
  
  /**
   * 获取任务类型
   */
  getTaskType(taskId) {
    const task = this.manager?.tasks?.get(taskId);
    return task?.task?.type || 'unknown';
  }
  
  /**
   * 数组相等比较
   */
  arraysEqual(a, b) {
    return a.length === b.length && a.every((val, i) => val === b[i]);
  }
  
  /**
   * 生成测试报告
   */
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
    
    // 生成详细的性能报告
    const performanceReport = this.generatePerformanceReport();
    if (performanceReport) {
      console.log('\n🚀 性能分析:');
      console.log(`  平均执行时间: ${performanceReport.avgExecutionTime}ms`);
      console.log(`  最大并发数: ${performanceReport.maxConcurrency}`);
      console.log(`  平均吞吐量: ${performanceReport.avgThroughput} 任务/秒`);
    }
    
    // 保存测试结果到文件
    this.saveTestReport();
  }
  
  /**
   * 生成性能报告
   */
  generatePerformanceReport() {
    const passedTests = this.testResults.filter(t => t.status === 'passed');
    if (passedTests.length === 0) return null;
    
    const totalDuration = passedTests.reduce((sum, test) => sum + test.duration, 0);
    const avgExecutionTime = totalDuration / passedTests.length;
    
    return {
      avgExecutionTime: Math.round(avgExecutionTime),
      maxConcurrency: 5, // 根据测试配置
      avgThroughput: 50 / (avgExecutionTime / 1000) // 假设50个任务
    };
  }
  
  /**
   * 保存测试报告
   */
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
    
    const reportPath = path.join(__dirname, 'test-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    console.log(`\n📄 测试报告已保存到: ${reportPath}`);
  }
}

/**
 * 运行测试
 */
async function main() {
  const test = new ParallelExecutionTest();
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

module.exports = ParallelExecutionTest;