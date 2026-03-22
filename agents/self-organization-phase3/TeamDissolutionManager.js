/**
 * 团队解散管理器 (Team Dissolution Manager)
 * 负责任务完成后自动清理和团队解散
 */

class TeamDissolutionManager {
    /**
     * 团队解散管理器
     * 自动管理团队的创建、运行和解散
     */
    
    constructor(config = {}) {
        this.config = {
            maxTeamAge: 24 * 60 * 60 * 1000, // 24小时
            maxIdleTime: 2 * 60 * 60 * 1000, // 2小时空闲
            dissolutionCooldown: 30 * 60 * 1000, // 30分钟冷却期
            enableAutoDissolution: true,
            enablePerformanceTracking: true,
            enableResourceCleanup: true,
            ...config
        };
        
        // 团队状态跟踪
        this.activeTeams = new Map();
        this.teamHistory = [];
        this.dissolutionEvents = [];
        this.performanceMetrics = new Map();
        
        // 清理定时器
        this.cleanupTimer = null;
        this.monitoringTimer = null;
        
        // 统计信息
        this.stats = {
            totalTeamsCreated: 0,
            totalTeamsDissolved: 0,
            averageTeamLifetime: 0,
            dissolutionReasons: {
                'natural_expiry': 0,
                'task_completion': 0,
                'performance_threshold': 0,
                'manual_intervention': 0,
                'resource_cleanup': 0
            }
        };
    }
    
    /**
     * 启动团队解散管理器
     */
    async start() {
        console.log('🚀 启动团队解散管理器');
        
        // 启动监控定时器
        this.startMonitoring();
        
        // 启动清理定时器
        this.startCleanup();
        
        console.log('✅ 团队解散管理器已启动');
        return this.getStatus();
    }
    
    /**
     * 注册新团队
     */
    async registerTeam(team) {
        console.log(`📝 注册新团队: ${team.id}`);
        
        const teamRecord = {
            id: team.id,
            name: team.name || `Team_${team.id.slice(-6)}`,
            members: team.members || [],
            leader: team.leader,
            createdAt: Date.now(),
            lastActivity: Date.now(),
            taskCount: 0,
            completedTasks: 0,
            failedTasks: 0,
            dissolutionDeadline: Date.now() + this.config.maxTeamAge,
            status: 'active',
            dissolutionReason: null,
            history: []
        };
        
        this.activeTeams.set(team.id, teamRecord);
        this.stats.totalTeamsCreated++;
        
        // 触发团队创建事件
        this.emitTeamEvent('created', teamRecord);
        
        console.log(`✅ 团队注册完成: ${team.id} (${teamRecord.members.length} 名成员)`);
        return teamRecord;
    }
    
    /**
     * 更新团队活动
     */
    async updateTeamActivity(teamId, activity) {
        const team = this.activeTeams.get(teamId);
        if (!team) return false;
        
        const now = Date.now();
        team.lastActivity = now;
        team.history.push({
            timestamp: now,
            activity: activity,
            details: activity.details || {}
        });
        
        // 更新任务统计
        if (activity.type === 'task_completed') {
            team.completedTasks++;
        } else if (activity.type === 'task_failed') {
            team.failedTasks++;
        }
        
        console.log(`📊 更新团队活动: ${teamId} - ${activity.type}`);
        return true;
    }
    
    /**
     * 检查团队解散条件
     */
    async checkDissolutionConditions(teamId) {
        const team = this.activeTeams.get(teamId);
        if (!team) return { shouldDissolve: false, reason: null };
        
        const now = Date.now();
        const reasons = [];
        
        // 1. 检查团队年龄
        if (now - team.createdAt > this.config.maxTeamAge) {
            reasons.push('natural_expiry');
        }
        
        // 2. 检查空闲时间
        if (now - team.lastActivity > this.config.maxIdleTime) {
            reasons.push('idle_timeout');
        }
        
        // 3. 检查任务完成率
        if (team.taskCount > 0) {
            const successRate = team.completedTasks / team.taskCount;
            if (successRate < 0.5) { // 成功率低于50%
                reasons.push('performance_threshold');
            }
        }
        
        // 4. 检查是否所有任务都已完成
        if (team.taskCount > 0 && team.completedTasks === team.taskCount) {
            reasons.push('all_tasks_completed');
        }
        
        // 5. 检查团队规模是否过小
        if (team.members.length < 1) {
            reasons.push('no_members');
        }
        
        return {
            shouldDissolve: reasons.length > 0,
            reasons: reasons,
            team: team
        };
    }
    
    /**
     * 执行团队解散
     */
    async dissolveTeam(teamId, reason = 'auto_dissolution') {
        console.log(`🧹 开始解散团队: ${teamId}`);
        
        const team = this.activeTeams.get(teamId);
        if (!team) {
            console.log(`❌ 团队不存在: ${teamId}`);
            return { success: false, error: 'Team not found' };
        }
        
        // 执行解散前检查
        const dissolutionCheck = await this.preDissolutionCheck(teamId, reason);
        if (!dissolutionCheck.canDissolve) {
            console.log(`⚠️  团队无法解散: ${teamId} - ${dissolutionCheck.reason}`);
            return { success: false, reason: dissolutionCheck.reason };
        }
        
        // 执行解散操作
        const dissolutionResult = await this.performDissolution(teamId, reason);
        
        // 更新统计
        this.updateDissolutionStats(team, reason);
        
        // 记录历史
        this.recordTeamHistory(team, reason);
        
        console.log(`✅ 团队解散完成: ${teamId} - 原因: ${reason}`);
        return dissolutionResult;
    }
    
    /**
     * 解散前检查
     */
    async preDissolutionCheck(teamId, reason) {
        const team = this.activeTeams.get(teamId);
        if (!team) {
            return { canDissolve: false, reason: 'Team not found' };
        }
        
        // 检查解散冷却期
        if (this.hasDissolutionCooldown(teamId)) {
            return { canDissolve: false, reason: 'Dissolution cooldown active' };
        }
        
        // 检查是否有关键任务正在执行
        if (this.hasCriticalTasks(teamId)) {
            return { canDissolve: false, reason: 'Critical tasks in progress' };
        }
        
        return { canDissolve: true, reason: 'Ready for dissolution' };
    }
    
    /**
     * 执行解散操作
     */
    async performDissolution(teamId, reason) {
        const team = this.activeTeams.get(teamId);
        
        // 1. 准备解散数据
        const dissolutionData = {
            teamId: teamId,
            reason: reason,
            timestamp: Date.now(),
            team: this.sanitizeTeamData(team),
            performance: this.getTeamPerformance(team)
        };
        
        // 2. 释放资源
        if (this.config.enableResourceCleanup) {
            await this.cleanupTeamResources(teamId);
        }
        
        // 3. 终止成员任务
        await this.terminateMemberTasks(teamId);
        
        // 4. 通知相关方
        await this.notifyStakeholders(teamId, reason);
        
        // 5. 移除活跃团队
        this.activeTeams.delete(teamId);
        
        // 6. 记录解散事件
        this.dissolutionEvents.push(dissolutionData);
        
        // 7. 设置解散冷却期
        this.setDissolutionCooldown(teamId);
        
        return {
            success: true,
            dissolution: dissolutionData,
            teamMembers: team.members.length
        };
    }
    
    /**
     * 清理团队资源
     */
    async cleanupTeamResources(teamId) {
        console.log(`🧹 清理团队资源: ${teamId}`);
        
        const cleanupTasks = [
            'clear_team_memory',
            'release_shared_resources',
            'close_communication_channels',
            'save_team_artifacts',
            'update_performance_metrics'
        ];
        
        const results = [];
        for (const task of cleanupTasks) {
            try {
                const result = await this.executeCleanupTask(task, teamId);
                results.push({ task, success: true, result });
            } catch (error) {
                results.push({ task, success: false, error: error.message });
            }
        }
        
        return results;
    }
    /**
     * 执行清理任务
     */
    async executeCleanupTask(task, teamId) {
        const cleanupMethods = {
            'clear_team_memory': async () => {
                // 清理团队记忆
                const memory = {
                    teamId: teamId,
                    clearedAt: Date.now(),
                    clearedBy: 'TeamDissolutionManager'
                };
                console.log(`🧠 清理团队记忆: ${teamId}`);
                return memory;
            },
            
            'release_shared_resources': async () => {
                // 释放共享资源
                const resources = {
                    teamId: teamId,
                    resourcesReleased: 2,
                    releaseTime: Date.now()
                };
                console.log(`🔓 释放共享资源: ${teamId}`);
                return resources;
            },
            
            'close_communication_channels': async () => {
                // 关闭通信通道
                const channels = {
                    teamId: teamId,
                    channelsClosed: ['chat', 'file_sharing', 'video_call'],
                    closedAt: Date.now()
                };
                console.log(`💬 关闭通信通道: ${teamId}`);
                return channels;
            },
            
            'save_team_artifacts': async () => {
                // 保存团队成果
                const artifacts = {
                    teamId: teamId,
                    artifactsSaved: ['reports', 'code', 'documentation'],
                    savedAt: Date.now()
                };
                console.log(`💾 保存团队成果: ${teamId}`);
                return artifacts;
            },
            
            'update_performance_metrics': async () => {
                // 更新性能指标
                const metrics = {
                    teamId: teamId,
                    metricsUpdated: ['efficiency', 'quality', 'collaboration'],
                    updatedAt: Date.now()
                };
                console.log(`📊 更新性能指标: ${teamId}`);
                return metrics;
            }
        };
        
        if (cleanupMethods[task]) {
            return await cleanupMethods[task]();
        } else {
            throw new Error(`Unknown cleanup task: ${task}`);
        }
    }
    
    /**
     * 终止成员任务
     */
    async terminateMemberTasks(teamId) {
        console.log(`🛑 终止成员任务: ${teamId}`);
        
        const team = this.activeTeams.get(teamId);
        if (!team) return { success: false, error: 'Team not found' };
        
        const terminationResults = [];
        
        for (const member of team.members) {
            try {
                const result = await this.terminateMemberTask(member.id, teamId);
                terminationResults.push({ memberId: member.id, success: true, result });
            } catch (error) {
                terminationResults.push({ memberId: member.id, success: false, error: error.message });
            }
        }
        
        return terminationResults;
    }
    
    /**
     * 终止单个成员任务
     */
    async terminateMemberTask(memberId, teamId) {
        // 模拟任务终止
        const termination = {
            memberId: memberId,
            teamId: teamId,
            terminatedAt: Date.now(),
            status: 'terminated',
            reason: 'team_dissolution'
        };
        
        console.log(`🛑 已终止成员任务: ${memberId} (团队: ${teamId})`);
        return termination;
    }
    
    /**
     * 通知相关方
     */
    async notifyStakeholders(teamId, reason) {
        console.log(`📢 通知相关方: ${teamId} - 原因: ${reason}`);
        
        // 通知团队领导
        const team = this.activeTeams.get(teamId);
        if (!team) return { success: false, error: 'Team not found' };
        
        const notifications = [
            {
                recipient: team.leader,
                type: 'team_dissolution',
                message: `团队 ${teamId} 已解散，原因: ${reason}`,
                timestamp: Date.now()
            },
            {
                recipient: 'system',
                type: 'team_dissolution_event',
                message: `团队解散事件: ${teamId}`,
                timestamp: Date.now()
            }
        ];
        
        return notifications;
    }
    
    /**
     * 设置解散冷却期
     */
    setDissolutionCooldown(teamId) {
        const cooldownKey = `cooldown_${teamId}`;
        setTimeout(() => {
            // 冷却期结束
            console.log(`⏰ 团队解散冷却期结束: ${teamId}`);
        }, this.config.dissolutionCooldown);
    }
    
    /**
     * 检查解散冷却期
     */
    hasDissolutionCooldown(teamId) {
        const now = Date.now();
        const cooldownKey = `cooldown_${teamId}`;
        // 这里应该检查实际的冷却期状态
        return false; // 简化实现
    }
    
    /**
     * 检查关键任务
     */
    hasCriticalTasks(teamId) {
        const team = this.activeTeams.get(teamId);
        if (!team) return false;
        
        // 检查是否有未完成的关键任务
        const hasCriticalTasks = team.history.some(event => 
            event.activity.type === 'critical_task_in_progress'
        );
        
        return hasCriticalTasks;
    }
    
    /**
     * 更新解散统计
     */
    updateDissolutionStats(team, reason) {
        this.stats.totalTeamsDissolved++;
        this.stats.dissolutionReasons[reason] = (this.stats.dissolutionReasons[reason] || 0) + 1;
        
        // 更新平均团队生命周期
        const teamLifetime = Date.now() - team.createdAt;
        this.stats.averageTeamLifetime = (
            this.stats.averageTeamLifetime + teamLifetime
        ) / this.stats.totalTeamsDissolved;
    }
    
    /**
     * 记录团队历史
     */
    recordTeamHistory(team, reason) {
        const historyRecord = {
            teamId: team.id,
            name: team.name,
            memberCount: team.members.length,
            lifetime: Date.now() - team.createdAt,
            tasksCompleted: team.completedTasks,
            tasksFailed: team.failedTasks,
            dissolutionReason: reason,
            dissolvedAt: Date.now(),
            performance: this.getTeamPerformance(team)
        };
        
        this.teamHistory.push(historyRecord);
        console.log(`📝 已记录团队历史: ${team.id}`);
    }
    
    /**
     * 获取团队性能数据
     */
    getTeamPerformance(team) {
        if (team.taskCount === 0) {
            return {
                successRate: 1.0,
                averageTaskTime: 0,
                efficiency: 1.0,
                collaboration: 1.0
            };
        }
        
        const successRate = team.completedTasks / team.taskCount;
        const efficiency = team.completedTasks / Math.max(team.taskCount, 1);
        const collaboration = this.calculateCollaborationScore(team);
        
        return {
            successRate: successRate,
            averageTaskTime: this.calculateAverageTaskTime(team),
            efficiency: efficiency,
            collaboration: collaboration
        };
    }
    
    /**
     * 计算协作分数
     */
    calculateCollaborationScore(team) {
        // 基于团队活动计算协作分数
        const collaborativeActivities = team.history.filter(event => 
            event.activity.type.includes('collaborate') || 
            event.activity.type.includes('communicate')
        ).length;
        
        const totalActivities = team.history.length;
        return totalActivities === 0 ? 1.0 : collaborativeActivities / totalActivities;
    }
    
    /**
     * 计算平均任务时间
     */
    calculateAverageTaskTime(team) {
        // 这里应该从实际的任务执行时间数据中计算
        // 现在返回模拟值
        return 45; // 45 分钟
    }
    
    /**
     * 清理团队数据
     */
    sanitizeTeamData(team) {
        return {
            id: team.id,
            name: team.name,
            memberCount: team.members.length,
            createdAt: team.createdAt,
            dissolvedAt: Date.now(),
            performance: this.getTeamPerformance(team)
        };
    }
    
    /**
     * 启动监控定时器
     */
    startMonitoring() {
        this.monitoringTimer = setInterval(async () => {
            await this.monitorTeams();
        }, 60000); // 每分钟检查一次
    }
    
    /**
     * 启动清理定时器
     */
    startCleanup() {
        this.cleanupTimer = setInterval(async () => {
            await this.cleanupOldData();
        }, 24 * 60 * 60 * 1000); // 每24小时清理一次
    }
    
    /**
     * 监控团队状态
     */
    async monitorTeams() {
        console.log('👀 监控团队状态');
        
        const teamsToDissolve = [];
        
        for (const [teamId, team] of this.activeTeams) {
            const checkResult = await this.checkDissolutionConditions(teamId);
            if (checkResult.shouldDissolve) {
                teamsToDissolve.push({ teamId, reasons: checkResult.reasons });
            }
        }
        
        for (const { teamId, reasons } of teamsToDissolve) {
            const primaryReason = reasons[0]; // 使用第一个原因作为主要解散原因
            await this.dissolveTeam(teamId, primaryReason);
        }
        
        return teamsToDissolve.length;
    }
    
    /**
     * 清理旧数据
     */
    async cleanupOldData() {
        console.log('🧹 清理旧数据');
        
        const cutoffDate = Date.now() - 30 * 24 * 60 * 60 * 1000; // 30天前
        
        // 清理历史记录
        this.teamHistory = this.teamHistory.filter(record => 
            record.dissolvedAt > cutoffDate
        );
        
        // 清理解散事件
        this.dissolutionEvents = this.dissolutionEvents.filter(event => 
            event.timestamp > cutoffDate
        );
        
        // 清理性能指标
        for (const [key, value] of this.performanceMetrics) {
            if (value.timestamp < cutoffDate) {
                this.performanceMetrics.delete(key);
            }
        }
        
        console.log(`✅ 数据清理完成 - 清理了 ${this.teamHistory.length} 条历史记录`);
    }
    
    /**
     * 获取状态
     */
    getStatus() {
        return {
            activeTeams: this.activeTeams.size,
            totalTeamsCreated: this.stats.totalTeamsCreated,
            totalTeamsDissolved: this.stats.totalTeamsDissolved,
            averageTeamLifetime: Math.round(this.stats.averageTeamLifetime / 1000 / 60), // 转换为分钟
            dissolutionReasons: this.stats.dissolutionReasons,
            recentDissolutions: this.dissolutionEvents.slice(-5),
            uptime: Date.now() - this.startTime
        };
    }
    
    /**
     * 获取团队详情
     */
    getTeamDetails(teamId) {
        const team = this.activeTeams.get(teamId);
        if (!team) return null;
        
        return {
            ...team,
            performance: this.getTeamPerformance(team),
            timeSinceLastActivity: Date.now() - team.lastActivity
        };
    }
    
    /**
     * 获取所有活跃团队
     */
    getAllActiveTeams() {
        const teams = [];
        for (const [teamId, team] of this.activeTeams) {
            teams.push({
                teamId: teamId,
                ...this.getTeamDetails(teamId)
            });
        }
        return teams;
    }
    
    /**
     * 发出团队事件
     */
    emitTeamEvent(eventType, team) {
        console.log(`📢 团队事件: ${eventType} - ${team.id}`);
        
        // 这里可以集成到事件系统
        // 现在只记录到控制台
    }
}

module.exports = TeamDissolutionManager;