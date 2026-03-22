/**
 * 并行执行管理器 (Parallel Execution Manager)
 * 
 * 整合并行执行编排器、任务优先级队列和结果收集器的主要管理类
 * 
 * 功能：
 * - 统一管理并行执行流程
 * - 任务分发和调度
 * - 结果收集和报告
 * - 监控和统计
 * - 错误处理和恢复
 */

const { EventEmitter } = require('events');
const ParallelExecutionOrchestrator = require('./ParallelExecutionOrchestrator');
const PriorityTaskQueue = require('./PriorityTaskQueue');
const ResultCollector = require('./ResultCollector');

class ParallelExecutionManager extends EventEmitter {
  constructor(config = {}) {
    super();
    
    // 配置参数
    this.config = {
      maxConcurrentAgents: config.maxConcurrentAgents || 5,
      enableTaskPrioritization: config.enableTaskPrioritization !== false,
      enableResultAggregation: config.enableResultAggregation !== false,
      enableMonitoring: config.enableMonitoring !== true,
      enableLogging: config.enableLogging !== false,
      ...config
    };
    
    // 初始化组件
    this.orchestrator = new ParallelExecutionOrchestrator({
      maxConcurrentAgents: this.config.maxConcurrentAgents,
      enableLogging: this.config.enableLogging
    });
    
    this.taskQueue = new PriorityTaskQueue({
      enableLogging: this.config.enableLogging
    });
    
    this.resultCollector = new ResultCollector({
      enableDeduplication: this.config.enableResultAggregation,
      enableQualityAssessment: this.config.enableResultAggregation,
      enableAggregation: this.config.enableResultAggregation,
      enableLogging: this.config.enableLogging
    });
    
    // 任务管理
    this.tasks = new Map(); // taskId -> task
    this.activeTasks = new Map(); // taskId -> task
    this.completedTasks = new Map(); // taskId -> result
    this.failedTasks = new Map(); // taskId -> error
    
    // 监控状态
    this.monitoringInterval = null;
    this.isRunning = false;
    
    // 设置组件间的事件监听
    this._setupComponentEvents();
  }
  
  /**
   * 设置组件间的事件监听
   */
  _setupComponentEvents() {
    // 并行编排器事件
    this.orchestrator.on('agentStarted', (data) => {
      this.activeTasks.set(data.taskId, {
        taskId: data.taskId,
        agentId: data.agentId,
        startedAt: new Date()
      });
      
      this.emit('taskStarted', data);
    });
    
    this.orchestrator.on('agentCompleted', (data) => {
      const task = this.activeTasks.get(data.taskId);
      if (task) {
        task.completedAt = new Date();
        task.executionTime = task.completedAt - task.startedAt;
        this.activeTasks.delete(data.taskId);
        this.completedTasks.set(data.taskId, {
          ...task,
          result: data.result
        });
      }
      
      // 将结果传递给结果收集器
      this.resultCollector.addResult(data.taskId, data.result, data.agentId, {
        completedAt: new Date(),
        executionTime: task?.executionTime || 0
      });
      
      this.emit('taskCompleted', data);
    });
    
    this.orchestrator.on('agentFailed', (data) => {
      const task = this.activeTasks.get(data.taskId);
      if (task) {
        task.failedAt = new Date();
        task.error = data.error;
        this.activeTasks.delete(data.taskId);
        this.failedTasks.set(data.taskId, {
          ...task,
          error: data.error
        });
      }
      
      this.emit('taskFailed', data);
    });
    
    // 任务队列事件
    this.taskQueue.on('taskEnqueued', (task) => {
      this.tasks.set(task.id, task);
      this.emit('taskQueued', task);
    });
    
    this.taskQueue.on('taskDequeued', (task) => {
      this.tasks.delete(task.id);
      this.emit('taskDequeued', task);
    });
    
    // 结果收集器事件
    this.resultCollector.on('resultReceived', (data) => {
      this.emit('resultReceived', data);
    });
    
    this.resultCollector.on('resultDeduplicated', (data) => {
      this.emit('resultDeduplicated', data);
    });
    
    this.resultCollector.on('resultsAggregated', (data) => {
      this.emit('resultsAggregated', data);
    });
  }
  
  /**
   * 添加任务
   * @param {string} taskId - 任务ID
   * @param {Object} task - 任务对象
   * @param {string} priority - 优先级 (high|medium|low)
   * @param {Object} metadata - 任务元数据
   * @returns {boolean} 是否成功添加
   */
  addTask(taskId, task, priority = 'medium', metadata = {}) {
    // 添加到任务队列
    const queued = this.taskQueue.enqueue(taskId, task, priority, metadata);
    
    if (queued) {
      // 自动启动处理
      if (this.isRunning) {
        this._processNextTask();
      }
    }
    
    return queued;
  }
  
  /**
   * 启动并行执行管理器
   */
  start() {
    if (this.isRunning) {
      this.emit('alreadyRunning');
      return false;
    }
    
    this.isRunning = true;
    
    // 启动监控
    if (this.config.enableMonitoring) {
      this._startMonitoring();
    }
    
    // 处理队列中的任务
    this._processNextTask();
    
    this.emit('started');
    this.config.enableLogging && console.log('[并行执行管理器] 已启动');
    
    return true;
  }
  
  /**
   * 停止并行执行管理器
   */
  stop() {
    if (!this.isRunning) {
      this.emit('notRunning');
      return false;
    }
    
    this.isRunning = false;
    
    // 停止监控
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
    
    // 等待所有活跃任务完成
    if (this.activeTasks.size > 0) {
      this.emit('waitingForCompletion', {
        activeTasks: this.activeTasks.size,
        pendingTasks: this.taskQueue.getStatus().queueSizes.total
      });
    }
    
    this.emit('stopped');
    this.config.enableLogging && console.log('[并行执行管理器] 已停止');
    
    return true;
  }
  
  /**
   * 处理下一个任务
   */
  _processNextTask() {
    if (!this.isRunning) return;
    
    // 如果任务队列已空，检查是否完成
    if (this.taskQueue._isEmpty() && this.activeTasks.size === 0) {
      this.emit('allTasksCompleted');
      return;
    }
    
    // 从队列中获取任务
    const task = this.taskQueue.dequeue({
      includeDynamic: this.config.enableTaskPrioritization,
      skipFairnessCheck: false
    });
    
    if (task) {
      // 启动任务
      this.orchestrator.addTask(task.id, task.task, task.priority, task.metadata);
      this._processNextTask(); // 继续处理下一个任务
    }
  }
  
  /**
   * 启动监控
   */
  _startMonitoring() {
    this.monitoringInterval = setInterval(() => {
      this._emitStatusUpdate();
    }, 5000); // 每5秒更新一次状态
  }
  
  /**
   * 发送状态更新
   */
  _emitStatusUpdate() {
    const status = this.getStatus();
    
    this.emit('statusUpdate', status);
    
    // 检查异常状态
    if (status.activeAgents > this.config.maxConcurrentAgents) {
      this.emit('overload', status);
    }
    
    if (status.tasks && status.tasks.failed > 0) {
      this.emit('errors', status);
    }
  }
  
  /**
   * 获取整体状态
   */
  getStatus() {
    return {
      manager: {
        isRunning: this.isRunning,
        startTime: this.startTime,
        uptime: this.isRunning ? Date.now() - (this.startTime || Date.now()) : 0
      },
      tasks: {
        total: this.tasks.size,
        active: this.activeTasks.size,
        completed: this.completedTasks.size,
        failed: this.failedTasks.size,
        pending: this.taskQueue.getStatus().queueSizes.total,
        byPriority: {
          high: this.taskQueue.getStatus().queueSizes.high,
          medium: this.taskQueue.getStatus().queueSizes.medium,
          low: this.taskQueue.getStatus().queueSizes.low
        }
      },
      agents: {
        active: this.orchestrator.getStatus().activeAgents,
        maxConcurrent: this.config.maxConcurrentAgents,
        utilization: this.orchestrator.getStatus().activeAgents / this.config.maxConcurrentAgents
      },
      results: {
        total: this.resultCollector.getStatus().totalResults,
        successRate: this.resultCollector.calculateAverageQuality(),
        byType: this.resultCollector.getStatus().byType || {}
      },
      performance: {
        averageExecutionTime: this._calculateAverageExecutionTime(),
        throughput: this._calculateThroughput()
      },
      timestamp: new Date()
    };
  }
  
  /**
   * 计算平均执行时间
   */
  _calculateAverageExecutionTime() {
    if (this.completedTasks.size === 0) return 0;
    
    const totalExecutionTime = Array.from(this.completedTasks.values())
      .reduce((sum, task) => sum + (task.executionTime || 0), 0);
    
    return totalExecutionTime / this.completedTasks.size;
  }
  
  /**
   * 计算吞吐量
   */
  _calculateThroughput() {
    // 简化的吞吐量计算 - 每分钟完成的任务数
    const completedTasks = this.completedTasks.size;
    const runningTime = this.isRunning ? (Date.now() - (this.startTime || Date.now())) / 60000 : 0;
    
    return runningTime > 0 ? completedTasks / runningTime : 0;
  }
  
  /**
   * 批量添加任务
   */
  addTasks(tasks) {
    const results = [];
    
    for (const task of tasks) {
      const result = this.addTask(task.id, task.task, task.priority, task.metadata);
      results.push({
        taskId: task.id,
        success: result
      });
    }
    
    return results;
  }
  
  /**
   * 获取特定任务的状态
   */
  getTaskStatus(taskId) {
    // 检查活跃任务
    if (this.activeTasks.has(taskId)) {
      return {
        status: 'active',
        task: this.activeTasks.get(taskId)
      };
    }
    
    // 检查已完成任务
    if (this.completedTasks.has(taskId)) {
      return {
        status: 'completed',
        task: this.completedTasks.get(taskId)
      };
    }
    
    // 检查失败任务
    if (this.failedTasks.has(taskId)) {
      return {
        status: 'failed',
        task: this.failedTasks.get(taskId)
      };
    }
    
    // 检查队列中的任务
    const queueStatus = this.taskQueue.getStatus();
    if (queueStatus.queueSizes.total > 0) {
      return {
        status: 'queued',
        task: this.tasks.get(taskId)
      };
    }
    
    return {
      status: 'unknown',
      task: null
    };
  }
  
  /**
   * 取消特定任务
   */
  cancelTask(taskId) {
    const taskStatus = this.getTaskStatus(taskId);
    
    if (taskStatus.status === 'active') {
      // 终止活跃的Agent
      this.orchestrator._killAgent(taskStatus.task.agentId, '任务被取消');
      this.activeTasks.delete(taskId);
      this.emit('taskCancelled', { taskId, reason: 'user_cancelled' });
      return true;
    }
    
    if (taskStatus.status === 'queued') {
      // 从队列中移除
      this.taskQueue.removeTask(taskId);
      this.tasks.delete(taskId);
      this.emit('taskCancelled', { taskId, reason: 'removed_from_queue' });
      return true;
    }
    
    return false;
  }
  
  /**
   * 等待所有任务完成
   */
  async waitForAll() {
    return new Promise((resolve) => {
      const checkCompletion = () => {
        if (this.activeTasks.size === 0 && this.taskQueue._isEmpty()) {
          resolve({
            completed: Array.from(this.completedTasks.values()),
            failed: Array.from(this.failedTasks.values()),
            status: this.getStatus()
          });
        } else {
          setTimeout(checkCompletion, 1000);
        }
      };
      
      checkCompletion();
    });
  }
  
  /**
   * 生成执行报告
   */
  generateReport() {
    const status = this.getStatus();
    const resultReport = this.resultCollector.generateReport();
    
    return {
      executiveSummary: {
        totalTasks: status.tasks.total,
        completed: status.tasks.completed,
        failed: status.tasks.failed,
        successRate: status.tasks.completed / (status.tasks.total || 1),
        averageExecutionTime: status.performance.averageExecutionTime,
        throughput: status.performance.throughput
      },
      taskDistribution: {
        byStatus: {
          active: status.tasks.active,
          completed: status.tasks.completed,
          failed: status.tasks.failed,
          pending: status.tasks.pending
        },
        byPriority: status.tasks.byPriority,
        byAgent: this._getTaskDistributionByAgent()
      },
      performanceMetrics: {
        agentUtilization: status.agents.utilization,
        averageQuality: status.results.successRate,
        totalResults: status.results.total
      },
      qualityAnalysis: {
        overallQuality: resultReport.qualityMetrics,
        typeBreakdown: resultReport.byType,
        failedAnalysis: this._analyzeFailedTasks()
      },
      recommendations: this._generateRecommendations(status),
      timestamp: new Date()
    };
  }
  
  /**
   * 获取按Agent分布的任务
   */
  _getTaskDistributionByAgent() {
    const distribution = {};
    
    for (const [agentId, results] of this.resultCollector.resultsByAgent) {
      distribution[agentId] = {
        total: results.length,
        completed: results.filter(taskId => this.completedTasks.has(taskId)).length,
        failed: results.filter(taskId => this.failedTasks.has(taskId)).length
      };
    }
    
    return distribution;
  }
  
  /**
   * 分析失败任务
   */
  _analyzeFailedTasks() {
    const failedAnalysis = {
      total: this.failedTasks.size,
      byErrorType: {},
      byPriority: {},
      trends: []
    };
    
    for (const [taskId, task] of this.failedTasks) {
      // 按错误类型分类
      const errorType = task.error?.type || 'unknown';
      failedAnalysis.byErrorType[errorType] = (failedAnalysis.byErrorType[errorType] || 0) + 1;
      
      // 按优先级分类
      const priority = task.metadata?.priority || 'unknown';
      failedAnalysis.byPriority[priority] = (failedAnalysis.byPriority[priority] || 0) + 1;
    }
    
    return failedAnalysis;
  }
  
  /**
   * 生成改进建议
   */
  _generateRecommendations(status) {
    const recommendations = [];
    
    // 检查并发数是否合理
    if (status.agents.utilization > 0.9) {
      recommendations.push({
        type: 'capacity',
        priority: 'high',
        message: '建议增加最大并发Agent数量，以提高处理能力',
        currentValue: this.config.maxConcurrentAgents,
        suggestedValue: Math.ceil(this.config.maxConcurrentAgents * 1.5)
      });
    }
    
    // 检查失败率
    const failureRate = status.tasks.failed / (status.tasks.total || 1);
    if (failureRate > 0.1) {
      recommendations.push({
        type: 'quality',
        priority: 'medium',
        message: '失败率较高，建议检查任务配置和Agent性能',
        currentValue: (failureRate * 100).toFixed(1) + '%',
        suggestedValue: '< 10%'
      });
    }
    
    // 检查平均执行时间
    if (status.performance.averageExecutionTime > 30000) {
      recommendations.push({
        type: 'performance',
        priority: 'low',
        message: '平均执行时间较长，建议优化任务复杂度',
        currentValue: `${(status.performance.averageExecutionTime / 1000).toFixed(1)}s`,
        suggestedValue: '< 30s'
      });
    }
    
    return recommendations;
  }
  
  /**
   * 导出任务数据
   */
  exportData(format = 'json') {
    const status = this.getStatus();
    
    const exportData = {
      status: status,
      tasks: Array.from(this.tasks.values()),
      completedTasks: Array.from(this.completedTasks.values()),
      failedTasks: Array.from(this.failedTasks.values()),
      results: this.resultCollector.exportResults('summary'),
      report: this.generateReport(),
      timestamp: new Date()
    };
    
    switch (format) {
      case 'json':
        return JSON.stringify(exportData, null, 2);
        
      case 'csv':
        return this._exportToCSV(exportData);
        
      default:
        throw new Error(`Unsupported export format: ${format}`);
    }
  }
  
  /**
   * 导出为CSV
   */
  _exportToCSV(data) {
    const headers = [
      'taskId', 'status', 'priority', 'agentId', 
      'startTime', 'completionTime', 'executionTime',
      'resultType', 'qualityScore'
    ];
    
    const rows = [
      // 活跃任务
      ...Array.from(this.activeTasks.values()).map(task => [
        task.taskId,
        'active',
        task.metadata?.priority || '',
        task.agentId,
        task.startedAt?.toISOString() || '',
        '',
        '',
        '',
        ''
      ]),
      // 已完成任务
      ...Array.from(this.completedTasks.values()).map(task => [
        task.taskId,
        'completed',
        task.metadata?.priority || '',
        task.agentId,
        task.startedAt?.toISOString() || '',
        task.completedAt?.toISOString() || '',
        task.executionTime || '',
        task.result?.type || '',
        task.result?.quality?.score || ''
      ]),
      // 失败任务
      ...Array.from(this.failedTasks.values()).map(task => [
        task.taskId,
        'failed',
        task.metadata?.priority || '',
        task.agentId,
        task.startedAt?.toISOString() || '',
        task.failedAt?.toISOString() || '',
        '',
        '',
        ''
      ])
    ];
    
    return [headers, ...rows].map(row => row.join(',')).join('\n');
  }
  
  /**
   * 清理资源
   */
  cleanup() {
    // 停止管理器
    this.stop();
    
    // 清理组件
    this.orchestrator.destroy();
    this.taskQueue.clear();
    this.resultCollector.cleanup();
    
    // 清理数据
    this.tasks.clear();
    this.activeTasks.clear();
    this.completedTasks.clear();
    this.failedTasks.clear();
    
    this.emit('cleanedUp');
  }
}

module.exports = ParallelExecutionManager;