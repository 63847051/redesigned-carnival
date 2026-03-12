"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.computeBudgetSummary = computeBudgetSummary;
const budget_policy_1 = require("./budget-policy");
const DEFAULT_WARN_RATIO = 0.8;
function computeBudgetSummary(sessions, statuses, tasks, projects, policy = budget_policy_1.DEFAULT_BUDGET_POLICY) {
    const evaluations = [];
    const statusBySessionKey = buildStatusMap(statuses);
    const agentBySessionKey = buildAgentMap(sessions);
    const projectById = new Map(projects.projects.map((project) => [project.projectId, project]));
    for (const agentBudget of tasks.agentBudgets) {
        const keys = [];
        for (const [sessionKey, agentId] of agentBySessionKey.entries()) {
            if (agentId === agentBudget.agentId)
                keys.push(sessionKey);
        }
        evaluations.push(evaluateBudget("agent", agentBudget.agentId, agentBudget.label ?? agentBudget.agentId, resolveThresholds("agent", agentBudget.agentId, agentBudget.thresholds, policy), aggregateUsage(statusBySessionKey, keys)));
    }
    const projectSessionKeys = new Map();
    for (const task of tasks.tasks) {
        const project = projectById.get(task.projectId);
        const projectTitle = project?.title ?? task.projectId;
        let keySet = projectSessionKeys.get(task.projectId);
        if (!keySet) {
            keySet = new Set();
            projectSessionKeys.set(task.projectId, keySet);
        }
        for (const sessionKey of task.sessionKeys)
            keySet.add(sessionKey);
        evaluations.push(evaluateBudget("task", task.taskId, `${projectTitle} / ${task.title}`, resolveThresholds("task", task.taskId, task.budget, policy), aggregateUsage(statusBySessionKey, task.sessionKeys)));
    }
    for (const project of projects.projects) {
        evaluations.push(evaluateBudget("project", project.projectId, project.title, resolveThresholds("project", project.projectId, project.budget, policy), aggregateUsage(statusBySessionKey, [...(projectSessionKeys.get(project.projectId) ?? new Set())])));
    }
    return {
        total: evaluations.length,
        ok: evaluations.filter((item) => item.status === "ok").length,
        warn: evaluations.filter((item) => item.status === "warn").length,
        over: evaluations.filter((item) => item.status === "over").length,
        evaluations,
    };
}
function buildStatusMap(statuses) {
    const map = new Map();
    for (const status of statuses) {
        map.set(status.sessionKey, status);
    }
    return map;
}
function buildAgentMap(sessions) {
    const map = new Map();
    for (const session of sessions) {
        if (!session.agentId)
            continue;
        map.set(session.sessionKey, session.agentId);
    }
    return map;
}
function aggregateUsage(statusBySessionKey, sessionKeys) {
    const keySet = new Set(sessionKeys);
    const usage = { tokensIn: 0, tokensOut: 0, totalTokens: 0, cost: 0 };
    for (const key of keySet) {
        const status = statusBySessionKey.get(key);
        if (!status)
            continue;
        usage.tokensIn += status.tokensIn ?? 0;
        usage.tokensOut += status.tokensOut ?? 0;
        usage.totalTokens += (status.tokensIn ?? 0) + (status.tokensOut ?? 0);
        usage.cost += status.cost ?? 0;
    }
    return usage;
}
function evaluateBudget(scope, scopeId, label, thresholds, usage) {
    const metrics = [];
    const warnRatio = thresholds.warnRatio ?? DEFAULT_WARN_RATIO;
    addMetric(metrics, "tokensIn", usage.tokensIn, thresholds.tokensIn, warnRatio);
    addMetric(metrics, "tokensOut", usage.tokensOut, thresholds.tokensOut, warnRatio);
    addMetric(metrics, "totalTokens", usage.totalTokens, thresholds.totalTokens, warnRatio);
    addMetric(metrics, "cost", usage.cost, thresholds.cost, warnRatio);
    return {
        scope,
        scopeId,
        label,
        thresholds,
        usage,
        metrics,
        status: highestStatus(metrics),
    };
}
function resolveThresholds(scope, scopeId, raw, policy) {
    const scopeOverrides = scope === "agent"
        ? policy.agent[scopeId]
        : scope === "project"
            ? policy.project[scopeId]
            : scope === "task"
                ? policy.task[scopeId]
                : undefined;
    return normalizeThresholds({
        ...policy.defaults,
        ...scopeOverrides,
        ...raw,
    });
}
function addMetric(metrics, metric, used, limit, warnRatio) {
    if (limit === undefined || limit <= 0)
        return;
    const warnAt = limit * warnRatio;
    let status = "ok";
    if (used > limit) {
        status = "over";
    }
    else if (used >= warnAt) {
        status = "warn";
    }
    metrics.push({
        metric,
        used,
        limit,
        warnAt,
        status,
    });
}
function highestStatus(metrics) {
    if (metrics.some((metric) => metric.status === "over"))
        return "over";
    if (metrics.some((metric) => metric.status === "warn"))
        return "warn";
    return "ok";
}
function normalizeThresholds(input) {
    const warnRatio = input.warnRatio;
    return {
        tokensIn: asPositiveNumber(input.tokensIn),
        tokensOut: asPositiveNumber(input.tokensOut),
        totalTokens: asPositiveNumber(input.totalTokens),
        cost: asPositiveNumber(input.cost),
        warnRatio: typeof warnRatio === "number" && Number.isFinite(warnRatio) && warnRatio > 0 && warnRatio < 1
            ? warnRatio
            : DEFAULT_WARN_RATIO,
    };
}
function asPositiveNumber(input) {
    if (typeof input !== "number" || !Number.isFinite(input) || input <= 0)
        return undefined;
    return input;
}
