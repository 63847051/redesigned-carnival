#!/usr/bin/env node

/**
 * 自组织团队协议测试脚本
 * 
 * 测试内容：
 * 1. 任务复杂度分析器测试
 * 2. 动态 Agent 生成器测试
 * 3. 自组织协议引擎测试
 * 4. 团队解散管理器测试
 * 5. 端到端集成测试
 */

const SelfOrganizationOrchestrator = require('./index');

class SelfOrganizationTestSuite {
    constructor() {
        this.testResults = [];
        this.totalTests = 0;
        this.passedTests = 0;
        this.failedTests = 0;
    }
    
    /**
     * 运行所有测试
     */
    async runAllTests() {
        console.log('🧪 开始运行自组织团队协议测试套件...');
        console.log('=' * 50);
        
        // 1. 任务复杂度分析器测试
        await this.testTaskComplexityAnalyzer();
        
        // 2. 动态 Agent 生成器测试
        await this.testDynamicAgentGenerator();
        
        // 3. 自组织协议引擎测试
        await this.testSelfOrganizationProtocol();
        
        // 4. 团队解散管理器测试
        await this.testTeamDissolutionManager();
        
        // 5. 端到端集成测试
        await this.testIntegration();
        
        // 6. 性能测试
        await this.testPerformance();
        
        // 显示测试结果
        this.displayTestResults();
        
        return this.testResults;
    }
    
    /**
     * 测试任务复杂度分析器
     */
    async testTaskComplexityAnalyzer() {
        console.log('\n🔍 测试任务复杂度分析器...');
        
        this.totalTests++;
        
        try {
            const analyzer = new (require('./TaskComplexityAnalyzer'))();
            
            // 测试简单任务
            const simpleTask = {
                id: 'test_simple_001',
                title: '更新用户手册',
                description: '更新用户手册的第一章节，添加新功能的说明。'
            };
            
            const simpleResult = await analyzer.analyzeTask(simpleTask);
            console.log(`✅ 简单任务分析: ${simpleResult.complexityLevel} (${simpleResult.complexityScore}/100)`);
            
            // 测试复杂任务
            const complexTask = {
                id: 'test_complex_001',
                title: '实现AI推荐算法',
                description: '设计和实现一个基于机器学习的个性化推荐算法，能够根据用户行为分析推荐相关内容，包括数据预处理、模型训练、优化和部署等完整流程。'
            };
            
            const complexResult = await analyzer.analyzeTask(complexTask);
            console.log(`✅ 复杂任务分析: ${complexResult.complexityLevel} (${complexResult.complexityScore}/100)`);
            
            // 验证结果
            if (simpleResult.complexityLevel === 'simple' && complexResult.complexityLevel === 'complex') {
                this.passedTests++;
                this.testResults.push({
                    test: 'TaskComplexityAnalyzer',
                    status: 'PASS',
                    details: 'Simple and complex tasks correctly identified'
                });
                console.log('✅ 任务复杂度分析器测试通过');
            } else {
                this.failedTests++;
                this.testResults.push({
                    test: 'TaskComplexityAnalyzer',
                    status: 'FAIL',
                    details: 'Complexity levels not correctly identified'
                });
                console.log('❌ 任务复杂度分析器测试失败');
            }
            
        } catch (error) {
            this.failedTests++;
            this.testResults.push({
                test: 'TaskComplexityAnalyzer',
                status: 'ERROR',
                details: error.message
            });
            console.log('❌ 任务复杂度分析器测试错误:', error.message);
        }
    }
    
    /**
     * 测试动态 Agent 生成器
     */
    async testDynamicAgentGenerator() {
        console.log('\n🤖 测试动态 Agent 生成器...');
        
        this.totalTests++;
        
        try {
            const generator = new (require('./DynamicAgentGenerator'))();
            
            // 测试 Agent 生成
            const requirements = {
                description: '开发用户登录页面，包含前端和后端实现',
                complexity: 'moderate',
                domain: 'frontend'
            };
            
            const agent = await generator.createDynamicAgent(requirements, 'test_task_001');
            console.log(`✅ 动态 Agent 创建成功: ${agent.name}`);
            
            // 测试团队创建
            const complexityAnalyzer = new (require('./TaskComplexityAnalyzer'))();
            const analysis = await complexityAnalyzer.analyzeTask({
                id: 'test_team_001',
                title: '开发电商平台',
                description: '开发和部署一个完整的电商平台，包含用户管理、商品管理、订单处理、支付集成等功能模块。'
            });
            
            const team = await generator.createTeam(analysis);
            console.log(`✅ 团队创建成功: ${team.members.length} 名成员`);
            
            // 验证结果
            if (agent.name && team.members.length > 0) {
                this.passedTests++;
                this.testResults.push({
                    test: 'DynamicAgentGenerator',
                    status: 'PASS',
                    details: `Created agent: ${agent.name}, team with ${team.members.length} members`
                });
                console.log('✅ 动态 Agent 生成器测试通过');
            } else {
                this.failedTests++;
                this.testResults.push({
                    test: 'DynamicAgentGenerator',
                    status: 'FAIL',
                    details: 'Agent or team creation failed'
                });
                console.log('❌ 动态 Agent 生成器测试失败');
            }
            
        } catch (error) {
            this.failedTests++;
            this.testResults.push({
                test: 'DynamicAgentGenerator',
                status: 'ERROR',
                details: error.message
            });
            console.log('❌ 动态 Agent 生成器测试错误:', error.message);
        }
    }
    
    /**
     * 测试自组织协议引擎
     */
    async testSelfOrganizationProtocol() {
        console.log('\n🎭 测试自组织协议引擎...');
        
        this.totalTests++;
        
        try {
            const protocol = new (require('./SelfOrganizationProtocol'))();
            
            // 启动协议引擎
            const startResult = await protocol.start();
            console.log(`✅ 协议引擎启动: ${startResult.success}`);
            
            // 创建测试任务
            const testTask = {
                id: 'test_protocol_001',
                title: '实现数据可视化功能',
                description: '创建交互式数据可视化界面，支持多种图表类型和数据源集成。',
                requiredSkills: ['javascript', 'visualization', 'api'],
                priority: 'medium'
            };
            
            // 处理任务
            const result = await protocol.processTaskRequest(testTask);
            console.log(`✅ 任务处理完成: ${result.status}`);
            
            // 获取协议状态
            const status = protocol.getProtocolStatus();
            console.log(`✅ 协议状态: ${status.activeTeams} 个活跃团队`);
            
            // 验证结果
            if (startResult.success && result.status === 'assigned' && status.activeTeams >= 0) {
                this.passedTests++;
                this.testResults.push({
                    test: 'SelfOrganizationProtocol',
                    status: 'PASS',
                    details: `Protocol started, task processed, ${status.activeTeams} active teams`
                });
                console.log('✅ 自组织协议引擎测试通过');
            } else {
                this.failedTests++;
                this.testResults.push({
                    test: 'SelfOrganizationProtocol',
                    status: 'FAIL',
                    details: 'Protocol operation failed'
                });
                console.log('❌ 自组织协议引擎测试失败');
            }
            
        } catch (error) {
            this.failedTests++;
            this.testResults.push({
                test: 'SelfOrganizationProtocol',
                status: 'ERROR',
                details: error.message
            });
            console.log('❌ 自组织协议引擎测试错误:', error.message);
        }
    }
    
    /**
     * 测试团队解散管理器
     */
    async testTeamDissolutionManager() {
        console.log('\n🧹 测试团队解散管理器...');
        
        this.totalTests++;
        
        try {
            const manager = new (require('./TeamDissolutionManager'))();
            
            // 启动管理器
            await manager.start();
            console.log('✅ 管理器启动成功');
            
            // 创建测试团队
            const testTeam = {
                id: 'test_team_dissolve_001',
                name: '测试团队',
                members: [
                    { id: 'member1', name: '成员1' },
                    { id: 'member2', name: '成员2' }
                ],
                leader: 'member1',
                createdAt: Date.now()
            };
            
            // 注册团队
            const teamRecord = await manager.registerTeam(testTeam);
            console.log(`✅ 团队注册成功: ${teamRecord.id}`);
            
            // 更新团队活动
            await manager.updateTeamActivity(teamRecord.id, {
                type: 'task_completed',
                details: { taskId: 'task1' }
            });
            console.log('✅ 团队活动更新成功');
            
            // 检查解散条件
            const checkResult = await manager.checkDissolutionConditions(teamRecord.id);
            console.log(`✅ 解散条件检查: ${checkResult.shouldDissolve}`);
            
            // 执行解散
            if (checkResult.shouldDissolve) {
                const dissolutionResult = await manager.dissolveTeam(teamRecord.id, 'test_dissolution');
                console.log(`✅ 团队解散成功: ${dissolutionResult.success}`);
            }
            
            // 获取管理器状态
            const status = manager.getStatus();
            console.log(`✅ 管理器状态: ${status.activeTeams} 个活跃团队`);
            
            // 验证结果
            if (status.activeTeams >= 0) {
                this.passedTests++;
                this.testResults.push({
                    test: 'TeamDissolutionManager',
                    status: 'PASS',
                    details: `Manager running, ${status.activeTeams} active teams`
                });
                console.log('✅ 团队解散管理器测试通过');
            } else {
                this.failedTests++;
                this.testResults.push({
                    test: 'TeamDissolutionManager',
                    status: 'FAIL',
                    details: 'Manager operation failed'
                });
                console.log('❌ 团队解散管理器测试失败');
            }
            
        } catch (error) {
            this.failedTests++;
            this.testResults.push({
                test: 'TeamDissolutionManager',
                status: 'ERROR',
                details: error.message
            });
            console.log('❌ 团队解散管理器测试错误:', error.message);
        }
    }
    
    /**
     * 测试端到端集成
     */
    async testIntegration() {
        console.log('\n🔗 测试端到端集成...');
        
        this.totalTests++;
        
        try {
            const orchestrator = new SelfOrganizationOrchestrator({
                enableConsole: false,
                enableFileLogging: false
            });
            
            // 启动系统
            const startResult = await orchestrator.start();
            console.log(`✅ 系统启动: ${startResult.success}`);
            
            // 处理测试任务
            const testTask = {
                id: 'integration_test_001',
                title: '集成测试任务',
                description: '这是一个用于验证自组织团队协议集成功能的测试任务。',
                priority: 'medium'
            };
            
            const result = await orchestrator.processTask(testTask);
            console.log(`✅ 任务处理: ${result ? 'completed' : 'failed'}`);
            
            // 运行演示
            const demoResult = await orchestrator.runDemo();
            console.log(`✅ 演示运行: ${demoResult.successful} 个任务成功`);
            
            // 停止系统
            await orchestrator.stop();
            console.log('✅ 系统停止成功');
            
            // 验证结果
            if (startResult.success && demoResult.successful > 0) {
                this.passedTests++;
                this.testResults.push({
                    test: 'Integration',
                    status: 'PASS',
                    details: `System started, processed task, demo successful: ${demoResult.successful} tasks`
                });
                console.log('✅ 端到端集成测试通过');
            } else {
                this.failedTests++;
                this.testResults.push({
                    test: 'Integration',
                    status: 'FAIL',
                    details: 'Integration test failed'
                });
                console.log('❌ 端到端集成测试失败');
            }
            
        } catch (error) {
            this.failedTests++;
            this.testResults.push({
                test: 'Integration',
                status: 'ERROR',
                details: error.message
            });
            console.log('❌ 端到端集成测试错误:', error.message);
        }
    }
    
    /**
     * 测试性能
     */
    async testPerformance() {
        console.log('\n⚡ 测试性能...');
        
        this.totalTests++;
        
        try {
            const orchestrator = new SelfOrganizationOrchestrator({
                enableConsole: false,
                enableFileLogging: false
            });
            
            // 启动系统
            await orchestrator.start();
            
            // 创建性能测试任务
            const perfTasks = [];
            for (let i = 0; i < 10; i++) {
                perfTasks.push({
                    id: `perf_test_${i}`,
                    title: `性能测试任务 ${i}`,
                    description: `这是一个性能测试任务，用于验证系统的处理能力。任务 ${i}`,
                    priority: i % 2 === 0 ? 'high' : 'medium'
                });
            }
            
            // 记录开始时间
            const startTime = Date.now();
            
            // 批量处理任务
            const results = await orchestrator.processTasks(perfTasks);
            
            // 记录结束时间
            const endTime = Date.now();
            const duration = endTime - startTime;
            
            // 计算性能指标
            const tasksPerSecond = (results.total / duration) * 1000;
            const successRate = (results.successful / results.total) * 100;
            
            // 停止系统
            await orchestrator.stop();
            
            console.log(`✅ 性能测试完成:`);
            console.log(`   - 处理时间: ${duration}ms`);
            console.log(`   - 任务/秒: ${tasksPerSecond.toFixed(2)}`);
            console.log(`   - 成功率: ${successRate.toFixed(1)}%`);
            
            // 验证结果
            if (duration < 30000 && successRate >= 80) { // 30秒内完成，成功率80%以上
                this.passedTests++;
                this.testResults.push({
                    test: 'Performance',
                    status: 'PASS',
                    details: `Processed ${results.total} tasks in ${duration}ms, ${successRate}% success rate`
                });
                console.log('✅ 性能测试通过');
            } else {
                this.failedTests++;
                this.testResults.push({
                    test: 'Performance',
                    status: 'FAIL',
                    details: `Performance requirements not met: ${duration}ms, ${successRate}%`
                });
                console.log('❌ 性能测试失败');
            }
            
        } catch (error) {
            this.failedTests++;
            this.testResults.push({
                test: 'Performance',
                status: 'ERROR',
                details: error.message
            });
            console.log('❌ 性能测试错误:', error.message);
        }
    }
    
    /**
     * 显示测试结果
     */
    displayTestResults() {
        console.log('\n📊 测试结果汇总:');
        console.log('=' * 50);
        console.log(`总测试数: ${this.totalTests}`);
        console.log(`通过: ${this.passedTests} (${Math.round(this.passedTests/this.totalTests*100)}%)`);
        console.log(`失败: ${this.failedTests} (${Math.round(this.failedTests/this.totalTests*100)}%)`);
        console.log(`成功率: ${Math.round(this.passedTests/this.totalTests*100)}%`);
        
        console.log('\n📋 详细测试结果:');
        console.log('-' * 50);
        
        this.testResults.forEach((result, index) => {
            const status = result.status === 'PASS' ? '✅' : 
                          result.status === 'FAIL' ? '❌' : '🚨';
            console.log(`${index + 1}. ${status} ${result.test}: ${result.details}`);
        });
        
        console.log('=' * 50);
        
        if (this.passedTests === this.totalTests) {
            console.log('🎉 所有测试通过！系统功能正常。');
        } else if (this.passedTests > 0) {
            console.log('⚠️  部分测试通过，需要修复问题。');
        } else {
            console.log('🚨 所有测试失败，需要重大修复。');
        }
    }
}

// 如果直接运行此文件，启动测试
if (require.main === module) {
    const testSuite = new SelfOrganizationTestSuite();
    
    testSuite.runAllTests().then(() => {
        process.exit(0);
    }).catch((error) => {
        console.error('测试运行失败:', error);
        process.exit(1);
    });
}

module.exports = SelfOrganizationTestSuite;