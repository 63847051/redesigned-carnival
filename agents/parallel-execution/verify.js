#!/usr/bin/env node

/**
 * 并行执行系统功能验证
 * 
 * 验证核心组件的基本功能
 */

const PriorityTaskQueue = require('./PriorityTaskQueue');
const ResultCollector = require('./ResultCollector');
const ParallelExecutionManager = require('./ParallelExecutionManager');

class Verification {
  constructor() {
    this.results = [];
  }
  
  async runVerification() {
    console.log('🔍 并行执行系统功能验证\n');
    
    try {
      // 1. 验证任务队列
      await this.verifyTaskQueue();
      
      // 2. 验证结果收集器
      await this.verifyResultCollector();
      
      // 3. 验证管理器基础功能
      await this.verifyManagerBasics();
      
      console.log('\n✅ 所有验证通过！');
      
    } catch (error) {
      console.error('❌ 验证失败:', error);
      throw error;
    }
  }
  
  async verifyTaskQueue() {
    console.log('📋 1. 验证任务优先级队列');
    
    const queue = new PriorityTaskQueue({ enableLogging: false });
    
    // 测试添加任务
    const tasks = [
      { id: 'high1', task: { type: 'code' }, priority: 'high' },
      { id: 'medium1', task: { type: 'design' }, priority: 'medium' },
      { id: 'low1', task: { type: 'log' }, priority: 'low' }
    ];
    
    tasks.forEach(task => {
      const success = queue.enqueue(task.id, task.task, task.priority);
      if (!success) {
        throw new Error(`任务添加失败: ${task.id}`);
      }
    });
    
    // 验证队列状态
    const status = queue.getStatus();
    if (status.queueSizes.total !== 3) {
      throw new Error(`队列状态不正确，期望3个任务，实际${status.queueSizes.total}个`);
    }
    
    // 验证优先级排序
    const dequeuedTasks = [];
    for (let i = 0; i < 3; i++) {
      const task = queue.dequeue();
      if (task) {
        dequeuedTasks.push(task.priority);
      }
    }
    
    const expectedOrder = ['high', 'medium', 'low'];
    if (!dequeuedTasks.every((priority, index) => priority === expectedOrder[index])) {
      throw new Error(`优先级顺序不正确，期望${expectedOrder}，实际${dequeuedTasks}`);
    }
    
    console.log('   ✓ 任务队列功能正常');
  }
  
  async verifyResultCollector() {
    console.log('📋 2. 验证结果收集器');
    
    const collector = new ResultCollector({ 
      enableDeduplication: true,
      enableQualityAssessment: true,
      enableLogging: false 
    });
    
    // 添加测试结果
    const results = [
      { 
        id: 'result1',
        content: 'Code completed successfully',
        type: 'code',
        score: 0.9
      },
      { 
        id: 'result2',
        content: 'Design mockup created',
        type: 'design',
        score: 0.8
      },
      { 
        id: 'result3',
        content: 'Code completed successfully', // 重复内容
        type: 'code',
        score: 0.7
      }
    ];
    
    results.forEach(result => {
      const success = collector.addResult(result.id, result, 'test-agent');
      if (!success) {
        throw new Error(`结果添加失败: ${result.id}`);
      }
    });
    
    // 验证结果收集
    const allResults = collector.getAllResults();
    if (allResults.length !== 3) {
      throw new Error(`结果收集不正确，期望3个结果，实际${allResults.length}个`);
    }
    
    // 验证质量评估
    const highQuality = collector.getHighQualityResults(0.8);
    if (highQuality.length !== 2) {
      throw new Error(`高质量结果筛选不正确，期望2个，实际${highQuality.length}个`);
    }
    
    // 验证报告生成
    const report = collector.generateReport();
    if (!report.summary || !report.qualityMetrics) {
      throw new Error('报告生成不正确');
    }
    
    console.log('   ✓ 结果收集器功能正常');
  }
  
  async verifyManagerBasics() {
    console.log('📋 3. 验证管理器基础功能');
    
    // 创建管理器但不启动实际的并行执行
    const manager = new ParallelExecutionManager({ 
      enableLogging: false,
      enableMonitoring: false // 禁用监控避免错误
    });
    
    // 测试任务添加
    const task = { id: 'test-task', task: { type: 'echo', data: 'Test' }, priority: 'medium' };
    const addSuccess = manager.addTask(task.id, task.task, task.priority);
    
    if (!addSuccess) {
      throw new Error('任务添加失败');
    }
    
    // 验证任务状态
    const taskStatus = manager.getTaskStatus(task.id);
    if (taskStatus.status !== 'queued') {
      throw new Error(`任务状态不正确，期望queued，实际${taskStatus.status}`);
    }
    
    // 验证管理器状态
    const status = manager.getStatus();
    if (status.tasks.total !== 1) {
      throw new Error(`管理器状态不正确，期望1个任务，实际${status.tasks.total}个`);
    }
    
    // 测试取消任务
    const cancelSuccess = manager.cancelTask(task.id);
    if (!cancelSuccess) {
      throw new Error('任务取消失败');
    }
    
    // 验证取消后状态
    const finalStatus = manager.getStatus();
    if (finalStatus.tasks.total !== 0) {
      throw new Error(`任务取消后状态不正确，期望0个任务，实际${finalStatus.tasks.total}个`);
    }
    
    console.log('   ✓ 管理器基础功能正常');
  }
}

// 运行验证
async function main() {
  const verification = new Verification();
  await verification.runVerification();
  
  console.log('\n🎉 系统验证完成！所有核心组件功能正常。');
  
  // 保存验证结果
  const fs = require('fs');
  const report = {
    timestamp: new Date(),
    status: 'success',
    verifiedComponents: [
      'PriorityTaskQueue',
      'ResultCollector', 
      'ParallelExecutionManager'
    ],
    message: '所有核心组件验证通过，系统功能正常'
  };
  
  fs.writeFileSync('./verification-report.json', JSON.stringify(report, null, 2));
  console.log('📄 验证报告已保存到: verification-report.json');
}

// 如果直接运行此脚本
if (require.main === module) {
  main().catch(error => {
    console.error('验证运行失败:', error);
    process.exit(1);
  });
}

module.exports = Verification;