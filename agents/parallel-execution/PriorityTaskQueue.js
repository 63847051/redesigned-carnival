/**
 * 任务优先级队列 (Priority Task Queue)
 * 
 * 实现带优先级的任务队列系统，支持多种优先级策略
 * 
 * 功能：
 * - 多级优先级管理
 * - 任务预定义分类
 * - 动态优先级调整
 * - 队列状态监控
 * - 公平性保障机制
 */

const EventEmitter = require('events');

class PriorityTaskQueue extends EventEmitter {
  constructor(config = {}) {
    super();
    
    // 配置参数
    this.config = {
      maxQueueSize: config.maxQueueSize || 1000,
      enableFairness: config.enableFairness !== false,
      fairnessWindow: config.fairnessWindow || 10, // 公平性窗口大小
      enableDynamicPriority: config.enableDynamicPriority !== false,
      priorityDecayRate: config.priorityDecayRate || 0.95, // 优先级衰减率
      enableLogging: config.enableLogging !== false,
      ...config
    };
    
    // 队列状态
    this.queues = {
      high: [], // 高优先级队列
      medium: [], // 中优先级队列
      low: [] // 低优先级队列
    };
    
    // 任务映射
    this.taskMap = new Map(); // taskId -> task
    this.priorityWeights = { 3: 'high', 2: 'medium', 1: 'low' };
    
    // 公平性保障
    this.recentlyProcessed = new Set(); // 最近处理的任务ID
    this.processHistory = []; // 处理历史
    
    // 统计信息
    this.stats = {
      totalEnqueued: 0,
      totalDequeued: 0,
      totalDiscarded: 0,
      priorityBreakdown: { high: 0, medium: 0, low: 0 }
    };
    
    // 启动公平性检查
    if (this.config.enableFairness) {
      this._startFairnessChecker();
    }
  }
  
  /**
   * 添加任务到队列
   * @param {string} taskId - 任务ID
   * @param {Object} task - 任务对象
   * @param {string} priority - 优先级 (high|medium|low)
   * @param {Object} metadata - 任务元数据
   * @returns {boolean} 是否成功添加
   */
  enqueue(taskId, task, priority = 'medium', metadata = {}) {
    // 检查队列大小限制
    if (this.taskMap.size >= this.config.maxQueueSize) {
      this.stats.totalDiscarded++;
      this.emit('queueFull', { taskId, priority });
      return false;
    }
    
    // 检查任务是否已存在
    if (this.taskMap.has(taskId)) {
      this.emit('taskExists', { taskId });
      return false;
    }
    
    // 创建任务对象
    const taskWithPriority = {
      id: taskId,
      task,
      priority,
      weight: this._getPriorityWeight(priority),
      metadata,
      createdAt: new Date(),
      lastAccessed: new Date(),
      accessCount: 0,
      dynamicPriority: this._getPriorityWeight(priority) // 动态优先级
    };
    
    // 添加到对应队列
    this.queues[priority].push(taskWithPriority);
    this.taskMap.set(taskId, taskWithPriority);
    
    // 更新统计
    this.stats.totalEnqueued++;
    this.stats.priorityBreakdown[priority]++;
    
    this.config.enableLogging && 
      console.log(`[优先级队列] 添加任务: ${taskId} | 优先级: ${priority}`);
    
    // 触发事件
    this.emit('taskEnqueued', taskWithPriority);
    
    return true;
  }
  
  /**
   * 从队列中取出任务
   * @param {Object} options - 取出选项
   * @returns {Object|null} 取出的任务或null
   */
  dequeue(options = {}) {
    const { 
      priority = null, 
      includeDynamic = this.config.enableDynamicPriority,
      skipFairnessCheck = false 
    } = options;
    
    // 检查队列是否为空
    if (this._isEmpty()) {
      this.emit('queueEmpty');
      return null;
    }
    
    // 选择要处理的优先级
    const targetPriority = priority || this._selectPriority(includeDynamic);
    
    // 从目标队列中取任务
    const taskIndex = this._findTaskInQueue(targetPriority);
    
    if (taskIndex !== -1) {
      const task = this.queues[targetPriority][taskIndex];
      
      // 移除任务
      this.queues[targetPriority].splice(taskIndex, 1);
      this.taskMap.delete(task.id);
      
      // 更新访问统计
      task.lastAccessed = new Date();
      task.accessCount++;
      
      // 记录处理历史（用于公平性检查）
      if (!skipFairnessCheck && this.config.enableFairness) {
        this.processHistory.push({
          taskId: task.id,
          priority: task.priority,
          timestamp: new Date()
        });
        this._enforceFairness();
      }
      
      // 更新统计
      this.stats.totalDequeued++;
      
      this.config.enableLogging && 
        console.log(`[优先级队列] 取出任务: ${task.id} | 优先级: ${task.priority}`);
      
      // 触发事件
      this.emit('taskDequeued', task);
      
      return task;
    }
    
    return null;
  }
  
  /**
   * 获取优先级权重
   */
  _getPriorityWeight(priority) {
    const weights = { high: 3, medium: 2, low: 1 };
    return weights[priority] || 1;
  }
  
  /**
   * 选择要处理的优先级
   */
  _selectPriority(includeDynamic = false) {
    let selectedPriority = null;
    let highestPriority = 0;
    
    // 遍历所有优先级队列
    for (const [priority, tasks] of Object.entries(this.queues)) {
      if (tasks.length === 0) continue;
      
      // 计算队列的实际优先级
      let queuePriority = this._getPriorityWeight(priority);
      
      // 如果启用动态优先级，考虑动态因素
      if (includeDynamic) {
        const dynamicFactor = this._calculateDynamicPriorityFactor(priority);
        queuePriority *= dynamicFactor;
      }
      
      // 如果启用公平性，考虑公平性因素
      if (this.config.enableFairness) {
        const fairnessFactor = this._calculateFairnessFactor(priority);
        queuePriority *= fairnessFactor;
      }
      
      // 选择最高优先级的队列
      if (queuePriority > highestPriority) {
        highestPriority = queuePriority;
        selectedPriority = priority;
      }
    }
    
    return selectedPriority || 'low';
  }
  
  /**
   * 计算动态优先级因子
   */
  _calculateDynamicPriorityFactor(priority) {
    const tasks = this.queues[priority];
    if (tasks.length === 0) return 1;
    
    // 计算队列中任务的平均等待时间
    const now = Date.now();
    const totalWaitTime = tasks.reduce((sum, task) => {
      return sum + (now - task.createdAt.getTime());
    }, 0);
    
    const avgWaitTime = totalWaitTime / tasks.length;
    
    // 等待时间越长，优先级越高
    const waitTimeBonus = Math.min(2, avgWaitTime / 60000); // 每分钟等待时间增加最多2倍优先级
    
    return 1 + waitTimeBonus;
  }
  
  /**
   * 计算公平性因子
   */
  _calculateFairnessFactor(priority) {
    const now = Date.now();
    const recentWindow = this.config.fairnessWindow * 60 * 1000; // 转换为毫秒
    
    // 计算该优先级最近的处理次数
    const recentCount = this.processHistory.filter(entry => {
      const timeDiff = now - entry.timestamp.getTime();
      return timeDiff <= recentWindow && entry.priority === priority;
    }).length;
    
    // 如果某个优先级被频繁处理，降低其优先级
    if (recentCount > 0) {
      return Math.max(0.5, 1 - (recentCount / this.config.fairnessWindow) * 0.3);
    }
    
    return 1;
  }
  
  /**
   * 查找队列中的任务
   */
  _findTaskInQueue(priority) {
    const tasks = this.queues[priority];
    if (tasks.length === 0) return -1;
    
    // 找到最早的任务（FIFO）
    let earliestTask = tasks[0];
    let earliestIndex = 0;
    
    for (let i = 1; i < tasks.length; i++) {
      if (tasks[i].createdAt < earliestTask.createdAt) {
        earliestTask = tasks[i];
        earliestIndex = i;
      }
    }
    
    return earliestIndex;
  }
  
  /**
   * 强制执行公平性
   */
  _enforceFairness() {
    const now = Date.now();
    const windowSize = this.config.fairnessWindow * 60 * 1000;
    
    // 清理过期的处理历史
    this.processHistory = this.processHistory.filter(entry => {
      return now - entry.timestamp.getTime() <= windowSize;
    });
  }
  
  /**
   * 检查队列是否为空
   */
  _isEmpty() {
    return Object.values(this.queues).every(queue => queue.length === 0);
  }
  
  /**
   * 启动公平性检查器
   */
  _startFairnessChecker() {
    setInterval(() => {
      if (!this._isEmpty()) {
        // 检查是否有优先级被忽视太久
        this._checkPriorityPriorityStarvation();
      }
    }, 5000); // 每5秒检查一次
  }
  
  /**
   * 检查优先级饥饿
   */
  _checkPriorityPriorityStarvation() {
    const now = Date.now();
    const starvationThreshold = 5 * 60 * 1000; // 5分钟饥饿阈值
    
    for (const [priority, tasks] of Object.entries(this.queues)) {
      if (tasks.length > 0) {
        const oldestTask = tasks[0];
        const timeSinceAccess = now - oldestTask.lastAccessed.getTime();
        
        if (timeSinceAccess > starvationThreshold) {
          // 将任务提升到高优先级
          const task = tasks.shift();
          task.priority = 'high';
          task.weight = this._getPriorityWeight('high');
          this.queues.high.push(task);
          
          this.emit('priorityStarvationRescued', {
            taskId: task.id,
            originalPriority: priority,
            promotedTo: 'high',
            waitTime: timeSinceAccess
          });
        }
      }
    }
  }
  
  /**
   * 获取队列状态
   */
  getStatus() {
    return {
      queueSizes: {
        high: this.queues.high.length,
        medium: this.queues.medium.length,
        low: this.queues.low.length,
        total: this.taskMap.size
      },
      stats: { ...this.stats },
      priorityBreakdown: { ...this.stats.priorityBreakdown },
      isProcessing: !this._isEmpty(),
      lastUpdate: new Date()
    };
  }
  
  /**
   * 获取队列中特定优先级的任务列表
   */
  getTasksByPriority(priority) {
    return this.queues[priority].map(task => ({
      id: task.id,
      createdAt: task.createdAt,
      accessCount: task.accessCount,
      metadata: task.metadata
    }));
  }
  
  /**
   * 移除特定任务
   */
  removeTask(taskId) {
    for (const [priority, tasks] of Object.entries(this.queues)) {
      const index = tasks.findIndex(task => task.id === taskId);
      if (index !== -1) {
        const task = tasks.splice(index, 1)[0];
        this.taskMap.delete(taskId);
        
        this.emit('taskRemoved', task);
        return task;
      }
    }
    return null;
  }
  
  /**
   * 清空队列
   */
  clear() {
    this.queues = { high: [], medium: [], low: [] };
    this.taskMap.clear();
    this.processHistory = [];
    
    this.emit('queueCleared');
  }
  
  /**
   * 获取队列快照
   */
  getSnapshot() {
    const snapshot = [];
    
    for (const [priority, tasks] of Object.entries(this.queues)) {
      for (const task of tasks) {
        snapshot.push({
          id: task.id,
          priority: task.priority,
          weight: task.weight,
          createdAt: task.createdAt,
          lastAccessed: task.lastAccessed,
          accessCount: task.accessCount,
          metadata: task.metadata
        });
      }
    }
    
    return snapshot.sort((a, b) => b.weight - a.weight);
  }
  
  /**
   * 更新任务元数据
   */
  updateTaskMetadata(taskId, metadata) {
    const task = this.taskMap.get(taskId);
    if (task) {
      task.metadata = { ...task.metadata, ...metadata };
      this.emit('taskMetadataUpdated', task);
      return true;
    }
    return false;
  }
  
  /**
   * 调整任务优先级
   */
  updateTaskPriority(taskId, newPriority) {
    const task = this.taskMap.get(taskId);
    if (task && task.priority !== newPriority) {
      // 从原队列移除
      const oldQueue = this.queues[task.priority];
      const index = oldQueue.findIndex(t => t.id === taskId);
      if (index !== -1) {
        oldQueue.splice(index, 1);
      }
      
      // 更新任务属性
      task.priority = newPriority;
      task.weight = this._getPriorityWeight(newPriority);
      
      // 添加到新队列
      this.queues[newPriority].push(task);
      
      this.emit('taskPriorityUpdated', {
        taskId,
        oldPriority: task.priority,
        newPriority,
        weight: task.weight
      });
      
      return true;
    }
    return false;
  }
}

module.exports = PriorityTaskQueue;