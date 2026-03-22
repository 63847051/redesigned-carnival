#!/usr/bin/env node
/**
 * 真实任务演示 - 并行执行系统
 * 
 * 演示场景：同时让小新、小蓝、设计专家并行工作
 */

const ParallelExecutionManager = require('./ParallelExecutionManager');

// 创建并行执行管理器
const manager = new ParallelExecutionManager({
  maxConcurrentAgents: 3,
  enableTaskPrioritization: true,
  enableResultAggregation: true,
  enableMonitoring: true,
  enableLogging: true
});

// 定义真实任务
const tasks = [
  {
    id: 'task-1',
    name: '编写 Python 爬虫脚本',
    type: 'tech',
    priority: 'high',
    agent: 'xiaoxin',
    model: 'glmcode/glm-4.5-air',
    description: '编写一个爬取新闻网站的 Python 脚本',
    estimatedTime: 5
  },
  {
    id: 'task-2',
    name: '更新工作日志',
    type: 'log',
    priority: 'medium',
    agent: 'xiaolan',
    model: 'glmcode/glm-4.5-air',
    description: '记录今天的工作内容到飞书日志',
    estimatedTime: 3
  },
  {
    id: 'task-3',
    name: '分析设计图纸',
    type: 'design',
    priority: 'medium',
    agent: 'designer',
    model: 'glmcode/glm-4.6',
    description: '分析 3F 平面图的设计问题',
    estimatedTime: 4
  }
];

console.log('🚀 大领导系统 v5.23 - 并行执行演示');
console.log('='.repeat(60));
console.log('');
console.log('📋 任务列表：');
console.log('');

tasks.forEach((task, index) => {
  console.log(`${index + 1}. [${task.priority.toUpperCase()}] ${task.name}`);
  console.log(`   专家: ${task.agent} | 模型: ${task.model} | 预计: ${task.estimatedTime}分钟`);
  console.log(`   描述: ${task.description}`);
  console.log('');
});

console.log('⏱️  串行执行需要: 5 + 3 + 4 = 12 分钟');
console.log('⚡ 并行执行预计: 5 分钟（最长的任务）');
console.log('🎯 效率提升: 140%');
console.log('');
console.log('🔄 开始并行执行...');
console.log('');

// 模拟并行执行
async function demonstrateParallelExecution() {
  const startTime = Date.now();

  // 模拟任务执行
  const results = await Promise.all(tasks.map(async (task) => {
    const taskStart = Date.now();
    
    // 模拟执行时间（毫秒）
    await new Promise(resolve => setTimeout(resolve, task.estimatedTime * 100));
    
    const taskEnd = Date.now();
    const actualTime = ((taskEnd - taskStart) / 1000).toFixed(1);
    
    return {
      id: task.id,
      name: task.name,
      agent: task.agent,
      status: 'completed',
      actualTime: `${actualTime}s`,
      result: `✅ ${task.name} 已完成`
    };
  }));

  const endTime = Date.now();
  const totalTime = ((endTime - startTime) / 1000).toFixed(1);

  console.log('');
  console.log('✅ 所有任务完成！');
  console.log('');
  console.log('📊 执行结果：');
  console.log('');

  results.forEach((result, index) => {
    console.log(`${index + 1}. ${result.result}`);
    console.log(`   专家: ${result.agent} | 实际用时: ${result.actualTime}`);
  });

  console.log('');
  console.log('⏱️  总用时:', totalTime, '秒');
  console.log('🎯 效率提升:', ((12 / parseFloat(totalTime)) * 100).toFixed(0), '%');
  console.log('');
  console.log('🎉 并行执行演示完成！');
}

// 执行演示
demonstrateParallelExecution().catch(console.error);
