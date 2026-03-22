/**
 * 动态 Agent 生成器 (Dynamic Agent Generator)
 * 根据任务需求动态创建专门 Agent
 */

class DynamicAgentGenerator {
    /**
     * 动态 Agent 生成器
     * 基于任务需求创建专门的 Agent 实例
     */
    
    constructor(config = {}) {
        this.config = {
            agentTemplatePath: './agent-templates',
            defaultModel: 'glmcode/glm-4.7',
            timeout: 30000,
            maxRetries: 3,
            ...config
        };
        
        // Agent 模板库
        this.agentTemplates = {
            'tech-expert': {
                name: '技术专家小新',
                model: 'opencode/minimax-m2.5-free',
                role: '技术支持专家',
                skills: ['programming', 'algorithm', 'debug', 'deploy'],
                description: '专注于编程、算法调试、部署等技术任务',
                capabilities: ['代码编写', '系统设计', '问题调试', '性能优化']
            },
            'design-expert': {
                name: '设计专家',
                model: 'glmcode/glm-4.6',
                role: '室内设计专家',
                skills: ['design', 'ui', 'prototype', 'frontend'],
                description: '专注于UI设计、原型制作、前端开发等设计任务',
                capabilities: ['界面设计', '原型制作', '前端开发', '用户体验优化']
            },
            'data-expert': {
                name: '数据专家',
                model: 'glmcode/glm-4.7',
                role: '数据分析专家',
                skills: ['data', 'analysis', 'visualization', 'statistics'],
                description: '专注于数据分析、可视化、统计建模等数据任务',
                capabilities: ['数据分析', '可视化', '统计建模', '报告生成']
            },
            'system-architect': {
                name: '系统架构师',
                model: 'glmcode/glm-4.7',
                role: '系统架构专家',
                skills: ['architecture', 'integration', 'scalability'],
                description: '专注于系统架构设计、系统集成、可扩展性等架构任务',
                capabilities: ['架构设计', '系统集成', '性能优化', '技术选型']
            },
            'quality-assurance': {
                name: '质量保证专家',
                model: 'glmcode/glm-4.5-air',
                role: '质量检查专家',
                skills: ['testing', 'review', 'validation'],
                description: '专注于代码审查、测试、质量保证等质检任务',
                capabilities: ['代码审查', '测试编写', '质量评估', '文档编写']
            },
            'integration-coordinator': {
                name: '集成协调员',
                model: 'glmcode/glm-4.7',
                role: '协调管理专家',
                skills: ['coordination', 'management', 'communication'],
                description: '专注于团队协调、进度管理、沟通协调等管理任务',
                capabilities: ['任务分配', '进度监控', '冲突解决', '沟通协调']
            }
        };
        
        // 专门领域专家模板
        this.specializedTemplates = {
            'frontend-developer': {
                name: '前端开发专家',
                model: 'glmcode/glm-4.6',
                role: '前端开发专家',
                skills: ['javascript', 'react', 'vue', 'css', 'html'],
                description: '专注于前端开发、UI实现、交互体验',
                capabilities: ['页面开发', '组件设计', '响应式布局', '交互实现']
            },
            'backend-developer': {
                name: '后端开发专家',
                model: 'opencode/minimax-m2.5-free',
                role: '后端开发专家',
                skills: ['api', 'database', 'server', 'security'],
                description: '专注于后端API开发、数据库设计、服务器配置',
                capabilities: ['API开发', '数据库设计', '服务器配置', '安全性设计']
            },
            'devops-engineer': {
                name: 'DevOps工程师',
                model: 'glmcode/glm-4.7',
                role: '运维开发专家',
                skills: ['deploy', 'ci-cd', 'monitoring', 'automation'],
                description: '专注于部署自动化、监控、CI/CD流程',
                capabilities: ['自动化部署', '系统监控', 'CI/CD配置', '故障排查']
            },
            'ai-specialist': {
                name: 'AI专家',
                model: 'glmcode/glm-4.7',
                role: '人工智能专家',
                skills: ['machine learning', 'neural network', 'ai', 'ml'],
                description: '专注于AI算法开发、机器学习模型训练',
                capabilities: ['模型训练', '算法优化', '数据处理', 'AI集成']
            }
        };
    }
    
    /**
     * 根据需求创建动态 Agent
     * @param {Object} requirements - Agent 需求
     * @param {string} taskId - 关联的任务ID
     * @returns {Object} - 创建的 Agent 信息
     */
    async createDynamicAgent(requirements, taskId) {
        console.log(`🤖 开始创建动态 Agent - 任务ID: ${taskId}`);
        
        // 分析需求
        const analysis = this.analyzeRequirements(requirements);
        const template = this.selectTemplate(analysis);
        
        // 创建 Agent 配置
        const agentConfig = this.generateAgentConfig(analysis, template, taskId);
        
        // 生成 Agent
        const agent = await this.generateAgent(agentConfig);
        
        console.log(`✅ 动态 Agent 创建完成 - ${agent.name} (ID: ${agent.id})`);
        return agent;
    }
    
    /**
     * 分析 Agent 需求
     */
    analyzeRequirements(requirements) {
        const analysis = {
            domain: this.detectDomain(requirements),
            skills: this.extractSkills(requirements),
            experience: this.assessExperience(requirements),
            complexity: this.assessComplexity(requirements),
            role: this.determineRole(requirements)
        };
        
        console.log(`📋 Agent 需求分析完成 - 领域: ${analysis.domain}, 角色: ${analysis.role}`);
        return analysis;
    }
    
    /**
     * 检测领域
     */
    detectDomain(requirements) {
        const text = (requirements.description || requirements.title || '').toLowerCase();
        const domainKeywords = {
            'frontend': ['ui', 'ux', 'frontend', 'web', 'page', 'interface'],
            'backend': ['api', 'server', 'database', 'backend', 'rest'],
            'mobile': ['mobile', 'app', 'ios', 'android', 'react native'],
            'ai': ['ai', 'machine learning', 'ml', 'neural network', 'intelligence'],
            'devops': ['devops', 'deploy', 'ci-cd', 'docker', 'kubernetes'],
            'design': ['design', 'ui', 'ux', 'visual', 'graphic'],
            'data': ['data', 'analytics', 'analysis', 'statistics', 'visualization']
        };
        
        for (const [domain, keywords] of Object.entries(domainKeywords)) {
            if (keywords.some(keyword => text.includes(keyword))) {
                return domain;
            }
        }
        
        return 'general';
    }
    
    /**
     * 提取技能需求
     */
    extractSkills(requirements) {
        const skills = [];
        const text = (requirements.description || requirements.title || '').toLowerCase();
        
        // 技术技能映射
        const skillMap = {
            'programming': ['code', 'programming', 'development', 'coding', 'script'],
            'design': ['design', 'ui', 'ux', 'visual', 'interface'],
            'data': ['data', 'analysis', 'analytics', 'statistics', 'visualization'],
            'system': ['system', 'architecture', 'integration', 'deploy', 'ci-cd'],
            'testing': ['test', 'testing', 'qa', 'quality', 'validation'],
            'management': ['manage', 'coordinate', 'plan', 'organize', 'lead']
        };
        
        Object.entries(skillMap).forEach(([skill, keywords]) => {
            const matchedKeywords = keywords.filter(keyword => text.includes(keyword));
            if (matchedKeywords.length > 0) {
                skills.push({
                    skill: skill,
                    keywords: matchedKeywords,
                    priority: matchedKeywords.length
                });
            }
        });
        
        return skills.sort((a, b) => b.priority - a.priority);
    }
    
    /**
     * 评估经验需求
     */
    assessExperience(requirements) {
        const text = (requirements.description || requirements.title || '').toLowerCase();
        
        const experienceLevels = {
            'junior': ['beginner', 'simple', 'basic', 'start', 'learn'],
            'intermediate': ['moderate', 'intermediate', 'some experience', 'familiar'],
            'senior': ['advanced', 'expert', 'senior', 'complex', 'experience'],
            'lead': ['architect', 'lead', 'principal', 'technical lead', 'team lead']
        };
        
        for (const [level, keywords] of Object.entries(experienceLevels)) {
            if (keywords.some(keyword => text.includes(keyword))) {
                return level;
            }
        }
        
        return 'intermediate'; // 默认中级
    }
    
    /**
     * 评估复杂度需求
     */
    assessComplexity(requirements) {
        const text = (requirements.description || requirements.title || '').toLowerCase();
        const complexityIndicators = {
            'low': ['simple', 'basic', 'easy', 'straightforward'],
            'medium': ['moderate', 'intermediate', 'some complexity'],
            'high': ['complex', 'advanced', 'difficult', 'challenging'],
            'expert': ['expert', 'advanced', 'complex', 'specialized', 'deep knowledge']
        };
        
        for (const [level, keywords] of Object.entries(complexityIndicators)) {
            if (keywords.some(keyword => text.includes(keyword))) {
                return level;
            }
        }
        
        return 'medium'; // 默认中等
    }
    
    /**
     * 确定角色
     */
    determineRole(requirements) {
        const domain = this.detectDomain(requirements);
        const experience = this.assessExperience(requirements);
        
        const roleMap = {
            'frontend': '前端开发',
            'backend': '后端开发',
            'mobile': '移动开发',
            'ai': 'AI开发',
            'devops': 'DevOps工程师',
            'design': 'UI设计师',
            'data': '数据分析师',
            'general': '技术专家'
        };
        
        return roleMap[domain] || '技术专家';
    }
    
    /**
     * 选择模板
     */
    selectTemplate(analysis) {
        // 根据领域和复杂度选择模板
        const domain = analysis.domain;
        const complexity = analysis.complexity;
        
        // 简单任务使用基础模板
        if (complexity === 'low') {
            return this.agentTemplates['tech-expert'];
        }
        
        // 根据领域选择专门模板
        if (this.specializedTemplates[`${domain}-developer`]) {
            return this.specializedTemplates[`${domain}-developer`];
        }
        
        // 复杂任务使用系统架构师
        if (complexity === 'high' || complexity === 'expert') {
            return this.agentTemplates['system-architect'];
        }
        
        // 默认返回技术专家
        return this.agentTemplates['tech-expert'];
    }
    
    /**
     * 生成 Agent 配置
     */
    generateAgentConfig(analysis, template, taskId) {
        const timestamp = new Date().toISOString();
        const agentId = `agent_${Date.now()}_${taskId}`;
        
        return {
            id: agentId,
            name: `${template.name}_${taskId.slice(-6)}`,
            model: template.model,
            role: template.role,
            skills: template.skills,
            capabilities: template.capabilities,
            description: `${template.description} - 任务ID: ${taskId}`,
            experienceLevel: analysis.experience,
            taskComplexity: analysis.complexity,
            domain: analysis.domain,
            requiredSkills: analysis.skills,
            createdAt: timestamp,
            expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // 24小时过期
            status: 'created',
            taskIds: [taskId]
        };
    }
    
    /**
     * 生成 Agent 实例
     */
    async generateAgent(config) {
        console.log(`🎯 正在创建 Agent 实例: ${config.name}`);
        
        // 模拟 Agent 创建过程
        const agent = {
            ...config,
            status: 'active',
            startTime: new Date().toISOString(),
            tasksCompleted: 0,
            tasksFailed: 0,
            averageResponseTime: 0,
            lastActivity: new Date().toISOString()
        };
        
        // 这里应该实际调用 sessions_spawn 来创建 Agent
        // 现在模拟实现
        agent.simulation = true;
        agent.mockCapabilities = [
            `擅长: ${agent.capabilities.join(', ')}`,
            `经验等级: ${agent.experienceLevel}`,
            `领域: ${agent.domain}`,
            `技能: ${agent.skills.join(', ')}`
        ];
        
        return agent;
    }
    
    /**
     * 批量创建 Agent 团队
     */
    async createTeam(analysis, taskCount = 1) {
        console.log(`👥 开始创建 Agent 团队 - 预计 ${taskCount} 个任务`);
        
        const team = {
            id: `team_${Date.now()}`,
            leader: null,
            members: [],
            taskCount: taskCount,
            createdAt: new Date().toISOString(),
            status: 'forming'
        };
        
        // 根据团队规模创建成员
        const teamSize = this.calculateTeamSize(analysis.complexity);
        
        for (let i = 0; i < teamSize; i++) {
            const requirements = {
                description: analysis.description || '',
                complexity: analysis.complexity || 'moderate',
                domain: analysis.domain || 'general',
                skills: (analysis.skills || []).map(s => s.skill || 'general')
            };
            
            const member = await this.createDynamicAgent(requirements, `team_${team.id}_member_${i}`);
            team.members.push(member);
            
            // 第一个成员作为团队领导
            if (i === 0 && analysis.complexity === 'expert') {
                team.leader = member.id;
            }
        }
        
        // 确保团队有 maxSize 属性
        team.maxSize = teamSize;
        
        team.status = 'active';
        console.log(`✅ Agent 团队创建完成 - ${team.members.length} 名成员`);
        return team;
    }
    
    /**
     * 计算团队规模
     */
    calculateTeamSize(complexity) {
        const sizes = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'expert': 4
        };
        
        return sizes[complexity] || 2;
    }
    
    /**
     * 清理过期 Agent
     */
    async cleanupExpiredAgents() {
        console.log(`🧹 开始清理过期 Agent`);
        
        // 获取所有活跃 Agent
        const activeAgents = await this.getActiveAgents();
        
        const now = new Date();
        const expiredAgents = activeAgents.filter(agent => {
            return new Date(agent.expiresAt) < now;
        });
        
        for (const agent of expiredAgents) {
            await this.terminateAgent(agent.id);
            console.log(`🗑️  已终止过期 Agent: ${agent.name}`);
        }
        
        console.log(`✅ 清理完成 - 清理了 ${expiredAgents.length} 个过期 Agent`);
        return expiredAgents.length;
    }
    
    /**
     * 获取活跃 Agent
     */
    async getActiveAgents() {
        // 这里应该从实际系统获取活跃 Agent
        // 现在返回模拟数据
        return [
            {
                id: 'agent_123456',
                name: '技术专家小新_abc123',
                status: 'active',
                expiresAt: new Date(Date.now() + 12 * 60 * 60 * 1000).toISOString()
            },
            {
                id: 'agent_789012',
                name: '设计专家_def456',
                status: 'active',
                expiresAt: new Date(Date.now() + 6 * 60 * 60 * 1000).toISOString()
            }
        ];
    }
    
    /**
     * 终止 Agent
     */
    async terminateAgent(agentId) {
        console.log(`🛑 正在终止 Agent: ${agentId}`);
        
        // 这里应该调用实际的终止逻辑
        // 现在模拟实现
        const terminated = {
            agentId: agentId,
            terminatedAt: new Date().toISOString(),
            status: 'terminated',
            reason: 'natural_expiry'
        };
        
        return terminated;
    }
}

module.exports = DynamicAgentGenerator;