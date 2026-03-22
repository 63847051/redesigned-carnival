#!/usr/bin/env node

/**
 * 自组织团队协议系统 - 主程序
 * 
 * 整合以下组件：
 * 1. TaskComplexityAnalyzer - 任务复杂度分析器
 * 2. DynamicAgentGenerator - 动态 Agent 生成器
 * 3. SelfOrganizationProtocol - 自组织协议引擎
 * 4. TeamDissolutionManager - 团队解散管理器
 * 
 * 功能特性：
 * - 智能任务复杂度分析
 * - 动态 Agent 创建和组队
 * - 自动任务分配和执行
 * - 智能团队解散和清理
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

// 导入核心组件
const TaskComplexityAnalyzer = require('./TaskComplexityAnalyzer');
const DynamicAgentGenerator = require('./DynamicAgentGenerator');
const SelfOrganizationProtocol = require('./SelfOrganizationProtocol');
const TeamDissolutionManager = require('./TeamDissolutionManager');

class SelfOrganizationOrchestrator {
    constructor(config = {}) {
        this.config = {
            logLevel: 'info',
            enableConsole: true,
            enableFileLogging: true,
            logFile: './self-organization.log',
            enableMetrics: true,
            enablePerformanceTracking: true,
            ...config
        };
        
        // 初始化核心组件
        this.taskAnalyzer = new TaskComplexityAnalyzer(this.config);
        this.agentGenerator = new DynamicAgentGenerator(this.config);
        this.selfOrganizationProtocol = new SelfOrganizationProtocol(this.config);
        this.teamManager = new TeamDissolutionManager(this.config);
        
        // 系统状态
        this.state = {
            running: false,
            startTime: null,
            lastActivity: null,
            totalTasksProcessed: 0,
            totalTeamsCreated: 0,
            totalTeamsDissolved: 0,
            averageTaskComplexity: 0
        };
        
        // 事件监听器
        this.eventListeners = new Map();
        
        // 启动日志系统
        this.initLogging();
    }
    
    /**
     * 初始化日志系统
     */
    initLogging() {
        if (this.config.enableFileLogging && !fs.existsSync(this.config.logFile)) {
            fs.writeFileSync(this.config.logFile, '');
        }
    }
    
    /**
     * 记录日志
     */
    log(level, message, data = null) {
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            level,
            message,
            data,
            pid: process.pid
        };
        
        const logMessage = `[${timestamp}] ${level.toUpperCase()}: ${message}`;
        
        if (this.config.enableConsole) {
            console.log(logMessage);
        }
        
        if (this.config.enableFileLogging) {
            fs.appendFileSync(this.config.logFile, JSON.stringify(logEntry) + '\n');
        }
        
        if (level === 'error') {
            console.error('🚨 ERROR:', message);
        } else if (level === 'warn') {
            console.warn('⚠️  WARNING:', message);
        } else if (level === 'info') {
            console.log('ℹ️  INFO:', message);
        } else if (level === 'debug') {
            console.log('🔍 DEBUG:', message);
        }
    }
    
    /**
     * 启动自组织系统
     */
    async start() {
        console.log('🚀 启动自组织团队协议系统...');
        
        try {
            // 1. 启动协议引擎
            await this.selfOrganizationProtocol.start();
            this.log('info', '自组织协议引擎已启动');
            
            // 2. 启动团队管理器
            await this.teamManager.start();
            this.log('info', '团队解散管理器已启动');
            
            // 3. 启动监控循环
            this.startMonitoring();
            
            // 4. 设置系统状态
            this.state.running = true;
            this.state.startTime = Date.now();
            this.state.lastActivity = Date.now();
            
            this.log('info', '自组织团队协议系统启动完成');
            this.log('info', `系统配置: ${JSON.stringify(this.config, null, 2)}`);
            
            // 5. 显示系统状态
            this.displaySystemStatus();
            
            return { success: true, message: 'System started successfully' };
            
        } catch (error) {
            this.log('error', `系统启动失败: ${error.message}`, { error: error.stack });
            return { success: false, error: error.message };
        }
    }
    
    /**
     * 停止系统
     */
    async stop() {
        console.log('🛑 停止自组织团队协议系统...');
        
        try {
            // 1. 停止监控循环
            this.stopMonitoring();
            
            // 2. 清理活跃团队
            await this.cleanupAllTeams();
            
            // 3. 更新系统状态
            this.state.running = false;
            
            this.log('info', '自组织团队协议系统已停止');
            return { success: true, message: 'System stopped successfully' };
            
        } catch (error) {
            this.log('error', `系统停止失败: ${error.message}`, { error: error.stack });
            return { success: false, error: error.message };
        }
    }
    
    /**
     * 处理任务
     */
    async processTask(task) {
        this.log('info', `开始处理任务: ${task.title || '无标题任务'}`);
        
        try {
            // 更新活动时间
            this.state.lastActivity = Date.now();
            this.state.totalTasksProcessed++;
            
            // 1. 任务复杂度分析
            this.log('debug', '分析任务复杂度...');
            const complexityAnalysis = await this.taskAnalyzer.analyzeTask(task);
            this.log('info', `任务复杂度: ${complexityAnalysis.complexityLevel} (${complexityAnalysis.complexityScore}/100)`);
            
            // 2. 注册团队
            this.log('debug', '注册团队...');
            const teamRecord = await this.teamManager.registerTeam({
                id: `team_${Date.now()}`,
                name: `Team_${task.title?.slice(0, 20) || 'unnamed'}_${Date.now().toString().slice(-4)}`,
                members: [],
                leader: null,
                complexity: complexityAnalysis.complexityLevel,
                createdAt: Date.now()
            });
            
            // 3. 创建动态 Agent 团队
            this.log('debug', '创建动态 Agent 团队...');
            const team = await this.agentGenerator.createTeam(complexityAnalysis, 1);
            this.log('info', `Agent 团队创建完成: ${team.members.length} 名成员`);
            
            // 4. 更新团队记录
            teamRecord.members = team.members;
            teamRecord.leader = team.leader;
            
            // 5. 处理任务请求
            this.log('debug', '处理任务请求...');
            const taskResult = await this.selfOrganizationProtocol.processTaskRequest({
                ...task,
                complexity: complexityAnalysis.complexityLevel,
                requiredSkills: complexityAnalysis.requiredSkills.map(s => s.skill),
                assignedTeam: teamRecord
            });
            
            // 6. 更新统计信息
            this.updateStatistics(complexityAnalysis);
            
            // 7. 触发任务完成事件
            this.emit('task_completed', {
                taskId: task.id,
                teamId: taskResult.teamId,
                complexity: complexityAnalysis,
                timestamp: Date.now()
            });
            
            this.log('info', `任务处理完成: ${task.id}`);
            return taskResult;
            
        } catch (error) {
            this.log('error', `任务处理失败: ${error.message}`, { error: error.stack, task });
            
            // 触发任务失败事件
            this.emit('task_failed', {
                taskId: task.id,
                error: error.message,
                timestamp: Date.now()
            });
            
            throw error;
        }
    }
    
    /**
     * 批量处理任务
     */
    async processTasks(tasks) {
        this.log('info', `开始批量处理 ${tasks.length} 个任务`);
        
        const results = [];
        const errors = [];
        
        for (const task of tasks) {
            try {
                const result = await this.processTask(task);
                results.push({ task: task.id, success: true, result });
            } catch (error) {
                results.push({ task: task.id, success: false, error: error.message });
                errors.push({ task: task.id, error: error.message });
            }
            
            // 添加延迟以避免过载
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        
        this.log('info', `批量处理完成: ${results.length} 个任务, ${errors.length} 个失败`);
        
        return {
            total: tasks.length,
            successful: results.filter(r => r.success).length,
            failed: errors.length,
            results,
            errors
        };
    }
    
    /**
     * 演示功能
     */
    async runDemo() {
        console.log('🎭 运行自组织团队协议演示...');
        
        try {
            // 创建示例任务
            const demoTasks = [
                {
                    id: 'demo_001',
                    title: '开发用户登录页面',
                    description: '创建一个响应式的用户登录页面，包含用户名和密码输入框，以及验证逻辑。',
                    priority: 'medium'
                },
                {
                    id: 'demo_002',
                    title: '设计API接口文档',
                    description: '为RESTful API设计完整的接口文档，包括所有端点的请求和响应格式。',
                    priority: 'high'
                },
                {
                    id: 'demo_003',
                    title: '优化数据库查询',
                    description: '分析现有查询性能，优化慢查询，添加适当的索引以提升数据库响应速度。',
                    priority: 'high'
                },
                {
                    id: 'demo_004',
                    title: '更新用户手册',
                    description: '更新用户手册的第一章节，添加新功能的说明和使用指南。',
                    priority: 'low'
                },
                {
                    id: 'demo_005',
                    title: '实现AI推荐算法',
                    description: '设计和实现一个基于机器学习的个性化推荐算法，能够根据用户行为分析推荐相关内容。',
                    priority: 'expert'
                }
            ];
            
            console.log(`📋 创建了 ${demoTasks.length} 个演示任务`);
            
            // 处理演示任务
            const results = await this.processTasks(demoTasks);
            
            // 显示结果摘要
            this.displayDemoResults(results);
            
            return results;
            
        } catch (error) {
            this.log('error', `演示运行失败: ${error.message}`, { error: error.stack });
            throw error;
        }
    }
    
    /**
     * 显示系统状态
     */
    displaySystemStatus() {
        const status = {
            running: this.state.running,
            uptime: this.state.startTime ? Date.now() - this.state.startTime : 0,
            totalTasksProcessed: this.state.totalTasksProcessed,
            totalTeamsCreated: this.state.totalTeamsCreated,
            totalTeamsDissolved: this.state.totalTeamsDissolved,
            averageTaskComplexity: this.state.averageTaskComplexity
        };
        
        console.log('\n📊 系统状态:');
        console.log('='.repeat(50));
        console.log(`运行状态: ${status.running ? '✅ 运行中' : '❌ 已停止'}`);
        console.log(`运行时间: ${Math.round(status.uptime / 1000 / 60)} 分钟`);
        console.log(`处理任务: ${status.totalTasksProcessed} 个`);
        console.log(`创建团队: ${status.totalTeamsCreated} 个`);
        console.log(`解散团队: ${status.totalTeamsDissolved} 个`);
        console.log(`平均复杂度: ${status.averageTaskComplexity.toFixed(1)}/100`);
        console.log('='.repeat(50));
    }
    
    /**
     * 显示演示结果
     */
    displayDemoResults(results) {
        console.log('\n🎯 演示结果:');
        console.log('='.repeat(50));
        console.log(`总任务数: ${results.total}`);
        console.log(`成功: ${results.successful} (${Math.round(results.successful/results.total*100)}%)`);
        console.log(`失败: ${results.failed} (${Math.round(results.failed/results.total*100)}%)`);
        
        console.log('\n📋 详细结果:');
        results.results.forEach((result, index) => {
            const status = result.success ? '✅' : '❌';
            console.log(`${index + 1}. ${status} 任务 ${result.task}: ${result.success ? '成功' : result.error}`);
        });
        
        console.log('='.repeat(50));
    }
    
    /**
     * 更新统计信息
     */
    updateStatistics(complexityAnalysis) {
        this.state.totalTeamsCreated++;
        
        // 更新平均复杂度
        const currentAverage = this.state.averageTaskComplexity;
        const newScore = complexityAnalysis.complexityScore;
        const totalProcessed = this.state.totalTasksProcessed;
        
        this.state.averageTaskComplexity = 
            (currentAverage * (totalProcessed - 1) + newScore) / totalProcessed;
    }
    
    /**
     * 启动监控循环
     */
    startMonitoring() {
        this.monitoringInterval = setInterval(() => {
            this.performHealthCheck();
            this.collectMetrics();
        }, 30000); // 每30秒检查一次
    }
    
    /**
     * 停止监控循环
     */
    stopMonitoring() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
        }
    }
    
    /**
     * 执行健康检查
     */
    async performHealthCheck() {
        try {
            // 检查核心组件状态
            const health = {
                timestamp: Date.now(),
                taskAnalyzer: this.taskAnalyzer ? 'healthy' : 'unhealthy',
                agentGenerator: this.agentGenerator ? 'healthy' : 'unhealthy',
                selfOrganizationProtocol: this.selfOrganizationProtocol ? 'healthy' : 'unhealthy',
                teamManager: this.teamManager ? 'healthy' : 'unhealthy',
                uptime: Date.now() - this.state.startTime,
                activeTeams: this.teamManager ? this.teamManager.getStatus().activeTeams : 0,
                totalTasks: this.state.totalTasksProcessed
            };
            
            this.log('debug', '健康检查完成', health);
            
        } catch (error) {
            this.log('warn', '健康检查失败', { error: error.message });
        }
    }
    
    /**
     * 收集指标
     */
    collectMetrics() {
        if (!this.config.enableMetrics) return;
        
        const metrics = {
            timestamp: Date.now(),
            tasksProcessed: this.state.totalTasksProcessed,
            teamsCreated: this.state.totalTeamsCreated,
            teamsDissolved: this.state.totalTeamsDissolved,
            averageComplexity: this.state.averageTaskComplexity,
            activeTeams: this.teamManager ? this.teamManager.getStatus().activeTeams : 0
        };
        
        this.log('debug', '收集性能指标', metrics);
    }
    
    /**
     * 清理所有团队
     */
    async cleanupAllTeams() {
        console.log('🧹 清理所有活跃团队...');
        
        try {
            if (this.teamManager) {
                const activeTeams = this.teamManager.getAllActiveTeams();
                this.log('info', `清理 ${activeTeams.length} 个活跃团队`);
                
                for (const team of activeTeams) {
                    await this.teamManager.dissolveTeam(team.teamId, 'system_shutdown');
                }
            }
            
            this.log('info', '所有团队清理完成');
            
        } catch (error) {
            this.log('error', '团队清理失败', { error: error.message });
        }
    }
    
    /**
     * 添加事件监听器
     */
    on(event, listener) {
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, []);
        }
        this.eventListeners.get(event).push(listener);
    }
    
    /**
     * 触发事件
     */
    emit(event, data) {
        if (this.eventListeners.has(event)) {
            this.eventListeners.get(event).forEach(listener => {
                try {
                    listener(data);
                } catch (error) {
                    this.log('error', `事件监听器失败: ${event}`, { error: error.message });
                }
            });
        }
    }
    
    /**
     * 获取系统信息
     */
    getSystemInfo() {
        return {
            version: '1.0.0',
            name: 'Self-Organization Team Protocol',
            description: '根据任务复杂度动态创建Agent，实现按需组建AI团队',
            components: {
                taskAnalyzer: 'TaskComplexityAnalyzer',
                agentGenerator: 'DynamicAgentGenerator',
                selfOrganizationProtocol: 'SelfOrganizationProtocol',
                teamManager: 'TeamDissolutionManager'
            },
            config: this.config,
            state: this.state
        };
    }
}

// 如果直接运行此文件，启动演示
if (require.main === module) {
    const orchestrator = new SelfOrganizationOrchestrator();
    
    // 启动系统
    orchestrator.start().then(() => {
        console.log('\n🎭 运行演示...\n');
        return orchestrator.runDemo();
    }).then(() => {
        console.log('\n🛑 停止系统...\n');
        return orchestrator.stop();
    }).then(() => {
        console.log('✅ 演示完成');
        process.exit(0);
    }).catch((error) => {
        console.error('❌ 演示失败:', error);
        process.exit(1);
    });
}

module.exports = SelfOrganizationOrchestrator;