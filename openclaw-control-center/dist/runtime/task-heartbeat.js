"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TASK_HEARTBEAT_LOG_PATH = void 0;
exports.runtimeTaskHeartbeatGate = runtimeTaskHeartbeatGate;
exports.selectHeartbeatTasks = selectHeartbeatTasks;
exports.runTaskHeartbeat = runTaskHeartbeat;
exports.readTaskHeartbeatRuns = readTaskHeartbeatRuns;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const config_1 = require("../config");
const task_store_1 = require("./task-store");
const RUNTIME_DIR = (0, node_path_1.join)(process.cwd(), "runtime");
exports.TASK_HEARTBEAT_LOG_PATH = (0, node_path_1.join)(RUNTIME_DIR, "task-heartbeat.log");
const DEFAULT_RECENT_RUN_LIMIT = 20;
const UNASSIGNED_OWNER_VALUES = new Set(["", "unassigned", "none", "n/a", "unknown", "na"]);
function runtimeTaskHeartbeatGate() {
    return {
        enabled: config_1.TASK_HEARTBEAT_ENABLED,
        dryRun: config_1.TASK_HEARTBEAT_DRY_RUN,
        maxTasksPerRun: config_1.TASK_HEARTBEAT_MAX_TASKS_PER_RUN,
        localTokenAuthRequired: config_1.LOCAL_TOKEN_AUTH_REQUIRED,
        localTokenConfigured: config_1.LOCAL_API_TOKEN !== "",
    };
}
function selectHeartbeatTasks(store, maxTasksPerRun) {
    const safeMax = Number.isFinite(maxTasksPerRun) && maxTasksPerRun > 0 ? Math.floor(maxTasksPerRun) : 0;
    if (safeMax === 0)
        return [];
    return store.tasks
        .filter((task) => task.status === "todo" && isAssignedOwner(task.owner))
        .sort(compareHeartbeatCandidateTasks)
        .slice(0, safeMax)
        .map((task) => ({
        projectId: task.projectId,
        taskId: task.taskId,
        title: task.title,
        owner: task.owner,
        dueAt: task.dueAt,
        fromStatus: "todo",
        toStatus: "in_progress",
    }));
}
async function runTaskHeartbeat(options = {}) {
    const gate = options.gate ?? runtimeTaskHeartbeatGate();
    const evaluatedAt = new Date().toISOString();
    try {
        const store = await (0, task_store_1.loadTaskStore)();
        const selections = selectHeartbeatTasks(store, gate.maxTasksPerRun);
        const base = {
            evaluatedAt,
            gate,
            checked: store.tasks.length,
            eligible: store.tasks.filter((task) => task.status === "todo" && isAssignedOwner(task.owner)).length,
            selected: selections.length,
            selections,
            logPath: exports.TASK_HEARTBEAT_LOG_PATH,
        };
        if (!gate.enabled) {
            return await writeHeartbeatAudit({
                ok: false,
                mode: "blocked",
                message: "Task heartbeat is disabled by runtime gate.",
                executed: 0,
                ...base,
            });
        }
        if (gate.maxTasksPerRun <= 0) {
            return await writeHeartbeatAudit({
                ok: false,
                mode: "blocked",
                message: "Task heartbeat maxTasksPerRun must be > 0.",
                executed: 0,
                ...base,
            });
        }
        if (gate.dryRun) {
            return await writeHeartbeatAudit({
                ok: true,
                mode: "dry_run",
                message: selections.length === 0
                    ? "Heartbeat dry-run found no assigned backlog tasks."
                    : `Heartbeat dry-run selected ${selections.length} assigned backlog task(s).`,
                executed: 0,
                ...base,
            });
        }
        if (gate.localTokenAuthRequired && !gate.localTokenConfigured) {
            return await writeHeartbeatAudit({
                ok: false,
                mode: "blocked",
                message: "Task heartbeat live mode requires LOCAL_API_TOKEN when local token auth gate is enabled.",
                executed: 0,
                ...base,
            });
        }
        if (selections.length === 0) {
            return await writeHeartbeatAudit({
                ok: true,
                mode: "live",
                message: "Heartbeat live run found no assigned backlog tasks.",
                executed: 0,
                ...base,
            });
        }
        const selectionKeys = new Set(selections.map((item) => taskSelectionKey(item.projectId, item.taskId)));
        const updatedAt = new Date().toISOString();
        const nextStore = {
            ...store,
            tasks: store.tasks.map((task) => {
                if (!selectionKeys.has(taskSelectionKey(task.projectId, task.taskId))) {
                    return task;
                }
                return {
                    ...task,
                    status: "in_progress",
                    updatedAt,
                };
            }),
            updatedAt,
        };
        const taskStorePath = await (0, task_store_1.saveTaskStore)(nextStore);
        return await writeHeartbeatAudit({
            ok: true,
            mode: "live",
            message: `Heartbeat started ${selections.length} assigned backlog task(s).`,
            executed: selections.length,
            taskStorePath,
            ...base,
        });
    }
    catch (error) {
        return await writeHeartbeatAudit({
            ok: false,
            mode: "blocked",
            message: error instanceof Error ? error.message : "Task heartbeat failed.",
            evaluatedAt,
            gate,
            checked: 0,
            eligible: 0,
            selected: 0,
            executed: 0,
            selections: [],
            logPath: exports.TASK_HEARTBEAT_LOG_PATH,
        });
    }
}
async function readTaskHeartbeatRuns(limit = DEFAULT_RECENT_RUN_LIMIT) {
    const safeLimit = Number.isFinite(limit) && limit > 0 ? Math.min(Math.floor(limit), 200) : DEFAULT_RECENT_RUN_LIMIT;
    try {
        const raw = await (0, promises_1.readFile)(exports.TASK_HEARTBEAT_LOG_PATH, "utf8");
        const lines = raw
            .split(/\r?\n/)
            .map((line) => line.trim())
            .filter((line) => line.length > 0);
        const runs = [];
        for (let index = lines.length - 1; index >= 0; index -= 1) {
            if (runs.length >= safeLimit)
                break;
            try {
                const parsed = JSON.parse(lines[index]);
                if (parsed && typeof parsed === "object" && typeof parsed.evaluatedAt === "string") {
                    runs.push(parsed);
                }
            }
            catch {
                continue;
            }
        }
        return {
            path: exports.TASK_HEARTBEAT_LOG_PATH,
            count: runs.length,
            runs,
        };
    }
    catch {
        return {
            path: exports.TASK_HEARTBEAT_LOG_PATH,
            count: 0,
            runs: [],
        };
    }
}
async function writeHeartbeatAudit(result) {
    await (0, promises_1.mkdir)(RUNTIME_DIR, { recursive: true });
    await (0, promises_1.appendFile)(exports.TASK_HEARTBEAT_LOG_PATH, `${JSON.stringify(result)}\n`, "utf8");
    return result;
}
function compareHeartbeatCandidateTasks(a, b) {
    const dueDiff = compareOptionalIsoAscending(a.dueAt, b.dueAt);
    if (dueDiff !== 0)
        return dueDiff;
    const updatedDiff = compareOptionalIsoAscending(a.updatedAt, b.updatedAt);
    if (updatedDiff !== 0)
        return updatedDiff;
    const ownerDiff = a.owner.localeCompare(b.owner);
    if (ownerDiff !== 0)
        return ownerDiff;
    const projectDiff = a.projectId.localeCompare(b.projectId);
    if (projectDiff !== 0)
        return projectDiff;
    return a.taskId.localeCompare(b.taskId);
}
function compareOptionalIsoAscending(left, right) {
    if (left && right) {
        const leftMs = Date.parse(left);
        const rightMs = Date.parse(right);
        if (Number.isFinite(leftMs) && Number.isFinite(rightMs)) {
            return leftMs - rightMs;
        }
        return left.localeCompare(right);
    }
    if (left)
        return -1;
    if (right)
        return 1;
    return 0;
}
function isAssignedOwner(owner) {
    if (!owner)
        return false;
    const normalized = owner.trim().toLowerCase();
    if (normalized === "")
        return false;
    return !UNASSIGNED_OWNER_VALUES.has(normalized);
}
function taskSelectionKey(projectId, taskId) {
    return `${projectId}::${taskId}`;
}
