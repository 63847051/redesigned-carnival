/**
 * 自组织协议引擎 (Self-Organization Protocol Engine)
 * 实现智能组队和任务分配的核心协议
 */

class SelfOrganizationProtocol {
    /**
     * 自组织协议引擎
     * 负责智能组队、任务分配、协调管理
     */
    
    constructor(config = {}) {
        this.config = {
            maxTeamSize: 5,
            minTeamSize: 1,
            teamTimeout: 24 * 60 * 60 * 1000, // 24小时
            taskTimeout: 2 * 60 * 60 * 1000, // 2小时
            enableAutoFormation: true,
            enableDynamicAssignment: true,
            enableSkillBalancing: true,
            ...config
        };
        
        // 初始化关键属性
        this.startTime = Date.now();
        this.activeTeams = new Map();
        
        // 团队状态管理
        this.activeTeams = new Map();
        this.taskQueue = [];
        this.agentPool = new Map();
        
        // 协议状态
        this.protocolState = 'initialized';
        this.lastActivity = Date.now();
        
        // 智能组队策略 - 绑定上下文
        this.teamFormationStrategies = {
            'skill-based': this.formSkillBasedTeam.bind(this),
            'expertise-based': this.formExpertiseBasedTeam.bind(this),
            'load-balanced': this.formLoadBalancedTeam.bind(this),
            'complexity-based': this.formComplexityBasedTeam.bind(this)
        };
        
        // 任务分配策略 - 绑定上下文
        this.taskAssignmentStrategies = {
            'round-robin': this.roundRobinAssignment.bind(this),
            'skill-matching': this.skillMatchingAssignment.bind(this),
            'load-balanced': this.loadBalancedAssignment.bind(this),
            'priority-based': this.priorityBasedAssignment.bind(this)
        };
        
        // 协调机制 - 绑定上下文
        this.coordinationMechanisms = {
            'centralized': this.centralizedCoordination.bind(this),
            'distributed': this.distributedCoordination.bind(this),
            'hierarchical': this.hierarchicalCoordination.bind(this),
            'market-based': this.marketBasedCoordination.bind(this)
        };
    }
    
    /**
     * 启动自组织协议
     */
    async start() {
        console.log('🚀 启动自组织协议引擎');
        
        this.protocolState = 'running';
        this.lastActivity = Date.now();
        
        // 启动后台任务
        this.startBackgroundTasks();
        
        console.log('✅ 自组织协议引擎已启动');
        return this.getProtocolStatus();
    }
    
    /**
     * 选择组队策略
     */
    selectTeamFormationStrategy(complexityAnalysis) {
        const { complexityLevel, requiredSkills } = complexityAnalysis;
        
        switch (complexityLevel) {
            case 'simple':
                return 'skill-based';
            case 'moderate':
                return 'expertise-based';
            case 'complex':
                return 'load-balanced';
            case 'expert':
                return 'complexity-based';
            default:
                return 'skill-based';
        }
    }
    
    /**
     * 处理任务请求
     */
    async processTaskRequest(task) {
        console.log(`📋 处理任务请求: ${task.title || '无标题任务'}`);
        
        // 1. 分析任务复杂度
        const complexityAnalyzer = new (require('./TaskComplexityAnalyzer'))();
        const complexityAnalysis = await complexityAnalyzer.analyzeTask(task);
        
        // 2. 智能组队
        const team = await this.formTeam(complexityAnalysis);
        
        // 3. 任务分配
        const assignment = await this.assignTask(task, team);
        
        // 4. 启动任务执行
        const execution = await this.startTaskExecution(assignment);
        
        // 5. 监控和协调
        this.monitorTaskExecution(execution);
        
        return {
            taskId: task.id,
            teamId: team.id,
            assignment: assignment,
            execution: execution,
            status: 'assigned'
        };
    }
    
    /**
     * 智能组队
     */
    async formTeam(complexityAnalysis) {
        console.log(`👥 开始智能组队 - 复杂度: ${complexityAnalysis.complexityLevel}`);
        
        const strategy = this.selectTeamFormationStrategy(complexityAnalysis);
        const team = await this.teamFormationStrategies[strategy](complexityAnalysis);
        
        // 注册团队
        this.activeTeams.set(team.id, {
            ...team,
            createdAt: Date.now(),
            lastActivity: Date.now(),
            taskCount: 0,
            successRate: 1.0
        });
        
        console.log(`✅ 团队组建完成 - ${team.members.length} 名成员`);
        return team;
    }
    
    /**
     * 选择组队策略
     */
    selectTeamFormationStrategy(complexityAnalysis) {
        const { complexityLevel, requiredSkills } = complexityAnalysis;
        
        switch (complexityLevel) {
            case 'simple':
                return 'skill-based';
            case 'moderate':
                return 'expertise-based';
            case 'complex':
                return 'load-balanced';
            case 'expert':
                return 'complexity-based';
            default:
                return 'skill-based';
        }
    }
    
    /**
     * 基于技能的组队策略
     */
    async formSkillBasedTeam(complexityAnalysis) {
        console.log('🔍 formSkillBasedTeam called, config:', this.config);
        const team = {
            id: `team_${Date.now()}`,
            strategy: 'skill-based',
            members: [],
            requiredSkills: complexityAnalysis.requiredSkills || [],
            maxSize: this.config?.minTeamSize || 1,
            formationTime: Date.now(),
            status: 'forming'
        };
        
        // 为每个必需技能选择一个专家
        for (const skillData of complexityAnalysis.requiredSkills || []) {
            const agent = await this.findBestAgentForSkill(skillData.skill);
            if (agent) {
                team.members.push(agent);
            }
        }
        
        team.status = 'formed';
        return team;
    }
    
    /**
     * 基于专业知识的组队策略
     */
    async formExpertiseBasedTeam(complexityAnalysis) {
        const team = {
            id: `team_${Date.now()}`,
            strategy: 'expertise-based',
            members: [],
            requiredSkills: complexityAnalysis.requiredSkills || [],
            maxSize: this.config.maxTeamSize || 3,
            formationTime: Date.now(),
            status: 'forming'
        };
        
        // 根据领域选择专家
        const domainExperts = await this.findDomainExperts(complexityAnalysis.domain || 'general');
        team.members.push(...domainExperts);
        
        team.status = 'formed';
        return team;
    }
    
    /**
     * 负载均衡组队策略
     */
    async formLoadBalancedTeam(complexityAnalysis) {
        const team = {
            id: `team_${Date.now()}`,
            strategy: 'load-balanced',
            members: [],
            requiredSkills: complexityAnalysis.requiredSkills || [],
            maxSize: Math.min(this.config.maxTeamSize || 3, 3),
            formationTime: Date.now(),
            status: 'forming'
        };
        
        // 选择负载最低的专家
        const availableAgents = await this.getAvailableAgents();
        const sortedAgents = availableAgents.sort((a, b) => (a.currentLoad || 0) - (b.currentLoad || 0));
        
        // 选择负载最低的专家
        for (let i = 0; i < Math.min(team.maxSize, sortedAgents.length); i++) {
            team.members.push(sortedAgents[i]);
        }
        
        team.status = 'formed';
        return team;
    }
    
    /**
     * 基于复杂度的组队策略
     */
    async formComplexityBasedTeam(complexityAnalysis) {
        const team = {
            id: `team_${Date.now()}`,
            strategy: 'complexity-based',
            members: [],
            requiredSkills: complexityAnalysis.requiredSkills || [],
            maxSize: this.config.maxTeamSize || 4,
            formationTime: Date.now(),
            status: 'forming',
            hasLeader: false
        };
        
        const teamSize = this.calculateTeamSize(complexityAnalysis.complexityLevel);
        
        // 选择专家
        for (let i = 0; i < teamSize; i++) {
            let agent;
            
            if (i === 0 && complexityAnalysis.complexityLevel === 'expert') {
                // 第一个专家作为团队领导
                agent = await this.findBestAgentForSkill('coordination');
                if (agent) {
                    team.leader = agent.id;
                    team.hasLeader = true;
                }
            } else {
                // 其他专家
                const skillIndex = i % (complexityAnalysis.requiredSkills?.length || 1);
                const skill = complexityAnalysis.requiredSkills[skillIndex]?.skill || 'general';
                agent = await this.findBestAgentForSkill(skill);
                if (agent) {
                    team.members.push(agent);
                }
            }
        }
        
        team.status = 'formed';
        return team;
    }
    
    /**
     * 计算团队规模
     */
    calculateTeamSize(complexityLevel) {
        const sizes = {
            'simple': 1,
            'moderate': 2,
            'complex': 3,
            'expert': 4
        };
        
        return sizes[complexityLevel] || 2;
    }
    
    /**
     * 任务分配
     */
    async assignTask(task, team) {
        console.log(`🎯 分配任务给团队: ${team.id}`);
        
        const strategy = this.selectTaskAssignmentStrategy(task, team);
        const assignment = await this.taskAssignmentStrategies[strategy](task, team);
        
        // 更新团队状态
        this.activeTeams.get(team.id).taskCount++;
        this.activeTeams.get(team.id).lastActivity = Date.now();
        
        console.log(`✅ 任务分配完成 - 策略: ${strategy}`);
        return assignment;
    }
    
    /**
     * 选择任务分配策略
     */
    selectTaskAssignmentStrategy(task, team) {
        const { requiredSkills } = team;
        
        if (requiredSkills.length > 2) {
            return 'skill-matching';
        }
        
        if (task.priority === 'high') {
            return 'priority-based';
        }
        
        return 'round-robin';
    }
    
    /**
     * 技能匹配分配
     */
    async skillMatchingAssignment(task, team) {
        const assignment = {
            taskId: task.id,
            teamId: team.id,
            assignments: [],
            startTime: Date.now(),
            status: 'assigning',
            strategy: 'skill-matching'
        };
        
        // 根据技能要求分配任务
        for (const member of team.members) {
            const memberSkills = member.skills || [];
            const matchingSkills = task.requiredSkills.filter(skill => 
                memberSkills.some(memberSkill => 
                    memberSkill.toLowerCase().includes(skill.toLowerCase())
                )
            );
            
            if (matchingSkills.length > 0) {
                assignment.assignments.push({
                    memberId: member.id,
                    memberName: member.name,
                    assignedSkills: matchingSkills,
                    taskPart: this.calculateTaskPart(matchingSkills, task.requiredSkills),
                    estimatedDuration: this.estimateTaskDuration(task, matchingSkills)
                });
            }
        }
        
        assignment.status = 'assigned';
        return assignment;
    }
    
    /**
     * 轮询分配
     */
    async roundRobinAssignment(task, team) {
        const assignment = {
            taskId: task.id,
            teamId: team.id,
            assignments: [],
            startTime: Date.now(),
            status: 'assigning',
            strategy: 'round-robin'
        };
        
        const teamMembers = [...team.members];
        const memberCount = teamMembers.length;
        
        // 轮询分配任务
        for (let i = 0; i < task.requiredSkills.length; i++) {
            const memberIndex = i % memberCount;
            const member = teamMembers[memberIndex];
            
            assignment.assignments.push({
                memberId: member.id,
                memberName: member.name,
                assignedSkills: [task.requiredSkills[i]],
                taskPart: `${i + 1}/${task.requiredSkills.length}`,
                estimatedDuration: this.estimateTaskDuration(task, [task.requiredSkills[i]])
            });
        }
        
        assignment.status = 'assigned';
        return assignment;
    }
    
    /**
     * 负载均衡分配
     */
    async loadBalancedAssignment(task, team) {
        const assignment = {
            taskId: task.id,
            teamId: team.id,
            assignments: [],
            startTime: Date.now(),
            status: 'assigning',
            strategy: 'load-balanced'
        };
        
        // 获取成员当前负载
        const memberLoads = team.members.map(member => ({
            member,
            load: member.currentLoad || 0
        }));
        
        // 按负载排序
        memberLoads.sort((a, b) => a.load - b.load);
        
        // 分配任务给负载最低的成员
        for (const skill of task.requiredSkills) {
            const member = memberLoads.shift();
            memberLoads.push(member); // 重新排队
            
            assignment.assignments.push({
                memberId: member.member.id,
                memberName: member.member.name,
                assignedSkills: [skill],
                taskPart: `${assignment.assignments.length + 1}/${task.requiredSkills.length}`,
                estimatedDuration: this.estimateTaskDuration(task, [skill])
            });
        }
        
        assignment.status = 'assigned';
        return assignment;
    }
    
    /**
     * 优先级分配
     */
    async priorityBasedAssignment(task, team) {
        const assignment = {
            taskId: task.id,
            teamId: team.id,
            assignments: [],
            startTime: Date.now(),
            status: 'assigning',
            strategy: 'priority-based'
        };
        
        // 如果有团队领导，优先分配给领导
        if (team.leader) {
            const leader = team.members.find(m => m.id === team.leader);
            if (leader) {
                assignment.assignments.push({
                    memberId: leader.id,
                    memberName: leader.name,
                    assignedSkills: task.requiredSkills.slice(0, Math.ceil(task.requiredSkills.length / 2)),
                    taskPart: 'leader',
                    estimatedDuration: this.estimateTaskDuration(task, task.requiredSkills.slice(0, Math.ceil(task.requiredSkills.length / 2)))
                });
            }
        }
        
        // 分配剩余任务
        const remainingSkills = task.requiredSkills.slice(assignment.assignments.length > 0 ? Math.ceil(task.requiredSkills.length / 2) : 0);
        for (let i = 0; i < remainingSkills.length; i++) {
            const member = team.members[(i + (assignment.assignments.length > 0 ? 1 : 0)) % team.members.length];
            assignment.assignments.push({
                memberId: member.id,
                memberName: member.name,
                assignedSkills: [remainingSkills[i]],
                taskPart: `member_${i}`,
                estimatedDuration: this.estimateTaskDuration(task, [remainingSkills[i]])
            });
        }
        
        assignment.status = 'assigned';
        return assignment;
    }
    
    /**
     * 计算任务分配比例
     */
    calculateTaskPart(assignedSkills, allSkills) {
        const ratio = assignedSkills.length / allSkills.length;
        if (ratio >= 0.5) return 'primary';
        if (ratio >= 0.3) return 'secondary';
        return 'support';
    }
    
    /**
     * 估算任务时长
     */
    estimateTaskDuration(task, skills) {
        const baseDuration = 30; // 基础时长 30 分钟
        const skillMultiplier = skills.length * 15; // 每个技能增加 15 分钟
        const complexityMultiplier = task.complexity === 'high' ? 2 : task.complexity === 'expert' ? 3 : 1;
        
        return baseDuration + skillMultiplier * complexityMultiplier;
    }
    
    /**
     * 启动任务执行
     */
    async startTaskExecution(assignment) {
        console.log(`🚀 启动任务执行: ${assignment.taskId}`);
        
        const execution = {
            ...assignment,
            actualStartTime: Date.now(),
            status: 'running',
            progress: 0,
            milestones: [],
            lastUpdate: Date.now()
        };
        
        // 模拟任务执行进度
        this.simulateProgress(execution);
        
        return execution;
    }
    
    /**
     * 模拟任务执行进度
     */
    async simulateProgress(execution) {
        const progressInterval = setInterval(() => {
            const elapsed = Date.now() - execution.actualStartTime;
            const totalDuration = execution.assignments.reduce((sum, a) => sum + (a.estimatedDuration || 30), 0);
            const progress = Math.min((elapsed / (totalDuration * 60 * 1000)) * 100, 100);
            
            execution.progress = progress;
            execution.lastUpdate = Date.now();
            
            if (progress >= 100) {
                clearInterval(progressInterval);
                execution.status = 'completed';
                execution.completedAt = Date.now();
                this.handleTaskCompletion(execution);
            }
        }, 1000);
    }
    
    /**
     * 处理任务完成
     */
    async handleTaskCompletion(execution) {
        console.log(`✅ 任务完成: ${execution.taskId}`);
        
        // 更新团队状态
        const teamData = this.activeTeams.get(execution.teamId);
        if (teamData) {
            teamData.taskCount++;
            teamData.lastActivity = Date.now();
            teamData.successRate = (teamData.successRate * teamData.taskCount + 1) / (teamData.taskCount + 1);
        }
        
        // 触发团队解散检查
        this.checkTeamDissolution(execution.teamId);
        
        return execution;
    }
    
    /**
     * 检查团队解散
     */
    async checkTeamDissolution(teamId) {
        const teamData = this.activeTeams.get(teamId);
        if (!teamData) return;
        
        const inactiveTime = Date.now() - teamData.lastActivity;
        const maxInactiveTime = this.config.teamTimeout;
        
        if (inactiveTime > maxInactiveTime) {
            await this.dissolveTeam(teamId);
        }
    }
    
    /**
     * 解散团队
     */
    async dissolveTeam(teamId) {
        console.log(`🧹 解散团队: ${teamId}`);
        
        const teamData = this.activeTeams.get(teamId);
        if (!teamData) return;
        
        // 保存团队历史
        const teamHistory = {
            teamId: teamId,
            dissolutionTime: Date.now(),
            memberCount: teamData.members.length,
            taskCount: teamData.taskCount,
            successRate: teamData.successRate,
            status: 'dissolved'
        };
        
        // 从活跃团队中移除
        this.activeTeams.delete(teamId);
        
        console.log(`✅ 团队解散完成: ${teamId}`);
        return teamHistory;
    }
    
    /**
     * 获取协议状态
     */
    getProtocolStatus() {
        return {
            protocolState: this.protocolState,
            activeTeams: this.activeTeams.size,
            totalTasksAssigned: this.getTotalTasksAssigned(),
            averageTeamSize: this.getAverageTeamSize(),
            successRate: this.getOverallSuccessRate(),
            lastActivity: this.lastActivity,
            uptime: Date.now() - this.lastActivity
        };
    }
    
    /**
     * 获取总任务数
     */
    getTotalTasksAssigned() {
        let total = 0;
        for (const teamData of this.activeTeams.values()) {
            total += teamData.taskCount;
        }
        return total;
    }
    
    /**
     * 获取平均团队规模
     */
    getAverageTeamSize() {
        if (this.activeTeams.size === 0) return 0;
        
        let totalSize = 0;
        for (const teamData of this.activeTeams.values()) {
            totalSize += teamData.members.length;
        }
        
        return totalSize / this.activeTeams.size;
    }
    
    /**
     * 获取整体成功率
     */
    getOverallSuccessRate() {
        if (this.activeTeams.size === 0) return 1.0;
        
        let totalSuccess = 0;
        let totalCount = 0;
        
        for (const teamData of this.activeTeams.values()) {
            if (teamData.taskCount > 0) {
                totalSuccess += teamData.successRate * teamData.taskCount;
                totalCount += teamData.taskCount;
            }
        }
        
        return totalCount === 0 ? 1.0 : totalSuccess / totalCount;
    }
    
    /**
     * 启动后台任务
     */
    startBackgroundTasks() {
        // 定期清理过期团队
        setInterval(() => {
            this.cleanupExpiredTeams();
        }, this.config.teamTimeout / 2);
        
        // 定期收集统计信息
        setInterval(() => {
            this.collectStatistics();
        }, 60000); // 每分钟
    }
    
    /**
     * 清理过期团队
     */
    async cleanupExpiredTeams() {
        const now = Date.now();
        const expiredTeams = [];
        
        for (const [teamId, teamData] of this.activeTeams) {
            if (now - teamData.lastActivity > this.config.teamTimeout) {
                expiredTeams.push(teamId);
            }
        }
        
        for (const teamId of expiredTeams) {
            await this.dissolveTeam(teamId);
        }
    }
    
    /**
     * 收集统计信息
     */
    collectStatistics() {
        const stats = {
            timestamp: Date.now(),
            activeTeams: this.activeTeams.size,
            totalTasks: this.getTotalTasksAssigned(),
            averageTeamSize: this.getAverageTeamSize(),
            successRate: this.getOverallSuccessRate()
        };
        
        console.log(`📊 协议统计: ${JSON.stringify(stats, null, 2)}`);
        return stats;
    }
    
    // Helper methods (would be implemented in real system)
    async findBestAgentForSkill(skill) {
        // 模拟实现
        return {
            id: `agent_${Date.now()}_${skill}`,
            name: `${skill}_expert_${Date.now()}`,
            skills: [skill],
            currentLoad: 0
        };
    }
    
    async monitorTaskExecution(execution) {
        // 模拟实现 - 监控任务执行进度
        console.log(`🔍 监控任务执行: ${execution.taskId}`);
        
        // 简单的监控逻辑
        const interval = setInterval(() => {
            const status = Math.random() > 0.8 ? 'completed' : 'running';
            console.log(`📊 任务 ${execution.taskId} 状态: ${status}`);
            
            if (status === 'completed') {
                clearInterval(interval);
            }
        }, 2000);
        
        return Promise.resolve({ monitored: true, executionId: execution.id });
    }
    
    async findDomainExperts(domain) {
        // 模拟实现
        return [
            {
                id: `expert_${Date.now()}_1`,
                name: `${domain}_expert_1`,
                skills: [domain],
                currentLoad: 0
            },
            {
                id: `expert_${Date.now()}_2`,
                name: `${domain}_expert_2`,
                skills: [domain],
                currentLoad: 0
            }
        ];
    }
    
    async getAvailableAgents() {
        // 模拟实现
        return [
            { id: 'agent1', name: 'Agent 1', currentLoad: 0.3 },
            { id: 'agent2', name: 'Agent 2', currentLoad: 0.5 },
            { id: 'agent3', name: 'Agent 3', currentLoad: 0.2 }
        ];
    }
    
    // 协调方法实现
    async centralizedCoordination(team, task) {
        console.log(`🎯 集中式协调: ${team.id} - ${task.title}`);
        return {
            type: 'centralized',
            leader: team.leader,
            decision: 'approved',
            timestamp: Date.now()
        };
    }
    
    async distributedCoordination(team, task) {
        console.log(`🌐 分布式协调: ${team.id} - ${task.title}`);
        return {
            type: 'distributed',
            votes: team.members.length,
            consensus: true,
            timestamp: Date.now()
        };
    }
    
    async hierarchicalCoordination(team, task) {
        console.log(`🏗️ 层次化协调: ${team.id} - ${task.title}`);
        return {
            type: 'hierarchical',
            hierarchy: ['leader', 'member', 'member'],
            approval: true,
            timestamp: Date.now()
        };
    }
    
    async marketBasedCoordination(team, task) {
        console.log(`💰 市场机制协调: ${team.id} - ${task.title}`);
        return {
            type: 'market',
            bidding: true,
            selected: true,
            timestamp: Date.now()
        };
    }
}

module.exports = SelfOrganizationProtocol;