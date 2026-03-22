#!/usr/bin/env node

/**
 * 并行执行系统演示
 * 
 * 展示 ParallelExecutionManager 的核心功能
 */

const ParallelExecutionManager = require('./ParallelExecutionManager');

class ParallelExecutionDemo {
  constructor() {
    this.manager = null;
  }
  
  async runDemo() {
    console.log('🚀 Multi-Agent 并行执行增强系统演示\n');
    
    try {
      // 1. 基础功能演示
      await this.demoBasicFunctionality();
      
      // 2. 优先级管理演示
      await this.demoPriorityManagement();
      
      // 3. 结果聚合演示
      await this.demoResultAggregation();
      
      // 4. 监控和报告演示
      await this.demoMonitoringAndReports();
      
      console.log('\n🎉 演示完成！');
      
    } catch (error) {
      console.error('❌ 演示失败:', error);
    }
  }
  
  async demoBasicFunctionality() {
    console.log('\n📋 1. 基础功能演示');
    console.log('='.repeat(25));
    
    this.manager = new ParallelExecutionManager({
      enableLogging: false,
      maxConcurrentAgents: 3,
      enableTaskPrioritization: true
    });
    
    // 添加一些示例任务
    const tasks = [
      { id: 'code_task', task: { type: 'code', data: '编写Python脚本' }, priority: 'high' },
      { id: 'design_task', task: { type: 'design', data: '设计用户界面' }, priority: 'medium' },
      { id: 'log_task', task: { type: 'log', data: '生成工作日志' }, priority: 'low' },
      { id: 'api_task', task: { type: 'api', data: '调用外部服务' }, priority: 'high' }
    ];
    
    // 添加任务
    for (const task of tasks) {
      this.manager.addTask(task.id, task.task, task.priority);
      console.log(`   ✓ 添加任务: ${task.id} (优先级: ${task.priority})`);
    }
    
    // 获取初始状态
    const status = this.manager.getStatus();
    console.log(`\n   当前状态:`);
    console.log(`   - 活跃任务: ${status.tasks.active}`);
    console.log(`   - 待处理任务: ${status.tasks.pending}`);
    console.log(`   - 已完成任务: ${status.tasks.completed}`);
    console.log(`   - 失败任务: ${status.tasks.failed}`);
    
    // 启动管理器
    console.log('\n   🚀 启动并行执行管理器...');
    this.manager.start();
    
    // 监听事件
    let completedCount = 0;
    this.manager.on('taskCompleted', (data) => {
      completedCount++;
      console.log(`   ✅ 任务完成: ${data.taskId} (Agent: ${data.agentId})`);
    });
    
    // 等待任务完成
    await this.waitForTasks(this.manager, tasks.length);
    
    console.log(`\n   📊 完成情况:`);
    console.log(`   - 总任务数: ${tasks.length}`);
    console.log(`   - 完成任务: ${status.tasks.completed}`);
    console.log(`   - 成功率: ${((status.tasks.completed / tasks.length) * 100).toFixed(1)}%`);
    
    this.manager.cleanup();
  }
  
  async demoPriorityManagement() {
    console.log('\n📋 2. 优先级管理演示');
    console.log('='.repeat(25));
    
    this.manager = new ParallelExecutionManager({
      enableLogging: false,
      maxConcurrentAgents: 2,
      enableTaskPrioritization: true
    });
    
    // 添加不同优先级的任务
    const tasks = [
      { id: 'urgent_bug', task: { type: 'bug', data: '修复紧急Bug' }, priority: 'high' },
      { id: 'feature_dev', task: { type: 'feature', data: '开发新功能' }, priority: 'medium' },
      { id: 'doc_update', task: { type: 'document', data: '更新文档' }, priority: 'low' },
      { id: 'critical_fix', task: { type: 'fix', data: '关键修复' }, priority: 'high' }
    ];
    
    // 添加任务
    for (const task of tasks) {
      this.manager.addTask(task.id, task.task, task.priority);
      console.log(`   ✓ 添加任务: ${task.id} (优先级: ${task.priority})`);
    }
    
    this.manager.start();
    
    // 监听执行顺序
    const executionOrder = [];
    this.manager.on('taskStarted', (data) => {
      executionOrder.push({
        taskId: data.taskId,
        timestamp: new Date().toISOString()
      });
    });
    
    await this.waitForTasks(this.manager, tasks.length);
    
    console.log(`\n   📈 执行顺序:`);
    executionOrder.forEach((item, index) => {
      console.log(`   ${index + 1}. ${item.taskId} (${item.timestamp})`);
    });
    
    // 验证优先级执行
    const highPriorityTasks = executionOrder.filter(item => 
      tasks.find(t => t.id === item.taskId)?.priority === 'high'
    );
    
    console.log(`\n   🎯 高优先级任务执行情况:`);
    console.log(`   - 高优先级任务数: ${highPriorityTasks.length}`);
    console.log(`   - 前2个任务中高优先级: ${executionOrder.slice(0, 2).filter(item => 
      tasks.find(t => t.id === item.taskId)?.priority === 'high'
    ).length}/2`);
    
    this.manager.cleanup();
  }
  
  async demoResultAggregation() {
    console.log('\n📋 3. 结果聚合演示');
    console.log('='.repeat(25));
    
    this.manager = new ParallelExecutionManager({
      enableLogging: false,
      maxConcurrentAgents: 3,
      enableResultAggregation: true
    });
    
    // 添加相似任务测试去重
    const tasks = [
      { 
        id: 'task1', 
        task: { type: 'report', data: '生成销售报告' },
        metadata: { content: '销售报告' }
      },
      { 
        id: 'task2', 
        task: { type: 'report', data: '生成销售报告' },
        metadata: { content: '销售报告' }
      },
      { 
        id: 'task3', 
        task: { type: 'report', data: '生成财务报告' },
        metadata: { content: '财务报告' }
      }
    ];
    
    // 添加任务
    for (const task of tasks) {
      this.manager.addTask(task.id, task.task, 'medium', task.metadata);
      console.log(`   ✓ 添加任务: ${task.id}`);
    }
    
    this.manager.start();
    await this.waitForTasks(this.manager, tasks.length);
    
    // 获取结果
    const results = this.manager.resultCollector.getAllResults();
    const report = this.manager.resultCollector.generateReport();
    
    console.log(`\n   📊 结果聚合统计:`);
    console.log(`   - 原始任务数: ${tasks.length}`);
    console.log(`   - 结果总数: ${results.length}`);
    console.log(`   - 高质量结果: ${this.manager.resultCollector.getHighQualityResults(0.8).length}`);
    console.log(`   - 去重率: ${((1 - results.length / tasks.length) * 100).toFixed(1)}%`);
    console.log(`   - 平均质量分数: ${(report.qualityMetrics.overallQuality?.score || 0).toFixed(2)}`);
    
    this.manager.cleanup();
  }
  
  async demoMonitoringAndReports() {
    console.log('\n📋 4. 监控和报告演示');
    console.log('='.repeat(25));
    
    this.manager = new ParallelExecutionManager({
      enableLogging: false,
      maxConcurrentAgents: 4,
      enableTaskPrioritization: true,
      enableResultAggregation: true
    });
    
    // 添加多种类型的任务
    const tasks = [
      { id: 'code1', task: { type: 'code', data: 'API开发' }, priority: 'high' },
      { id: 'design1', task: { type: 'design', data: 'UI设计' }, priority: 'medium' },
      { id: 'code2', task: { type: 'code', data: '数据处理' }, priority: 'high' },
      { id: 'log1', task: { type: 'log', data: '日志分析' }, priority: 'low' },
      { id: 'design2', task: { type: 'design', data: '原型设计' }, priority: 'medium' }
    ];
    
    // 添加任务并监控
    for (const task of tasks) {
      this.manager.addTask(task.id, task.task, task.priority);
    }
    
    this.manager.start();
    
    // 监控状态变化
    let statusUpdates = [];
    this.manager.on('statusUpdate', (status) => {
      statusUpdates.push({
        timestamp: status.timestamp,
        active: status.tasks.active,
        completed: status.tasks.completed,
        pending: status.tasks.pending,
        agentsUtilization: status.agents.utilization
      });
    });
    
    await this.waitForTasks(this.manager, tasks.length);
    
    // 生成详细报告
    const report = this.manager.generateReport();
    
    console.log(`\n   📊 监控数据:`);
    console.log(`   - 状态更新次数: ${statusUpdates.length}`);
    console.log(`   - 最终Agent利用率: ${(report.performanceMetrics.agentUtilization * 100).toFixed(1)}%`);
    console.log(`   - 平均执行时间: ${report.performanceMetrics.averageExecutionTime}ms`);
    console.log(`   - 吞吐量: ${report.performanceMetrics.throughput.toFixed(2)} 任务/秒`);
    
    console.log(`\n   📈 报告摘要:`);
    console.log(`   - 总任务数: ${report.executiveSummary.totalTasks}`);
    console.log(`   - 完成任务: ${report.executiveSummary.completed}`);
    console.log(`   - 失败任务: ${report.executiveSummary.failed}`);
    console.log(`   - 成功率: ${(report.executiveSummary.successRate * 100).toFixed(1)}%`);
    
    // 导出数据
    const exportedData = this.manager.exportData('json');
    console.log(`\n   📁 数据导出:`);
    console.log(`   - JSON格式: ${exportedData.length} 字符`);
    console.log(`   - 包含 ${JSON.parse(exportedData).tasks.length} 个任务`);
    
    this.manager.cleanup();
  }
  
  async waitForTasks(manager, expectedCount, timeout = 10000) {
    return new Promise((resolve, reject) => {
      const startTime = Date.now();
      
      const checkStatus = () => {
        const status = manager.getStatus();
        if (status.tasks.completed >= expectedCount || 
            status.tasks.failed >= expectedCount ||
            Date.now() - startTime > timeout) {
          resolve(status);
        } else {
          setTimeout(checkStatus, 500);
        }
      };
      
      checkStatus();
    });
  }
}

// 运行演示
async function main() {
  const demo = new ParallelExecutionDemo();
  await demo.runDemo();
}

// 如果直接运行此脚本
if (require.main === module) {
  main().catch(error => {
    console.error('演示运行失败:', error);
    process.exit(1);
  });
}

module.exports = ParallelExecutionDemo;