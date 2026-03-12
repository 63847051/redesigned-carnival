"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TaskStoreValidationError = exports.TASKS_PATH = void 0;
exports.loadTaskStore = loadTaskStore;
exports.saveTaskStore = saveTaskStore;
exports.listTasks = listTasks;
exports.createTask = createTask;
exports.updateTaskStatus = updateTaskStatus;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const project_store_1 = require("./project-store");
const RUNTIME_DIR = (0, node_path_1.join)(process.cwd(), "runtime");
exports.TASKS_PATH = (0, node_path_1.join)(RUNTIME_DIR, "tasks.json");
const DEFAULT_WARN_RATIO = 0.8;
const PROJECT_ID_REGEX = /^[A-Za-z0-9._:-]+$/;
const TASK_ID_REGEX = /^[A-Za-z0-9._:-]+$/;
const EMPTY_STORE = {
    tasks: [],
    agentBudgets: [],
    updatedAt: "1970-01-01T00:00:00.000Z",
};
class TaskStoreValidationError extends Error {
    statusCode;
    issues;
    constructor(message, issues = [], statusCode = 400) {
        super(message);
        this.name = "TaskStoreValidationError";
        this.issues = issues;
        this.statusCode = statusCode;
    }
}
exports.TaskStoreValidationError = TaskStoreValidationError;
async function loadTaskStore() {
    try {
        const raw = await (0, promises_1.readFile)(exports.TASKS_PATH, "utf8");
        return normalizeTaskStore(JSON.parse(raw));
    }
    catch {
        return cloneEmptyStore();
    }
}
async function saveTaskStore(next) {
    const normalized = normalizeTaskStore({
        ...next,
        updatedAt: new Date().toISOString(),
    });
    await (0, promises_1.mkdir)(RUNTIME_DIR, { recursive: true });
    await (0, promises_1.writeFile)(exports.TASKS_PATH, JSON.stringify(normalized, null, 2), "utf8");
    return exports.TASKS_PATH;
}
function listTasks(store, projectTitleById = new Map()) {
    return [...store.tasks]
        .map((task) => ({
        projectId: task.projectId,
        projectTitle: projectTitleById.get(task.projectId) ?? task.projectId,
        taskId: task.taskId,
        title: task.title,
        status: task.status,
        owner: task.owner,
        dueAt: task.dueAt,
        sessionKeys: task.sessionKeys,
        updatedAt: task.updatedAt,
    }))
        .sort((a, b) => {
        if (a.dueAt && b.dueAt)
            return a.dueAt.localeCompare(b.dueAt);
        if (a.dueAt)
            return -1;
        if (b.dueAt)
            return 1;
        return a.taskId.localeCompare(b.taskId);
    });
}
async function createTask(input) {
    const payload = validateCreateTaskInput(input);
    const [store, projectStore] = await Promise.all([loadTaskStore(), (0, project_store_1.loadProjectStore)()]);
    const project = projectStore.projects.find((item) => item.projectId === payload.projectId);
    if (!project) {
        throw new TaskStoreValidationError(`projectId '${payload.projectId}' not found.`, ["projectId"], 404);
    }
    if (findTaskMatches(store, payload.taskId).length > 0) {
        throw new TaskStoreValidationError(`taskId '${payload.taskId}' already exists.`, ["taskId"], 409);
    }
    const now = new Date().toISOString();
    const task = {
        projectId: payload.projectId,
        taskId: payload.taskId,
        title: payload.title,
        status: payload.status ?? "todo",
        owner: payload.owner ?? "unassigned",
        dueAt: payload.dueAt,
        definitionOfDone: payload.definitionOfDone ?? [],
        artifacts: payload.artifacts ?? [],
        rollback: payload.rollback ?? {
            strategy: "manual-rollback",
            steps: [],
        },
        sessionKeys: payload.sessionKeys ?? [],
        budget: payload.budget ?? normalizeThresholds(undefined),
        updatedAt: now,
    };
    store.tasks.push(task);
    store.updatedAt = now;
    const path = await saveTaskStore(store);
    return {
        path,
        projectId: task.projectId,
        projectTitle: project.title,
        task,
    };
}
async function updateTaskStatus(input) {
    const payload = validateUpdateTaskStatusInput(input);
    const [store, projectStore] = await Promise.all([loadTaskStore(), (0, project_store_1.loadProjectStore)()]);
    const matches = findTaskMatches(store, payload.taskId, payload.projectId);
    if (matches.length === 0) {
        throw new TaskStoreValidationError(`taskId '${payload.taskId}' was not found${payload.projectId ? ` in project '${payload.projectId}'` : ""}.`, [], 404);
    }
    if (matches.length > 1) {
        throw new TaskStoreValidationError(`taskId '${payload.taskId}' is ambiguous. Provide projectId.`, ["projectId"], 409);
    }
    const target = matches[0];
    const project = projectStore.projects.find((item) => item.projectId === target.task.projectId);
    if (!project) {
        throw new TaskStoreValidationError(`projectId '${target.task.projectId}' referenced by task '${target.task.taskId}' was not found.`, ["projectId"], 409);
    }
    const now = new Date().toISOString();
    target.task.status = payload.status;
    target.task.updatedAt = now;
    store.updatedAt = now;
    const path = await saveTaskStore(store);
    return {
        path,
        projectId: target.task.projectId,
        projectTitle: project.title,
        task: target.task,
    };
}
function findTaskMatches(store, taskId, projectId) {
    const matches = [];
    for (const task of store.tasks) {
        if (projectId && task.projectId !== projectId)
            continue;
        if (task.taskId === taskId) {
            matches.push({ task });
        }
    }
    return matches;
}
function validateCreateTaskInput(input) {
    const obj = ensureObject(input, "create task payload");
    const issues = [];
    const projectId = requiredProjectId(obj.projectId, "projectId", issues);
    const taskId = requiredTaskId(obj.taskId, "taskId", issues);
    const title = requiredBoundedString(obj.title, "title", 180, issues);
    const status = optionalTaskState(obj.status, "status", issues);
    const owner = optionalBoundedString(obj.owner, "owner", 80, issues);
    const dueAt = optionalIsoString(obj.dueAt, "dueAt", issues);
    const definitionOfDone = optionalStringArray(obj.definitionOfDone, "definitionOfDone", issues);
    const sessionKeys = optionalStringArray(obj.sessionKeys, "sessionKeys", issues);
    const artifacts = optionalArtifacts(obj.artifacts, "artifacts", issues);
    const rollback = optionalRollback(obj.rollback, "rollback", issues);
    const budget = optionalBudget(obj.budget, "budget", issues);
    if (issues.length > 0) {
        throw new TaskStoreValidationError("Invalid create task payload.", issues, 400);
    }
    return {
        projectId,
        taskId,
        title,
        status,
        owner,
        dueAt,
        definitionOfDone,
        sessionKeys,
        artifacts,
        rollback,
        budget,
    };
}
function validateUpdateTaskStatusInput(input) {
    const obj = ensureObject(input, "update task status payload");
    const issues = [];
    const taskId = requiredTaskId(obj.taskId, "taskId", issues);
    const projectId = optionalProjectId(obj.projectId, "projectId", issues);
    const status = requiredTaskState(obj.status, "status", issues);
    if (issues.length > 0) {
        throw new TaskStoreValidationError("Invalid update status payload.", issues, 400);
    }
    return { taskId, status, projectId };
}
function normalizeTaskStore(input) {
    const obj = asObject(input);
    if (!obj)
        return cloneEmptyStore();
    const tasks = normalizeTasks(asArray(obj.tasks)) ??
        normalizeLegacyProjectTasks(asArray(obj.projects));
    return {
        tasks,
        agentBudgets: normalizeAgentBudgets(asArray(obj.agentBudgets)),
        updatedAt: asIsoString(obj.updatedAt),
    };
}
function normalizeLegacyProjectTasks(projects) {
    if (!projects)
        return [];
    const out = [];
    for (const project of projects) {
        const projectObj = asObject(project);
        if (!projectObj)
            continue;
        const projectId = asString(projectObj.projectId);
        if (!projectId)
            continue;
        const tasks = asArray(projectObj.tasks);
        if (!tasks)
            continue;
        for (const task of tasks) {
            const normalized = normalizeTask(task, projectId);
            if (normalized)
                out.push(normalized);
        }
    }
    return out;
}
function normalizeTasks(tasks) {
    if (!tasks)
        return undefined;
    return tasks
        .map((task) => normalizeTask(task))
        .filter((task) => Boolean(task));
}
function normalizeTask(input, fallbackProjectId) {
    const obj = asObject(input);
    if (!obj)
        return null;
    const taskId = asString(obj.taskId);
    if (!taskId)
        return null;
    const projectId = asString(obj.projectId) ?? fallbackProjectId;
    if (!projectId)
        return null;
    return {
        projectId,
        taskId,
        title: asString(obj.title) ?? taskId,
        status: normalizeTaskState(asString(obj.status)),
        owner: asString(obj.owner) ?? "unassigned",
        dueAt: asOptionalIsoString(obj.dueAt),
        definitionOfDone: toStringArray(obj.definitionOfDone),
        artifacts: normalizeArtifacts(asArray(obj.artifacts)),
        rollback: normalizeRollback(asObject(obj.rollback)),
        sessionKeys: toStringArray(obj.sessionKeys),
        budget: normalizeThresholds(asObject(obj.budget)),
        updatedAt: asIsoString(obj.updatedAt),
    };
}
function normalizeAgentBudgets(agentBudgets) {
    if (!agentBudgets)
        return [];
    return agentBudgets
        .map((agentBudget) => normalizeAgentBudget(agentBudget))
        .filter((agentBudget) => Boolean(agentBudget));
}
function normalizeAgentBudget(input) {
    const obj = asObject(input);
    if (!obj)
        return null;
    const agentId = asString(obj.agentId);
    if (!agentId)
        return null;
    return {
        agentId,
        label: asString(obj.label),
        thresholds: normalizeThresholds(asObject(obj.thresholds)),
    };
}
function normalizeArtifacts(artifacts) {
    if (!artifacts)
        return [];
    const normalized = [];
    for (const item of artifacts) {
        const obj = asObject(item);
        if (!obj)
            continue;
        const artifactId = asString(obj.artifactId);
        const label = asString(obj.label);
        const location = asString(obj.location);
        if (!artifactId || !label || !location)
            continue;
        const type = asString(obj.type);
        normalized.push({
            artifactId,
            type: type === "code" || type === "doc" || type === "link" || type === "other" ? type : "other",
            label,
            location,
        });
    }
    return normalized;
}
function normalizeRollback(input) {
    if (!input) {
        return {
            strategy: "manual-rollback",
            steps: [],
        };
    }
    return {
        strategy: asString(input.strategy) ?? "manual-rollback",
        steps: toStringArray(input.steps),
        verification: asString(input.verification),
    };
}
function normalizeTaskState(input) {
    if (input === "todo" || input === "in_progress" || input === "blocked" || input === "done") {
        return input;
    }
    return "todo";
}
function normalizeThresholds(input) {
    const warnRatio = asNumber(input?.warnRatio) ?? DEFAULT_WARN_RATIO;
    return {
        tokensIn: asPositiveNumber(input?.tokensIn),
        tokensOut: asPositiveNumber(input?.tokensOut),
        totalTokens: asPositiveNumber(input?.totalTokens),
        cost: asPositiveNumber(input?.cost),
        warnRatio: warnRatio > 0 && warnRatio < 1 ? warnRatio : DEFAULT_WARN_RATIO,
    };
}
function cloneEmptyStore() {
    return {
        tasks: [],
        agentBudgets: [],
        updatedAt: EMPTY_STORE.updatedAt,
    };
}
function ensureObject(input, label) {
    const obj = asObject(input);
    if (!obj)
        throw new TaskStoreValidationError(`${label} must be a JSON object.`, [], 400);
    return obj;
}
function requiredProjectId(value, field, issues) {
    if (typeof value !== "string" || value.trim() === "") {
        issues.push(`${field} must be a non-empty string`);
        return "";
    }
    const trimmed = value.trim();
    if (!PROJECT_ID_REGEX.test(trimmed)) {
        issues.push(`${field} may only contain letters, numbers, '.', '_', ':', '-'`);
    }
    if (trimmed.length > 100) {
        issues.push(`${field} must be <= 100 characters`);
    }
    return trimmed;
}
function optionalProjectId(value, field, issues) {
    if (value === undefined)
        return undefined;
    return requiredProjectId(value, field, issues);
}
function requiredTaskId(value, field, issues) {
    if (typeof value !== "string" || value.trim() === "") {
        issues.push(`${field} must be a non-empty string`);
        return "";
    }
    const trimmed = value.trim();
    if (!TASK_ID_REGEX.test(trimmed)) {
        issues.push(`${field} may only contain letters, numbers, '.', '_', ':', '-'`);
    }
    if (trimmed.length > 120) {
        issues.push(`${field} must be <= 120 characters`);
    }
    return trimmed;
}
function requiredBoundedString(value, field, maxLength, issues) {
    if (typeof value !== "string" || value.trim() === "") {
        issues.push(`${field} must be a non-empty string`);
        return "";
    }
    const trimmed = value.trim();
    if (trimmed.length > maxLength) {
        issues.push(`${field} must be <= ${maxLength} characters`);
    }
    return trimmed;
}
function optionalBoundedString(value, field, maxLength, issues) {
    if (value === undefined)
        return undefined;
    if (typeof value !== "string") {
        issues.push(`${field} must be a string`);
        return undefined;
    }
    const trimmed = value.trim();
    if (!trimmed) {
        issues.push(`${field} cannot be empty when provided`);
        return undefined;
    }
    if (trimmed.length > maxLength) {
        issues.push(`${field} must be <= ${maxLength} characters`);
        return undefined;
    }
    return trimmed;
}
function optionalStringArray(value, field, issues) {
    if (value === undefined)
        return undefined;
    if (!Array.isArray(value) || value.some((item) => typeof item !== "string")) {
        issues.push(`${field} must be an array of strings`);
        return undefined;
    }
    const out = [...new Set(value.map((item) => item.trim()).filter((item) => item.length > 0))];
    if (out.some((item) => item.length > 200)) {
        issues.push(`${field} values must be <= 200 characters`);
    }
    return out;
}
function optionalIsoString(value, field, issues) {
    if (value === undefined)
        return undefined;
    if (typeof value !== "string" || Number.isNaN(Date.parse(value))) {
        issues.push(`${field} must be an ISO date-time string`);
        return undefined;
    }
    return new Date(value).toISOString();
}
function optionalTaskState(value, field, issues) {
    if (value === undefined)
        return undefined;
    return requiredTaskState(value, field, issues);
}
function requiredTaskState(value, field, issues) {
    if (value === "todo" || value === "in_progress" || value === "blocked" || value === "done") {
        return value;
    }
    issues.push(`${field} must be one of: todo, in_progress, blocked, done`);
    return "todo";
}
function optionalArtifacts(value, field, issues) {
    if (value === undefined)
        return undefined;
    if (!Array.isArray(value)) {
        issues.push(`${field} must be an array`);
        return undefined;
    }
    const artifacts = [];
    value.forEach((item, idx) => {
        const obj = asObject(item);
        if (!obj) {
            issues.push(`${field}[${idx}] must be an object`);
            return;
        }
        const artifactId = requiredBoundedString(obj.artifactId, `${field}[${idx}].artifactId`, 120, issues);
        const label = requiredBoundedString(obj.label, `${field}[${idx}].label`, 180, issues);
        const location = requiredBoundedString(obj.location, `${field}[${idx}].location`, 200, issues);
        const rawType = obj.type;
        const type = rawType === "code" || rawType === "doc" || rawType === "link" || rawType === "other"
            ? rawType
            : undefined;
        if (!type) {
            issues.push(`${field}[${idx}].type must be one of: code, doc, link, other`);
            return;
        }
        artifacts.push({ artifactId, type, label, location });
    });
    return artifacts;
}
function optionalRollback(value, field, issues) {
    if (value === undefined)
        return undefined;
    const obj = asObject(value);
    if (!obj) {
        issues.push(`${field} must be an object`);
        return undefined;
    }
    const strategy = requiredBoundedString(obj.strategy, `${field}.strategy`, 120, issues);
    const steps = optionalStringArray(obj.steps, `${field}.steps`, issues) ?? [];
    const verification = optionalBoundedString(obj.verification, `${field}.verification`, 220, issues);
    return { strategy, steps, verification };
}
function optionalBudget(value, field, issues) {
    if (value === undefined)
        return undefined;
    const obj = asObject(value);
    if (!obj) {
        issues.push(`${field} must be an object`);
        return undefined;
    }
    const numericFields = [
        "tokensIn",
        "tokensOut",
        "totalTokens",
        "cost",
        "warnRatio",
    ];
    for (const key of numericFields) {
        const raw = obj[key];
        if (raw === undefined)
            continue;
        if (typeof raw !== "number" || !Number.isFinite(raw)) {
            issues.push(`${field}.${key} must be a finite number`);
        }
    }
    const warnRatio = obj.warnRatio;
    if (typeof warnRatio === "number" && (warnRatio <= 0 || warnRatio >= 1)) {
        issues.push(`${field}.warnRatio must be > 0 and < 1`);
    }
    return normalizeThresholds(obj);
}
function asIsoString(v) {
    if (typeof v === "string" && !Number.isNaN(Date.parse(v)))
        return new Date(v).toISOString();
    return new Date().toISOString();
}
function asOptionalIsoString(v) {
    if (typeof v !== "string")
        return undefined;
    if (Number.isNaN(Date.parse(v)))
        return undefined;
    return new Date(v).toISOString();
}
function toStringArray(v) {
    if (!Array.isArray(v))
        return [];
    return [...new Set(v
            .filter((item) => typeof item === "string")
            .map((item) => item.trim())
            .filter((item) => item.length > 0))];
}
function asObject(v) {
    return v !== null && typeof v === "object" && !Array.isArray(v) ? v : undefined;
}
function asArray(v) {
    return Array.isArray(v) ? v : undefined;
}
function asString(v) {
    return typeof v === "string" ? v : undefined;
}
function asNumber(v) {
    return typeof v === "number" && Number.isFinite(v) ? v : undefined;
}
function asPositiveNumber(v) {
    const parsed = asNumber(v);
    if (parsed === undefined || parsed <= 0)
        return undefined;
    return parsed;
}
