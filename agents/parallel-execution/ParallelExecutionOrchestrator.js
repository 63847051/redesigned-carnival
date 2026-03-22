/**
 * 并行执行编排器 (Parallel Execution Orchestrator)
 * 
 * 负责协调多个 Agent 的并行执行，实现真正的并行处理能力
 * 
 * 功能：
 * - 并行启动多个 Agent
 * - 任务优先级管理
 * - 结果自动聚合
 * - 错误处理和重试机制
 * - 执行状态监控
 */

const { spawn } = require('child_process');
const { EventEmitter } = require('events');

class ParallelExecutionOrchestrator extends EventEmitter {
  constructor(config = {}) {
    super();
    
    // 配置参数
    this.config = {
      maxConcurrentAgents: config.maxConcurrentAgents || 5,
      taskTimeout: config.taskTimeout || 30000, // 30秒超时
      retryAttempts: config.retryAttempts || 2,
      enableLogging: config.enableLogging !== false,
      ...config
    };
    
    // 状态管理
    this.activeAgents = new Map(); // 当前运行的 Agent
    this.taskQueue = []; // 任务队列
    this.completedTasks = []; // 已完成的任务
    this.failedTasks = []; // 失败的任务
    this.priorityWeights = { // 任务优先级权重
      high: 3,
      medium: 2,
      low: 1
    };
    
    // 统计信息
    this.stats = {
      totalStarted: 0,
      totalCompleted: 0,
      totalFailed: 0,
      totalRetries: 0
    };
    
    this._setupEventHandlers();
  }
  
  /**
   * 设置事件处理器
   */
  _setupEventHandlers() {
    this.on('agentStarted', (data) => {
      this.config.enableLogging && console.log(`[并行编排器] Agent 启动: ${data.agentId} | 任务: ${data.taskId}`);
    });
    
    this.on('agentCompleted', (data) => {
      this.config.enableLogging && console.log(`[并行编排器] Agent 完成: ${data.agentId} | 任务: ${data.taskId}`);
      this._processNextAgent();
    });
    
    this.on('agentFailed', (data) => {
      this.config.enableLogging && console.log(`[并行编排器] Agent 失败: ${data.agentId} | 任务: ${data.taskId} | 错误: ${data.error}`);
      this._handleTaskFailure(data);
    });
    
    this.on('queueEmpty', () => {
      this.config.enableLogging && console.log('[并行编排器] 队列已清空，所有任务完成');
    });
  }
  
  /**
   * 添加任务到队列
   * @param {Object} task - 任务对象
   * @param {string} taskId - 任务ID
   * @param {string} priority - 优先级 (high|medium|low)
   * @param {Object} taskData - 任务数据
   */
  addTask(taskId, task, priority = 'medium', taskData = {}) {
    const taskWithPriority = {
      id: taskId,
      task,
      priority: priority,
      weight: this.priorityWeights[priority],
      data: taskData,
      createdAt: new Date(),
      retries: 0
    };
    
    // 按优先级插入队列
    this._insertTaskByPriority(taskWithPriority);
    this.config.enableLogging && console.log(`[并行编排器] 添加任务: ${taskId} | 优先级: ${priority}`);
    
    // 如果有可用槽位，立即执行
    if (this.activeAgents.size < this.config.maxConcurrentAgents) {
      this._processNextAgent();
    }
  }
  
  /**
   * 按优先级插入任务
   */
  _insertTaskByPriority(task) {
    let inserted = false;
    
    // 找到合适的位置插入
    for (let i = 0; i < this.taskQueue.length; i++) {
      if (this.taskQueue[i].weight < task.weight) {
        this.taskQueue.splice(i, 0, task);
        inserted = true;
        break;
      }
    }
    
    // 如果没有插入，添加到末尾
    if (!inserted) {
      this.taskQueue.push(task);
    }
  }
  
  /**
   * 处理下一个任务
   */
  _processNextAgent() {
    if (this.taskQueue.length === 0) {
      this.emit('queueEmpty');
      return;
    }
    
    if (this.activeAgents.size >= this.config.maxConcurrentAgents) {
      return; // 已达到最大并发数
    }
    
    // 获取下一个最高优先级任务
    const nextTask = this.taskQueue.shift();
    this._executeTask(nextTask);
  }
  
  /**
   * 执行单个任务
   */
  _executeTask(task) {
    const agentId = `agent_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;
    
    this.activeAgents.set(agentId, task);
    this.stats.totalStarted++;
    
    // 触发 Agent 启动事件
    this.emit('agentStarted', {
      agentId,
      taskId: task.id,
      priority: task.priority
    });
    
    // 创建并启动 Agent
    const agentProcess = this._createAgentProcess(agentId, task);
    
    // 设置超时
    const timeout = setTimeout(() => {
      this._killAgent(agentId, '任务超时');
    }, this.config.taskTimeout);
    
    // 监听进程事件
    agentProcess.on('message', (message) => {
      this._handleAgentMessage(agentId, message);
    });
    
    agentProcess.on('error', (error) => {
      clearTimeout(timeout);
      this._handleAgentError(agentId, error);
    });
    
    agentProcess.on('exit', (code) => {
      clearTimeout(timeout);
      this._handleAgentExit(agentId, code);
    });
    
    // 启动任务 - 确保task是字符串
    const taskToSend = {
      type: 'execute',
      taskId: task.id,
      task: typeof task.task === 'string' ? task.task : JSON.stringify(task.task),
      data: task.data
    };
    
    agentProcess.send(taskToSend);
  }
  
  /**
   * 创建 Agent 进程
   */
  _createAgentProcess(agentId, task) {
    // 使用 sessions_spawn 创建子 Agent
    return spawn('sessions_spawn', [
      '-runtime', 'subagent',
      '-model', this._getModelForTask(task.task),
      '-session-id', agentId,
      '-background', 'true'
    ]);
  }
  
  /**
   * 根据任务类型选择合适的模型
   */
  _getModelForTask(taskType) {
    // 确保 taskType 是字符串
    if (typeof taskType !== 'string') {
      taskType = String(taskType);
    }
    
    const modelMapping = {
      '代码': 'opencode/minimax-m2.5-free',
      '技术': 'opencode/minimax-m2.5-free',
      'API': 'opencode/minimax-m2.5-free',
      '爬虫': 'opencode/minimax-m2.5-free',
      '日志': 'glmcode/glm-4.5-air',
      '记录': 'glmcode/glm-4.5-air',
      '工作': 'glmcode/glm-4.5-air',
      '任务': 'glmcode/glm-4.5-air',
      '设计': 'glmcode/glm-4.6',
      '图纸': 'glmcode/glm-4.6',
      '平面图': 'glmcode/glm-4.6'
    };
    
    // 匹配任务类型
    for (const [type, model] of Object.entries(modelMapping)) {
      if (taskType.includes(type)) {
        return model;
      }
    }
    
    // 默认模型
    return 'glmcode/glm-4.7';
  }
  
  /**
   * 处理 Agent 消息
   */
  _handleAgentMessage(agentId, message) {
    const task = this.activeAgents.get(agentId);
    if (!task) return;
    
    switch (message.type) {
      case 'progress':
        this.emit('agentProgress', {
          agentId,
          taskId: task.id,
          progress: message.progress,
          message: message.message
        });
        break;
        
      case 'result':
        this._handleAgentResult(agentId, message.result);
        break;
        
      case 'error':
        this._handleAgentError(agentId, new Error(message.error));
        break;
    }
  }
  
  /**
   * 处理 Agent 结果
   */
  _handleAgentResult(agentId, result) {
    const task = this.activeAgents.get(agentId);
    if (!task) return;
    
    // 记录完成的任务
    const completedTask = {
      ...task,
      agentId,
      result,
      completedAt: new Date(),
      executionTime: Date.now() - task.createdAt.getTime()
    };
    
    this.completedTasks.push(completedTask);
    this.activeAgents.delete(agentId);
    this.stats.totalCompleted++;
    
    // 触发完成事件
    this.emit('agentCompleted', {
      agentId,
      taskId: task.id,
      result,
      completedTask
    });
  }
  
  /**
   * 处理 Agent 错误
   */
  _handleAgentError(agentId, error) {
    const task = this.activeAgents.get(agentId);
    if (!task) return;
    
    this._killAgent(agentId, error.message);
  }
  
  /**
   * 处理 Agent 退出
   */
  _handleAgentExit(agentId, code) {
    const task = this.activeAgents.get(agentId);
    if (!task) return;
    
    if (code === 0) {
      // 正常退出，等待结果消息
      return;
    } else {
      this._killAgent(agentId, `进程异常退出，代码: ${code}`);
    }
  }
  
  /**
   * 处理任务失败
   */
  _handleTaskFailure(data) {
    const task = this.activeAgents.get(data.agentId);
    if (!task) return;
    
    const failedTaskData = {
      ...task,
      agentId: data.agentId,
      error: data.error,
      failedAt: new Date()
    };
    
    // 检查是否需要重试
    if (task.retries < this.config.retryAttempts) {
      task.retries++;
      this.stats.totalRetries++;
      
      // 重新加入队列，降低优先级
      task.weight = Math.max(1, task.weight - 1);
      this._insertTaskByPriority(task);
      
      this.config.enableLogging && 
        console.log(`[并行编排器] 任务 ${task.id} 第 ${task.retries} 次重试`);
      
      this.emit('taskRetry', {
        taskId: task.id,
        retryCount: task.retries,
        agentId: data.agentId
      });
    } else {
      // 不再重试，标记为失败
      this.failedTasks.push(failedTaskData);
      this.activeAgents.delete(data.agentId);
      this.stats.totalFailed++;
      
      this.emit('agentFailed', {
        ...data,
        final: true
      });
    }
  }
  
  /**
   * 终止 Agent
   */
  _killAgent(agentId, reason) {
    this.config.enableLogging && console.log(`[并行编排器] 终止 Agent: ${agentId} | 原因: ${reason}`);
    
    const task = this.activeAgents.get(agentId);
    if (task) {
      this.emit('agentFailed', {
        agentId,
        taskId: task.id,
        error: reason,
        final: false
      });
    }
  }
  
  /**
   * 获取当前状态
   */
  getStatus() {
    return {
      activeAgents: this.activeAgents.size,
      pendingTasks: this.taskQueue.length,
      completedTasks: this.completedTasks.length,
      failedTasks: this.failedTasks.length,
      stats: { ...this.stats },
      timestamp: new Date()
    };
  }
  
  /**
   * 等待所有任务完成
   */
  async waitForAll() {
    return new Promise((resolve) => {
      const checkCompletion = () => {
        if (this.taskQueue.length === 0 && this.activeAgents.size === 0) {
          resolve({
            completed: this.completedTasks,
            failed: this.failedTasks,
            stats: this.getStatus()
          });
        } else {
          setTimeout(checkCompletion, 100);
        }
      };
      
      checkCompletion();
    });
  }
  
  /**
   * 清理资源
   */
  destroy() {
    // 终止所有活跃的 Agent
    for (const [agentId] of this.activeAgents) {
      this._killAgent(agentId, '编排器销毁');
    }
    
    this.activeAgents.clear();
    this.taskQueue = [];
    this.removeAllListeners();
  }
}

module.exports = ParallelExecutionOrchestrator;