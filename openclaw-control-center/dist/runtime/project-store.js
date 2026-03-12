"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ProjectStoreValidationError = exports.PROJECT_STATES = exports.PROJECTS_PATH = void 0;
exports.loadProjectStore = loadProjectStore;
exports.saveProjectStore = saveProjectStore;
exports.listProjects = listProjects;
exports.createProject = createProject;
exports.updateProject = updateProject;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const RUNTIME_DIR = (0, node_path_1.join)(process.cwd(), "runtime");
exports.PROJECTS_PATH = (0, node_path_1.join)(RUNTIME_DIR, "projects.json");
const DEFAULT_WARN_RATIO = 0.8;
const PROJECT_ID_REGEX = /^[A-Za-z0-9._:-]+$/;
exports.PROJECT_STATES = ["planned", "active", "blocked", "done"];
const EMPTY_STORE = {
    projects: [],
    updatedAt: "1970-01-01T00:00:00.000Z",
};
class ProjectStoreValidationError extends Error {
    statusCode;
    issues;
    constructor(message, issues = [], statusCode = 400) {
        super(message);
        this.name = "ProjectStoreValidationError";
        this.statusCode = statusCode;
        this.issues = issues;
    }
}
exports.ProjectStoreValidationError = ProjectStoreValidationError;
async function loadProjectStore() {
    try {
        const raw = await (0, promises_1.readFile)(exports.PROJECTS_PATH, "utf8");
        return normalizeProjectStore(JSON.parse(raw));
    }
    catch {
        return cloneEmptyStore();
    }
}
async function saveProjectStore(next) {
    const normalized = normalizeProjectStore({
        ...next,
        updatedAt: new Date().toISOString(),
    });
    await (0, promises_1.mkdir)(RUNTIME_DIR, { recursive: true });
    await (0, promises_1.writeFile)(exports.PROJECTS_PATH, JSON.stringify(normalized, null, 2), "utf8");
    return exports.PROJECTS_PATH;
}
function listProjects(store) {
    return [...store.projects].sort((a, b) => a.projectId.localeCompare(b.projectId));
}
async function createProject(input) {
    const payload = validateCreateProjectInput(input);
    const store = await loadProjectStore();
    if (store.projects.some((item) => item.projectId === payload.projectId)) {
        throw new ProjectStoreValidationError(`projectId '${payload.projectId}' already exists.`, ["projectId"], 409);
    }
    const now = new Date().toISOString();
    const project = {
        projectId: payload.projectId,
        title: payload.title,
        status: payload.status ?? "planned",
        owner: payload.owner ?? "unassigned",
        budget: normalizeThresholds(undefined),
        updatedAt: now,
    };
    store.projects.push(project);
    store.updatedAt = now;
    const path = await saveProjectStore(store);
    return { path, project };
}
async function updateProject(input) {
    const payload = validateUpdateProjectInput(input);
    const store = await loadProjectStore();
    const project = store.projects.find((item) => item.projectId === payload.projectId);
    if (!project) {
        throw new ProjectStoreValidationError(`projectId '${payload.projectId}' was not found.`, [], 404);
    }
    const now = new Date().toISOString();
    if (payload.title !== undefined)
        project.title = payload.title;
    if (payload.status !== undefined)
        project.status = payload.status;
    if (payload.owner !== undefined)
        project.owner = payload.owner;
    project.updatedAt = now;
    store.updatedAt = now;
    const path = await saveProjectStore(store);
    return { path, project };
}
function validateCreateProjectInput(input) {
    const obj = ensureObject(input, "create project payload");
    const issues = [];
    const projectId = requiredProjectId(obj.projectId, "projectId", issues);
    const title = requiredBoundedString(obj.title, "title", 120, issues);
    const status = optionalProjectState(obj.status, "status", issues);
    const owner = optionalBoundedString(obj.owner, "owner", 80, issues);
    if (issues.length > 0) {
        throw new ProjectStoreValidationError("Invalid create project payload.", issues, 400);
    }
    return { projectId, title, status, owner };
}
function validateUpdateProjectInput(input) {
    const obj = ensureObject(input, "update project payload");
    const issues = [];
    const projectId = requiredProjectId(obj.projectId, "projectId", issues);
    const title = optionalBoundedString(obj.title, "title", 120, issues);
    const status = optionalProjectState(obj.status, "status", issues);
    const owner = optionalBoundedString(obj.owner, "owner", 80, issues);
    if (title === undefined && status === undefined && owner === undefined) {
        issues.push("at least one updatable field is required: title, status, owner");
    }
    if (issues.length > 0) {
        throw new ProjectStoreValidationError("Invalid update project payload.", issues, 400);
    }
    return { projectId, title, status, owner };
}
function normalizeProjectStore(input) {
    const obj = asObject(input);
    if (!obj)
        return cloneEmptyStore();
    return {
        projects: normalizeProjects(asArray(obj.projects)),
        updatedAt: asIsoString(obj.updatedAt),
    };
}
function normalizeProjects(projects) {
    if (!projects)
        return [];
    const unique = new Map();
    for (const input of projects) {
        const project = normalizeProject(input);
        if (!project)
            continue;
        unique.set(project.projectId, project);
    }
    return [...unique.values()].sort((a, b) => a.projectId.localeCompare(b.projectId));
}
function normalizeProject(input) {
    const obj = asObject(input);
    if (!obj)
        return null;
    const projectId = asString(obj.projectId)?.trim();
    if (!projectId || !PROJECT_ID_REGEX.test(projectId))
        return null;
    return {
        projectId,
        title: asString(obj.title)?.trim() || projectId,
        status: normalizeProjectState(asString(obj.status)),
        owner: asString(obj.owner)?.trim() || "unassigned",
        budget: normalizeThresholds(asObject(obj.budget)),
        updatedAt: asIsoString(obj.updatedAt),
    };
}
function normalizeProjectState(input) {
    if (input === "planned" || input === "active" || input === "blocked" || input === "done") {
        return input;
    }
    return "planned";
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
        projects: [],
        updatedAt: EMPTY_STORE.updatedAt,
    };
}
function ensureObject(input, label) {
    const obj = asObject(input);
    if (!obj)
        throw new ProjectStoreValidationError(`${label} must be a JSON object.`, [], 400);
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
function optionalProjectState(value, field, issues) {
    if (value === undefined)
        return undefined;
    if (value === "planned" || value === "active" || value === "blocked" || value === "done") {
        return value;
    }
    issues.push(`${field} must be one of: planned, active, blocked, done`);
    return undefined;
}
function asIsoString(v) {
    if (typeof v === "string" && !Number.isNaN(Date.parse(v)))
        return new Date(v).toISOString();
    return new Date().toISOString();
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
