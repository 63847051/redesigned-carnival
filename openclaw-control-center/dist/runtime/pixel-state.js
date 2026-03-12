"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildPixelState = buildPixelState;
function buildPixelState(snapshot) {
    const generatedAt = new Date().toISOString();
    const rooms = [
        {
            id: "room:ops",
            label: "Ops",
            kind: "ops",
            x: 0,
            y: 0,
            w: 24,
            h: 18,
        },
    ];
    const projectSet = new Set(snapshot.projects.projects.map((project) => project.projectId));
    const tasksByProject = new Map();
    const backlogTasks = [];
    for (const task of snapshot.tasks.tasks) {
        if (!projectSet.has(task.projectId)) {
            backlogTasks.push(task);
            continue;
        }
        const list = tasksByProject.get(task.projectId) ?? [];
        list.push(task);
        tasksByProject.set(task.projectId, list);
    }
    const roomByProjectId = new Map();
    for (const [idx, project] of snapshot.projects.projects.entries()) {
        const row = Math.floor(idx / 3);
        const col = idx % 3;
        const roomId = `room:project:${project.projectId}`;
        roomByProjectId.set(project.projectId, roomId);
        rooms.push({
            id: roomId,
            label: project.title,
            kind: "project",
            x: 24 + col * 24,
            y: row * 16,
            w: 23,
            h: 15,
            status: project.status,
        });
    }
    if (backlogTasks.length > 0) {
        rooms.push({
            id: "room:backlog",
            label: "Backlog",
            kind: "backlog",
            x: 24,
            y: Math.max(1, Math.ceil(snapshot.projects.projects.length / 3)) * 16,
            w: 23,
            h: 15,
            status: "todo",
        });
    }
    const entitiesById = new Map();
    const linksById = new Map();
    for (const [idx, project] of snapshot.projects.projects.entries()) {
        const roomId = roomByProjectId.get(project.projectId);
        addEntity(entitiesById, {
            id: `project:${project.projectId}`,
            roomId,
            kind: "project",
            label: project.title,
            status: project.status,
            ...slotCoords(0, idx),
        });
    }
    for (const [projectId, tasks] of tasksByProject.entries()) {
        const roomId = roomByProjectId.get(projectId);
        for (const [idx, task] of tasks.entries()) {
            const entityId = taskEntityId(task.projectId, task.taskId);
            addEntity(entitiesById, {
                id: entityId,
                roomId,
                kind: "task",
                label: task.title,
                status: task.status,
                ...slotCoords(1, idx),
            });
            addLink(linksById, {
                id: `project_task:${task.projectId}:${task.taskId}`,
                from: `project:${task.projectId}`,
                to: entityId,
                type: "project_task",
            });
        }
    }
    for (const [idx, task] of backlogTasks.entries()) {
        addEntity(entitiesById, {
            id: taskEntityId(task.projectId, task.taskId),
            roomId: "room:backlog",
            kind: "task",
            label: task.title,
            status: task.status,
            ...slotCoords(0, idx),
        });
    }
    const sessionByKey = new Map(snapshot.sessions.map((session) => [session.sessionKey, session]));
    const sessionsWithEntity = new Set();
    for (const [idx, session] of snapshot.sessions.entries()) {
        sessionsWithEntity.add(session.sessionKey);
        addEntity(entitiesById, {
            id: `session:${session.sessionKey}`,
            roomId: "room:ops",
            kind: "session",
            label: session.label ?? session.sessionKey,
            status: session.state,
            ...slotCoords(0, idx),
        });
        if (session.agentId) {
            addEntity(entitiesById, {
                id: `agent:${session.agentId}`,
                roomId: "room:ops",
                kind: "agent",
                label: session.agentId,
                ...slotCoords(1, hashIndex(session.agentId)),
            });
            addLink(linksById, {
                id: `agent_session:${session.agentId}:${session.sessionKey}`,
                from: `agent:${session.agentId}`,
                to: `session:${session.sessionKey}`,
                type: "agent_session",
            });
        }
    }
    for (const task of snapshot.tasks.tasks) {
        for (const [idx, sessionKey] of task.sessionKeys.entries()) {
            if (!sessionsWithEntity.has(sessionKey)) {
                sessionsWithEntity.add(sessionKey);
                const session = sessionByKey.get(sessionKey);
                addEntity(entitiesById, {
                    id: `session:${sessionKey}`,
                    roomId: "room:ops",
                    kind: "session",
                    label: session?.label ?? sessionKey,
                    status: session?.state ?? "unknown",
                    ...slotCoords(0, entitiesById.size + idx),
                });
                if (session?.agentId) {
                    addEntity(entitiesById, {
                        id: `agent:${session.agentId}`,
                        roomId: "room:ops",
                        kind: "agent",
                        label: session.agentId,
                        ...slotCoords(1, hashIndex(session.agentId)),
                    });
                    addLink(linksById, {
                        id: `agent_session:${session.agentId}:${sessionKey}`,
                        from: `agent:${session.agentId}`,
                        to: `session:${sessionKey}`,
                        type: "agent_session",
                    });
                }
            }
            addLink(linksById, {
                id: `task_session:${task.projectId}:${task.taskId}:${sessionKey}`,
                from: taskEntityId(task.projectId, task.taskId),
                to: `session:${sessionKey}`,
                type: "task_session",
            });
        }
    }
    const entities = [...entitiesById.values()].sort((a, b) => a.id.localeCompare(b.id));
    const links = [...linksById.values()].sort((a, b) => a.id.localeCompare(b.id));
    return {
        generatedAt,
        snapshotGeneratedAt: snapshot.generatedAt,
        rooms: rooms.sort((a, b) => a.id.localeCompare(b.id)),
        entities,
        links,
        counts: {
            rooms: rooms.length,
            entities: entities.length,
            links: links.length,
            projects: entities.filter((entity) => entity.kind === "project").length,
            tasks: entities.filter((entity) => entity.kind === "task").length,
            sessions: entities.filter((entity) => entity.kind === "session").length,
            agents: entities.filter((entity) => entity.kind === "agent").length,
        },
    };
}
function slotCoords(lane, index) {
    const col = index % 4;
    const row = Math.floor(index / 4);
    return {
        x: 2 + col * 5,
        y: 2 + lane * 6 + row * 2,
    };
}
function hashIndex(input) {
    let hash = 0;
    for (const ch of input) {
        hash = (hash * 31 + ch.charCodeAt(0)) >>> 0;
    }
    return hash % 12;
}
function taskEntityId(projectId, taskId) {
    return `task:${projectId}:${taskId}`;
}
function addEntity(target, entity) {
    if (target.has(entity.id))
        return;
    target.set(entity.id, entity);
}
function addLink(target, link) {
    if (target.has(link.id))
        return;
    target.set(link.id, link);
}
