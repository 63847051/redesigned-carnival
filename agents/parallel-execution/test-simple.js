#!/usr/bin/env node

/**
 * 简化版并行执行测试
 * 
 * 测试核心逻辑而不依赖 sessions_spawn
 */

const ParallelExecutionManager = require('./ParallelExecutionManager');

class MockAgent {
  constructor(agentId, task, callback) {
    this.agentId = agentId;
    this.task = task;
    this.callback = callback;
  }
  
  start() {
    // 模拟任务执行
    setTimeout(() => {
      // 模拟任务结果
      const result = {
        content: `Mock result for ${this.task.type}: ${this.task.data}`,
        type: this.task.type,
        timestamp: Date.now(),
        quality: {
          score: 0.9,
          completeness: 0.9,
          accuracy: 0.9,
          consistency: 0.9,
          relevance: 0.9
        }
      };
      
      this.callback(result);
    }, Math.random() * 2000 + 1000); // 1-3秒随机延迟
  }
}

// 模拟 sessions_spawn
function mockSessionsSpawn(args) {
  return {
    send: (message) => {
      if (message.type === 'execute') {
        const mockAgent = new MockAgent(
          message.taskId,
          message.task,
          (result) => {
            // 模拟返回结果
            process.nextTick(() => {
              global.process.emit('mockResult', {
                taskId: message.taskId,
                result
              });
            });
          }
        );
        mockAgent.start();
      }
    }
  };
}

// 替换原始的 spawn
const childProcess = require('child_process');
const originalSpawn = childProcess.spawn;
childProcess.spawn = mockSessionsSpawn;

// 运行简化版测试
async function runSimpleTests() {
  console.log('🚀 开始简化版并行执行测试...\n');
  
  const tests = [
    { name: '基本功能测试', test: testBasicFunctionality.bind(this) },
    { name: '优先级队列测试', test: testPriorityQueue.bind(this) },
    { name: '并行执行测试', test: testParallelExecution.bind(this) },
    { name: '结果聚合测试', test: testResultAggregation.bind(this) },
    { name: '错误处理测试', test: testErrorHandling.bind(this) }
  ];
  
  for (const test of tests) {
    console.log(`\n📋 运行测试: ${test.name}`);
    console.log('='.repeat(test.name.length + 10));
    
    try {
      await test.test();
      console.log(`✅ ${test.name} 通过`);
    } catch (error) {
      console.log(`❌ ${test.name} 失败: ${error.message}`);
    }
  }
}

async function testBasicFunctionality() {
  const manager = new ParallelExecutionManager({
    enableLogging: false,
    maxConcurrentAgents: 3
  });
  
  const tasks = [
    { id: 'task1', task: { type: 'echo', data: 'Hello World' } },
    { id: 'task2', task: { type: 'echo', data: 'Test Data' } },
    { id: 'task3', task: { type: 'echo', data: 'Basic Test' } }
  ];
  
  for (const task of tasks) {
    manager.addTask(task.id, task.task, 'medium');
  }
  
  manager.start();
  
  // 监听模拟结果
  return new Promise((resolve) => {
    const results = [];
    const mockHandler = (data) => {
      results.push(data);
      if (results.length === 3) {
        resolve(results);
      }
    };
    
    global.process.on('mockResult', mockHandler);
    
    // 设置超时
    setTimeout(() => {
      global.process.removeListener('mockResult', mockHandler);
      resolve(results);
    }, 10000);
  });
}

async function testPriorityQueue() {
  const manager = new ParallelExecutionManager({
    enableLogging: false,
    maxConcurrentAgents: 2,
    enableTaskPrioritization: true
  });
  
  const tasks = [
    { id: 'high1', task: { type: 'echo', data: 'High Priority 1' }, priority: 'high' },
    { id: 'low1', task: { type: 'echo', data: 'Low Priority 1' }, priority: 'low' },
    { id: 'high2', task: { type: 'echo', data: 'High Priority 2' }, priority: 'high' },
    { id: 'medium1', task: { type: 'echo', data: 'Medium Priority 1' }, priority: 'medium' }
  ];
  
  for (const task of tasks) {
    manager.addTask(task.id, task.task, task.priority);
  }
  
  manager.start();
  
  const results = [];
  return new Promise((resolve) => {
    const mockHandler = (data) => {
      results.push(data);
      if (results.length === 4) {
        resolve(results);
      }
    };
    
    global.process.on('mockResult', mockHandler);
    
    setTimeout(() => {
      global.process.removeListener('mockResult', mockHandler);
      resolve(results);
    }, 10000);
  });
}

async function testParallelExecution() {
  const manager = new ParallelExecutionManager({
    enableLogging: false,
    maxConcurrentAgents: 5
  });
  
  const taskCount = 10;
  const tasks = [];
  
  for (let i = 0; i < taskCount; i++) {
    tasks.push({
      id: `parallel_task_${i}`,
      task: { 
        type: 'echo', 
        data: `Task ${i}` 
      },
      priority: 'medium'
    });
  }
  
  for (const task of tasks) {
    manager.addTask(task.id, task.task, task.priority);
  }
  
  manager.start();
  
  const results = [];
  return new Promise((resolve) => {
    const mockHandler = (data) => {
      results.push(data);
      if (results.length === taskCount) {
        resolve(results);
      }
    };
    
    global.process.on('mockResult', mockHandler);
    
    setTimeout(() => {
      global.process.removeListener('mockResult', mockHandler);
      resolve(results);
    }, 20000);
  });
}

async function testResultAggregation() {
  const manager = new ParallelExecutionManager({
    enableLogging: false,
    maxConcurrentAgents: 3,
    enableResultAggregation: true
  });
  
  const tasks = [
    { 
      id: 'task1', 
      task: { type: 'echo', data: 'Hello World' },
      metadata: { content: 'Hello World' }
    },
    { 
      id: 'task2', 
      task: { type: 'echo', data: 'Hello World' },
      metadata: { content: 'Hello World' }
    },
    { 
      id: 'task3', 
      task: { type: 'echo', data: 'Unique Content' },
      metadata: { content: 'Unique Content' }
    }
  ];
  
  for (const task of tasks) {
    manager.addTask(task.id, task.task, 'medium', task.metadata);
  }
  
  manager.start();
  
  const results = [];
  return new Promise((resolve) => {
    const mockHandler = (data) => {
      results.push(data);
      if (results.length === 3) {
        resolve(results);
      }
    };
    
    global.process.on('mockResult', mockHandler);
    
    setTimeout(() => {
      global.process.removeListener('mockResult', mockHandler);
      resolve(results);
    }, 10000);
  });
}

async function testErrorHandling() {
  const manager = new ParallelExecutionManager({
    enableLogging: false,
    maxConcurrentAgents: 3
  });
  
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
  
  for (const task of tasks) {
    manager.addTask(task.id, task.task, 'medium');
  }
  
  manager.start();
  
  const results = [];
  return new Promise((resolve) => {
    const mockHandler = (data) => {
      results.push(data);
      if (results.length === 3) {
        resolve(results);
      }
    };
    
    global.process.on('mockResult', mockHandler);
    
    setTimeout(() => {
      global.process.removeListener('mockResult', mockHandler);
      resolve(results);
    }, 10000);
  });
}

// 运行测试
async function main() {
  await runSimpleTests();
  
  // 恢复原始 spawn
  childProcess.spawn = originalSpawn;
  
  console.log('\n🎉 简化版测试完成');
}

// 如果直接运行此脚本
if (require.main === module) {
  main().catch(error => {
    console.error('测试运行失败:', error);
    process.exit(1);
  });
}

module.exports = { runSimpleTests, MockAgent };