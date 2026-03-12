"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OpenClawReadonlyAdapter = void 0;
const openclaw_mappers_1 = require("../mappers/openclaw-mappers");
const session_status_parser_1 = require("../mappers/session-status-parser");
const budget_governance_1 = require("../runtime/budget-governance");
const budget_policy_1 = require("../runtime/budget-policy");
const project_store_1 = require("../runtime/project-store");
const project_summary_1 = require("../runtime/project-summary");
const task_store_1 = require("../runtime/task-store");
const task_summary_1 = require("../runtime/task-summary");
/**
 * Official-first adapter (read path only).
 *
 * In readonly mode it uses a no-op client.
 * In live mode it uses a client that is currently guarded and not enabled yet.
 */
class OpenClawReadonlyAdapter {
    client;
    constructor(client) {
        this.client = client;
    }
    async listSessions() {
        const raw = await this.client.sessionsList();
        return (0, openclaw_mappers_1.mapSessionsListToSummaries)(raw);
    }
    async listSessionStatuses(sessionKeys) {
        const statuses = await Promise.all(sessionKeys.map(async (sessionKey) => {
            const raw = await this.client.sessionStatus(sessionKey);
            return (0, session_status_parser_1.parseSessionStatusText)(sessionKey, raw.rawText);
        }));
        return statuses;
    }
    async listCronJobs() {
        const raw = await this.client.cronList();
        return (0, openclaw_mappers_1.mapCronListToSummaries)(raw);
    }
    async listApprovals() {
        const raw = await this.client.approvalsGet();
        return (0, openclaw_mappers_1.mapApprovalsGetToSummaries)(raw);
    }
    async snapshot() {
        const sessions = await this.listSessions();
        const statuses = await this.listSessionStatuses(sessions.map((s) => s.sessionKey));
        const cronJobs = await this.listCronJobs();
        const approvals = await this.listApprovals();
        const [projects, tasks] = await Promise.all([(0, project_store_1.loadProjectStore)(), (0, task_store_1.loadTaskStore)()]);
        const budgetPolicy = await (0, budget_policy_1.loadBudgetPolicy)();
        const tasksSummary = (0, task_summary_1.computeTasksSummary)(tasks, projects.projects.length);
        const projectSummaries = (0, project_summary_1.computeProjectSummaries)(projects, tasks);
        const budgetSummary = (0, budget_governance_1.computeBudgetSummary)(sessions, statuses, tasks, projects, budgetPolicy.policy);
        if (budgetPolicy.issues.length > 0) {
            console.warn("[mission-control] budget policy issues", {
                path: budgetPolicy.path,
                issues: budgetPolicy.issues,
            });
        }
        return {
            sessions,
            statuses,
            cronJobs,
            approvals,
            projects,
            projectSummaries,
            tasks,
            tasksSummary,
            budgetSummary,
            generatedAt: new Date().toISOString(),
        };
    }
}
exports.OpenClawReadonlyAdapter = OpenClawReadonlyAdapter;
