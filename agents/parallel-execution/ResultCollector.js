/**
 * 结果自动聚合器 (Result Collector)
 * 
 * 负责收集、处理和聚合多个 Agent 的执行结果
 * 
 * 功能：
 * - 自动收集 Agent 结果
 * - 结果格式标准化
 * - 结果去重和合并
 * - 结果质量评估
 * - 结果导出和报告生成
 */

const EventEmitter = require('events');

class ResultCollector extends EventEmitter {
  constructor(config = {}) {
    super();
    
    // 配置参数
    this.config = {
      maxResults: config.maxResults || 1000,
      enableDeduplication: config.enableDeduplication !== false,
      enableQualityAssessment: config.enableQualityAssessment !== false,
      enableAggregation: config.enableAggregation !== false,
      enableLogging: config.enableLogging !== false,
      resultTimeout: config.resultTimeout || 30000, // 30秒结果超时
      ...config
    };
    
    // 结果存储
    this.results = new Map(); // taskId -> result
    this.resultsByAgent = new Map(); // agentId -> [taskIds]
    this.resultsByType = new Map(); // type -> [taskIds]
    this.failedResults = new Map(); // taskId -> error
    
    // 元数据
    this.resultMetadata = new Map(); // taskId -> metadata
    
    // 去重配置
    this.dedupKeys = ['content', 'summary', 'output'];
    this.similarityThreshold = 0.85;
    
    // 统计信息
    this.stats = {
      totalReceived: 0,
      totalProcessed: 0,
      totalDeduplicated: 0,
      totalAggregated: 0,
      successRate: 0,
      averageProcessingTime: 0,
      typeBreakdown: {}
    };
    
    // 质量评估
    this.qualityMetrics = {
      completeness: 0,
      accuracy: 0,
      consistency: 0,
      relevance: 0
    };
    
    this._setupEventHandlers();
  }
  
  /**
   * 设置事件处理器
   */
  _setupEventHandlers() {
    this.on('resultReceived', (data) => {
      this.config.enableLogging && 
        console.log(`[结果收集器] 收到结果: ${data.taskId} | 类型: ${data.type}`);
    });
    
    this.on('resultProcessed', (data) => {
      this.config.enableLogging && 
        console.log(`[结果收集器] 处理完成: ${data.taskId}`);
    });
    
    this.on('resultDeduplicated', (data) => {
      this.config.enableLogging && 
        console.log(`[结果收集器] 结果去重: ${data.originalTaskId} -> ${data.deduplicatedToTaskId}`);
    });
    
    this.on('resultsAggregated', (data) => {
      this.config.enableLogging && 
        console.log(`[结果收集器] 结果聚合: ${data.aggregatedCount} 个结果合并为 1 个`);
    });
  }
  
  /**
   * 添加结果
   * @param {string} taskId - 任务ID
   * @param {Object} result - 结果对象
   * @param {string} agentId - Agent ID
   * @param {Object} metadata - 结果元数据
   * @returns {boolean} 是否成功添加
   */
  addResult(taskId, result, agentId, metadata = {}) {
    // 检查是否已存在
    if (this.results.has(taskId)) {
      this.emit('resultExists', { taskId });
      return false;
    }
    
    // 检查队列是否已满
    if (this.results.size >= this.config.maxResults) {
      this.emit('queueFull', { taskId });
      return false;
    }
    
    // 创建标准化结果
    const normalizedResult = this._normalizeResult(result, taskId, agentId, metadata);
    
    // 检查超时
    if (Date.now() - normalizedResult.timestamp > this.config.resultTimeout) {
      this.emit('resultTimeout', { taskId });
      return false;
    }
    
    // 存储结果
    this.results.set(taskId, normalizedResult);
    this._updateAgentMapping(agentId, taskId);
    this._updateTypeMapping(normalizedResult.type, taskId);
    this.resultMetadata.set(taskId, metadata);
    
    // 更新统计
    this.stats.totalReceived++;
    
    // 触发事件
    this.emit('resultReceived', {
      taskId,
      result: normalizedResult,
      agentId,
      metadata
    });
    
    // 处理结果
    this._processResult(taskId);
    
    return true;
  }
  
  /**
   * 处理结果
   */
  _processResult(taskId) {
    const result = this.results.get(taskId);
    if (!result) return;
    
    // 去重处理
    let deduplicatedResult = result;
    if (this.config.enableDeduplication) {
      deduplicatedResult = this._deduplicateResult(taskId, result);
    }
    
    // 质量评估
    if (this.config.enableQualityAssessment) {
      this._assessQuality(taskId, deduplicatedResult);
    }
    
    // 结果聚合
    if (this.config.enableAggregation) {
      this._aggregateResults(taskId, deduplicatedResult);
    }
    
    // 更新统计
    this.stats.totalProcessed++;
    
    // 触发处理完成事件
    this.emit('resultProcessed', {
      taskId,
      result: deduplicatedResult,
      processingTime: Date.now() - result.timestamp
    });
  }
  
  /**
   * 标准化结果格式
   */
  _normalizeResult(result, taskId, agentId, metadata) {
    const normalized = {
      id: taskId,
      content: result.content || '',
      summary: result.summary || '',
      output: result.output || result.content || '',
      type: result.type || 'unknown',
      agentId,
      timestamp: Date.now(),
      metadata: {
        ...metadata,
        source: metadata.source || 'agent',
        priority: metadata.priority || 'medium'
      },
      quality: {
        completeness: 0,
        accuracy: 0,
        consistency: 0,
        relevance: 0,
        score: 0
      },
      tags: result.tags || [],
      attachments: result.attachments || []
    };
    
    // 计算结果大小
    normalized.size = JSON.stringify(normalized).length;
    
    return normalized;
  }
  
  /**
   * 结果去重
   */
  _deduplicateResult(taskId, result) {
    // 检查是否与现有结果相似
    const similarResults = this._findSimilarResults(result);
    
    if (similarResults.length > 0) {
      // 找到最相似的现有结果
      const bestMatch = similarResults[0];
      const existingTaskId = bestMatch.taskId;
      const existingResult = this.results.get(existingTaskId);
      
      // 合并结果
      const mergedResult = this._mergeResults(existingResult, result);
      
      // 标记为已去重
      mergedResult.metadata.deduplicated = true;
      mergedResult.metadata.deduplicatedFrom = [taskId, existingTaskId];
      
      // 更新现有结果
      this.results.set(existingTaskId, mergedResult);
      this.resultMetadata.set(existingTaskId, {
        ...this.resultMetadata.get(existingTaskId),
        merged: true,
        mergedTasks: [taskId, existingTaskId]
      });
      
      // 删除原始结果
      this.results.delete(taskId);
      this.resultMetadata.delete(taskId);
      
      // 更新统计
      this.stats.totalDeduplicated++;
      
      // 触发去重事件
      this.emit('resultDeduplicated', {
        originalTaskId: taskId,
        deduplicatedToTaskId: existingTaskId,
        similarity: bestMatch.similarity
      });
      
      return mergedResult;
    }
    
    return result;
  }
  
  /**
   * 查找相似结果
   */
  _findSimilarResults(targetResult) {
    const similarResults = [];
    
    for (const [taskId, existingResult] of this.results) {
      const similarity = this._calculateSimilarity(existingResult, targetResult);
      
      if (similarity >= this.similarityThreshold) {
        similarResults.push({
          taskId,
          similarity,
          result: existingResult
        });
      }
    }
    
    // 按相似度排序
    similarResults.sort((a, b) => b.similarity - a.similarity);
    
    return similarResults;
  }
  
  /**
   * 计算结果相似度
   */
  _calculateSimilarity(result1, result2) {
    // 简单的文本相似度计算
    const content1 = (result1.content || '').toLowerCase();
    const content2 = (result2.content || '').toLowerCase();
    
    if (content1 === content2) return 1.0;
    
    // 使用简单的词汇重叠
    const words1 = new Set(content1.split(/\s+/));
    const words2 = new Set(content2.split(/\s+/));
    
    const intersection = new Set([...words1].filter(word => words2.has(word)));
    const union = new Set([...words1, ...words2]);
    
    return intersection.size / union.size;
  }
  
  /**
   * 合并结果
   */
  _mergeResults(result1, result2) {
    const merged = {
      ...result1,
      content: `${result1.content}\n\n${result2.content}`,
      summary: result1.summary || result2.summary || '',
      output: `${result1.output}\n\n${result2.output}`,
      agentIds: [result1.agentId, result2.agentId],
      timestamp: Math.max(result1.timestamp, result2.timestamp),
      metadata: {
        ...result1.metadata,
        merged: true,
        mergeTime: Date.now()
      },
      tags: [...new Set([...(result1.tags || []), ...(result2.tags || [])])],
      attachments: [...new Set([...(result1.attachments || []), ...(result2.attachments || [])])]
    };
    
    // 重新计算质量分数
    merged.quality.score = (merged.quality.completeness + merged.quality.accuracy + 
                           merged.quality.consistency + merged.quality.relevance) / 4;
    
    return merged;
  }
  
  /**
   * 质量评估
   */
  _assessQuality(taskId, result) {
    const quality = {
      completeness: this._calculateCompleteness(result),
      accuracy: this._calculateAccuracy(result),
      consistency: this._calculateConsistency(result),
      relevance: this._calculateRelevance(result)
    };
    
    // 计算总体质量分数
    quality.score = (quality.completeness + quality.accuracy + quality.consistency + quality.relevance) / 4;
    
    result.quality = quality;
    
    // 更新平均质量指标
    this._updateAverageQuality(quality);
  }
  
  /**
   * 计算完整性
   */
  _calculateCompleteness(result) {
    const content = (result.content || '').length;
    const expectedLength = 500; // 预期最小长度
    return Math.min(1, content / expectedLength);
  }
  
  /**
   * 计算准确性
   */
  _calculateAccuracy(result) {
    // 简单的准确性评估 - 实际项目中应该使用更复杂的算法
    const hasValidContent = result.content && result.content.length > 50;
    const hasValidStructure = result.type && result.type !== 'unknown';
    const hasAgentId = result.agentId && result.agentId !== '';
    
    return (hasValidContent ? 0.4 : 0) + (hasValidStructure ? 0.3 : 0) + (hasAgentId ? 0.3 : 0);
  }
  
  /**
   * 计算一致性
   */
  _calculateConsistency(result) {
    // 检查结果内部的一致性
    const hasValidFormat = result.type && result.content;
    const hasValidMetadata = result.metadata && result.metadata.source;
    const hasValidTimestamp = result.timestamp;
    
    return (hasValidFormat ? 0.5 : 0) + (hasValidMetadata ? 0.3 : 0) + (hasValidTimestamp ? 0.2 : 0);
  }
  
  /**
   * 计算相关性
   */
  _calculateRelevance(result) {
    // 根据任务类型和内容计算相关性
    const content = (result.content || '').toLowerCase();
    const typeRelevance = this._getTypeRelevance(result.type);
    const contentRelevance = this._getContentRelevance(content);
    
    return (typeRelevance * 0.6) + (contentRelevance * 0.4);
  }
  
  /**
   * 获取类型相关性
   */
  _getTypeRelevance(type) {
    const relevantTypes = ['code', 'analysis', 'design', 'documentation'];
    return relevantTypes.includes(type) ? 1.0 : 0.5;
  }
  
  /**
   * 获取内容相关性
   */
  _getContentRelevance(content) {
    const relevantKeywords = ['solution', 'analysis', 'design', 'code', 'documentation'];
    const foundKeywords = relevantKeywords.filter(keyword => content.includes(keyword));
    return foundKeywords.length / relevantKeywords.length;
  }
  
  /**
   * 更新平均质量指标
   */
  _updateAverageQuality(quality) {
    const count = this.stats.totalProcessed + 1;
    
    this.qualityMetrics.completeness = 
      (this.qualityMetrics.completeness * (count - 1) + quality.completeness) / count;
    this.qualityMetrics.accuracy = 
      (this.qualityMetrics.accuracy * (count - 1) + quality.accuracy) / count;
    this.qualityMetrics.consistency = 
      (this.qualityMetrics.consistency * (count - 1) + quality.consistency) / count;
    this.qualityMetrics.relevance = 
      (this.qualityMetrics.relevance * (count - 1) + quality.relevance) / count;
  }
  
  /**
   * 结果聚合
   */
  _aggregateResults(taskId, result) {
    // 查找相同类型的结果
    const sameTypeResults = [];
    
    for (const [otherTaskId, otherResult] of this.results) {
      if (otherTaskId !== taskId && otherResult.type === result.type) {
        sameTypeResults.push(otherResult);
      }
    }
    
    // 如果有相同类型的结果，进行聚合
    if (sameTypeResults.length > 0) {
      const aggregatedResult = this._aggregateWithType(result, sameTypeResults);
      
      // 更新统计
      this.stats.totalAggregated++;
      
      // 触发聚合事件
      this.emit('resultsAggregated', {
        aggregatedCount: sameTypeResults.length + 1,
        result: aggregatedResult
      });
      
      return aggregatedResult;
    }
    
    return result;
  }
  
  /**
   * 按类型聚合结果
   */
  _aggregateWithType(result, sameTypeResults) {
    const allResults = [result, ...sameTypeResults];
    
    const aggregated = {
      id: `aggregated_${Date.now()}`,
      content: allResults.map(r => r.content).filter(c => c).join('\n\n---\n\n'),
      summary: this._generateSummary(allResults),
      output: allResults.map(r => r.output).filter(o => o).join('\n\n'),
      type: result.type,
      agentIds: allResults.map(r => r.agentId),
      timestamp: Date.now(),
      metadata: {
        ...result.metadata,
        aggregated: true,
        aggregatedFrom: allResults.map(r => r.id),
        aggregateCount: allResults.length
      },
      tags: [...new Set(allResults.flatMap(r => r.tags || []))],
      attachments: [...new Set(allResults.flatMap(r => r.attachments || []))],
      quality: this._calculateAggregatedQuality(allResults)
    };
    
    return aggregated;
  }
  
  /**
   * 生成汇总摘要
   */
  _generateSummary(results) {
    // 简单的摘要生成 - 实际项目中应该使用更复杂的算法
    const summaries = results.map(r => r.summary || r.content.substring(0, 100));
    const uniqueSummaries = [...new Set(summaries)];
    return uniqueSummaries.slice(0, 3).join(' | ');
  }
  
  /**
   * 计算聚合质量
   */
  _calculateAggregatedQuality(results) {
    const avgQuality = {
      completeness: results.reduce((sum, r) => sum + r.quality.completeness, 0) / results.length,
      accuracy: results.reduce((sum, r) => sum + r.quality.accuracy, 0) / results.length,
      consistency: results.reduce((sum, r) => sum + r.quality.consistency, 0) / results.length,
      relevance: results.reduce((sum, r) => sum + r.quality.relevance, 0) / results.length,
      score: results.reduce((sum, r) => sum + r.quality.score, 0) / results.length
    };
    
    return avgQuality;
  }
  
  /**
   * 更新Agent映射
   */
  _updateAgentMapping(agentId, taskId) {
    if (!this.resultsByAgent.has(agentId)) {
      this.resultsByAgent.set(agentId, []);
    }
    this.resultsByAgent.get(agentId).push(taskId);
  }
  
  /**
   * 更新类型映射
   */
  _updateTypeMapping(type, taskId) {
    if (!this.resultsByType.has(type)) {
      this.resultsByType.set(type, []);
    }
    this.resultsByType.get(type).push(taskId);
    
    // 更新类型统计
    if (!this.stats.typeBreakdown[type]) {
      this.stats.typeBreakdown[type] = 0;
    }
    this.stats.typeBreakdown[type]++;
  }
  
  /**
   * 获取结果
   */
  getResult(taskId) {
    return this.results.get(taskId);
  }
  
  /**
   * 获取所有结果
   */
  getAllResults() {
    return Array.from(this.results.values());
  }
  
  /**
   * 按Agent获取结果
   */
  getResultsByAgent(agentId) {
    const taskIds = this.resultsByAgent.get(agentId) || [];
    return taskIds.map(taskId => this.results.get(taskId)).filter(Boolean);
  }
  
  /**
   * 按类型获取结果
   */
  getResultsByType(type) {
    const taskIds = this.resultsByType.get(type) || [];
    return taskIds.map(taskId => this.results.get(taskId)).filter(Boolean);
  }
  
  /**
   * 获取高质量结果
   */
  getHighQualityResults(minScore = 0.8) {
    return this.getAllResults().filter(result => 
      result.quality && result.quality.score >= minScore
    );
  }
  
  /**
   * 获取失败结果
   */
  getFailedResults() {
    return Array.from(this.failedResults.values());
  }
  
  /**
   * 生成报告
   */
  generateReport() {
    const status = this.getStatus();
    
    return {
      summary: {
        totalResults: this.results.size,
        successRate: this.stats.successRate,
        averageQuality: this.calculateAverageQuality(),
        processingTime: this.calculateAverageProcessingTime()
      },
      qualityMetrics: this.qualityMetrics,
      statistics: this.stats,
      byType: this.stats.typeBreakdown,
      status: status,
      timestamp: new Date()
    };
  }
  
  /**
   * 获取状态
   */
  getStatus() {
    return {
      totalResults: this.results.size,
      failedResults: this.failedResults.size,
      agentsActive: this.resultsByAgent.size,
      typesActive: this.resultsByType.size,
      isProcessing: this.results.size > 0,
      timestamp: new Date()
    };
  }
  
  /**
   * 计算平均质量分数
   */
  calculateAverageQuality() {
    if (this.results.size === 0) return 0;
    
    const totalQuality = Array.from(this.results.values())
      .reduce((sum, result) => sum + (result.quality?.score || 0), 0);
    
    return totalQuality / this.results.size;
  }
  
  /**
   * 计算平均处理时间
   */
  calculateAverageProcessingTime() {
    // 简化实现 - 实际项目中应该记录每个结果的处理时间
    return 1000; // 默认1秒
  }
  
  /**
   * 清理过期结果
   */
  cleanup(maxAge = 86400000) { // 默认24小时
    const cutoff = Date.now() - maxAge;
    const expiredResults = [];
    
    for (const [taskId, result] of this.results) {
      if (result.timestamp < cutoff) {
        expiredResults.push(taskId);
      }
    }
    
    // 删除过期结果
    for (const taskId of expiredResults) {
      this.removeResult(taskId);
    }
    
    return expiredResults.length;
  }
  
  /**
   * 移除结果
   */
  removeResult(taskId) {
    const result = this.results.get(taskId);
    if (!result) return false;
    
    // 从结果列表中移除
    this.results.delete(taskId);
    this.resultMetadata.delete(taskId);
    
    // 从Agent映射中移除
    for (const [agentId, taskIds] of this.resultsByAgent) {
      const index = taskIds.indexOf(taskId);
      if (index !== -1) {
        taskIds.splice(index, 1);
        if (taskIds.length === 0) {
          this.resultsByAgent.delete(agentId);
        }
      }
    }
    
    // 从类型映射中移除
    for (const [type, taskIds] of this.resultsByType) {
      const index = taskIds.indexOf(taskId);
      if (index !== -1) {
        taskIds.splice(index, 1);
        if (taskIds.length === 0) {
          this.resultsByType.delete(type);
        }
      }
    }
    
    this.emit('resultRemoved', { taskId, result });
    return true;
  }
  
  /**
   * 导出结果
   */
  exportResults(format = 'json') {
    const results = this.getAllResults();
    
    switch (format) {
      case 'json':
        return JSON.stringify(results, null, 2);
        
      case 'csv':
        return this._exportToCSV(results);
        
      case 'summary':
        return this.generateReport();
        
      default:
        throw new Error(`Unsupported export format: ${format}`);
    }
  }
  
  /**
   * 导出为CSV
   */
  _exportToCSV(results) {
    const headers = [
      'taskId', 'type', 'agentId', 'timestamp', 
      'qualityScore', 'completeness', 'accuracy', 
      'consistency', 'relevance', 'contentLength'
    ];
    
    const rows = results.map(result => [
      result.id,
      result.type,
      result.agentId,
      new Date(result.timestamp).toISOString(),
      result.quality?.score || 0,
      result.quality?.completeness || 0,
      result.quality?.accuracy || 0,
      result.quality?.consistency || 0,
      result.quality?.relevance || 0,
      result.content.length
    ]);
    
    return [headers, ...rows].map(row => row.join(',')).join('\n');
  }
}

module.exports = ResultCollector;