/**
 * 自组织团队协议系统 (Self-Organization Team Protocol)
 * Phase 3: 动态 Agent 创建和智能组队
 * 
 * 核心组件：
 * 1. TaskComplexityAnalyzer - 任务复杂度分析器
 * 2. DynamicAgentGenerator - 动态 Agent 生成器
 * 3. SelfOrganizationProtocol - 自组织协议引擎
 * 4. TeamDissolutionManager - 团队解散管理器
 * 
 * 智能组队策略：
 * - 简单任务 → 单个专家处理
 * - 中等任务 → 2-3 个专家协作
 * - 复杂任务 → 创建新的专门 Agent + 团队协作
 * - 超复杂任务 → 多个专门 Agent + 协调器
 */

class TaskComplexityAnalyzer {
    /**
     * 任务复杂度分析器
     * 根据任务特征自动评估复杂度等级
     */
    
    constructor(config = {}) {
        this.config = {
            maxIterations: 10,
            confidenceThreshold: 0.8,
            ...config
        };
        
        // 复杂度权重配置
        this.complexityWeights = {
            taskLength: 0.2,        // 任务描述长度
            technicalTerms: 0.3,    // 技术术语数量
            domainComplexity: 0.2,  // 领域复杂度
            scope: 0.2,            // 任务范围
            dependencies: 0.1      // 依赖关系
        };
        
        // 技术术语库
        this.technicalTerms = {
            programming: ['开发', '编程', 'code', 'script', 'algorithm', '算法', 'api', '接口', 'database', '数据库', 'framework', '框架', 'debug', '调试', 'deploy', '部署', 'test', '测试', 'refactor', '重构'],
            design: ['设计', 'design', 'ui', '用户界面', 'ux', '用户体验', 'frontend', '前端', 'backend', '后端', 'responsive', '响应式', 'prototype', '原型', 'mockup', '模型', 'wireframe', '线框图'],
            data: ['数据', 'data', 'analysis', '分析', 'visualization', '可视化', 'statistics', '统计', 'machine learning', '机器学习', 'model', '模型', 'dataset', '数据集', 'query', '查询'],
            system: ['系统', 'system', 'architecture', '架构', 'integration', '集成', 'optimization', '优化', 'performance', '性能', 'security', '安全', 'scalability', '可扩展性']
        };
        
        // 领域复杂度映射
        this.domainComplexity = {
            'simple': { weight: 1.0, tasks: ['todo', 'note', 'reminder', 'simple', '更新', '修改'] },
            'moderate': { weight: 2.0, tasks: ['update', 'modify', 'create', 'design', 'develop', '开发', '创建', '设计'] },
            'complex': { weight: 3.0, tasks: ['integrate', 'optimize', 'analyze', 'implement', 'architecture', '集成', '优化', '分析', '实现', '架构'] },
            'expert': { weight: 4.0, tasks: ['architect', 'scale', 'secure', 'automate', 'optimize', '架构设计', '扩展', '安全', '自动化'] }
        };
    }
    
    /**
     * 分析任务复杂度
     * @param {Object} task - 任务对象
     * @returns {Object} - 复杂度分析结果
     */
    async analyzeTask(task) {
        console.log(`🔍 开始分析任务复杂度: ${task.title || '无标题任务'}`);
        
        const taskText = (task.description || task.title || '').toLowerCase();
        const complexityScore = await this.calculateComplexityScore(taskText);
        const complexityLevel = this.determineComplexityLevel(complexityScore);
        const recommendedTeam = this.recommendTeamSize(complexityLevel);
        const requiredSkills = this.extractRequiredSkills(taskText);
        
        const analysisResult = {
            taskId: task.id || Date.now().toString(),
            taskTitle: task.title || '无标题任务',
            taskDescription: task.description || '',
            complexityScore: complexityScore,
            complexityLevel: complexityLevel,
            recommendedTeam: recommendedTeam,
            requiredSkills: requiredSkills,
            analysisTime: new Date().toISOString(),
            confidence: this.calculateConfidence(taskText)
        };
        
        console.log(`✅ 任务复杂度分析完成 - 等级: ${complexityLevel}, 推荐团队: ${recommendedTeam.size}人`);
        return analysisResult;
    }
    
    /**
     * 计算复杂度分数
     */
    async calculateComplexityScore(taskText) {
        let score = 0;
        
        // 1. 任务长度权重
        const lengthScore = Math.min(taskText.length / 200, 1) * this.complexityWeights.taskLength * 100;
        score += lengthScore;
        
        // 2. 技术术语数量
        const technicalTermScore = this.countTechnicalTerms(taskText) * this.complexityWeights.technicalTerms * 10;
        score += technicalTermScore;
        
        // 3. 领域复杂度
        const domainScore = this.calculateDomainComplexity(taskText) * this.complexityWeights.domainComplexity * 25;
        score += domainScore;
        
        // 4. 任务范围
        const scopeScore = this.calculateTaskScope(taskText) * this.complexityWeights.scope * 20;
        score += scopeScore;
        
        // 5. 依赖关系
        const dependencyScore = this.countDependencies(taskText) * this.complexityWeights.dependencies * 15;
        score += dependencyScore;
        
        console.log(`复杂度计算详情 - 长度: ${lengthScore}, 术语: ${technicalTermScore}, 领域: ${domainScore}, 范围: ${scopeScore}, 依赖: ${dependencyScore}, 总分: ${Math.min(Math.round(score), 100)}`);
        
        return Math.min(Math.round(score), 100);
    }
    
    /**
     * 计算技术术语数量
     */
    countTechnicalTerms(taskText) {
        let count = 0;
        let matchedTerms = [];
        
        Object.values(this.technicalTerms).forEach(terms => {
            terms.forEach(term => {
                // 简单的包含检查，对于中文更有效
                if (taskText.includes(term)) {
                    count++;
                    matchedTerms.push(term);
                }
            });
        });
        
        console.log(`技术术语匹配: ${count} 个 - ${matchedTerms.join(', ')}`);
        return count;
    }
    
    /**
     * 计算领域复杂度
     */
    calculateDomainComplexity(taskText) {
        let maxComplexity = 1.0;
        let matchedDomains = [];
        
        Object.entries(this.domainComplexity).forEach(([domain, config]) => {
            config.tasks.forEach(task => {
                if (taskText.includes(task)) {
                    maxComplexity = Math.max(maxComplexity, config.weight);
                    matchedDomains.push(`${domain}(${config.weight})`);
                }
            });
        });
        
        console.log(`领域复杂度: ${maxComplexity} - ${matchedDomains.join(', ')}`);
        return maxComplexity;
    }
    
    /**
     * 计算任务范围
     */
    calculateTaskScope(taskText) {
        const scopeIndicators = ['all', 'entire', 'complete', 'comprehensive', 'full', 'global'];
        let scopeScore = 1.0;
        
        scopeIndicators.forEach(indicator => {
            if (taskText.includes(indicator)) {
                scopeScore += 0.5;
            }
        });
        
        return Math.min(scopeScore, 4.0);
    }
    
    /**
     * 计算依赖数量
     */
    countDependencies(taskText) {
        const dependencyWords = ['require', 'depend', 'need', 'based on', 'integrate with', 'connect to'];
        let count = 0;
        
        dependencyWords.forEach(word => {
            if (taskText.includes(word)) {
                count++;
            }
        });
        
        return count;
    }
    
    /**
     * 确定复杂度等级
     */
    determineComplexityLevel(score) {
        if (score <= 20) return 'simple';
        if (score <= 40) return 'moderate';
        if (score <= 70) return 'complex';
        return 'expert';
    }
    
    /**
     * 推荐团队规模
     */
    recommendTeamSize(complexityLevel) {
        const teamConfig = {
            'simple': { size: 1, description: '单个专家处理', coordinator: false },
            'moderate': { size: 2, description: '2个专家协作', coordinator: false },
            'complex': { size: 3, description: '3个专家协作', coordinator: true },
            'expert': { size: 5, description: '5个专家协作', coordinator: true }
        };
        
        return teamConfig[complexityLevel];
    }
    
    /**
     * 提取所需技能
     */
    extractRequiredSkills(taskText) {
        const skills = [];
        
        Object.entries(this.technicalTerms).forEach(([domain, terms]) => {
            const matchingTerms = terms.filter(term => taskText.includes(term));
            if (matchingTerms.length > 0) {
                skills.push({
                    domain: domain,
                    terms: matchingTerms,
                    priority: matchingTerms.length
                });
            }
        });
        
        // 按优先级排序
        return skills.sort((a, b) => b.priority - a.priority);
    }
    
    /**
     * 计算分析置信度
     */
    calculateConfidence(taskText) {
        const factors = [];
        
        // 任务长度因素
        if (taskText.length > 50) factors.push(0.3);
        else factors.push(0.1);
        
        // 技术术语因素
        const termCount = this.countTechnicalTerms(taskText);
        if (termCount > 0) factors.push(Math.min(termCount * 0.1, 0.3));
        else factors.push(0.1);
        
        // 复杂度因素
        const domainCount = Object.keys(this.domainComplexity).filter(domain => 
            this.domainComplexity[domain].tasks.some(task => taskText.includes(task))
        ).length;
        factors.push(Math.min(domainCount * 0.2, 0.4));
        
        return Math.min(factors.reduce((sum, factor) => sum + factor, 0), 1.0);
    }
}

module.exports = TaskComplexityAnalyzer;