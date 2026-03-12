"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildActionQueueLinks = buildActionQueueLinks;
const notification_center_1 = require("./notification-center");
const task_store_1 = require("./task-store");
function buildActionQueueLinks(feed, snapshot) {
    const linksByItemId = new Map();
    const tasks = (0, task_store_1.listTasks)(snapshot.tasks, projectTitleMap(snapshot));
    const taskById = new Map(tasks.map((task) => [task.taskId, task]));
    const projectById = new Map(snapshot.projects.projects.map((project) => [project.projectId, project]));
    const approvalById = new Map(snapshot.approvals.map((approval) => [approval.approvalId, approval]));
    const sessionsByAgent = buildSessionsByAgent(snapshot);
    for (const item of feed.items) {
        if (!(item.route === "action-queue" || item.level === "action-required"))
            continue;
        const links = [];
        if (item.source === "session") {
            addSessionLink(links, item.sourceId);
        }
        if (item.source === "task") {
            const task = taskById.get(item.sourceId);
            if (task) {
                addTaskLink(links, task.taskId, task.projectId);
                addProjectLink(links, task.projectId);
                for (const sessionKey of task.sessionKeys) {
                    addSessionLink(links, sessionKey);
                }
            }
        }
        if (item.source === "approval") {
            const approval = approvalById.get(item.sourceId);
            if (approval?.sessionKey) {
                addSessionLink(links, approval.sessionKey);
            }
            if (approval?.agentId) {
                addAgentSessionsLink(links, approval.agentId);
                const sessionKeys = sessionsByAgent.get(approval.agentId) ?? [];
                for (const sessionKey of sessionKeys) {
                    addSessionLink(links, sessionKey);
                }
            }
        }
        if (item.source === "budget") {
            const [scope, scopeId] = splitScopeId(item.sourceId);
            if (scope === "project") {
                if (projectById.has(scopeId))
                    addProjectLink(links, scopeId);
            }
            else if (scope === "task") {
                const task = taskById.get(scopeId);
                if (task) {
                    addTaskLink(links, task.taskId, task.projectId);
                    addProjectLink(links, task.projectId);
                    for (const sessionKey of task.sessionKeys) {
                        addSessionLink(links, sessionKey);
                    }
                }
            }
            else if (scope === "agent") {
                addAgentSessionsLink(links, scopeId);
                const sessionKeys = sessionsByAgent.get(scopeId) ?? [];
                for (const sessionKey of sessionKeys) {
                    addSessionLink(links, sessionKey);
                }
            }
        }
        linksByItemId.set((0, notification_center_1.actionQueueItemId)(item), dedupeLinks(links));
    }
    return linksByItemId;
}
function buildSessionsByAgent(snapshot) {
    const byAgent = new Map();
    for (const session of snapshot.sessions) {
        if (!session.agentId)
            continue;
        const bucket = byAgent.get(session.agentId) ?? [];
        bucket.push(session.sessionKey);
        byAgent.set(session.agentId, bucket);
    }
    return byAgent;
}
function splitScopeId(input) {
    const idx = input.indexOf(":");
    if (idx <= 0 || idx === input.length - 1)
        return ["unknown", input];
    const scope = input.slice(0, idx);
    const scopeId = input.slice(idx + 1);
    if (scope === "agent" || scope === "project" || scope === "task")
        return [scope, scopeId];
    return ["unknown", scopeId];
}
function addSessionLink(links, sessionKey) {
    const key = sessionKey.trim();
    if (!key)
        return;
    links.push({
        type: "session",
        id: key,
        href: `/session/${encodeURIComponent(key)}`,
        label: `session:${key}`,
    });
}
function addTaskLink(links, taskId, projectId) {
    const taskKey = taskId.trim();
    const projectKey = projectId.trim();
    if (!taskKey || !projectKey)
        return;
    links.push({
        type: "task",
        id: taskKey,
        href: `/tasks?project=${encodeURIComponent(projectKey)}`,
        label: `task:${taskKey}`,
    });
}
function addProjectLink(links, projectId) {
    const key = projectId.trim();
    if (!key)
        return;
    links.push({
        type: "project",
        id: key,
        href: `/projects?projectId=${encodeURIComponent(key)}`,
        label: `project:${key}`,
    });
}
function addAgentSessionsLink(links, agentId) {
    const key = agentId.trim();
    if (!key)
        return;
    links.push({
        type: "session",
        id: key,
        href: `/sessions?agentId=${encodeURIComponent(key)}`,
        label: `agent:${key}`,
    });
}
function dedupeLinks(links) {
    const seen = new Set();
    const out = [];
    for (const link of links) {
        const key = `${link.type}|${link.id}|${link.href}`;
        if (seen.has(key))
            continue;
        seen.add(key);
        out.push(link);
    }
    return out;
}
function projectTitleMap(snapshot) {
    return new Map(snapshot.projects.projects.map((project) => [project.projectId, project.title]));
}
